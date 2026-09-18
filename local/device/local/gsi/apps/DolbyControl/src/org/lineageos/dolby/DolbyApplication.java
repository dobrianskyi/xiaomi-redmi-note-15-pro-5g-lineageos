package org.lineageos.dolby;

public class DolbyApplication extends android.app.Application {
    @Override public void onCreate() {
        super.onCreate();
        if (android.os.UserHandle.myUserId() == 0) Engine.get(this);
    }
}
