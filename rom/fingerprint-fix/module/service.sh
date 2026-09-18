#!/system/bin/sh
MODDIR=${0%/*}
[ ! -e "$MODDIR/disable" ] && [ ! -e "$MODDIR/remove" ] || exit 0
sh "$MODDIR/device-node.sh" || exit 1
sh "$MODDIR/state-bridge.sh" &
