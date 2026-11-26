package ai.eightbitoracle.garden.identity;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

/** Versioned plaintext payload inside the authenticated envelope; never a log format. */
final class RecordsStateCodec {
    static byte[] encode(RecordsSessionState state) {
        try {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            DataOutputStream out = new DataOutputStream(bytes);
            out.writeByte(2);
            out.writeUTF(state.revision);
            out.writeBoolean(state.credentials != null);
            if (state.credentials != null) {
                RecordsCredentials c = state.credentials;
                out.writeUTF(state.ownerEpoch);
                out.writeUTF(c.owner);
                out.writeUTF(c.accessToken);
                out.writeLong(c.accessExpiresAt);
                out.writeBoolean(c.refreshToken != null);
                if (c.refreshToken != null) {
                    out.writeUTF(c.refreshToken);
                    out.writeLong(c.refreshExpiresAt);
                }
            }
            out.flush();
            return bytes.toByteArray();
        } catch (IOException failure) {
            throw new IllegalArgumentException("Cannot encode Records state", failure);
        }
    }

    static RecordsSessionState decode(byte[] bytes) {
        if (bytes == null || bytes.length > 20000) throw new IllegalArgumentException("Invalid Records payload size");
        try {
            DataInputStream in = new DataInputStream(new ByteArrayInputStream(bytes));
            if (in.readUnsignedByte() != 2) throw new IllegalArgumentException("Unknown Records payload version");
            String revision = in.readUTF();
            String ownerEpoch = null;
            RecordsCredentials credentials = null;
            if (in.readBoolean()) {
                ownerEpoch = in.readUTF();
                String owner = in.readUTF(), access = in.readUTF();
                long expiration = in.readLong();
                boolean refresh = in.readBoolean();
                credentials = new RecordsCredentials(owner, access, expiration,
                        refresh ? in.readUTF() : null, refresh ? in.readLong() : 0);
            }
            if (in.available() != 0) throw new IllegalArgumentException("Trailing Records payload bytes");
            return new RecordsSessionState(revision, ownerEpoch, credentials);
        } catch (IOException failure) {
            throw new IllegalArgumentException("Truncated Records payload", failure);
        }
    }
}
