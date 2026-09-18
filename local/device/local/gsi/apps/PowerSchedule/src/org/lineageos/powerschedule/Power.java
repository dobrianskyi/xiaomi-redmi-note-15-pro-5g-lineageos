package org.lineageos.powerschedule;
import android.app.*;import android.content.*;import android.media.AudioManager;import java.io.*;import java.util.*;
final class Power {
 static final String ROLL="org.lineageos.powerschedule.ROLL",OFF="org.lineageos.powerschedule.OFF";static final Object LOCK=new Object();
 static Context dp(Context c){return c.createDeviceProtectedStorageContext();}
 static SharedPreferences prefs(Context c){return dp(c).getSharedPreferences("schedule",0);}
 static String rtc(Context c,String action)throws Exception{
  if(!Rtc.supported())throw new IOException("Power scheduling is unavailable on this device.");
  return Rtc.execute(action);
 }
 static long next(int h,int m,long after){return TimePlan.next(h,m,after);}
 static PendingIntent pi(Context c,long when){Intent i=new Intent(c,ScheduleReceiver.class).setAction(OFF).putExtra("when",when);return PendingIntent.getBroadcast(c,1,i,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);}
 static AlarmManager am(Context c){return (AlarmManager)c.getSystemService(Context.ALARM_SERVICE);}
 static void armOff(Context c,long off){am(c).cancel(pi(c,off));if(off>0)am(c).setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,off,pi(c,off));}
 static void armRoll(Context c,long when){Intent i=new Intent(c,ScheduleReceiver.class).setAction(ROLL);PendingIntent p=PendingIntent.getBroadcast(c,2,i,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);am(c).cancel(p);if(when>0)am(c).setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,when,p);}
 static String date(long n){return n==0?"Not scheduled":new java.text.SimpleDateFormat("EEE, d MMM • HH:mm",Locale.ENGLISH).format(new Date(n));}
 static void save(Context c,boolean on,boolean off,int oh,int om,int fh,int fm,boolean daily)throws Exception{long now=System.currentTimeMillis(),f=off?next(fh,fm,now):0,o=on?next(oh,om,now):0;saveAt(c,on,off,oh,om,fh,fm,daily,f,o);}
 static void saveAt(Context c,boolean on,boolean off,int oh,int om,int fh,int fm,boolean daily,long f,long o)throws Exception{synchronized(LOCK){
  if(!on&&!off){cancel(c);return;}if((off||on)&&!am(c).canScheduleExactAlarms())throw new IOException("Allow exact alarms to use power scheduling.");
  long now=System.currentTimeMillis();if((off&&f<=now+5000)||(on&&o<=now+5000))throw new IOException("The selected time has passed or is less than five seconds away. Choose a new time.");
  // Cancel shutdown first: a failed RTC write must never leave an old shutdown armed.
  armOff(c,0);prefs(c).edit().putLong("off",0).putBoolean("offEnabled",false).putString("message","Applying schedule…").commit();
  String result=rtc(c,on?"set "+o/1000:"cancel");
  prefs(c).edit().putBoolean("onEnabled",on).putBoolean("offEnabled",off).putBoolean("daily",daily).putInt("oh",oh).putInt("om",om).putInt("fh",fh).putInt("fm",fm).putLong("on",o).putLong("off",f).putString("message","Schedule applied.").putString("rtc",result).commit();
  armOff(c,f);armRoll(c,on?o+1000:0);
 }}
 static void cancel(Context c)throws Exception{synchronized(LOCK){armOff(c,0);armRoll(c,0);prefs(c).edit().putLong("off",0).putBoolean("offEnabled",false).commit();try{String r=rtc(c,"cancel");prefs(c).edit().clear().putString("message","Schedule cancelled").putString("rtc",r).commit();}catch(Exception e){prefs(c).edit().putString("message","Power off cancelled. Could not cancel power on: "+e.getMessage()).commit();throw e;}}}
 static void skip(Context c,String why)throws Exception{SharedPreferences p=prefs(c);p.edit().putLong("off",0).commit();if(p.getBoolean("daily",false))save(c,p.getBoolean("onEnabled",false),p.getBoolean("offEnabled",false),p.getInt("oh",7),p.getInt("om",0),p.getInt("fh",23),p.getInt("fm",0),true);p.edit().putString("message",why).commit();}
 static void receive(Context c,Intent i)throws Exception{synchronized(LOCK){SharedPreferences p=prefs(c);long now=System.currentTimeMillis();
  if(OFF.equals(i.getAction())){long f=p.getLong("off",0);if(f==0||f!=i.getLongExtra("when",-1)||now<f)return;if(now-f>90000){skip(c,"Power off skipped because the event arrived late.");return;}
   p.edit().putLong("off",0).putString("message","Scheduled power off").commit();
   if(((AudioManager)c.getSystemService(Context.AUDIO_SERVICE)).getMode()!=AudioManager.MODE_NORMAL){skip(c,"Power off skipped during a call or communication session.");return;}
   long o=p.getLong("on",0);if(p.getBoolean("onEnabled",false)){if(o<=now&&p.getBoolean("daily",false)){o=next(p.getInt("oh",7),p.getInt("om",0),now);rtc(c,"set "+o/1000);p.edit().putLong("on",o).commit();}else if(o>now){if(o<=now+5000)throw new IOException("Power off cancelled: power on is less than five seconds away.");rtc(c,"set "+o/1000);}}
   ((android.os.PowerManager)c.getSystemService(Context.POWER_SERVICE)).shutdown(false,"scheduled",false);return;
  }
  if(p.getBoolean("daily",false)&&(p.getBoolean("onEnabled",false)||p.getBoolean("offEnabled",false)))save(c,p.getBoolean("onEnabled",false),p.getBoolean("offEnabled",false),p.getInt("oh",7),p.getInt("om",0),p.getInt("fh",23),p.getInt("fm",0),true);
  else {long o=p.getLong("on",0),f=p.getLong("off",0);if(o>now+5000){rtc(c,"set "+o/1000);armRoll(c,o+1000);}else if(o<=now){p.edit().putLong("on",0).putBoolean("onEnabled",false).commit();armRoll(c,0);}if(f>now&&am(c).canScheduleExactAlarms())armOff(c,f);else {armOff(c,0);p.edit().putLong("off",0).commit();}}
 }}
}
