package org.lineageos.powerschedule;
import android.content.*;import android.os.PowerManager;
public class ScheduleReceiver extends BroadcastReceiver {
 public void onReceive(Context c,Intent i){
  boolean supported=android.os.UserHandle.myUserId()==0 && Rtc.supported();
  c.getPackageManager().setComponentEnabledSetting(new ComponentName(c,MainActivity.class),
   supported?android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_ENABLED:android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
   android.content.pm.PackageManager.DONT_KILL_APP);
  if(!supported){Power.armOff(c,0);Power.armRoll(c,0);return;}
PendingResult r=goAsync();PowerManager.WakeLock w=((PowerManager)c.getSystemService(Context.POWER_SERVICE)).newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"lapis:schedule");w.acquire(60000);new Thread(()->{try{Power.receive(c,i);}catch(Exception e){Power.prefs(c).edit().putString("message","Error: "+e.getMessage()).commit();}finally{if(w.isHeld())w.release();r.finish();}},"power-schedule").start();}
}
