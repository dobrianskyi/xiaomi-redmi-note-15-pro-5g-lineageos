#!/system/bin/sh
MODDIR=${0%/*}
[ "$(getprop ro.product.vendor.device)" = lapis ] || exit 1
[ -s "$MODDIR/bridge.dex" ] || exit 1
while [ "$(getprop sys.boot_completed)" != 1 ]; do sleep 3; done
mkdir -p /data/adb/lapis_call_volume
chmod 700 /data/adb/lapis_call_volume
pm disable-user --user 0 org.lineageos.mediatek.incallservice >/dev/null
while [ ! -f "$MODDIR/disable" ] && [ ! -f "$MODDIR/remove" ]; do
 CLASSPATH="$MODDIR/bridge.dex" app_process /system/bin CallVolumeBridge >/data/adb/lapis_call_volume/log 2>&1
 [ "$?" = 42 ] && exit 0
 sleep 3
done
