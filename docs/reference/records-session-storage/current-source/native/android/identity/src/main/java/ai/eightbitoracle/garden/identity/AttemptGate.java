package ai.eightbitoracle.garden.identity;

/** A provider completion must still be current when its render callback runs. */
final class AttemptGate {
    private int generation;
    private boolean pending;

    synchronized int begin() {
        if (generation == Integer.MAX_VALUE) throw new IllegalStateException("Attempt counter exhausted");
        pending = true;
        return ++generation;
    }

    synchronized int invalidate() {
        if (generation == Integer.MAX_VALUE) throw new IllegalStateException("Attempt counter exhausted");
        ++generation;
        pending = false;
        return generation;
    }

    synchronized boolean isPending(int attempt) {
        return pending && generation == attempt;
    }

    synchronized boolean publish(int attempt, Runnable action) {
        if (!isPending(attempt)) return false;
        pending = false;
        action.run();
        return true;
    }
}
