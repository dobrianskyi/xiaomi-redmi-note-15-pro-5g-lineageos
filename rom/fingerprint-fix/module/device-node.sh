#!/system/bin/sh
[ "$(getprop ro.product.vendor.device)" = lapis ] || exit 1
case "$(getprop ro.lineage.version)" in
    23.2-*gsi_lapis*) exit 1 ;;
    23.2-*) ;;
    *) exit 1 ;;
esac
[ "$(getprop ro.build.version.sdk)" = 36 ] || exit 1
[ "$(getprop ro.vendor.build.version.incremental)" = 'OS3.0.307.0.WPPMIXM' ] || exit 1
[ ! -f /system/etc/ueventd/lapis.rc ] || exit 1
node=/dev/mi_display/disp_feature
sys=/sys/devices/virtual/mi_display/disp_feature
[ -r "$sys/dev" ] || exit 2
[ "$(sed -n 's/^DEVNAME=//p' "$sys/uevent")" = mi_display/disp_feature ] || exit 2
dev=$(cat "$sys/dev")
case "$dev" in *[!0-9:]*|'') exit 2;; esac
mkdir -p /dev/mi_display || exit 3
if [ ! -e "$node" ]; then
 mknod "$node" c "${dev%:*}" "${dev#*:}" || exit 3
fi
[ -c "$node" ] || exit 3
chown system:system "$node"
chmod 0660 "$node"
restorecon "$node"
