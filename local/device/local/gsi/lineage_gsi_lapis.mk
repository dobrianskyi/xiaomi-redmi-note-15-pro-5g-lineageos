# LineageOS with a root-free lapis profile for the preserved stock vendor.
$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_arm64.mk)
$(call inherit-product, device/local/gsi/lapis-base.mk)
$(call inherit-product, device/phh/treble/lineage.mk)

# lapis stock vendor reports VNDK 34. Do not pull Android 9/10 snapshots into
# this device baseline: their vendorcompat modules collide with Lineage compat.
PRODUCT_EXTRA_VNDK_VERSIONS := 34

PRODUCT_NAME := lineage_gsi_lapis
PRODUCT_DEVICE := tdgsi_arm64_ab
PRODUCT_BRAND := LineageOS
PRODUCT_SYSTEM_BRAND := LineageOS
PRODUCT_MODEL := LineageOS ARM64 GSI
PRODUCT_CHARACTERISTICS := device

DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE += device/local/gsi/compatibility_matrix.xml
# Avoid duplicating the camera prefix already declared by the stock vendor.
BOARD_SEPOLICY_M4DEFS += lapis_stock_camera_property=true

PRODUCT_PACKAGES += LapisPowerSchedule LapisDolby LapisUdfpsGeometry LapisShadeGestures LapisMtkIms
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += device/local/gsi/sepolicy/private

PRODUCT_COPY_FILES += \
    device/local/gsi/ueventd/lapis.rc:$(TARGET_COPY_OUT_SYSTEM)/etc/ueventd/lapis.rc

PRODUCT_PACKAGES += LapisImsFramework LapisImsTelephony LapisImsCarriers

$(call inherit-product, device/local/gsi/gapps.mk)

# Stock lapis display cutout and safe status-bar geometry.
PRODUCT_PACKAGES += LapisDisplayGeometry LapisStatusBarGeometry
