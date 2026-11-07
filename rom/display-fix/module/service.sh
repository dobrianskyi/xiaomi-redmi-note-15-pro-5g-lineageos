#!/system/bin/sh
MODDIR=${0%/*}
[ ! -e "$MODDIR/disable" ] && [ ! -e "$MODDIR/remove" ] || exit 0
[ "$(getprop ro.product.vendor.device)" = lapis ] || exit 1
case "$(getprop ro.lineage.version)" in
    23.2-*gsi_lapis*) exit 1 ;;
    23.2-*) ;;
    *) exit 1 ;;
esac
[ "$(getprop ro.build.version.sdk)" = 36 ] || exit 1
[ "$(getprop ro.vendor.build.version.incremental)" = 'OS3.0.307.0.WPPMIXM' ] || exit 1
[ ! -f /system/etc/ueventd/lapis.rc ] || exit 1
src=/sys/class/leds/lcd-backlight/brightness
dst=/sys/class/mi_display/disp-DSI-0/backlight
attempt=0
while [ ! -r "$src" ] || [ ! -w "$dst" ]; do
    attempt=$((attempt + 1))
    [ "$attempt" -lt 60 ] || exit 2
    sleep 1
done
[ "$(cat /sys/class/mi_display/disp-DSI-0/panel_info)" = 'panel_name=dsi_p16_42_02_0a_dsc_vdo' ] || exit 3
# Singleton is enforced inside the binary via flock. Disable/remove stops it live.
"$MODDIR/lapis-backlight" "$src" "$dst" "$MODDIR/disable" "$MODDIR/remove" "$MODDIR/daemon.lock" &
