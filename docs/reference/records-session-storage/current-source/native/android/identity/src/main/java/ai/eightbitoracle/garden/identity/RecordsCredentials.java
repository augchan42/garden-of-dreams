package ai.eightbitoracle.garden.identity;

import java.util.UUID;

/** Persist only a server-verified Records response; this type does not authenticate it. */
final class RecordsCredentials {
    final String owner, accessToken, refreshToken;
    final long accessExpiresAt, refreshExpiresAt;

    RecordsCredentials(String owner, String accessToken, long accessExpiresAt,
                       String refreshToken, long refreshExpiresAt) {
        canonicalUuid(owner);
        token(accessToken, 16384);
        if (accessExpiresAt <= 0) throw new IllegalArgumentException("Invalid access expiration");
        if (refreshToken == null) {
            if (refreshExpiresAt != 0) throw new IllegalArgumentException("Refresh expiration without credential");
        } else {
            token(refreshToken, 500);
            if (refreshExpiresAt <= 0) throw new IllegalArgumentException("Invalid refresh expiration");
        }
        this.owner = owner;
        this.accessToken = accessToken;
        this.accessExpiresAt = accessExpiresAt;
        this.refreshToken = refreshToken;
        this.refreshExpiresAt = refreshExpiresAt;
    }

    static UUID canonicalUuid(String value) {
        if (value == null) throw new IllegalArgumentException("Missing UUID");
        UUID uuid = UUID.fromString(value);
        if (!uuid.toString().equals(value)) throw new IllegalArgumentException("Noncanonical UUID");
        return uuid;
    }

    private static void token(String value, int limit) {
        if (value == null || value.isEmpty() || value.length() > limit)
            throw new IllegalArgumentException("Invalid credential length");
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (c < 33 || c > 126) throw new IllegalArgumentException("Invalid credential character");
        }
    }
}
