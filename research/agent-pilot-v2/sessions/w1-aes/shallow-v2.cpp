// Original timed-session depth-3 synthesis. No upstream optimizer code.
#define main toolkit_original_main
#include "search.cpp"
#undef main
struct Node { U val; int rank; vector<pair<int,int>> opts; };
int main(int argc,char**argv){
 try {
  if(argc<6)return 2;rng.seed(stoull(argv[1]));cpu_limit=stod(argv[2]);wall_limit=stod(argv[3]);cpu_start=double(clock())/CLOCKS_PER_SEC;wall_start=chrono::steady_clock::now();
  ifstream f(argv[4]);int n,m;f>>n>>m;vector<U>targets(m);for(U&t:targets)f>>t;if(n!=32)throw runtime_error("only n32");
  vector<Circuit> starts,front;for(int i=5;i<argc;i++){ifstream in(argv[i]);auto c=read_circuit(in);if(!valid(c,targets))throw runtime_error("bad start");starts.push_back(c);}
  auto offer=[&](const Circuit&c){if(!valid(c,targets))throw runtime_error("invalid result");auto z=metric(c);for(auto&b:front){auto x=metric(b);if(x.first<=z.first&&x.second<=z.second)return;}front.erase(remove_if(front.begin(),front.end(),[&](const Circuit&b){auto x=metric(b);return z.first<=x.first&&z.second<=x.second;}),front.end());front.push_back(c);emit(c,"depth3-complete-support-annealing");};
  for(auto&c:starts)offer(c);
  vector<Node> nodes;unordered_map<U,int> idx;
  auto addnode=[&](U v,int rank){idx[v]=nodes.size();nodes.push_back({v,rank,{}});};
  for(int i=0;i<n;i++)addnode(U(1)<<i,0);
  for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)addnode((U(1)<<a)|(U(1)<<b),1);
  for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)for(int c=b+1;c<n;c++)addnode((U(1)<<a)|(U(1)<<b)|(U(1)<<c),2);
  for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)for(int c=b+1;c<n;c++)for(int d=c+1;d<n;d++)addnode((U(1)<<a)|(U(1)<<b)|(U(1)<<c)|(U(1)<<d),2);
  int layer=nodes.size();vector<int> outids;for(U t:targets){outids.push_back(nodes.size());addnode(t,3);}
  for(int i=n;i<layer;i++){U v=nodes[i].val;for(U s=(v-1)&v;s;s=(s-1)&v){U t=v^s;if(s<t&&__builtin_popcountll(s)<=2&&__builtin_popcountll(t)<=2)nodes[i].opts.push_back({idx.at(s),idx.at(t)});}}
  for(int i:outids){for(int a=0;a<layer;a++){U bval=nodes[i].val^nodes[a].val;auto it=idx.find(bval);if(it!=idx.end()&&it->second<layer&&a<it->second)nodes[i].opts.push_back({a,it->second});}}
  vector<int> initial(nodes.size(),0);bool found=false;
  for(auto&c:starts)if(metric(c).second==3){auto vals=values(c);for(size_t k=0;k<c.gates.size();k++){auto[a,b]=c.gates[k];int u=idx.at(vals[c.n+k]),aa=idx.at(vals[a]),bb=idx.at(vals[b]);if(aa>bb)swap(aa,bb);bool ok=false;for(size_t j=0;j<nodes[u].opts.size();j++){auto[x,y]=nodes[u].opts[j];if(x>y)swap(x,y);if(x==aa&&y==bb){initial[u]=j;ok=true;break;}}if(!ok)throw runtime_error("start decomposition absent");}found=true;break;}
  if(!found)throw runtime_error("depth3 start required");
  vector<int> choice=initial,refs(nodes.size(),0);int cost=0;
  function<void(int,int)> adjust=[&](int u,int delta){int before=refs[u];refs[u]+=delta;if(refs[u]<0)throw runtime_error("negative refcount");if((before==0&&refs[u]>0)||(before>0&&refs[u]==0)){if(u>=n){cost+=delta>0?1:-1;auto[a,b]=nodes[u].opts[choice[u]];adjust(a,delta>0?1:-1);adjust(b,delta>0?1:-1);}}};
  auto change=[&](int u,int op){if(refs[u]){auto[a,b]=nodes[u].opts[choice[u]];adjust(a,-1);adjust(b,-1);choice[u]=op;tie(a,b)=nodes[u].opts[op];adjust(a,1);adjust(b,1);}else choice[u]=op;};
  auto initialize=[&](){fill(refs.begin(),refs.end(),0);cost=0;for(int o:outids)adjust(o,1);};initialize();
  auto materialize=[&](){Circuit c;c.n=n;vector<int> wire(nodes.size(),-1);iota(wire.begin(),wire.begin()+n,0);for(int i=n;i<(int)nodes.size();i++)if(refs[i]){auto[a,b]=nodes[i].opts[choice[i]];if(wire[a]<0||wire[b]<0)throw runtime_error("non-topological rank DAG");wire[i]=n+c.gates.size();c.gates.push_back({wire[a],wire[b]});}for(int o:outids)c.outputs.push_back(wire[o]);return c;};
  auto initial_circuit=materialize();if(!valid(initial_circuit,targets)||int(initial_circuit.gates.size())!=cost)throw runtime_error("initial structure/cost mismatch");
  int best=cost;vector<int> bestchoices=choice;cerr<<"universe="<<nodes.size()<<" starting_cost="<<cost<<" output_options=";for(int o:outids)cerr<<nodes[o].opts.size()<<",";cerr<<"\n";
  size_t accepts=0;while(!expired()){
   if(iterations&&iterations%250000==0){choice=(rng()%4)?bestchoices:initial;initialize();}
   double phase=double(iterations%250000)/250000.;double temp=0.025+0.75*pow(1.0-phase,2.0);
   int out=outids[rng()%outids.size()],u=out;
   if(rng()%100<35){auto[a,b]=nodes[out].opts[choice[out]];u=(rng()%2)?a:b;if(nodes[u].opts.size()<2){iterations++;continue;}}
   int oldcost=cost,oldop=choice[u];vector<pair<int,int>> undo={{u,oldop}};int proposed=rng()%nodes[u].opts.size();
   if(nodes[u].rank==3 && rng()%100<85){
    auto estimate=[&](int v){if(v<n||refs[v])return 0;int z=10;if(nodes[v].rank==1)return 1;for(auto[a,b]:nodes[v].opts)z=min(z,1+int(a>=n&&!refs[a])+int(b>=n&&!refs[b]));return z;};
    int score=100;for(int k=0;k<12;k++){int op=rng()%nodes[u].opts.size();auto[a,b]=nodes[u].opts[op];int x=estimate(a)+estimate(b);if(x<score||(x==score&&rng()%2)){score=x;proposed=op;}}
   }
   change(u,proposed);
   // Coordinate-minimize the selected output's rank-2 partitions, keeping
   // transaction history so rejection restores every live dependency.
   if(nodes[u].rank==3 && rng()%100<80){auto[a,b]=nodes[u].opts[choice[u]];for(int v:{a,b})if(nodes[v].rank==2){int op=choice[v],bestop=op,bc=cost;for(int j=0;j<(int)nodes[v].opts.size();j++){change(v,j);if(cost<bc||(cost==bc&&rng()%2)){bc=cost;bestop=j;}}change(v,bestop);undo.push_back({v,op});}}
   bool accept=cost<=oldcost||double(rng())/double(UINT64_MAX)<exp((oldcost-cost)/temp);
   if(accept)accepts++;else for(auto it=undo.rbegin();it!=undo.rend();++it)change(it->first,it->second);
   if(cost<best){best=cost;bestchoices=choice;auto c=materialize();if((int)c.gates.size()!=cost)throw runtime_error("cost mismatch");offer(c);cerr<<"best="<<best<<" iteration="<<iterations<<" cpu="<<cpu()<<"\n";}
   iterations++;if(iterations%100000==0)cerr<<"iterations="<<iterations<<" cpu="<<cpu()<<" cost="<<cost<<" best="<<best<<" accepted="<<accepts<<"\n";
  }
  cerr<<"done iterations="<<iterations<<" cpu="<<cpu()<<" best="<<best<<"\n";
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}return 0;
}
