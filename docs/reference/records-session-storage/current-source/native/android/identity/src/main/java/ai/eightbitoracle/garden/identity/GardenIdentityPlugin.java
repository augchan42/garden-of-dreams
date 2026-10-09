package ai.eightbitoracle.garden.identity;

import android.app.Activity;
import android.os.CancellationSignal;
import androidx.core.content.ContextCompat;
import androidx.credentials.CredentialManager;
import androidx.credentials.CredentialManagerCallback;
import androidx.credentials.CustomCredential;
import androidx.credentials.GetCredentialRequest;
import androidx.credentials.GetCredentialResponse;
import androidx.credentials.exceptions.GetCredentialException;
import androidx.credentials.exceptions.GetCredentialCancellationException;
import com.google.android.libraries.identity.googleid.GetSignInWithGoogleOption;
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential;
import java.util.HashSet;
import java.util.Set;
import org.godotengine.godot.Godot;
import org.godotengine.godot.plugin.GodotPlugin;
import org.godotengine.godot.plugin.SignalInfo;
import org.godotengine.godot.plugin.UsedByGodot;
import org.json.JSONObject;

/** Acquires a provider proof; only the server can mint an authenticated Records session. */
public final class GardenIdentityPlugin extends GodotPlugin {
    private final AttemptGate gate = new AttemptGate();
    private CancellationSignal cancellation;
    private int cancellationAttempt;
    private DeviceIdentityStore identity;

    public GardenIdentityPlugin(Godot godot) { super(godot); }
    @Override public String getPluginName() { return "GardenIdentity"; }
    @Override public Set<SignalInfo> getPluginSignals() {
        Set<SignalInfo> signals = new HashSet<>();
        signals.add(new SignalInfo("google_token_ready", Integer.class, String.class));
        signals.add(new SignalInfo("google_sign_in_failed", Integer.class, String.class));
        signals.add(new SignalInfo("identity_error", String.class));
        return signals;
    }

    @UsedByGodot public int beginGoogleSignIn(String webClientId) {
        int attempt = gate.begin();
        runOnUiThread(() -> {
            if (!gate.isPending(attempt)) return;
            if (cancellation != null) cancellation.cancel();
            Activity activity = getActivity();
            if (activity == null || webClientId == null || !webClientId.endsWith(".apps.googleusercontent.com")) {
                fail(attempt, "configuration_required");
                return;
            }
            try {
                cancellation = new CancellationSignal();
                cancellationAttempt = attempt;
                GetSignInWithGoogleOption option = new GetSignInWithGoogleOption.Builder(webClientId).build();
                GetCredentialRequest request = new GetCredentialRequest.Builder().addCredentialOption(option).build();
                CredentialManager.create(activity).getCredentialAsync(activity, request, cancellation,
                        ContextCompat.getMainExecutor(activity), new CredentialManagerCallback<GetCredentialResponse, GetCredentialException>() {
                    @Override public void onResult(GetCredentialResponse result) {
                        try {
                            if (!(result.getCredential() instanceof CustomCredential)) {
                                fail(attempt, "unsupported_credential");
                                return;
                            }
                            String type = result.getCredential().getType();
                            if (!type.equals(GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL)
                                    && !type.equals(GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_SIWG_CREDENTIAL)) {
                                fail(attempt, "unsupported_credential");
                                return;
                            }
                            String token = GoogleIdTokenCredential.createFrom(result.getCredential().getData()).getIdToken();
                            if (token.isEmpty()) { fail(attempt, "invalid_provider_response"); return; }
                            // Recheck on the render thread after cancellation or another chooser.
                            runOnRenderThread(() -> gate.publish(attempt, () -> emitSignal("google_token_ready", attempt, token)));
                        } catch (Exception invalid) { fail(attempt, "invalid_provider_response"); }
                    }
                    @Override public void onError(GetCredentialException error) {
                        fail(attempt, error instanceof GetCredentialCancellationException ? "cancelled" : "provider_unavailable");
                    }
                });
            } catch (Exception failure) { fail(attempt, "provider_unavailable"); }
        });
        return attempt;
    }

    private void fail(int attempt, String code) {
        runOnRenderThread(() -> gate.publish(attempt, () -> emitSignal("google_sign_in_failed", attempt, code)));
    }

    @UsedByGodot public void cancelSignIn() {
        int invalidated = gate.invalidate();
        runOnUiThread(() -> {
            if (cancellation != null && cancellationAttempt < invalidated) cancellation.cancel();
        });
    }
    @Override public void onGodotTerminating() { cancelSignIn(); }

    private synchronized DeviceIdentityStore store() {
        if (identity == null) identity = new DeviceIdentityStore(getContext());
        return identity;
    }

    @UsedByGodot public String getDeviceClaimBody() {
        try { return store().claimBody(); }
        catch (Exception failure) { emitSignal("identity_error", "device_storage_failed"); return ""; }
    }

    @UsedByGodot public String signedDeviceHeaders(String apiKey, String signingSecret, String serializedBody) {
        try {
            if (apiKey == null || apiKey.isEmpty() || apiKey.indexOf('\r') >= 0 || apiKey.indexOf('\n') >= 0)
                throw new IllegalArgumentException("Missing client key");
            long timestamp = System.currentTimeMillis() / 1000;
            return new JSONObject().put("X-API-Key", apiKey).put("X-Timestamp", Long.toString(timestamp))
                    .put("X-Signature", RequestSigner.signature(signingSecret, timestamp, serializedBody))
                    .put("X-Device-Credential", store().credential()).toString();
        } catch (IllegalArgumentException missing) { emitSignal("identity_error", "configuration_required"); return ""; }
        catch (Exception failure) { emitSignal("identity_error", "device_storage_failed"); return ""; }
    }
}
