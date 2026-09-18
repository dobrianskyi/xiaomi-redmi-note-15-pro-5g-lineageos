package org.lineageos.powerschedule;
import java.time.*;import java.util.*;
public class TimePlanTest {
 static long at(String s){return ZonedDateTime.parse(s).toInstant().toEpochMilli();}
 static void check(long a,String b){if(a!=at(b))throw new AssertionError(Instant.ofEpochMilli(a)+" != "+b);}
 public static void main(String[] args){TimeZone.setDefault(TimeZone.getTimeZone("Europe/Kyiv"));
 long now=at("2026-09-14T16:00:00+03:00[Europe/Kyiv]");long off=TimePlan.next(23,0,now);check(off,"2026-09-14T23:00:00+03:00[Europe/Kyiv]");check(TimePlan.next(7,0,off),"2026-09-15T07:00:00+03:00[Europe/Kyiv]");
 check(TimePlan.next(0,1,at("2026-12-31T23:59:00+02:00[Europe/Kyiv]")),"2027-01-01T00:01:00+02:00[Europe/Kyiv]");
 check(TimePlan.next(7,0,at("2028-02-28T23:00:00+02:00[Europe/Kyiv]")),"2028-02-29T07:00:00+02:00[Europe/Kyiv]");
 check(TimePlan.next(7,0,at("2026-03-28T23:00:00+02:00[Europe/Kyiv]")),"2026-03-29T07:00:00+03:00[Europe/Kyiv]");
 check(TimePlan.next(7,0,at("2026-10-24T23:00:00+03:00[Europe/Kyiv]")),"2026-10-25T07:00:00+02:00[Europe/Kyiv]");
 check(TimePlan.next(16,2,now),"2026-09-14T16:02:00+03:00[Europe/Kyiv]");
 try{TimePlan.next(24,0,now);throw new AssertionError();}catch(IllegalArgumentException expected){}
 System.out.println("TimePlan: overnight pair, year/leap boundary, DST, near-future time stays today, validation passed");}
}
