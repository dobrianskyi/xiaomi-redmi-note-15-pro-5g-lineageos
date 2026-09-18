package org.lineageos.dolby;
import android.content.*;
import android.media.*;
import android.media.audiofx.AudioEffect;
import java.util.*;
import java.nio.*;
import java.nio.file.*;
import java.util.concurrent.*;

final class Engine {
 private static Engine instance;
 static Path DIR;
 static final String DEFAULT_CONFIG="1 20 9 0";
 final ExecutorService worker=Executors.newSingleThreadExecutor();
 final SharedPreferences prefs;
 final AudioManager audio;
 final AudioAttributes media=new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).build();
 AudioEffect current;
 String status="Not applied", originalTuning;
 int originalProfile,originalProcessing;
 boolean originalEnabled;
 static synchronized Engine get(Context context) {
  if(instance==null)instance=new Engine(context.getApplicationContext());
  return instance;
 }
 private Engine(Context context) {
  Context storage=context.createDeviceProtectedStorageContext();
  DIR=storage.getFilesDir().toPath().resolve("profiles-"+Integer.toUnsignedString(android.os.SystemProperties.get("ro.vendor.build.fingerprint").hashCode(),16));
  prefs=storage.getSharedPreferences("dolby",0);
  audio=context.getSystemService(AudioManager.class);
  worker.execute(() -> {
   try {
    Files.createDirectories(DIR);
    audio.addOnModeChangedListener(worker,mode -> reapply());
    audio.addOnDevicesForAttributesChangedListener(media,worker,(attributes,devices)->reapply());
    audio.setAudioServerStateCallback(worker,new AudioManager.AudioServerStateCallback() {
     @Override public void onAudioServerDown() {
      synchronized(Engine.this) {
       if(current!=null){current.release();current=null;}
       status="Audio service is restarting.";
      }
     }
     @Override public void onAudioServerUp() {reapply();}
    });
    reapply();
   } catch(Exception ex) { synchronized(this) {status="Unavailable: "+ex.getMessage();} }
  });
 }
 static boolean supported() {
  if(android.os.UserHandle.myUserId()!=0 || !"lapis".equals(android.os.SystemProperties.get("ro.product.vendor.device")))return false;
  AudioEffect.Descriptor[] effects=AudioEffect.queryEffects();
  if(effects==null)return false;
  for(AudioEffect.Descriptor d:effects)if(d.uuid.equals(UUID.fromString("9d4921da-8225-4f29-aefa-39537a04bcaa")))return true;
  return false;
 }
 synchronized String state() {return prefs.getString("config",DEFAULT_CONFIG)+"\n"+status;}
 synchronized void reapply() {try{apply(prefs.getString("config",DEFAULT_CONFIG));}catch(Exception ex){status="Error: "+ex.getMessage();}}
 private boolean speakerMedia() {
  List<AudioDeviceAttributes> devices=audio.getDevicesForAttributes(media);
  return audio.getMode()==AudioManager.MODE_NORMAL && !devices.isEmpty() &&
   devices.stream().allMatch(d->d.getType()==AudioDeviceInfo.TYPE_BUILTIN_SPEAKER);
 }
 private void release()throws Exception {
  if(current==null)return;
  AudioEffect e=current;current=null;
  try {
   if(e.hasControl()) {
    restoreProfiles(e);
    tuning(e,originalTuning);si(e,0xA000000,originalProfile);si(e,0,originalProcessing);
    e.setEnabled(originalEnabled);
   }
  }finally{e.release();}
 }
 synchronized String apply(String config)throws Exception {
  String[] a=config.split("\\s+");
  if(a.length!=4)throw new IllegalArgumentException("Invalid configuration");
  int on=Integer.parseInt(a[0]),gain=Integer.parseInt(a[1]),choice=Integer.parseInt(a[2]),device=Integer.parseInt(a[3]);
  if((on!=0&&on!=1)||gain< -6||gain>50||choice<0||choice>9||device<0||device>=TUNINGS.length)
   throw new IllegalArgumentException("Invalid setting value");
  try {
   if(on==0) {release();status="Processing is off.";}
   else if(!supported())throw new IllegalStateException("Dolby is unavailable on this device.");
   else if(!speakerMedia()) {release();status="Saved. Processing resumes for speaker media after calls or headphones.";}
   else {
    if(current==null) {
     AudioEffect created=effect();
     try {
      if(!created.hasControl())throw new IllegalStateException("Another app controls Dolby.");
      Path baseline=DIR.resolve("baseline");
      if(!Files.exists(baseline)) {
       String state=selected(created)+"\n"+iv(created,0xA000000)+"\n"+iv(created,0)+"\n"+created.getEnabled();
       Path temp=DIR.resolve("baseline.tmp");Files.writeString(temp,state);Files.move(temp,baseline,StandardCopyOption.ATOMIC_MOVE);
      }
      List<String> original=Files.readAllLines(baseline);
      originalTuning=original.get(0);originalProfile=Integer.parseInt(original.get(1));
      originalProcessing=Integer.parseInt(original.get(2));originalEnabled=Boolean.parseBoolean(original.get(3));
      current=created;
      current.setControlStatusListener((effect,granted)->{if(granted)worker.execute(this::reapply);});
     }catch(Exception ex){created.release();throw ex;}
    }
    AudioEffect e=current;
    if(!e.hasControl())throw new IllegalStateException("Another app controls Dolby.");
    restoreProfiles(e);
    int profile=choice==9?3:choice;
    for(int param:PARAMS)original(e,profile,param);
    tuning(e,TUNINGS[device]);
    int[] bands=original(e,profile,110).clone();
    for(int i=0;i<bands.length;i++)bands[i]=(choice==9?0:bands[i])+gain*16;
    for(int param:PARAMS)if(param!=110&&param!=106)sp(e,profile,param,original(e,profile,param));
    if(choice==9) {
     int[] keys={103,104,105,107,108,111,112},values={0,1,1,6,8,0,1};
     for(int i=0;i<keys.length;i++)sp(e,profile,keys[i],new int[]{values[i]});
    }
    sp(e,profile,106,new int[]{1});sp(e,profile,110,bands);si(e,0xA000000,profile);si(e,0,1);
    int result=e.setEnabled(true);boolean verified=false;
    for(int attempt=0;attempt<4;attempt++) {
     if(attempt>0)Thread.sleep(150);
     verified=result==0&&e.getEnabled()&&Arrays.equals(gp(e,profile,110,20),bands)&&selected(e).equals(TUNINGS[device]);
     if(verified)break;
    }
    if(!verified)throw new IllegalStateException("The audio effect did not confirm the requested settings.");
    status="Applied: "+gain+" dB. Profile saved.";
   }
   if(!prefs.edit().putString("config",config).commit())throw new java.io.IOException("Could not save settings.");
   return status;
  }catch(Exception ex){try{release();}catch(Exception restoreError){ex.addSuppressed(restoreError);}status="Error: "+ex.getMessage();throw ex;}
 }
 static int iv(AudioEffect e,int p)throws Exception{byte[]b=ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN).putInt(p).array();int rc=(Integer)AudioEffect.class.getMethod("getParameter",int.class,byte[].class).invoke(e,5+p,b);if(rc<0)throw new Exception("get="+rc);return ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).getInt();}
 static void sv(AudioEffect e,int key,byte[] b)throws Exception{int rc=(Integer)AudioEffect.class.getMethod("setParameter",int.class,byte[].class).invoke(e,key,b);if(rc<0)throw new Exception("set="+rc);}
 static void si(AudioEffect e,int p,int v)throws Exception{sv(e,5,ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN).putInt(p).putInt(1).putInt(v).array());}
 static void tuning(AudioEffect e,String name)throws Exception{byte[]b=name.getBytes(java.nio.charset.StandardCharsets.UTF_8);sv(e,4,ByteBuffer.allocate(4+b.length).order(ByteOrder.LITTLE_ENDIAN).putInt(0).put(b).array());}
 static int[] gp(AudioEffect e,int profile,int p,int len)throws Exception {byte[] b=new byte[(len+2)*4];int rc=(Integer)AudioEffect.class.getMethod("getParameter",int.class,byte[].class).invoke(e,0x1000005+(p<<16)+(profile<<8),b);if(rc<len*4)throw new Exception("param read="+rc);int[]v=new int[len];ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).asIntBuffer().get(v);return v;}
 static void sp(AudioEffect e,int profile,int p,int[]v)throws Exception{ByteBuffer b=ByteBuffer.allocate((v.length+4)*4).order(ByteOrder.LITTLE_ENDIAN);b.putInt(0x1000000).putInt(v.length+1).putInt(profile).putInt(p);for(int a:v)b.putInt(a);sv(e,5,b.array());}

 static AudioEffect effect()throws Exception{return AudioEffect.class.getConstructor(UUID.class,UUID.class,int.class,int.class).newInstance(new UUID(0,0),UUID.fromString("9d4921da-8225-4f29-aefa-39537a04bcaa"),0,0);}

 static final int[] PARAMS={103,104,105,106,107,108,110,111,112};
 static int[] original(AudioEffect e,int profile,int param)throws Exception{
  Path f=DIR.resolve("original-"+profile+"-"+param);
  if(!Files.exists(f)){
   int[] v=gp(e,profile,param,param==110?20:1);
   StringJoiner j=new StringJoiner(" ");for(int n:v)j.add(Integer.toString(n));
   Path t=DIR.resolve(f.getFileName()+".tmp");Files.write(t,j.toString().getBytes("UTF-8"));Files.move(t,f,StandardCopyOption.ATOMIC_MOVE);
  }
  return Arrays.stream(new String(Files.readAllBytes(f),"UTF-8").trim().split("\\s+")).mapToInt(Integer::parseInt).toArray();
 }
 static void restoreProfiles(AudioEffect e)throws Exception{
  for(int pr:new int[]{0,1,2,3,4,5,6,7,8})for(int param:PARAMS)if(Files.exists(DIR.resolve("original-"+pr+"-"+param)))sp(e,pr,param,original(e,pr,param));
 }
 static final String[] TUNINGS={"speaker_portrait","speaker_landscape","default_internal_speaker","speaker_spatilizer_90","speaker_spatilizer_270"};
 static String selected(AudioEffect e)throws Exception{byte[] b=new byte[512];int rc=(Integer)AudioEffect.class.getMethod("getParameter",int.class,byte[].class).invoke(e,4,b);if(rc<0)throw new Exception("tuning read "+rc);return new String(b,"UTF-8").trim();}
}
