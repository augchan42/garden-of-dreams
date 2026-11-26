package ai.eightbitoracle.garden.identity;

public final class RequestSignerTest {
    public static void main(String[] args) throws Exception {
        String body = "{ \"text\": \"沁芳\", \"value\": 1 }\n";
        if (!RequestSigner.signature("garden-fixture-key", 1791440000L, body).equals("578dad5917aa288b6b4e941ca898eb6bdcd5ac0cdf558d7e62df8d21903ff08e"))
            throw new AssertionError("Timestamp/body UTF-8 signature differs from independent Python vector");
        if (!RequestSigner.signature("garden-fixture-key", 1791440000L, "").equals("ed000d656fb2eeb85068949bbd87a82f1a8afed7e46d89044339da070247946f"))
            throw new AssertionError("Bodyless GET signature differs");
        if (RequestSigner.signature("garden-fixture-key", 1791440000L, body.trim()).equals("578dad5917aa288b6b4e941ca898eb6bdcd5ac0cdf558d7e62df8d21903ff08e"))
            throw new AssertionError("Signing normalized away the serialized body newline");
        try { RequestSigner.signature("", 1791440000L, body); throw new AssertionError("Empty key accepted"); }
        catch (IllegalArgumentException expected) {}
        System.out.println("IDENTITY_REQUEST_SIGNER_PASS 4");
    }
}
