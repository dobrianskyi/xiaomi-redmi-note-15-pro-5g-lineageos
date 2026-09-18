/* Tiny static AArch64 Linux/Android daemon; no libc or Android ABI dependency.
 * Input: source, panel, disable flag, remove flag, lockfile.
 * Mirror the proven sysfs path. Poll source at 10 Hz; reconcile panel at 1 Hz
 * or immediately on a source change. No writes on invalid/missing inputs.
 */
typedef unsigned long usize;
static long call(long n,long a,long b,long c,long d){
 register long x0 __asm__("x0")=a,x1 __asm__("x1")=b,x2 __asm__("x2")=c,x3 __asm__("x3")=d,x8 __asm__("x8")=n;
 __asm__ volatile("svc 0":"+r"(x0):"r"(x1),"r"(x2),"r"(x3),"r"(x8):"memory");return x0;
}
static long op(const char*p,long flags,long mode){return call(56,-100,(long)p,flags,mode);}
static void cl(long fd){call(57,fd,0,0,0);}
static int exists(const char*p){long f=op(p,0,0);if(f<0)return 0;cl(f);return 1;}
static int number(const char*p){char b[32];long f=op(p,0,0);if(f<0)return -1;long n=call(63,f,(long)b,sizeof(b),0);cl(f);if(n<1||n>=32)return -1;
 int v=0,digits=0,tail=0;for(long i=0;i<n;i++){if(b[i]>='0'&&b[i]<='9'&&!tail){v=v*10+b[i]-'0';digits++;if(v>16383)return -1;}else if(b[i]=='\n'||b[i]=='\r'||b[i]==' '||b[i]=='\t')tail=1;else return -1;}return digits?v:-1;}
static int put(const char*p,int v){char b[8],r[8];int n=0,k=0;do{r[n++]=(char)('0'+v%10);v/=10;}while(v);while(n)b[k++]=r[--n];b[k++]='\n';long f=op(p,1|512,0);if(f<0)return -1;long w=call(64,f,(long)b,k,0);cl(f);return w==k?0:-1;}
long bridge_main(long argc,char**argv){
 if(argc!=6)return 2;
 long lock=op(argv[5],2|64,0600);if(lock<0)return 3;
 if(call(32,lock,2|4,0,0)<0){cl(lock);return 4;}
 call(167,15,(long)"lapis-backlight",0,0);
 int previous=-1,tick=0;
 for(;;){
  if(exists(argv[3])||exists(argv[4]))return 0;
  int wanted=number(argv[1]);if(wanted<0)return 5;
  if(wanted!=previous||tick==0){int actual=number(argv[2]);if(actual<0)return 6;if(actual!=wanted&&put(argv[2],wanted))return 7;previous=wanted;}
  tick=(tick+1)%10;
  struct {long sec,nsec;} delay={0,100000000};call(101,(long)&delay,0,0,0);
 }
}
__asm__(".global _start\n_start:\nldr x0, [sp]\nadd x1, sp, #8\nbl bridge_main\nmov x8, #93\nsvc 0\n");
