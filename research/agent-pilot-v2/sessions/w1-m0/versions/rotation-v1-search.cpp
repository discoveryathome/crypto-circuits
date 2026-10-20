// Original local implementation, 2026. No upstream executable/source incorporated.
// Cancellation-aware bounded-distance BP-style synthesis and exact-distance windows.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <ctime>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using namespace std;
using U=uint64_t;
struct Circuit { int n; vector<pair<int,int>> gates; vector<int> outputs; };
struct Rep { array<int,3> a; uint8_t size; };
static mt19937_64 rng;
static double cpu_start, cpu_limit, wall_limit;
static chrono::steady_clock::time_point wall_start;
static size_t iterations=0, syntheses=0, windows=0;
static bool expired(){return double(clock())/CLOCKS_PER_SEC-cpu_start>=cpu_limit || chrono::duration<double>(chrono::steady_clock::now()-wall_start).count()>=wall_limit;}
static double cpu(){return double(clock())/CLOCKS_PER_SEC-cpu_start;}
static vector<int> depths(const Circuit& c){ vector<int>d(c.n,0); for(auto[a,b]:c.gates)d.push_back(1+max(d[a],d[b]));return d; }
static pair<int,int> metric(const Circuit& c){auto d=depths(c);int z=0;for(int a:c.outputs)z=max(z,d[a]);return{int(c.gates.size()),z};}
static Circuit prune(const Circuit& c){int k=c.n+c.gates.size();vector<bool>live(k,false);for(int a:c.outputs)live[a]=true;for(int i=k-1;i>=c.n;--i)if(live[i]){auto[a,b]=c.gates[i-c.n];live[a]=live[b]=true;}Circuit out;out.n=c.n;vector<int>map(k,-1);iota(map.begin(),map.begin()+c.n,0);for(int i=c.n;i<k;i++)if(live[i]){map[i]=out.n+out.gates.size();auto[a,b]=c.gates[i-c.n];out.gates.push_back({map[a],map[b]});}for(int a:c.outputs)out.outputs.push_back(map[a]);return out;}
static vector<U> values(const Circuit& c){vector<U>v;for(int i=0;i<c.n;i++)v.push_back(U(1)<<i);for(auto[a,b]:c.gates)v.push_back(v[a]^v[b]);return v;}
static bool valid(const Circuit& c,const vector<U>&target){if(c.outputs.size()!=target.size())return false;auto v=values(c);for(size_t i=0;i<target.size();i++)if(v[c.outputs[i]]!=target[i])return false;return true;}
static vector<int> initial_rep(U t){vector<int>r;for(int i=0;i<64;i++)if(t>>i&1)r.push_back(i);return r;}
static void simplify(vector<int>&r){sort(r.begin(),r.end());vector<int>z;for(size_t i=0;i<r.size();){size_t j=i+1;while(j<r.size()&&r[j]==r[i])j++;if((j-i)%2)z.push_back(r[i]);i=j;}r=std::move(z);}
// Exact shortest representation over all current signals in an r-bit vector
// space uses D_new(x)=min(D_old(x),1+D_old(x XOR newly_added_signal)).
// Every signal occurs at most once in a shortest representation over GF(2).
static Circuit synthesize(int n,const vector<U>&targets,bool bounded,int variant){
 Circuit c;c.n=n;vector<U>b;vector<int>d(n,0);unordered_set<U>have;
 for(int i=0;i<n;i++){b.push_back(U(1)<<i);have.insert(U(1)<<i);}
 vector<vector<int>> reps;for(U t:targets)reps.push_back(initial_rep(t));
 bool exact=n<=16&&!bounded;vector<uint8_t>dist;
 if(exact){dist.resize(size_t(1)<<n);for(size_t i=0;i<dist.size();i++)dist[i]=__builtin_popcountll(i);}
 while(true){
  if(expired())throw runtime_error("budget");
  bool done=true;for(U t:targets)if(!have.count(t)){done=false;break;}if(done)break;
  int k=b.size();unordered_map<U,Rep> table;
  if(!exact){
   table.reserve(size_t(k)*k*k/6+size_t(k)*k);
   table[0]={{{-1,-1,-1}},0};
   for(int i=0;i<k;i++)table.emplace(b[i],Rep{{i,-1,-1},1});
   for(int i=0;i<k;i++)for(int j=i+1;j<k;j++)table.emplace(b[i]^b[j],Rep{{i,j,-1},2});
   // Exact representation lengths up to three; larger distances remain upper bounds.
   for(int i=0;i<k;i++)for(int j=i+1;j<k;j++)for(int l=j+1;l<k;l++)table.emplace(b[i]^b[j]^b[l],Rep{{i,j,l},3});
  }
  int oldsum=0;for(size_t q=0;q<targets.size();q++)oldsum+=exact?dist[targets[q]]:reps[q].size();
  int bestsum=1000000,bestnorm=-1,bestdepth=1000000,ai=-1,aj=-1;uint64_t ties=0;
  auto repfor=[&](size_t q,int i,int j,U z){
   vector<int> r=reps[q];
   bool a=find(r.begin(),r.end(),i)!=r.end(),bb=find(r.begin(),r.end(),j)!=r.end();
   if(a&&bb){r.erase(remove(r.begin(),r.end(),i),r.end());r.erase(remove(r.begin(),r.end(),j),r.end());r.push_back(k);}
   auto it=table.find(targets[q]^z);
   if(it!=table.end()&&int(it->second.size)+1<int(r.size())){r.clear();for(int p=0;p<it->second.size;p++)r.push_back(it->second.a[p]);r.push_back(k);}
   return r;
  };
  for(int i=0;i<k;i++)for(int j=i+1;j<k;j++){
   U z=b[i]^b[j];if(!z||have.count(z))continue;
   int sum=0,norm=0,dep=1+max(d[i],d[j]);
   for(size_t q=0;q<targets.size();q++){
    int dd;
    if(exact)dd=min(int(dist[targets[q]]),1+int(dist[targets[q]^z]));
    else{
     dd=reps[q].size();bool a=find(reps[q].begin(),reps[q].end(),i)!=reps[q].end();bool bb=find(reps[q].begin(),reps[q].end(),j)!=reps[q].end();if(a&&bb)--dd;
     auto it=table.find(targets[q]^z);if(it!=table.end())dd=min(dd,1+int(it->second.size));
    }
    sum+=dd;norm+=dd*dd;
   }
   // Fixed randomized tie modes sample count-biased and shallow constructions.
   int ns=variant==0?norm:0;int nd=variant==2?dep:0;
   if(sum<bestsum || (sum==bestsum&&ns>bestnorm) || (sum==bestsum&&ns==bestnorm&&nd<bestdepth)){
    bestsum=sum;bestnorm=ns;bestdepth=nd;ai=i;aj=j;ties=1;
   }else if(sum==bestsum&&ns==bestnorm&&nd==bestdepth){if(rng()%++ties==0){ai=i;aj=j;}}
  }
  if(ai<0 || bestsum>=oldsum)throw runtime_error("no progress in synthesis");
  U z=b[ai]^b[aj];
  if(exact){auto prior=dist;for(size_t x=0;x<dist.size();x++)dist[x]=min(int(prior[x]),1+int(prior[x^z]));}
  else for(size_t q=0;q<targets.size();q++){reps[q]=repfor(q,ai,aj,z);simplify(reps[q]);}
  c.gates.push_back({ai,aj});b.push_back(z);d.push_back(1+max(d[ai],d[aj]));have.insert(z);
  if(c.gates.size()>1000)throw runtime_error("gate cap");
 }
 for(U t:targets){auto it=find(b.begin(),b.end(),t);if(it==b.end())throw runtime_error("missing output");c.outputs.push_back(it-b.begin());}
 return prune(c);
}
static Circuit window_replace(const Circuit& c){
 if(c.gates.size()<3)return c;int start=rng()%c.gates.size();int len=3+rng()%18;int end=min(int(c.gates.size()),start+len);if(end-start<3)return c;
 set<int> incoming,external;
 for(int i=start;i<end;i++)for(int a:{c.gates[i].first,c.gates[i].second})if(a<c.n+start)incoming.insert(a);
 if(incoming.empty()||incoming.size()>16)return c;
 for(size_t i=end;i<c.gates.size();i++)for(int a:{c.gates[i].first,c.gates[i].second})if(a>=c.n+start&&a<c.n+end)external.insert(a);
 for(int a:c.outputs)if(a>=c.n+start&&a<c.n+end)external.insert(a);
 if(external.empty())return prune(c);
 vector<int>ins(incoming.begin(),incoming.end());unordered_map<int,U>v;for(size_t i=0;i<ins.size();i++)v[ins[i]]=U(1)<<i;
 for(int i=start;i<end;i++){auto[a,b]=c.gates[i];v[c.n+i]=v[a]^v[b];}
 vector<U>ts;for(int a:external)ts.push_back(v[a]);
 // The local cut wires are independent formal variables, a conservative model.
 // Zero local outputs are not expected from pruned published linear circuits.
 for(U t:ts)if(!t)return c;
 Circuit sub=synthesize(ins.size(),ts,false,rng()%3);windows++;
 if(sub.gates.size()>size_t(end-start))return c;
 Circuit out;out.n=c.n;vector<int>map(c.n+c.gates.size(),-1);iota(map.begin(),map.begin()+c.n,0);
 for(int i=0;i<start;i++){auto[a,b]=c.gates[i];map[c.n+i]=out.n+out.gates.size();out.gates.push_back({map[a],map[b]});}
 vector<int>sm;for(int a:ins)sm.push_back(map[a]);for(auto[a,b]:sub.gates){sm.push_back(out.n+out.gates.size());out.gates.push_back({sm[a],sm[b]});}
 size_t z=0;for(int a:external)map[a]=sm[sub.outputs[z++]];
 for(size_t i=end;i<c.gates.size();i++){auto[a,b]=c.gates[i];if(map[a]<0||map[b]<0)throw runtime_error("bad splice");map[c.n+i]=out.n+out.gates.size();out.gates.push_back({map[a],map[b]});}
 for(int a:c.outputs)out.outputs.push_back(map[a]);return prune(out);
}
static Circuit read_circuit(istream& in){Circuit c;int g,o;if(!(in>>c.n>>g>>o))throw runtime_error("bad circuit header");for(int i=0;i<g;i++){int a,b;in>>a>>b;if(a<0||b<0||a>=c.n+i||b>=c.n+i)throw runtime_error("bad circuit wire");c.gates.push_back({a,b});}for(int i=0;i<o;i++){int a;in>>a;if(a<0||a>=c.n+g)throw runtime_error("bad output");c.outputs.push_back(a);}return c;}
static void emit(const Circuit& c,const string& method){auto [g,d]=metric(c);cout<<"{\"method\":\""<<method<<"\",\"iteration\":"<<iterations<<",\"cpu_seconds\":"<<cpu()<<",\"XOR\":"<<g<<",\"depth\":"<<d<<",\"circuit\":{\"inputs\":"<<c.n<<",\"gates\":[";bool first=true;for(auto[a,b]:c.gates){if(!first)cout<<",";first=false;cout<<"[\"XOR\","<<a<<","<<b<<"]";}cout<<"],\"outputs\":[";first=true;for(int a:c.outputs){if(!first)cout<<",";first=false;cout<<a;}cout<<"]}}"<<endl;}

// Session-local algebraic DAG rotations. Each rotation preserves semantic values.
static Circuit rotate_dag(const Circuit& c){
 auto vals=values(c);int k=vals.size();
 unordered_map<U,int> index;for(int i=0;i<k;i++)index[vals[i]]=i;
 int target=c.n+rng()%c.gates.size();auto[a,b]=c.gates[target-c.n];
 if(rng()%2)swap(a,b);if(a<c.n)return c;
 auto[x,y]=c.gates[a-c.n];if(rng()%2)swap(x,y);
 U v=vals[b]^vals[x];if(!v)return c;
 vector<pair<int,int>> recipe=c.gates;
 int middle;auto it=index.find(v);
 if(it==index.end()){middle=k;recipe.push_back({b,x});}else middle=it->second;
 if(middle==target)return c;
 recipe[target-c.n]={middle,y};
 Circuit out;out.n=c.n;vector<int>state(c.n+recipe.size(),0),ren(c.n+recipe.size(),-1);
 for(int i=0;i<c.n;i++){state[i]=2;ren[i]=i;}
 auto visit=[&](auto&&self,int v)->bool{
  if(state[v]==2)return true;if(state[v]==1)return false;state[v]=1;
  auto[a,b]=recipe[v-c.n];if(!self(self,a)||!self(self,b))return false;
  ren[v]=out.n+out.gates.size();out.gates.push_back({ren[a],ren[b]});state[v]=2;return true;
 };
 for(int v:c.outputs){if(!visit(visit,v))return c;out.outputs.push_back(ren[v]);}
 return out;
}
int main(int argc,char**argv){
 try{
  if(argc<6)return 2;
  rng.seed(stoull(argv[1]));cpu_limit=stod(argv[2]);wall_limit=stod(argv[3]);cpu_start=double(clock())/CLOCKS_PER_SEC;wall_start=chrono::steady_clock::now();
  ifstream f(argv[4]);int n,m;f>>n>>m;vector<U>targets(m);for(U&t:targets)f>>t;
  vector<Circuit>front,starts;for(int i=5;i<argc;i++){ifstream s(argv[i]);auto c=read_circuit(s);if(c.n!=n||!valid(c,targets))throw runtime_error("incorrect start");starts.push_back(c);}
  auto offer=[&](const Circuit&c,const string&method){auto z=metric(c);for(auto&b:front){auto x=metric(b);if(x.first<=z.first&&x.second<=z.second)return;}if(!valid(c,targets))throw runtime_error("incorrect candidate");front.erase(remove_if(front.begin(),front.end(),[&](const Circuit&b){auto x=metric(b);return z.first<=x.first&&z.second<=x.second;}),front.end());front.push_back(c);emit(c,method);};
  for(auto&c:starts)offer(c,"start");Circuit current=starts[0];
  double weight=0.3,temp=0.1;size_t accepted=0,restarts=0;
  while(!expired()){
   try{
    if(iterations%2500==0){current=front[rng()%front.size()];weight=array<double,6>{0,0.1,0.3,0.7,1.5,3.0}[rng()%6];temp=array<double,4>{0,0.05,0.15,0.3}[rng()%4];restarts++;}
    Circuit next;
    if(iterations%50==49){next=window_replace(current);}else next=rotate_dag(current);
    auto a=metric(next),b=metric(current);
    double delta=a.first-b.first+weight*(a.second-b.second);
    bool accept=delta<=0 || (temp>0 && generate_canonical<double,53>(rng)<exp(-delta/temp));
    if(accept){current=std::move(next);accepted++;offer(current,"rotation-and-exact-window");}
   }catch(const runtime_error&e){if(string(e.what())=="budget")break;throw;}
   iterations++;
   if(iterations%5000==0)cerr<<"checkpoint iterations="<<iterations<<" cpu="<<cpu()<<" accepted="<<accepted<<" windows="<<windows<<" restarts="<<restarts<<"\n";
  }
  cerr<<"done iterations="<<iterations<<" cpu="<<cpu()<<" accepted="<<accepted<<" windows="<<windows<<" restarts="<<restarts<<"\n";
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}return 0;
}
