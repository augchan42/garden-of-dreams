package ai.eightbitoracle.garden.identity;

import java.util.concurrent.atomic.AtomicInteger;

public final class IdentityCoreTest {
    private static int passed;
    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
        passed++;
    }
    public static void main(String[] args) throws Exception {
        AttemptGate gate = new AttemptGate();
        AtomicInteger delivered = new AtomicInteger();
        int old = gate.begin();
        gate.invalidate();
        check(!gate.publish(old, delivered::incrementAndGet), "Cancelled provider result was published");
        check(delivered.get() == 0, "Cancelled token reached the consumer");
        int first = gate.begin();
        int second = gate.begin();
        check(!gate.publish(first, delivered::incrementAndGet), "Old account chooser result was published");
        check(gate.publish(second, delivered::incrementAndGet), "Current provider result was lost");
        check(!gate.publish(second, delivered::incrementAndGet), "Duplicate provider completion was published");
        check(delivered.get() == 1, "Provider result must publish once");
        int queued = gate.begin();
        Runnable renderCallback = () -> gate.publish(queued, delivered::incrementAndGet);
        gate.invalidate();
        renderCallback.run();
        check(delivered.get() == 1, "Result queued before cancellation survived the render-thread check");
        check(!gate.isPending(queued), "Cancelled chooser remains pending");
        System.out.println("IDENTITY_ATTEMPT_GATE_PASS " + passed);
    }
}
