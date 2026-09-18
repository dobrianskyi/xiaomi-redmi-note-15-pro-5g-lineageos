#!/system/bin/sh
umask 077
MODDIR=${0%/*}
lock=/dev/.lapis-fod-bridge-lock
mkdir "$lock" 2>/dev/null || exit 0
svc=vendor.xiaomi.hardware.fingerprintextension.IXiaomiFingerprint/default
ext() { service call "$svc" 1 i32 "$1" i32 "$2" >/dev/null 2>&1; }
cleanup() {
 [ -z "$logger" ] || kill "$logger" 2>/dev/null
 [ -z "$ticker" ] || kill "$ticker" 2>/dev/null
 ext 1 0; ext 4 2
 rm -f "$lock/events"; rmdir "$lock"
}
trap cleanup EXIT HUP INT TERM
last=
sync_state() {
 pid=$(pidof android.hardware.biometrics.fingerprint-service.odm)
 if [ -z "$pid" ]; then last=; return; fi
 operation=$(dumpsys fingerprint | sed -n 's/^Current operation: //p')
 case "$operation" in
  *FingerprintEnrollClient*) state=1;;
  *FingerprintAuthenticationClient*|*FingerprintDetectClient*) state=3;;
  *) state=2;;
 esac
 if [ "$state" = 2 ]; then
  key="$pid:idle"
  if [ "$key" != "$last" ]; then ext 1 0; ext 4 2; last=$key; fi
 else
  wake=$(dumpsys power | sed -n 's/^  mWakefulness=//p' | head -n 1)
  case "$wake" in Awake) power=2;; Dozing) power=1;; Asleep) power=0;; *) return;; esac
  key="$pid:$operation:$power"
  if [ "$key" != "$last" ]; then
   ext 2 0; ext 3 "$power"; ext 4 "$state"; ext 1 1
   last=$key
  fi
 fi
}
mkfifo "$lock/events" || exit 1
# Main reader opens the pipe after these producers; process IDs are retained.
logcat -b main -b system -v brief -T 1 'BiometricStateCallback:D' 'PowerManagerService:I' '*:S' > "$lock/events" 2>/dev/null &
logger=$!
(while :; do echo LAPIS_TICK; sleep 5; done) > "$lock/events" &
ticker=$!
while IFS= read -r event; do
 [ ! -e "$MODDIR/disable" ] && [ ! -e "$MODDIR/remove" ] || break
 case "$event" in
  LAPIS_TICK|*'State updated from '*|*'Client finished, state updated to '*|*'Waking up from '*|*'Going to sleep due to '*|*'Dozing...'*|*'Sleeping...'*) sync_state;;
 esac
done < "$lock/events"
