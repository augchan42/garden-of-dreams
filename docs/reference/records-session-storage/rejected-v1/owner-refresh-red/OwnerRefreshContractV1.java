package ai.eightbitoracle.garden.identity;
public final class OwnerRefreshContractV1 {
 public static void main(String[] args) {
  RecordsCredentials c=new RecordsCredentials("11111111-1111-4111-8111-111111111111","fixture.access",10,"fixture.refresh",20);
  RecordsSessionState before=RecordsSessionState.next(c);RecordsOwnerLease owner=before.ownerLease();
  // Exact factory used by v1 RecordsSessionStore.rotate; no Android/crypto simulation claim.
  RecordsSessionState renewed=RecordsSessionState.next(c);
  if(!renewed.canPublish(owner))throw new AssertionError("OWNER_LEASE_REFRESH_RETRY_CONTRACT_REJECTED");
 }
}
