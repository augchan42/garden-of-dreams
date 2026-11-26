package ai.eightbitoracle.garden.identity;

import android.content.Context;
import android.util.AtomicFile;
import android.util.Base64;
import androidx.test.platform.app.InstrumentationRegistry;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.UUID;
import org.json.JSONObject;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public final class DeviceIdentityStoreTest {
    private Context context;
    private File file;

    @Before public void prepare() throws Exception {
        context = InstrumentationRegistry.getInstrumentation().getTargetContext();
        // All destructive fixtures are restricted to this dedicated test package.
        assertEquals("ai.eightbitoracle.garden.identity.tests", context.getPackageName());
        file = new File(context.getNoBackupFilesDir(), "garden-device-identity.bin");
        cleanup();
    }

    @After public void cleanup() throws Exception {
        if (file == null) return;
        new AtomicFile(file).delete();
        KeyStore keys = KeyStore.getInstance("AndroidKeyStore");
        keys.load(null);
        keys.deleteEntry("garden_device_identity_v1");
    }

    @Test public void persistentCredentialMatchesClaim() throws Exception {
        DeviceIdentityStore first = new DeviceIdentityStore(context);
        String body = first.claimBody();
        JSONObject claim = new JSONObject(body);
        assertEquals(4, UUID.fromString(claim.getString("anonymousId")).version());
        assertEquals("android", claim.getString("platform"));
        byte[] secret = Base64.decode(first.credential(), Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
        assertEquals(32, secret.length);
        assertEquals(RequestSigner.hex(MessageDigest.getInstance("SHA-256").digest(secret)), claim.getString("secretHash"));
        DeviceIdentityStore reopened = new DeviceIdentityStore(context);
        assertEquals(body, reopened.claimBody());
        assertTrue(Arrays.equals(secret, Base64.decode(reopened.credential(), Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING)));
        String ciphertext = new String(new AtomicFile(file).readFully(), StandardCharsets.ISO_8859_1);
        assertFalse(ciphertext.contains(claim.getString("anonymousId")));
        assertFalse(ciphertext.contains(first.credential()));
    }

    @Test public void corruptedCiphertextFailsWithoutReplacingIdentity() throws Exception {
        new DeviceIdentityStore(context).claimBody();
        byte[] damaged = new AtomicFile(file).readFully();
        damaged[damaged.length - 1] ^= 1;
        try (FileOutputStream output = new FileOutputStream(file)) { output.write(damaged); }
        try {
            new DeviceIdentityStore(context).claimBody();
            fail("Corrupted identity was silently replaced");
        } catch (javax.crypto.AEADBadTagException expected) {}
        assertArrayEquals(damaged, new AtomicFile(file).readFully());
    }

    @Test public void missingKeyFailsWithoutCreatingAnotherIdentity() throws Exception {
        new DeviceIdentityStore(context).claimBody();
        byte[] original = new AtomicFile(file).readFully();
        KeyStore keys = KeyStore.getInstance("AndroidKeyStore");
        keys.load(null);
        keys.deleteEntry("garden_device_identity_v1");
        try {
            new DeviceIdentityStore(context).claimBody();
            fail("Missing key silently replaced the installation id");
        } catch (IllegalStateException expected) {}
        assertArrayEquals(original, new AtomicFile(file).readFully());
        assertFalse(keys.containsAlias("garden_device_identity_v1"));
    }
}
