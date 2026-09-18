# Device status — 2026-09-18

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
| Other hardware | Not comprehensively certified; camera, NFC, Bluetooth, sensors and long-term suspend require further testing |

The project does not claim all issues are closed. No Magisk, su, diagnostic ADB
startup file or host ADB public key is included in the release. The public build
uses Android test keys and is not an official supported LineageOS release.
