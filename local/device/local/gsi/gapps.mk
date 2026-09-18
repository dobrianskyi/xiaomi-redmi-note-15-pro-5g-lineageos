# Selected by build.sh under the build lock. Manual lunch defaults to vanilla.
-include device/local/gsi/build-variant.mk
LAPIS_GAPPS ?= none

ifneq ($(filter minimal full,$(LAPIS_GAPPS)),)
PRODUCT_SOONG_NAMESPACES += vendor/gapps/arm64 vendor/gapps/common
PRODUCT_PACKAGES += \
    GmsCore Phonesky GoogleServicesFramework SetupWizard \
    GooglePartnerSetup GoogleFeedback \
    GoogleCalendarSyncAdapter GoogleContactsSyncAdapter \
    default-permissions-google.xml default-permissions-mtg.xml \
    gms_fsverity_cert.der google-hiddenapi-package-allowlist.xml google.xml \
    privapp-permissions-google-product.xml privapp-permissions-google-system-ext.xml \
    privapp-permissions-mtg.xml \
    GmsSettingsOverlay GmsSettingsProviderOverlay GmsSetupWizardOverlay

ifeq ($(LAPIS_GAPPS),full)
# MindTheGapps ARM64 selection except the legacy Exchange APK: its pinned
# signature fails verification. Do not advertise its Exchange feature either.
PRODUCT_PACKAGES += \
    GmsOverlay gapps.rc lapis-sysconfig-gapps-full.xml \
    AndroidAutoStub FamilyLinkParentalControls GoogleRestore MarkupGoogle_v2 \
    SpeechServicesByGoogle Velvet Wellbeing talkback libjni_latinimegoogle \
    com.google.android.dialer.support com.google.android.dialer.support.xml \
    d2d_cable_migration_feature.xml wellbeing.xml
else
PRODUCT_PACKAGES += \
    LapisGmsMinimalOverlay lapis-gapps-minimal.rc lapis-sysconfig-gapps-minimal.xml
endif
else ifneq ($(LAPIS_GAPPS),none)
$(error Unknown LAPIS_GAPPS: $(LAPIS_GAPPS))
endif
