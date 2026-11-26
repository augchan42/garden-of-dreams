package ai.eightbitoracle.garden.identity;

import java.util.UUID;

final class RecordsSessionState {
    final String revision;
    final RecordsCredentials credentials;

    RecordsSessionState(String revision, RecordsCredentials credentials) {
        if (RecordsCredentials.canonicalUuid(revision).version() != 4)
            throw new IllegalArgumentException("Invalid session revision");
        this.revision = revision;
        this.credentials = credentials;
    }

    static RecordsSessionState next(RecordsCredentials credentials) {
        return new RecordsSessionState(UUID.randomUUID().toString(), credentials);
    }

    RecordsOwnerLease ownerLease() {
        return credentials == null ? null : new RecordsOwnerLease(credentials.owner, revision);
    }

    boolean canPublish(RecordsOwnerLease lease) {
        return credentials != null && lease != null && credentials.owner.equals(lease.owner)
                && revision.equals(lease.revision);
    }
}
