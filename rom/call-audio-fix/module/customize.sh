# Installed by the Magisk app; this does not install Magisk itself.
[ "$BOOTMODE" = true ] || abort "Install this ZIP from the Magisk app."
[ "$(getprop ro.product.vendor.device)" = lapis ] || abort "This module is for Xiaomi lapis only."
case "$(getprop ro.lineage.version)" in
    23.2-*) ;;
    *) abort "Requires LineageOS 23.2 / Android 16; the build date does not need to match." ;;
esac
[ "$(getprop ro.build.version.sdk)" = 36 ] || abort "Requires Android 16 (SDK 36)."
[ "$(getprop ro.vendor.build.version.incremental)" = 'OS3.0.307.0.WPPMIXM' ] || abort "Requires Xiaomi vendor OS3.0.307.0.WPPMIXM."
case "$(getprop ro.lineage.version)" in
    *gsi_lapis*) abort "This lapis ROM already integrates the fix. Install the system image without this legacy module." ;;
esac
[ ! -f /system/etc/ueventd/lapis.rc ] || abort "Integrated lapis fixes detected; this legacy module would duplicate them."
ui_print "Build-date restriction removed. Compatibility with this exact GSI is unverified."
set_perm_recursive "$MODPATH" 0 0 0755 0644
for script in "$MODPATH"/*.sh; do set_perm "$script" 0 0 0755; done
[ ! -f "$MODPATH/lapis-backlight" ] || set_perm "$MODPATH/lapis-backlight" 0 0 0755
ui_print "Experimental lapis workaround installed. Reboot and test the affected feature."
