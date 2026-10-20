#define main search_cli_main
#include "search.cpp"
#undef main
#include <cassert>
int main(){
 cpu_start=double(clock())/CLOCKS_PER_SEC;cpu_limit=60;wall_limit=90;wall_start=chrono::steady_clock::now();
 bool cancellation=false;
 vector<U> t={31,47,55,59,61,62};
 Circuit first;
 for(int s=0;s<20;s++){
  rng.seed(s);auto c=synthesize(6,t,false,s%3);assert(valid(c,t));auto v=values(c);
  for(auto[a,b]:c.gates)if(v[a]&v[b])cancellation=true;
  if(s==0)first=c;
 }
 assert(cancellation);
 // A seed and operation sequence must replay exactly, independent of the clock.
 rng.seed(0);auto again=synthesize(6,t,false,0);assert(first.gates==again.gates&&first.outputs==again.outputs);
 for(int i=0;i<100;i++){auto c=window_replace(first);assert(valid(c,t));}
 // A 32-input map containing cancelling outputs exercises the bounded method.
 vector<U> big={0x0000001f,0x0000002f,0x00000037,0x0000003b,0x0000003d,0x0000003e,
                0x80000001,0x40000003,0x20000007};
 rng.seed(123);auto c=synthesize(32,big,true,0);assert(valid(c,big));
 emit(first,"test-exact-cancellation");emit(c,"test-bounded-cancellation");
 cerr<<"PASS: exact/bounded synthesis, semantic cancellation, deterministic replay, 100 valid window replacements\n";
}
