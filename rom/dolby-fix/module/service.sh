#!/system/bin/sh
MODDIR=${0%/*}
[ "$(getprop ro.product.vendor.device)" = lapis ] || exit 1
case "$(getprop ro.lineage.version)" in
    23.2-*gsi_lapis*) exit 1 ;;
    23.2-*) ;;
    *) exit 1 ;;
esac
[ "$(getprop ro.build.version.sdk)" = 36 ] || exit 1
[ "$(getprop ro.vendor.build.version.incremental)" = 'OS3.0.307.0.WPPMIXM' ] || exit 1
[ ! -f /system/etc/ueventd/lapis.rc ] || exit 1
mkdir -p /data/adb/lapis_dolby
chmod 700 /data/adb/lapis_dolby
[ -f /data/adb/lapis_dolby/config ] || echo '1 20 9 0' > /data/adb/lapis_dolby/config
while [ "$(getprop sys.boot_completed)" != 1 ]; do sleep 3; done
while [ ! -e "$MODDIR/disable" ] && [ ! -e "$MODDIR/remove" ]; do
 CLASSPATH="$MODDIR/daemon.dex" app_process /system/bin DolbyDaemon > /data/adb/lapis_dolby/daemon.log 2>&1
 [ "$?" = 42 ] && exit 0
 sleep 5
done
