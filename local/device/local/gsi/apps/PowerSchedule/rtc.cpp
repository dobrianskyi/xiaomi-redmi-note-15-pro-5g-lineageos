// Uses the RTC_POFF_ALM_SET ABI verified in lapis stock rtc-mt6685.ko.
#include <jni.h>
#include <linux/rtc.h>
#include <sys/ioctl.h>
#include <sys/system_properties.h>
#include <sys/utsname.h>
#include <fcntl.h>
#include <unistd.h>
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>

static constexpr unsigned long kPowerOffAlarm = _IOW('p', 0x15, struct rtc_time);
static_assert(kPowerOffAlarm == 0x40247015);

static bool supportedDevice() {
    char device[PROP_VALUE_MAX] = {};
    __system_property_get("ro.product.vendor.device", device);
    struct utsname kernel {};
    // Other devices and kernel revisions need their own verified backend.
    return !strcmp(device, "lapis") && uname(&kernel) == 0 &&
            !strcmp(kernel.release, "6.1.138-android14-11-g51f8c580613d-ab13911623");
}

static int openRtc() {
    if (!supportedDevice()) { errno = ENODEV; return -1; }
    int fd = open("/dev/rtc0", O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) return -1;
    // This driver's NULL argument path returns before changing the timer.
    if (ioctl(fd, kPowerOffAlarm, nullptr) == -1 && errno == EFAULT) return fd;
    close(fd);
    errno = ENOTSUP;
    return -1;
}

static jstring fail(JNIEnv* env, const char* message) {
    env->ThrowNew(env->FindClass("java/io/IOException"), message);
    return nullptr;
}

extern "C" JNIEXPORT jboolean JNICALL
Java_org_lineageos_powerschedule_Rtc_supported(JNIEnv*, jclass) {
    int fd = openRtc();
    if (fd < 0) return false;
    close(fd);
    return true;
}

extern "C" JNIEXPORT jstring JNICALL
Java_org_lineageos_powerschedule_Rtc_execute(JNIEnv* env, jclass, jstring input) {
    const char* text = env->GetStringUTFChars(input, nullptr);
    if (!text) return nullptr;
    std::string action(text);
    env->ReleaseStringUTFChars(input, text);
    int fd = openRtc();
    if (fd < 0) return fail(env, "Power-off RTC is unavailable or access was denied.");
    struct rtc_time rtc {};
    if (ioctl(fd, RTC_RD_TIME, &rtc) < 0) {
        close(fd);
        return fail(env, "Could not read the hardware clock.");
    }
    struct tm calendar {};
    calendar.tm_sec = rtc.tm_sec; calendar.tm_min = rtc.tm_min;
    calendar.tm_hour = rtc.tm_hour; calendar.tm_mday = rtc.tm_mday;
    calendar.tm_mon = rtc.tm_mon; calendar.tm_year = rtc.tm_year;
    time_t rtcNow = timegm(&calendar), now = time(nullptr), target;
    if (rtcNow < 0 || calendar.tm_year < 70 || calendar.tm_year > 199) {
        close(fd);
        return fail(env, "The hardware clock has an unsupported date.");
    }
    if (action == "cancel") {
        target = rtcNow - 1;
    } else if (action.rfind("set ", 0) == 0) {
        char* end = nullptr;
        errno = 0;
        long long requested = strtoll(action.c_str() + 4, &end, 10);
        if (errno || end == action.c_str() + 4 || *end || requested < now + 5 ||
                requested > now + 370LL * 86400) {
            close(fd);
            return fail(env, "Choose a time between five seconds and 370 days from now.");
        }
        target = rtcNow + requested - now;
    } else {
        close(fd);
        return fail(env, "Unknown RTC operation.");
    }
    if (!gmtime_r(&target, &calendar) || calendar.tm_year < 70 || calendar.tm_year > 199) {
        close(fd);
        return fail(env, "The scheduled date is outside the supported RTC range.");
    }
    rtc = {calendar.tm_sec, calendar.tm_min, calendar.tm_hour, calendar.tm_mday,
           calendar.tm_mon, calendar.tm_year, calendar.tm_wday, calendar.tm_yday, 0};
    int result = ioctl(fd, kPowerOffAlarm, &rtc);
    close(fd);
    if (result < 0) return fail(env, "The hardware clock rejected the schedule.");
    return env->NewStringUTF("Hardware schedule updated.");
}
