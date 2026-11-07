# Magisk-app ZIP installer; this does not install Magisk itself.
[ "$BOOTMODE" = true ] || abort "Install this ZIP from the Magisk app."
[ "$(getprop ro.product.vendor.device)" = lapis ] || abort "This module is for Xiaomi lapis only."
case "$(getprop ro.lineage.version)" in
    23.2-*gsi_lapis) ;;
    *) abort "Requires a LineageOS 23.2 gsi_lapis build; the build date does not need to match." ;;
esac
[ "$(getprop ro.build.version.sdk)" = 36 ] || abort "Requires Android 16 (SDK 36)."
ui_print "Only missing Bluetooth defaults are added; existing values are preserved."
[ "$(getprop ro.vendor.build.version.incremental)" = 'OS3.0.307.0.WPPMIXM' ] || abort "Only the tested Xiaomi OS3.0.307.0.WPPMIXM vendor is supported."
set_perm_recursive "$MODPATH" 0 0 0755 0644
set_perm "$MODPATH/post-fs-data.sh" 0 0 0755
ui_print "Missing Bluetooth profile defaults will be restored at the next boot."
ui_print "Explicit vendor settings are preserved. Pairings are not reset."
