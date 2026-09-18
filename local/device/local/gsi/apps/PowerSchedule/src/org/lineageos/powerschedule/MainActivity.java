package org.lineageos.powerschedule;

import android.app.TimePickerDialog;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.Preference;
import android.preference.PreferenceActivity;
import android.preference.PreferenceCategory;
import android.preference.PreferenceScreen;
import android.preference.SwitchPreference;
import android.view.MenuItem;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends PreferenceActivity {
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private SwitchPreference on, off, daily;
    private Preference onTime, offTime, status;
    private boolean busy;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        if (android.os.UserHandle.myUserId() != 0 || !Rtc.supported()) { finish(); return; }
        setTitle("Power schedule");
        if (getActionBar() != null) getActionBar().setDisplayHomeAsUpEnabled(true);
        PreferenceScreen screen = getPreferenceManager().createPreferenceScreen(this);
        setPreferenceScreen(screen);
        PreferenceCategory powerOn = new PreferenceCategory(this);
        powerOn.setTitle("Power on"); screen.addPreference(powerOn);
        on = toggle("Turn on automatically", powerOn);
        onTime = new Preference(this); onTime.setTitle("Power on time"); powerOn.addPreference(onTime);
        PreferenceCategory powerOff = new PreferenceCategory(this);
        powerOff.setTitle("Power off"); screen.addPreference(powerOff);
        off = toggle("Turn off automatically", powerOff);
        offTime = new Preference(this); offTime.setTitle("Power off time"); powerOff.addPreference(offTime);
        daily = new SwitchPreference(this); daily.setTitle("Repeat every day");
        daily.setPersistent(false); screen.addPreference(daily);
        status = new Preference(this); status.setTitle("Next scheduled events");
        status.setSelectable(false); screen.addPreference(status);
        Preference cancel = new Preference(this); cancel.setTitle("Cancel all schedules");
        screen.addPreference(cancel);
        Preference note = new Preference(this); note.setSelectable(false);
        note.setSummary("Power on time is when the phone starts, not when Android finishes loading. "
                + "Power off is skipped during a call. Changes are saved immediately.");
        screen.addPreference(note);
        on.setOnPreferenceChangeListener((p,v) -> { save((boolean)v,off.isChecked(),daily.isChecked()); return false; });
        off.setOnPreferenceChangeListener((p,v) -> { save(on.isChecked(),(boolean)v,daily.isChecked()); return false; });
        daily.setOnPreferenceChangeListener((p,v) -> { save(on.isChecked(),off.isChecked(),(boolean)v); return false; });
        onTime.setOnPreferenceClickListener(p -> { pick(true); return true; });
        offTime.setOnPreferenceClickListener(p -> { pick(false); return true; });
        cancel.setOnPreferenceClickListener(p -> {
            new android.app.AlertDialog.Builder(this).setTitle("Cancel all schedules?")
                    .setMessage("Turn off scheduled power on and power off.")
                    .setNegativeButton("Keep schedules", null)
                    .setPositiveButton("Cancel schedules", (d,w) -> run(() -> Power.cancel(this))).show();
            return true;
        });
        refresh();
    }

    private SwitchPreference toggle(String title, PreferenceCategory group) {
        SwitchPreference preference = new SwitchPreference(this);
        preference.setTitle(title); preference.setPersistent(false); group.addPreference(preference);
        return preference;
    }

    private void pick(boolean powerOn) {
        SharedPreferences p = Power.prefs(this);
        String h = powerOn ? "oh" : "fh", m = powerOn ? "om" : "fm";
        new TimePickerDialog(this, (view,hour,minute) -> {
            if (busy) return;
            int oh = powerOn ? hour : p.getInt("oh",7), om = powerOn ? minute : p.getInt("om",0);
            int fh = powerOn ? p.getInt("fh",23) : hour, fm = powerOn ? p.getInt("fm",0) : minute;
            boolean active = powerOn ? on.isChecked() : off.isChecked();
            if (active) {
                boolean a = on.isChecked(), b = off.isChecked(), repeat = daily.isChecked();
                run(() -> Power.save(this,a,b,oh,om,fh,fm,repeat));
            } else { p.edit().putInt(h,hour).putInt(m,minute).apply(); refresh(); }
        }, p.getInt(h,powerOn?7:23), p.getInt(m,0), true).show();
    }

    private void save(boolean a, boolean b, boolean repeat) {
        SharedPreferences p = Power.prefs(this);
        int oh=p.getInt("oh",7), om=p.getInt("om",0), fh=p.getInt("fh",23), fm=p.getInt("fm",0);
        run(() -> {
            Power.save(this,a,b,oh,om,fh,fm,repeat);
            if (!a && !b) p.edit().putBoolean("daily",repeat).putInt("oh",oh).putInt("om",om)
                    .putInt("fh",fh).putInt("fm",fm).commit();
        });
    }

    private interface Job { void run() throws Exception; }
    private void run(Job job) {
        if (busy) return;
        busy=true; getPreferenceScreen().setEnabled(false); status.setSummary("Applying schedule…");
        worker.execute(() -> {
            try { job.run(); }
            catch (Exception e) { Power.prefs(this).edit().putString("message","Error: "+e.getMessage()).commit(); }
            runOnUiThread(() -> { busy=false; if (!isDestroyed()) { getPreferenceScreen().setEnabled(true); refresh(); } });
        });
    }

    private void refresh() {
        SharedPreferences p=Power.prefs(this); long now=System.currentTimeMillis();
        long start=p.getLong("on",0), end=p.getLong("off",0);
        on.setChecked(p.getBoolean("onEnabled",false) && start>now);
        off.setChecked(p.getBoolean("offEnabled",false) && end>now);
        daily.setChecked(p.getBoolean("daily",false));
        onTime.setSummary(String.format(Locale.ENGLISH,"%02d:%02d",p.getInt("oh",7),p.getInt("om",0)));
        offTime.setSummary(String.format(Locale.ENGLISH,"%02d:%02d",p.getInt("fh",23),p.getInt("fm",0)));
        status.setSummary("Power on: "+Power.date(start>now?start:0)+"\nPower off: "+Power.date(end>now?end:0)
                +"\n"+p.getString("message", "No schedule set."));
    }
    @Override public void onResume() { super.onResume(); if (status!=null && !busy) refresh(); }
    @Override public void onDestroy() { worker.shutdown(); super.onDestroy(); }
    @Override public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId()==android.R.id.home) { finish(); return true; }
        return super.onOptionsItemSelected(item);
    }
}
