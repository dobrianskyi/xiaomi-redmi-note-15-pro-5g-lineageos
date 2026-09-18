package org.lineageos.powerschedule;

import java.io.IOException;

final class Rtc {
    static { System.loadLibrary("lapis_power_rtc"); }
    static native boolean supported();
    static native String execute(String action) throws IOException;
}
