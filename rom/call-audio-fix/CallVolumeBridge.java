import java.nio.file.*;import java.lang.reflect.*;
public class CallVolumeBridge {
 static final Path DIR=Paths.get("/data/adb/lapis_call_volume");
 static void status(String s)throws Exception{Files.write(DIR.resolve("status"),s.getBytes("UTF-8"));}
 public static void main(String[] args)throws Exception{
  Files.createDirectories(DIR);
  java.nio.channels.FileChannel channel=java.nio.channels.FileChannel.open(DIR.resolve("lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE);
  java.nio.channels.FileLock lock=channel.tryLock();if(lock==null){System.exit(42);return;}
  Files.write(DIR.resolve("pid"),Integer.toString(android.os.Process.myPid()).getBytes("UTF-8"));
  Class<?> iface=Class.forName("android.media.IAudioService"),sys=Class.forName("android.media.AudioSystem");
  Object binder=Class.forName("android.os.ServiceManager").getMethod("getService",String.class).invoke(null,"audio");
  Object audio=Class.forName("android.media.IAudioService$Stub").getMethod("asInterface",Class.forName("android.os.IBinder")).invoke(null,binder);
  Method mode=iface.getMethod("getMode"),volume=iface.getMethod("getStreamVolume",int.class),route=sys.getMethod("getDevicesForStream",int.class),set=sys.getMethod("setParameters",String.class);
  String prior="";int stable=0;
  while(true){
   int m=(Integer)mode.invoke(audio),dev=(Integer)route.invoke(null,0),v=(Integer)volume.invoke(audio,0);
   String key=m+":"+dev+":"+v;
   if(!key.equals(prior)){prior=key;stable=0;}
   if((m==2||m==3)&&dev==2){
    // Preserve the existing Lineage MTK loudness curve, but respect Xiaomi's max11.
    // Wait for native routing/float-volume updates, then apply the vendor index.
    if(stable==1||stable==3){
     int gain=Math.max(0,Math.min(11,(int)Math.round(15.0/Math.log(12.0)*Math.log(Math.min(11,v)+1.0))));
     int rc=(Integer)set.invoke(null,"volumeDevice=2;volumeIndex="+gain+";volumeStreamType=0");
     status("speaker mode="+m+" ui="+v+" vendor="+gain+" rc="+rc);
    }
   }else if(stable==0)status("inactive mode="+m+" device="+dev);
   stable=Math.min(4,stable+1);Thread.sleep(250);
  }
 }
}
