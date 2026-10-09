package ai.eightbitoracle.garden.identity;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.AtomicFile;
import java.io.File;
import java.io.ByteArrayOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.Arrays;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/** One active owner, with persistent revisions. Invoke off the main thread.
 * AtomicFile does not lock; serialize all same-process readers and writers here.
 * The current Garden addon has one process. A multiprocess caller needs an OS lock.
 */
final class RecordsSessionStore {
    private static final Object STORAGE_LOCK = new Object();
    private static final String KEY_ALIAS = "garden_records_session_v1";
    private static final byte[] AAD = "GardenRecordsSession:v1".getBytes(StandardCharsets.UTF_8);
    private final AtomicFile file;

    RecordsSessionStore(Context context) {
        file = new AtomicFile(new File(context.getNoBackupFilesDir(), "garden-records-session.bin"));
    }

    RecordsSessionState readOrCreate() throws Exception {
        synchronized (STORAGE_LOCK) {
            byte[] envelope;
            try {
                envelope = readEnvelope();
            } catch (java.io.FileNotFoundException missing) {
                if (file.getBaseFile().exists()) throw missing;
                RecordsSessionState empty = RecordsSessionState.next(null);
                write(empty, true);
                return empty;
            }
            if (envelope.length < 30 || envelope.length > 20029 || envelope[0] != 1)
                throw new IllegalStateException("Invalid Records envelope");
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.DECRYPT_MODE, key(false),
                    new GCMParameterSpec(128, Arrays.copyOfRange(envelope, 1, 13)));
            cipher.updateAAD(AAD);
            return RecordsStateCodec.decode(cipher.doFinal(Arrays.copyOfRange(envelope, 13, envelope.length)));
        }
    }

    boolean install(String expectedRevision, RecordsCredentials verified) throws Exception {
        if (verified == null) throw new IllegalArgumentException("Missing verified Records response");
        synchronized (STORAGE_LOCK) {
            RecordsSessionState current = readOrCreate();
            if (!current.revision.equals(expectedRevision)) return false;
            write(RecordsSessionState.next(verified), false);
            return true;
        }
    }

    boolean rotate(RecordsRefreshLease expected, RecordsCredentials verified) throws Exception {
        if (verified == null) throw new IllegalArgumentException("Missing verified refresh response");
        synchronized (STORAGE_LOCK) {
            RecordsSessionState current = readOrCreate();
            if (!current.canRefresh(expected) || !expected.owner.owner.equals(verified.owner)) return false;
            write(current.rotated(verified), false);
            return true;
        }
    }

    boolean isCurrent(RecordsOwnerLease expected) throws Exception {
        synchronized (STORAGE_LOCK) { return readOrCreate().canPublish(expected); }
    }

    /** Check and publish in the same lock. A queued UI callback must revalidate there too. */
    boolean publishCurrent(RecordsOwnerLease expected, Runnable publication) throws Exception {
        synchronized (STORAGE_LOCK) {
            if (!readOrCreate().canPublish(expected)) return false;
            publication.run();
            return true;
        }
    }

    void signOut() throws Exception {
        synchronized (STORAGE_LOCK) {
            readOrCreate(); // Validate existing storage; never erase a corrupt envelope silently.
            write(RecordsSessionState.next(null), false);
        }
    }

    private SecretKey key(boolean create) throws Exception {
        KeyStore keys = KeyStore.getInstance("AndroidKeyStore");
        keys.load(null);
        if (keys.containsAlias(KEY_ALIAS)) return (SecretKey) keys.getKey(KEY_ALIAS, null);
        if (!create) throw new IllegalStateException("Records session key unavailable");
        KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256).build());
        return generator.generateKey();
    }

    private byte[] readEnvelope() throws Exception {
        try (FileInputStream input = file.openRead()) {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            byte[] chunk = new byte[4096];
            int count;
            while ((count = input.read(chunk)) != -1) {
                if (bytes.size() + count > 20029) throw new IllegalStateException("Records envelope too large");
                bytes.write(chunk, 0, count);
            }
            return bytes.toByteArray();
        }
    }

    private void write(RecordsSessionState state, boolean createKey) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key(createKey));
        cipher.updateAAD(AAD);
        byte[] iv = cipher.getIV();
        if (iv.length != 12) throw new IllegalStateException("Unexpected Records nonce size");
        byte[] encrypted = cipher.doFinal(RecordsStateCodec.encode(state));
        byte[] envelope = new byte[13 + encrypted.length];
        envelope[0] = 1;
        System.arraycopy(iv, 0, envelope, 1, 12);
        System.arraycopy(encrypted, 0, envelope, 13, encrypted.length);
        FileOutputStream out = file.startWrite();
        boolean finished = false;
        try {
            out.write(envelope);
            file.finishWrite(out);
            finished = true;
            if (!Arrays.equals(file.readFully(), envelope))
                throw new IllegalStateException("Records session was not persisted");
        } catch (Exception failure) {
            if (!finished) file.failWrite(out);
            throw failure;
        }
    }
}
