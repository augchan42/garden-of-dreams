package ai.eightbitoracle.garden.identity;
import java.util.Arrays;
public final class RecordsSessionCoreTest {
 private static int checks;
 private static final String A="11111111-1111-4111-8111-111111111111", B="22222222-2222-4222-8222-222222222222";
 private static RecordsCredentials creds(String owner,String token){return new RecordsCredentials(owner,token,10,"refresh.fixture",20);}
 private static void check(boolean okay,String message){checks++;if(!okay)throw new AssertionError(message);}
 private static void reject(Runnable action,String message){try{action.run();throw new AssertionError(message);}catch(IllegalArgumentException expected){checks++;}}
 public static void main(String[] args) throws Exception {
  RecordsSessionState first=RecordsSessionState.next(creds(A,"access.fixture"));
  RecordsSessionState round=RecordsStateCodec.decode(RecordsStateCodec.encode(first));
  check(round.revision.equals(first.revision)&&round.credentials.owner.equals(A)&&round.credentials.accessToken.equals("access.fixture")&&round.credentials.refreshToken.equals("refresh.fixture"),"Credential round trip");
  check(round.credentials.accessExpiresAt==10&&round.credentials.refreshExpiresAt==20,"Expiration preserved independently; expiry is not anonymous fallback");
  RecordsOwnerLease lease=first.ownerLease();
  check(round.canPublish(lease),"Reopened same owner/revision lost lease");
  check(!RecordsSessionState.next(creds(B,"access.other")).canPublish(lease),"Cross-owner completion published");
  RecordsSessionState refreshed=first.rotated(creds(A,"access.rotated"));
  check(!refreshed.canRefresh(first.refreshLease()),"Late predecessor refresh published");
  check(refreshed.canPublish(lease),"Refresh invalidated legitimate owner publication");
  check(refreshed.ownerLease().equals(lease)&&refreshed.ownerLease().hashCode()==lease.hashCode(),"401 retry owner lease equality lost");
  check(refreshed.canRefresh(refreshed.refreshLease()),"Successor cannot refresh");
  check(!refreshed.revision.equals(first.revision)&&refreshed.ownerEpoch.equals(first.ownerEpoch),"Refresh revision/owner epoch conflated");
  check(!RecordsSessionState.next(creds(A,"access.resigned")).canPublish(lease),"Same-owner re-sign-in restored old lease");
  RecordsSessionState out=RecordsSessionState.next(null);
  check(out.ownerLease()==null&&!out.canPublish(lease)&&RecordsStateCodec.decode(RecordsStateCodec.encode(out)).credentials==null,"Sign-out tombstone lost revocation");
  RecordsSessionState noRefresh=RecordsSessionState.next(new RecordsCredentials(A,"access.only",100,null,0));
  check(RecordsStateCodec.decode(RecordsStateCodec.encode(noRefresh)).credentials.refreshToken==null,"Optional refresh invented");
  reject(()->new RecordsCredentials("1-1-1-1-1","access",1,null,0),"Noncanonical UUID owner accepted");
  reject(()->new RecordsCredentials(A,"access\nforged",1,null,0),"Header-injection credential accepted");
  reject(()->new RecordsCredentials(A,"access",1,null,2),"Refresh expiry without credential accepted");
  reject(()->new RecordsCredentials(A,"access",1,"refresh",0),"Refresh without expiration accepted");
  reject(()->new RecordsCredentials(A,"access",0,null,0),"Missing access expiry accepted");
  reject(()->new RecordsCredentials(A,"x".repeat(16385),1,null,0),"Oversized access credential accepted");
  reject(()->new RecordsCredentials(A,"access",1,"x".repeat(501),2),"Refresh beyond server request bound accepted");
  byte[] valid=RecordsStateCodec.encode(first),trailing=Arrays.copyOf(valid,valid.length+1),badVersion=valid.clone();badVersion[0]=0;
  reject(()->RecordsStateCodec.decode(trailing),"Trailing payload accepted");
  reject(()->RecordsStateCodec.decode(badVersion),"Unknown version accepted");
  reject(()->RecordsStateCodec.decode(Arrays.copyOf(valid,valid.length-1)),"Truncated payload accepted");
  System.out.println("RECORDS_SESSION_CORE_PASS "+checks+" checks");
 }
}
