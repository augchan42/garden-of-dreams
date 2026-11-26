package ai.eightbitoracle.garden.identity;
import android.content.Context;
import android.util.AtomicFile;
import androidx.test.platform.app.InstrumentationRegistry;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public final class RecordsSessionStoreTest {
 private Context context;
 private File file;
 private static final String A="11111111-1111-4111-8111-111111111111",B="22222222-2222-4222-8222-222222222222";
 private static RecordsCredentials creds(String owner,String token){return new RecordsCredentials(owner,token,10,"refresh.fixture."+token,20);}
 @Before public void prepare() throws Exception {
  context=InstrumentationRegistry.getInstrumentation().getTargetContext();
  assertEquals("ai.eightbitoracle.garden.identity.tests",context.getPackageName());
  file=new File(context.getNoBackupFilesDir(),"garden-records-session.bin");cleanup();
 }
 @After public void cleanup() throws Exception {
  if(file==null)return;
  new AtomicFile(file).delete();KeyStore keys=KeyStore.getInstance("AndroidKeyStore");keys.load(null);keys.deleteEntry("garden_records_session_v1");
 }
 private RecordsSessionStore signedIn() throws Exception {
  RecordsSessionStore store=new RecordsSessionStore(context);String revision=store.readOrCreate().revision;
  assertTrue(store.install(revision,creds(A,"access.fixture")));return store;
 }
 @Test public void encryptedPersistenceRetainsOwnerAndBothCredentials() throws Exception {
  RecordsSessionStore store=signedIn();RecordsSessionState first=store.readOrCreate(),again=new RecordsSessionStore(context).readOrCreate();
  assertEquals(first.revision,again.revision);assertEquals(A,again.credentials.owner);assertEquals("access.fixture",again.credentials.accessToken);assertEquals(10,again.credentials.accessExpiresAt);assertEquals("refresh.fixture.access.fixture",again.credentials.refreshToken);assertEquals(20,again.credentials.refreshExpiresAt);
  String cipher=new String(new AtomicFile(file).readFully(),StandardCharsets.ISO_8859_1);
  assertFalse(cipher.contains(A));assertFalse(cipher.contains(first.credentials.accessToken));assertFalse(cipher.contains(first.credentials.refreshToken));assertFalse(cipher.contains(first.revision));
  assertEquals(context.getNoBackupFilesDir(),file.getParentFile());
 }
 @Test public void rotationPersistsSuccessorAndRejectsPredecessor() throws Exception {
  RecordsSessionStore store=signedIn();RecordsRefreshLease lease=store.readOrCreate().refreshLease();
  assertTrue(store.rotate(lease,creds(A,"access.rotated")));byte[] committed=new AtomicFile(file).readFully();
  assertFalse(store.rotate(lease,creds(A,"access.late")));assertArrayEquals(committed,new AtomicFile(file).readFully());
  RecordsSessionState reopened=new RecordsSessionStore(context).readOrCreate();assertEquals("access.rotated",reopened.credentials.accessToken);assertEquals("refresh.fixture.access.rotated",reopened.credentials.refreshToken);assertFalse(reopened.canRefresh(lease));
 }
 @Test public void accountSwitchAndQueuedPublicationCannotCrossOwners() throws Exception {
  RecordsSessionStore first=signedIn();RecordsSessionState a=first.readOrCreate();RecordsSessionStore otherHandle=new RecordsSessionStore(context);
  assertTrue(otherHandle.install(a.revision,creds(B,"access.other")));
  AtomicInteger publishes=new AtomicInteger();assertFalse(first.publishCurrent(a.ownerLease(),publishes::incrementAndGet));assertEquals(0,publishes.get());assertFalse(first.rotate(a.refreshLease(),creds(A,"access.old")));
  RecordsOwnerLease current=otherHandle.readOrCreate().ownerLease();assertTrue(first.publishCurrent(current,publishes::incrementAndGet));assertEquals(1,publishes.get());assertEquals(B,first.readOrCreate().credentials.owner);
 }
 @Test public void signOutTombstoneRejectsLateSigninAndRefreshAfterReopen() throws Exception {
  RecordsSessionStore first=signedIn();RecordsSessionState signed=first.readOrCreate();first.signOut();byte[] out=new AtomicFile(file).readFully();RecordsSessionStore reopened=new RecordsSessionStore(context);
  assertNull(reopened.readOrCreate().credentials);assertNotEquals(signed.revision,reopened.readOrCreate().revision);
  assertFalse(reopened.install(signed.revision,creds(A,"access.late")));assertFalse(reopened.rotate(signed.refreshLease(),creds(A,"access.late")));assertFalse(reopened.publishCurrent(signed.ownerLease(),()->fail("Signed-out response published")));assertArrayEquals(out,new AtomicFile(file).readFully());
 }
 @Test public void ownerMismatchRefreshLeavesCurrentBytesIntact() throws Exception {
  RecordsSessionStore store=signedIn();RecordsRefreshLease lease=store.readOrCreate().refreshLease();byte[] current=new AtomicFile(file).readFully();assertFalse(store.rotate(lease,creds(B,"access.wrong")));assertArrayEquals(current,new AtomicFile(file).readFully());assertEquals(A,store.readOrCreate().credentials.owner);
 }
 @Test public void corruptionCannotBeOverwrittenByReadInstallOrSignOut() throws Exception {
  RecordsSessionStore store=signedIn();String revision=store.readOrCreate().revision;byte[] bad=new AtomicFile(file).readFully();bad[bad.length-1]^=1;
  try(FileOutputStream output=new FileOutputStream(file)){output.write(bad);}
  try{store.readOrCreate();fail("Corruption hidden");}catch(javax.crypto.AEADBadTagException expected){}
  try{store.install(revision,creds(B,"access.other"));fail("Corruption overwritten");}catch(javax.crypto.AEADBadTagException expected){}
  try{store.signOut();fail("Corruption silently reset");}catch(javax.crypto.AEADBadTagException expected){}
  assertArrayEquals(bad,new AtomicFile(file).readFully());
 }
 @Test public void missingKeystoreKeyCannotReplaceSession() throws Exception {
  RecordsSessionStore store=signedIn();String revision=store.readOrCreate().revision;byte[] current=new AtomicFile(file).readFully();KeyStore keys=KeyStore.getInstance("AndroidKeyStore");keys.load(null);keys.deleteEntry("garden_records_session_v1");
  try{store.readOrCreate();fail("Missing key hidden");}catch(IllegalStateException expected){}
  try{store.install(revision,creds(B,"access.other"));fail("Missing key recreated");}catch(IllegalStateException expected){}
  assertFalse(keys.containsAlias("garden_records_session_v1"));assertArrayEquals(current,new AtomicFile(file).readFully());
 }
 @Test public void oversizedEnvelopeIsRejectedWithoutReplacingBytes() throws Exception {
  byte[] oversized=new byte[20030];try(FileOutputStream output=new FileOutputStream(file)){output.write(oversized);}
  try{new RecordsSessionStore(context).readOrCreate();fail("Oversized envelope read");}catch(IllegalStateException expected){}
  assertArrayEquals(oversized,new AtomicFile(file).readFully());KeyStore keys=KeyStore.getInstance("AndroidKeyStore");keys.load(null);assertFalse(keys.containsAlias("garden_records_session_v1"));
 }
 @Test public void competingRefreshesCommitOnlyOneSuccessor() throws Exception {
  RecordsSessionStore first=signedIn(),second=new RecordsSessionStore(context);RecordsRefreshLease lease=first.readOrCreate().refreshLease();
  java.util.concurrent.CountDownLatch start=new java.util.concurrent.CountDownLatch(1);
  java.util.concurrent.atomic.AtomicInteger accepted=new java.util.concurrent.atomic.AtomicInteger();
  java.util.concurrent.atomic.AtomicReference<Throwable> failure=new java.util.concurrent.atomic.AtomicReference<>();
  Thread a=new Thread(()->{try{start.await();if(first.rotate(lease,creds(A,"access.one")))accepted.incrementAndGet();}catch(Throwable e){failure.compareAndSet(null,e);}});
  Thread b=new Thread(()->{try{start.await();if(second.rotate(lease,creds(A,"access.two")))accepted.incrementAndGet();}catch(Throwable e){failure.compareAndSet(null,e);}});
  a.start();b.start();start.countDown();a.join(10000);b.join(10000);
  assertFalse("Refresh thread did not finish",a.isAlive()||b.isAlive());assertNull(failure.get());assertEquals(1,accepted.get());
  RecordsSessionState committed=new RecordsSessionStore(context).readOrCreate();
  assertTrue(committed.credentials.accessToken.equals("access.one")||committed.credentials.accessToken.equals("access.two"));
  assertEquals("refresh.fixture."+committed.credentials.accessToken,committed.credentials.refreshToken);assertFalse(committed.canRefresh(lease));
 }

 @Test public void refreshRetainsOwnerLeaseForRetryAndHistoryPublication() throws Exception {
  RecordsSessionStore store=signedIn();RecordsSessionState before=store.readOrCreate();RecordsOwnerLease owner=before.ownerLease();
  assertTrue(store.rotate(before.refreshLease(),creds(A,"access.renewed")));RecordsSessionState after=new RecordsSessionStore(context).readOrCreate();
  assertEquals(owner,after.ownerLease());assertEquals(owner.hashCode(),after.ownerLease().hashCode());assertEquals(before.ownerEpoch,after.ownerEpoch);assertNotEquals(before.revision,after.revision);
  AtomicInteger calls=new AtomicInteger();assertTrue(store.publishCurrent(owner,calls::incrementAndGet));assertEquals(1,calls.get());assertFalse(store.rotate(before.refreshLease(),creds(A,"access.stale")));
 }
 @Test public void sameOwnerSigninStartsNewOwnerSession() throws Exception {
  RecordsSessionStore store=signedIn();RecordsSessionState before=store.readOrCreate();assertTrue(store.install(before.revision,creds(A,"access.newsignin")));RecordsSessionState after=store.readOrCreate();
  assertEquals(before.credentials.owner,after.credentials.owner);assertNotEquals(before.ownerEpoch,after.ownerEpoch);assertFalse(store.isCurrent(before.ownerLease()));assertFalse(store.publishCurrent(before.ownerLease(),()->fail("Previous signin response published")));
 }

}
