# The lapis product does not inherit PHH base.mk/system.prop. Android's profile
# services default to disabled when these properties are absent. Use optional
# defaults so explicit stock vendor settings (especially unsupported LE Audio)
# remain authoritative.
PRODUCT_SYSTEM_PROPERTIES += \
    bluetooth.device.class_of_device=90,2,12 \
    bluetooth.profile.a2dp.source.enabled?=true \
    bluetooth.profile.asha.central.enabled?=true \
    bluetooth.profile.avrcp.target.enabled?=true \
    bluetooth.profile.bas.client.enabled?=true \
    bluetooth.profile.gatt.enabled?=true \
    bluetooth.profile.hfp.ag.enabled?=true \
    bluetooth.profile.hid.device.enabled?=true \
    bluetooth.profile.hid.host.enabled?=true \
    bluetooth.profile.map.server.enabled?=true \
    bluetooth.profile.opp.enabled?=true \
    bluetooth.profile.pan.nap.enabled?=true \
    bluetooth.profile.pan.panu.enabled?=true \
    bluetooth.profile.pbap.server.enabled?=true
