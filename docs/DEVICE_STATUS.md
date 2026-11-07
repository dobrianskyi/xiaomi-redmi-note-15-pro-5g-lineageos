# Device status — updated 2026-11-07

**November 7 Android 17 update:** the exact refreshed image passed boot,
encrypted unlock and enforcing SELinux checks, retaining all 35 existing user-app
UIDs and data directories. Framework vibrator ID0 is present; a 1500ms one-shot
completed and the user confirmed the Ring preview physically. Explicit media
mute survived a real reboot with effective volume zero, then unmute restored the
prior level4. Accessibility and TTS remained unmuted. Earlier PIN auto-confirm
and other integrated fixes are retained. These observations do not certify every
hardware path below. See [Android 17 release details](ANDROID17.md).

## Earlier hardware observations (Android 16)


**October Bluetooth hotfix:** missing profile defaults were restored on the
installed `23.2-20260918-UNOFFICIAL-gsi_lapis` using the separate Magisk payload.
A2DP/HFP and other ordinary profile services started; controlled Classic and BLE
discovery passed, with zero Bluetooth crashes. Real pairing/audio/calls, connection
stability, long-term battery use and a full reboot with the module are not yet
verified. These checks do not constitute a new complete-image test.
[Hotfix details](../rom/bluetooth-fix/README.md).

Test device: Xiaomi `lapis`, stock vendor/firmware OS3.0.307.0.WPPMIXM.
A clean installation of the immediately preceding build booted and reached setup.
The final clock-geometry correction was then applied as platform-signed overlays
on that phone and confirmed physically by its user. The downloadable final image
includes the same overlays, but its exact complete bytes have not received another
clean-flash test. It passed all ten offline baseline checks.

| Area | Evidence / limit |
|---|---|
| Boot, setup, screen wake | Working after prior fixes; user confirmed stable display and Power wake |
| Fingerprint | User confirmed unlocking; enrolled fingerprint must be added again after a reset |
| Dolby | User confirmed working stock vendor effect |
| Call / communication speaker gain | User confirmed improvement before integration |
| Home / lockscreen shade gestures | User confirmed top-edge behavior |
| Left status-bar clock | User confirmed complete digits after stock geometry correction |
| Wi-Fi | User confirmed connectivity |
| VoLTE | IMS over LTE observed on both tested SIM slots; final-build real calls still need validation |
| VoWi-Fi | IWLAN registration observed on lifecell; tunnel rejection/timeouts also logged; not certified stable for both carriers |
| Power schedule | Battery entry and private storage work; powered-off RTC boot still needs physical testing |
| SELinux | Enforcing, no permissive domains in the merged policy checks |
| Bluetooth | October hotfix: profile startup and controlled Classic/BLE discovery passed; pairing, sustained connections, battery use and reboot still require testing |
| Vibration (Android 17) | Framework discovery and one-shot passed; user confirmed Ring preview; vibration strength remains vendor/settings dependent |
| Media mute (Android 17) | Real reboot retained mute; unmute restored prior level |
| Other hardware | Not comprehensively certified; camera, NFC, sensors and long-term suspend require further testing |

The project does not claim all issues are closed. No Magisk, su, diagnostic ADB
startup file or host ADB public key is included in the release. The public build
uses Android test keys and is not an official supported LineageOS release.
