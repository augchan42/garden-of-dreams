package ai.eightbitoracle.garden.identity;

import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

final class RequestSigner {
    static String signature(String secret, long timestamp, String body) throws GeneralSecurityException {
        if (secret == null || secret.isEmpty() || body == null || timestamp < 0) {
            throw new IllegalArgumentException("Missing signing input");
        }
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
        return hex(mac.doFinal((Long.toString(timestamp) + body).getBytes(StandardCharsets.UTF_8)));
    }
    static String hex(byte[] bytes) {
        char[] alphabet = "0123456789abcdef".toCharArray();
        char[] result = new char[bytes.length * 2];
        for (int i = 0; i < bytes.length; i++) {
            result[i * 2] = alphabet[(bytes[i] & 255) >>> 4];
            result[i * 2 + 1] = alphabet[bytes[i] & 15];
        }
        return new String(result);
    }
}
