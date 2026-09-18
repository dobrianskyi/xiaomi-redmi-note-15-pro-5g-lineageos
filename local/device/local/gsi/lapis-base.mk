# Modern stock lapis vendor; no generic PHH boot scripts or permissive policy.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_base_telephony.mk)

# Keep device resource overlays; these contain no root service.
$(call inherit-product, vendor/hardware_overlay/overlay.mk)
include build/make/target/product/gsi_release.mk

# Explicit activation is required when a partition has overlay/config/config.xml.
PRODUCT_COPY_FILES := $(filter-out device/generic/common/overlays/overlay-config.xml:%,$(PRODUCT_COPY_FILES))
PRODUCT_COPY_FILES += \
    device/local/gsi/overlays/config.xml:$(TARGET_COPY_OUT_SYSTEM_EXT)/overlay/config/config.xml \
    frameworks/native/data/etc/android.hardware.fingerprint.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/android.hardware.fingerprint.xml \
    frameworks/native/data/etc/android.hardware.telephony.gsm.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/android.hardware.telephony.gsm.xml \
    frameworks/native/data/etc/android.hardware.telephony.ims.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/android.hardware.telephony.ims.xml \
    frameworks/native/data/etc/android.hardware.bluetooth.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/android.hardware.bluetooth.xml \
    frameworks/native/data/etc/android.hardware.bluetooth_le.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/android.hardware.bluetooth_le.xml \
    frameworks/native/data/etc/android.hardware.usb.host.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/android.hardware.usb.host.xml

PRODUCT_PACKAGES := $(filter-out TrebleApp,$(PRODUCT_PACKAGES))
PRODUCT_PACKAGES += LapisTrebleApp

PRODUCT_PACKAGES += Stk Iwlan QualifiedNetworksService MtkInCallService
# hardware_overlay includes TrebleApp; its privileged permissions must be
# allowlisted even though this profile does not inherit PHH's generic base.mk.
PRODUCT_COPY_FILES += \
    device/phh/treble/privapp-permissions-me.phh.treble.app.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/privapp-permissions-me.phh.treble.app.xml

# Build the lapis app without Qualcomm handlers; keep non-QTI interfaces used
# by the remaining generic/Xiaomi settings.
PRODUCT_PACKAGES += \
    android.hidl.manager-V1.0-java \
    vendor.huawei.hardware.biometrics.fingerprint-V2.1-java \
    vendor.huawei.hardware.tp-V1.0-java \
    vendor.xiaomi.hardware.displayfeature-V1.0-java
PRODUCT_COPY_FILES += \
    device/local/gsi/treble-interfaces.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/interfaces.xml
PRODUCT_SYSTEM_PROPERTIES += ro.adb.secure=1
SELINUX_IGNORE_NEVERALLOWS := false
