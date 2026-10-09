package ai.eightbitoracle.garden.identity;

/** Captured before an owner-scoped request; invalid after any session replacement. */
final class RecordsOwnerLease {
    final String owner, revision;

    RecordsOwnerLease(String owner, String revision) {
        this.owner = owner;
        this.revision = revision;
    }
}
