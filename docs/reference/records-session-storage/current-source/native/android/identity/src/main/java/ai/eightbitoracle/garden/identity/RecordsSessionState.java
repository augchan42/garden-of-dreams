package ai.eightbitoracle.garden.identity;

import java.util.UUID;

final class RecordsSessionState {
    final String revision, ownerEpoch;
    final RecordsCredentials credentials;

    RecordsSessionState(String revision, String ownerEpoch, RecordsCredentials credentials) {
        if (RecordsCredentials.canonicalUuid(revision).version() != 4)
            throw new IllegalArgumentException("Invalid session revision");
        this.revision = revision;
        if (credentials == null) {
            if (ownerEpoch != null) throw new IllegalArgumentException("Signed-out owner epoch");
        } else if (RecordsCredentials.canonicalUuid(ownerEpoch).version() != 4) {
            throw new IllegalArgumentException("Invalid owner epoch");
        }
        this.ownerEpoch = ownerEpoch;
        this.credentials = credentials;
    }

    static RecordsSessionState next(RecordsCredentials credentials) {
        return new RecordsSessionState(UUID.randomUUID().toString(),
                credentials == null ? null : UUID.randomUUID().toString(), credentials);
    }

    RecordsSessionState rotated(RecordsCredentials verified) {
        if (credentials == null || verified == null || !credentials.owner.equals(verified.owner))
            throw new IllegalArgumentException("Refresh changed owner");
        return new RecordsSessionState(UUID.randomUUID().toString(), ownerEpoch, verified);
    }

    RecordsOwnerLease ownerLease() {
        return credentials == null ? null : new RecordsOwnerLease(credentials.owner, ownerEpoch);
    }

    RecordsRefreshLease refreshLease() {
        return credentials == null ? null : new RecordsRefreshLease(ownerLease(), revision);
    }

    boolean canRefresh(RecordsRefreshLease lease) {
        return lease != null && canPublish(lease.owner) && revision.equals(lease.revision);
    }

    boolean canPublish(RecordsOwnerLease lease) {
        return credentials != null && lease != null && credentials.owner.equals(lease.owner)
                && ownerEpoch.equals(lease.epoch);
    }
}
