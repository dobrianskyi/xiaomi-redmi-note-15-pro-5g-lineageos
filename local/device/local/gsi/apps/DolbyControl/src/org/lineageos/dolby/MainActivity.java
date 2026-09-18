package org.lineageos.dolby;
import android.app.*;import android.os.*;import android.widget.*;import java.io.*;import java.util.concurrent.*;
public class MainActivity extends Activity {
 Spinner preset,tuning;Button defaults;
 final int[] profiles={9,0,1,2,3,4,5,6,7,8};
 final String[] names={"Favorite","Dynamic","Movie","Music","Xiaomi custom","Mobile: Default","Mobile: On the go","Mobile: Commute","Mobile: Travel","Voice"};
 TextView value,status;SeekBar slider;Switch enabled;Button apply,refresh;boolean loaded=false;
 final ExecutorService worker=Executors.newSingleThreadExecutor();
 int dp(int n){return (int)(n*getResources().getDisplayMetrics().density);}
 TextView text(LinearLayout l,String s,int size){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setPadding(0,dp(10),0,dp(10));l.addView(t);return t;}
 Spinner choice(LinearLayout l,String title,String[] choices){text(l,title,18);Spinner sp=new Spinner(this);ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,choices);sp.setAdapter(adapter);l.addView(sp);return sp;}
 SeekBar tone(LinearLayout l,String title){TextView label=text(l,title+": 0 dB",18);SeekBar bar=new SeekBar(this);bar.setMax(12);bar.setProgress(6);l.addView(bar);bar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){public void onProgressChanged(SeekBar s,int p,boolean u){label.setText(title+": "+(p-6)+" dB");}public void onStartTrackingTouch(SeekBar s){}public void onStopTrackingTouch(SeekBar s){}});return bar;}
 public void onCreate(Bundle b){super.onCreate(b);
  ScrollView scroll=new ScrollView(this);LinearLayout l=new LinearLayout(this);l.setOrientation(1);l.setPadding(dp(24),dp(32),dp(24),dp(24));scroll.addView(l);setContentView(scroll);
  text(l,"Sound for your phone speakers",18);
  enabled=new Switch(this);enabled.setText("Dolby processing");l.addView(enabled);
  preset=choice(l,"Profile",names);
  tuning=choice(l,"Speaker tuning",new String[]{"Portrait (recommended)","Landscape","Factory default","Spatializer 90°","Spatializer 270°"});
  value=text(l,"0 dB",28);slider=new SeekBar(this);slider.setMax(56);slider.setProgress(6);l.addView(slider);
  slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){public void onProgressChanged(SeekBar s,int p,boolean u){int g=p-6;value.setText((g>0?"+":"")+g+" dB");}public void onStartTrackingTouch(SeekBar s){}public void onStopTrackingTouch(SeekBar s){}});
  text(l,"Range: −6 to +50 dB",14);
  text(l,"Choose your settings, then tap Apply and save. Settings are retained after closing the app and restarting the phone.",16);
  apply=new Button(this);apply.setText("Apply and save");l.addView(apply);
  defaults=new Button(this);defaults.setText("Restore favorite: +20 dB");l.addView(defaults);defaults.setOnClickListener(v->{enabled.setChecked(true);preset.setSelection(0);tuning.setSelection(0);slider.setProgress(26);save();});
  refresh=new Button(this);refresh.setText("Refresh status");l.addView(refresh);
  status=text(l,"Reading settings…",16);
  text(l,"Speaker processing pauses during calls and when media routes to headphones or Bluetooth. Reduce gain if sound distorts. Turning processing off restores the saved original settings.",14);
  apply.setOnClickListener(v->save());refresh.setOnClickListener(v->load());load();
 }
 void busy(boolean b){apply.setEnabled(!b&&loaded);refresh.setEnabled(!b);slider.setEnabled(!b&&loaded);enabled.setEnabled(!b&&loaded);preset.setEnabled(!b&&loaded);tuning.setEnabled(!b&&loaded);defaults.setEnabled(!b&&loaded);}
 void load(){busy(true);worker.execute(()->{try{
  String[] lines=Engine.get(this).state().split("\n",2);String[] p=lines[0].split("\\s+");
  int on=Integer.parseInt(p[0]),gain=Integer.parseInt(p[1]),profile=Integer.parseInt(p[2]),device=Integer.parseInt(p[3]);
  boolean available=Engine.supported();
  runOnUiThread(()->{loaded=available;enabled.setChecked(on==1);slider.setProgress(gain+6);
   for(int i=0;i<profiles.length;i++)if(profiles[i]==profile)preset.setSelection(i);
   tuning.setSelection(device);status.setText(available?lines[1]:"Dolby is unavailable on this device.");busy(false);});
 }catch(Exception e){runOnUiThread(()->{status.setText("Error: "+e.getMessage());busy(false);});}});}
 void save(){final String config=(enabled.isChecked()?1:0)+" "+(slider.getProgress()-6)+" "+profiles[preset.getSelectedItemPosition()]+" "+tuning.getSelectedItemPosition();busy(true);status.setText("Applying…");
  Engine engine=Engine.get(this);engine.worker.execute(()->{try{String result=engine.apply(config);runOnUiThread(()->{status.setText(result);busy(false);});}
  catch(Exception e){runOnUiThread(()->{status.setText("Error: "+e.getMessage());busy(false);});}});
 }
 @Override public void onDestroy(){worker.shutdown();super.onDestroy();}
}
