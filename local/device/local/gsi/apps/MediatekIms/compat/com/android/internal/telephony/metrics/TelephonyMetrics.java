/* SPDX-License-Identifier: Apache-2.0 */
package com.android.internal.telephony.metrics;

/**
 * Binary compatibility for the pinned MediaTek IMS APK's legacy Clearcut calls.
 *
 * Android removed this statistics backend in telephony commit
 * a1e87f8d20c88efa8887091059d6abb5b5b2f0d0. These void methods only collected
 * legacy metrics; they never sent radio requests or determined call results.
 * The platform's current telephony metrics remain independent and unchanged.
 * This class is packaged inside the IMS APK only, not exposed as a platform API.
 */
public final class TelephonyMetrics {
    private static final TelephonyMetrics INSTANCE = new TelephonyMetrics();

    private TelephonyMetrics() {}

    public static TelephonyMetrics getInstance() {
        return INSTANCE;
    }

    // The retired Clearcut collector intentionally receives no new events.
    public void writeOnRilTimeoutResponse(int phoneId, int serial, int request) {}

    public void writeOnRilSolicitedResponse(
            int phoneId, int serial, int error, int request, Object result) {}

    public void writeRilAnswer(int phoneId, int serial) {}

    public void writeRilSendSms(int phoneId, int serial, int tech, int format, long messageId) {}
}
