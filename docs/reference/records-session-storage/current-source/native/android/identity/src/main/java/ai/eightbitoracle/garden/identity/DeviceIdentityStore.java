package ai.eightbitoracle.garden.identity;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.AtomicFile;
import android.util.Base64;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.UUID;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import org.json.JSONObject;

/** One installation-owned identity, saved before any device claim is sent. */
final class DeviceIdentityStore {
    private static final String KEY_ALIAS = "garden_device_identity_v1";
    private static final byte[] AAD = "GardenDeviceIdentity:v1".getBytes(StandardCharsets.UTF_8);
    private static final int BASE64_FLAGS = Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING;
    private final AtomicFile file;

    DeviceIdentityStore(Context context) {
        file = new AtomicFile(new File(context.getNoBackupFilesDir(), "garden-device-identity.bin"));
    }

    synchronized JSONObject readOrCreate() throws Exception {
        byte[] encrypted;
        try {
            encrypted = file.readFully();
        } catch (java.io.FileNotFoundException missing) {
            // Only absence creates an identity. Corruption or inaccessible storage fails.
            if (file.getBaseFile().exists()) throw missing;
            byte[] secret = new byte[32];
            new SecureRandom().nextBytes(secret);
            JSONObject identity = new JSONObject()
                    .put("anonymousId", UUID.randomUUID().toString())
                    .put("secret", Base64.encodeToString(secret, BASE64_FLAGS));
            save(identity);
            return identity;
        }
        if (encrypted.length < 30 || encrypted[0] != 1) throw new IllegalStateException("Invalid identity envelope");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, key(false), new GCMParameterSpec(128, Arrays.copyOfRange(encrypted, 1, 13)));
        cipher.updateAAD(AAD);
        JSONObject identity = new JSONObject(new String(cipher.doFinal(Arrays.copyOfRange(encrypted, 13, encrypted.length)), StandardCharsets.UTF_8));
        UUID id = UUID.fromString(identity.getString("anonymousId"));
        if (id.version() != 4 || !id.toString().equals(identity.getString("anonymousId")))
            throw new IllegalStateException("Invalid installation id");
        if (Base64.decode(identity.getString("secret"), BASE64_FLAGS).length != 32)
            throw new IllegalStateException("Invalid device credential");
        return identity;
    }

    private SecretKey key(boolean create) throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        if (store.containsAlias(KEY_ALIAS)) return (SecretKey) store.getKey(KEY_ALIAS, null);
        if (!create) throw new IllegalStateException("Device identity key unavailable");
        KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256).build());
        return generator.generateKey();
    }

    private void save(JSONObject identity) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key(true));
        cipher.updateAAD(AAD);
        byte[] iv = cipher.getIV();
        if (iv.length != 12) throw new IllegalStateException("Unexpected identity nonce size");
        byte[] ciphertext = cipher.doFinal(identity.toString().getBytes(StandardCharsets.UTF_8));
        FileOutputStream output = file.startWrite();
        try {
            output.write(1);
            output.write(iv);
            output.write(ciphertext);
            file.finishWrite(output);
            byte[] persisted = file.readFully();
            byte[] expected = new byte[1 + iv.length + ciphertext.length];
            expected[0] = 1;
            System.arraycopy(iv, 0, expected, 1, iv.length);
            System.arraycopy(ciphertext, 0, expected, 1 + iv.length, ciphertext.length);
            if (!Arrays.equals(persisted, expected)) throw new IllegalStateException("Identity was not persisted");
        } catch (Exception failure) {
            file.failWrite(output);
            throw failure;
        }
    }

    synchronized String claimBody() throws Exception {
        JSONObject identity = readOrCreate();
        byte[] secret = Base64.decode(identity.getString("secret"), BASE64_FLAGS);
        return new JSONObject().put("anonymousId", identity.getString("anonymousId"))
                .put("secretHash", RequestSigner.hex(MessageDigest.getInstance("SHA-256").digest(secret)))
                .put("platform", "android").toString();
    }

    synchronized String credential() throws Exception { return readOrCreate().getString("secret"); }
}
