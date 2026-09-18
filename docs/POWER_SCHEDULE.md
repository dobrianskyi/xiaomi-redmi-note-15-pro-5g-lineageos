# Power schedule on lapis

Open **Settings → Battery → Power schedule**. The entry appears only for the
primary user when the RTC capability check succeeds. Custom UI labels are English.
Changes are saved immediately; no separate Save button is required.

## First hardware test

1. Leave **Turn off automatically** and **Repeat every day** off.
2. Set **Power on time** to 5–10 minutes from now, then enable
   **Turn on automatically**.
3. Check **Next scheduled events**: it must show the intended date/time and
   **Schedule applied.** If an error appears, do not proceed with shutdown.
4. Disconnect USB/charging, then shut down normally using the Power menu.
5. Leave the phone off and wait. At the chosen time it should start booting;
   Android reaching the lock screen takes additional time.
6. Afterwards use **Cancel all schedules → Cancel schedules** to clear the test.

This physical test is distinct from verifying that the UI opens or an RTC ioctl
succeeds. Do not mark powered-off wake-up as passed until the user observes it.
Test automatic shutdown separately after this succeeds. Choose power-off several
minutes before power-on; shutdown is skipped during a call/communication session.
A clock time already passed is scheduled for the next day, so check the date too.
