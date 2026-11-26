package ai.eightbitoracle.garden.identity;

/** Only this exact predecessor may rotate its refresh credential. */
final class RecordsRefreshLease {
    final RecordsOwnerLease owner;
    final String revision;

    RecordsRefreshLease(RecordsOwnerLease owner, String revision) {
        this.owner = owner;
        this.revision = revision;
    }
}
