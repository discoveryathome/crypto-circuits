// Original wave-2 search: semantic union of all starts and cyclic byte symmetries.
#define main toolkit_main
#include "toolkit.cpp"
#undef main
#include <functional>
struct Node{U v;vector<pair<int,int>> opts;int init=-1;};
int main(int argc,char**argv){try{
 if(argc<7)return 2;rng.seed(stoull(argv[1]));cpu_limit=stod(argv[2]);wall_limit=stod(argv[3]);cpu_start=double(clock())/CLOCKS_PER_SEC;wall_start=chrono::steady_clock::now();int bridges=stoi(argv[4]);
 ifstream f(argv[5]);int n,m;f>>n>>m;vector<U> targets(m);for(auto&t:targets)f>>t;
 vector<Circuit>starts,front;for(int i=6;i<argc;i++){ifstream s(argv[i]);auto c=read_circuit(s);if(!valid(c,targets))throw runtime_error("bad start");starts.push_back(c);}
 auto offer=[&](const Circuit&c,string method){if(!valid(c,targets))throw runtime_error("invalid candidate");auto z=metric(c);for(auto&b:front){auto x=metric(b);if(x.first<=z.first&&x.second<=z.second)return;}front.erase(remove_if(front.begin(),front.end(),[&](const Circuit&b){auto x=metric(b);return z.first<=x.first&&z.second<=x.second;}),front.end());front.push_back(c);emit(c,method);};
 for(auto&c:starts)offer(c,"start");
 vector<Node>nodes;unordered_map<U,int>ids;auto add=[&](U v){auto it=ids.find(v);if(it!=ids.end())return it->second;int i=nodes.size();ids[v]=i;nodes.push_back({v,{},-1});return i;};for(int i=0;i<n;i++)add(U(1)<<i);
 vector<vector<pair<int,pair<int,int>>>> startdefs;
 for(auto&c:starts)for(int shift=0;shift<4;shift++){
  auto vals=values(c);for(auto&v:vals){uint32_t x=v;v=shift?uint32_t((x<<(8*shift))|(x>>(32-8*shift))):x;}
  vector<pair<int,pair<int,int>>> defs;for(size_t i=0;i<c.gates.size();i++){auto[a,b]=c.gates[i];int z=add(vals[n+i]),x=add(vals[a]),y=add(vals[b]);if(x>y)swap(x,y);defs.push_back({z,{x,y}});}
  startdefs.push_back(defs);
 }
 int original_nodes=nodes.size();
 if(bridges){unordered_map<U,int> freq;for(int a=0;a<original_nodes;a++)for(int b=a+1;b<original_nodes;b++){U z=nodes[a].v^nodes[b].v;if(z&&!ids.count(z)&&__builtin_popcountll(z)<=6)freq[z]++;}vector<pair<int,U>>rank;for(auto[z,k]:freq)if(k>=3)rank.push_back({k,z});sort(rank.rbegin(),rank.rend());for(int i=0;i<min(bridges,int(rank.size()));i++)add(rank[i].second);}
 int N=nodes.size();for(int a=0;a<N;a++)for(int b=a+1;b<N;b++){auto it=ids.find(nodes[a].v^nodes[b].v);if(it!=ids.end()&&it->second>=n)nodes[it->second].opts.push_back({a,b});}
 vector<int> lowdepth(N,999),lowchoice(N,-1);for(int i=0;i<n;i++)lowdepth[i]=0;
 for(int pass=0;pass<20;pass++){bool ch=false;for(int u=n;u<N;u++)for(int j=0;j<(int)nodes[u].opts.size();j++){auto[a,b]=nodes[u].opts[j];int d=1+max(lowdepth[a],lowdepth[b]);if(d<lowdepth[u]){lowdepth[u]=d;lowchoice[u]=j;ch=true;}}if(!ch)break;}
 vector<vector<int>> initials;for(auto&defs:startdefs){auto ch=lowchoice;for(auto&[u,ab]:defs){auto it=find(nodes[u].opts.begin(),nodes[u].opts.end(),ab);if(it==nodes[u].opts.end())throw runtime_error("missing choice");ch[u]=it-nodes[u].opts.begin();}initials.push_back(ch);}
 vector<int>out;for(U t:targets)out.push_back(ids.at(t));
 vector<int> choice=initials[0],state(N),dep(N),live;int cost,depth;bool bad;
 function<int(int)> visit=[&](int u){if(u<n)return 0;if(state[u]==2)return dep[u];if(state[u]==1){bad=true;return 99;}state[u]=1;if(choice[u]<0){bad=true;return 99;}auto[a,b]=nodes[u].opts[choice[u]];int da=visit(a);if(bad)return 99;int db=visit(b);if(bad)return 99;dep[u]=1+max(da,db);state[u]=2;live.push_back(u);cost++;return dep[u];};
 auto evaluate=[&](){fill(state.begin(),state.end(),0);live.clear();cost=depth=0;bad=false;for(int o:out){depth=max(depth,visit(o));if(bad)break;}return !bad;};
 auto materialize=[&](){Circuit c;c.n=n;vector<int>w(N,-1);iota(w.begin(),w.begin()+n,0);for(int u:live){auto[a,b]=nodes[u].opts[choice[u]];w[u]=n+c.gates.size();c.gates.push_back({w[a],w[b]});}for(int o:out)c.outputs.push_back(w[o]);return c;};
 for(auto&ch:initials){choice=ch;if(!evaluate())throw runtime_error("cyclic initialization");auto c=materialize();if(!valid(c,targets))throw runtime_error("bad symmetry initialization");}
 cerr<<"universe="<<N<<" original="<<original_nodes<<" initializations="<<initials.size()<<" options=";size_t opts=0;for(auto&x:nodes)opts+=x.opts.size();cerr<<opts<<"\n";
 int targetdep=5,bestscore=9999;vector<int>bestchoice=initials[0];choice=bestchoice;evaluate();size_t acc=0,cyclic=0;int bestbydepth[20];fill(bestbydepth,bestbydepth+20,999);
 for(auto&ch:initials){choice=ch;evaluate();if(depth<20)bestbydepth[depth]=min(bestbydepth[depth],cost);}choice=bestchoice;evaluate();
 auto scorefn=[&](){int excess=0;for(int o:out)excess+=max(0,dep[o]-targetdep);return cost+2*excess+5*max(0,depth-targetdep);};
 vector<vector<int>> banks=initials;vector<int> bankscore;for(auto&ch:banks){choice=ch;evaluate();bankscore.push_back(cost);}choice=banks[0];evaluate();
 while(!expired()){
  if(iterations%40000==0){targetdep=3+int(rng()%3);int si=(targetdep==3?8:(targetdep==4?4:0))+rng()%4;choice=initials[si];if(rng()%3==0)choice=banks[rng()%banks.size()];evaluate();bestscore=scorefn();}
  auto oldlive=live;int oldscore=scorefn();int u=oldlive[rng()%oldlive.size()];vector<pair<int,int>>undo={{u,choice[u]}};choice[u]=rng()%nodes[u].opts.size();
  bool good=evaluate();
  if(good&&iterations%8==0){auto newlive=live;shuffle(newlive.begin(),newlive.end(),rng);int tries=0;for(int v:newlive){if(find(oldlive.begin(),oldlive.end(),v)!=oldlive.end())continue;if(++tries>4)break;int old=choice[v],best=old,bs=scorefn();for(int k=0;k<min(12,int(nodes[v].opts.size()));k++){int op=rng()%nodes[v].opts.size();choice[v]=op;if(evaluate()){int z=scorefn();if(z<bs||(z==bs&&rng()%2)){bs=z;best=op;}}}choice[v]=best;undo.push_back({v,old});evaluate();}}
  double phase=double(iterations%40000)/40000.;double temp=0.025+0.7*pow(1-phase,2);int score=scorefn();
  bool accept=good&&(score<=oldscore||double(rng())/double(UINT64_MAX)<exp((oldscore-score)/temp));
  if(!good)cyclic++;
  if(!accept){for(auto it=undo.rbegin();it!=undo.rend();++it)choice[it->first]=it->second;evaluate();}else{acc++;if(score<bestscore){bestscore=score;if(cost<=90)bestchoice=choice;}if(depth<20&&cost<bestbydepth[depth]){bestbydepth[depth]=cost;cerr<<"best="<<cost<<","<<depth<<" iteration="<<iterations<<" cpu="<<cpu()<<"\n";offer(materialize(),"bridge-union-DAG-coordinate-annealing");}if(iterations%1000==0&&cost<=bestbydepth[min(depth,19)]+1&&cost<100){if(banks.size()<100)banks.push_back(choice);else banks[12+rng()%88]=choice;}}
  iterations++;if(iterations%100000==0)cerr<<"iteration="<<iterations<<" cpu="<<cpu()<<" current="<<cost<<","<<depth<<" accepted="<<acc<<" cycles="<<cyclic<<" bank="<<banks.size()<<"\n";
 }
 cerr<<"done iterations="<<iterations<<" cpu="<<cpu()<<" accepted="<<acc<<" cycles="<<cyclic<<"\n";
}catch(exception&e){cerr<<e.what()<<"\n";return 1;}return 0;}
