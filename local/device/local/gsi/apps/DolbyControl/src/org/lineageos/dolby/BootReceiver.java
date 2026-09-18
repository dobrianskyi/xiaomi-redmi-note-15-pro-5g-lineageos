package org.lineageos.dolby;

public class BootReceiver extends android.content.BroadcastReceiver {
    @Override public void onReceive(android.content.Context context, android.content.Intent intent) {
        if (android.os.UserHandle.myUserId() != 0) return;
        Engine engine = Engine.get(context);
        engine.worker.execute(engine::reapply);
    }
}
