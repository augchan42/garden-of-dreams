package ai.eightbitoracle.garden.identity;

/** An authenticated owner session; survives refresh, invalid after sign-in or sign-out. */
final class RecordsOwnerLease {
    final String owner, epoch;

    RecordsOwnerLease(String owner, String epoch) {
        this.owner = owner;
        this.epoch = epoch;
    }

    @Override public boolean equals(Object other) {
        if (!(other instanceof RecordsOwnerLease)) return false;
        RecordsOwnerLease lease = (RecordsOwnerLease) other;
        return owner.equals(lease.owner) && epoch.equals(lease.epoch);
    }

    @Override public int hashCode() { return java.util.Objects.hash(owner, epoch); }
}
