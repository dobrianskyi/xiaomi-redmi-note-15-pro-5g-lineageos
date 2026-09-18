# Installed by the Magisk app; this does not install Magisk itself.
[ "$(getprop ro.product.vendor.device)" = lapis ] || abort "This module is for Xiaomi lapis only."
[ "$(getprop ro.lineage.version)" = '23.2-20260524-GAPPS-EXT4-GSI' ] || abort "Only the documented reference GSI is supported. Do not stack on the root-free lapis ROM."
set_perm_recursive "$MODPATH" 0 0 0755 0644
for script in "$MODPATH"/*.sh; do set_perm "$script" 0 0 0755; done
[ ! -f "$MODPATH/lapis-backlight" ] || set_perm "$MODPATH/lapis-backlight" 0 0 0755
ui_print "Experimental lapis workaround installed. Reboot and test the affected feature."
