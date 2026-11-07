#!/system/bin/sh
# No daemon, polling, Bluetooth database edits or SELinux changes.
[ "$(getprop ro.product.vendor.device)" = lapis ] || exit 0
case "$(getprop ro.lineage.version)" in
    23.2-*gsi_lapis) ;;
    *) exit 0 ;;
esac
[ "$(getprop ro.build.version.sdk)" = 36 ] || exit 0
[ "$(getprop ro.vendor.build.version.incremental)" = 'OS3.0.307.0.WPPMIXM' ] || exit 0
MODDIR=${0%/*}
[ -f "$MODDIR/disable" ] && exit 0
[ -f "$MODDIR/remove" ] && exit 0
RESETPROP=$(command -v resetprop) || exit 1
while IFS='=' read -r key value; do
    case "$key" in
        bluetooth.profile.*.enabled|bluetooth.device.class_of_device) ;;
        *) continue ;;
    esac
    [ -n "$(getprop "$key")" ] || "$RESETPROP" -n "$key" "$value"
done < "$MODDIR/profiles.prop"
