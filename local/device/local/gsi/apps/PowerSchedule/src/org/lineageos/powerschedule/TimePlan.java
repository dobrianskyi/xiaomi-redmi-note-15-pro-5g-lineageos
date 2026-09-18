package org.lineageos.powerschedule;
import java.util.Calendar;
final class TimePlan {
 static long next(int h,int m,long after){
  if(h<0||h>23||m<0||m>59)throw new IllegalArgumentException("Invalid local time");
  Calendar t=Calendar.getInstance();t.setTimeInMillis(after);t.set(Calendar.HOUR_OF_DAY,h);t.set(Calendar.MINUTE,m);t.set(Calendar.SECOND,0);t.set(Calendar.MILLISECOND,0);if(t.getTimeInMillis()<=after)t.add(Calendar.DAY_OF_YEAR,1);return t.getTimeInMillis();
 }
}
