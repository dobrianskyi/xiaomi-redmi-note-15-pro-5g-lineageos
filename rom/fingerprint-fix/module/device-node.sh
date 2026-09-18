#!/system/bin/sh
[ "$(getprop ro.product.vendor.device)" = lapis ] || exit 1
[ "$(getprop ro.lineage.version)" = '23.2-20260524-GAPPS-EXT4-GSI' ] || exit 1
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
