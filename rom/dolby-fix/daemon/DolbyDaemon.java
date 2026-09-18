import android.media.audiofx.AudioEffect;
import java.util.*;
import java.nio.*;
import java.nio.file.*;
public class DolbyDaemon {
 static final Path DIR=Paths.get("/data/adb/lapis_dolby");
 static void status(String value)throws Exception {Path t=DIR.resolve("status.tmp");Files.write(t,value.getBytes("UTF-8"));Files.move(t,DIR.resolve("status"),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
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
   // v0.1 owned Custom EQ/leveler; use its documented pre-app baseline.
   if(profile==3&&param==110)Arrays.fill(v,0);
   if(profile==3&&(param==103||param==106))v[0]=1;
   StringJoiner j=new StringJoiner(" ");for(int n:v)j.add(Integer.toString(n));
   Path t=DIR.resolve(f.getFileName()+".tmp");Files.write(t,j.toString().getBytes("UTF-8"));Files.move(t,f,StandardCopyOption.ATOMIC_MOVE);
  }
  return Arrays.stream(new String(Files.readAllBytes(f),"UTF-8").trim().split("\\s+")).mapToInt(Integer::parseInt).toArray();
 }
 static void restoreProfiles(AudioEffect e)throws Exception{
  for(int pr:new int[]{0,1,2,3,4,5,6,7,8})for(int param:PARAMS)if(Files.exists(DIR.resolve("original-"+pr+"-"+param)))sp(e,pr,param,original(e,pr,param));
 }
 static final String[] TUNINGS={"speaker_portrait","speaker_landscape","default_internal_speaker","speaker_spatilizer_90","speaker_spatilizer_270"};
 static void baseline(AudioEffect e)throws Exception{restoreProfiles(e);si(e,0,1);tuning(e,"default_internal_speaker");si(e,0xA000000,0);e.setEnabled(false);}
 static String selected(AudioEffect e)throws Exception{byte[] b=new byte[512];int rc=(Integer)AudioEffect.class.getMethod("getParameter",int.class,byte[].class).invoke(e,4,b);if(rc<0)throw new Exception("tuning read "+rc);return new String(b,"UTF-8").trim();}
 static void snapshot(AudioEffect e,int profile)throws Exception{
  StringBuilder b=new StringBuilder("enabled="+e.getEnabled()+" profile="+iv(e,0xA000000)+" tuning="+selected(e)+"\n");
  for(int p=101;p<=116;p++)try{b.append(p+"="+Arrays.toString(gp(e,profile,p,p==110?20:1))+"\n");}catch(Exception ex){b.append(p+" unavailable\n");}
  Files.write(DIR.resolve("snapshot"),b.toString().getBytes("UTF-8"));
 }
 public static void main(String[] args)throws Exception{
  java.nio.channels.FileChannel lc=java.nio.channels.FileChannel.open(DIR.resolve("java.lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE);
  java.nio.channels.FileLock lock=lc.tryLock();if(lock==null){System.exit(42);return;}
  Files.write(DIR.resolve("pid"),Integer.toString(android.os.Process.myPid()).getBytes("UTF-8"));
  AudioEffect e=null;String previous="",lastTuning="";int ticks=0;
  while(true){try{
   String config=new String(Files.readAllBytes(DIR.resolve("config")),"UTF-8").trim();String[] a=config.split("\\s+");
   if(a.length!=2&&a.length!=4)throw new Exception("invalid config");int on=Integer.parseInt(a[0]),gain=Integer.parseInt(a[1]);if((on!=0&&on!=1)||gain< -6||gain>50)throw new Exception("range");
   int choice=a.length==2?9:Integer.parseInt(a[2]),device=a.length==2?0:Integer.parseInt(a[3]);
   if(choice<0||choice>9||device<0||device>=TUNINGS.length)throw new Exception("invalid profile");
   int profile=choice==9?3:choice;String result=on+" "+gain+" "+choice+" "+device;
   if(!config.equals(previous)||++ticks>=5){ticks=0;
    if(on==0){if(e!=null){baseline(e);e.release();e=null;}status("OK "+result);}
    else {if(e==null)e=effect();if(!e.hasControl())throw new Exception("no control");
     if(!config.equals(previous))restoreProfiles(e);
     for(int param:PARAMS)original(e,profile,param);
     if(!selected(e).equals(TUNINGS[device]))tuning(e,TUNINGS[device]);
     int[] bands=original(e,profile,110).clone();
     for(int i=0;i<bands.length;i++)bands[i]=(choice==9?0:bands[i])+gain*16;
     for(int param:PARAMS)if(param!=110&&param!=106)sp(e,profile,param,original(e,profile,param));
     if(choice==9){
      int[] keys={103,104,105,107,108,111,112},values={0,1,1,6,8,0,1};
      for(int i=0;i<keys.length;i++)sp(e,profile,keys[i],new int[]{values[i]});
     }
     sp(e,profile,106,new int[]{1});sp(e,profile,110,bands);si(e,0xA000000,profile);si(e,0,1);
     int rc=e.setEnabled(true);boolean verified=false;
     for(int attempt=0;attempt<4;attempt++){
      if(attempt>0)Thread.sleep(150);
      verified=rc==0&&e.getEnabled()&&Arrays.equals(gp(e,profile,110,20),bands)&&selected(e).equals(TUNINGS[device]);
      if(verified)break;
     }
     if(!verified)throw new Exception("profile/gain verification failed");
     snapshot(e,profile);status("OK "+result);
    }previous=config;
   }
  }catch(Throwable ex){if(e!=null){try{baseline(e);}catch(Throwable ignored){}e.release();e=null;}previous="";status("ERROR "+ex);}
  Thread.sleep(1000);}
 }
}
