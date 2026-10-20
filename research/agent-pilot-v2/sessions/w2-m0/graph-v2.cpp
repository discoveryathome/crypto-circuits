// Session-local original semantic equality DAG extraction, 2026-10-20.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <unordered_map>
#include <vector>
using namespace std;
using U=uint64_t; using P=pair<int,int>;
struct C {vector<P>g; vector<int>o;};
struct State {vector<int> choice; vector<int> live; C c; int count,dep;};
mt19937_64 rng;vector<U> vals;unordered_map<U,int> ids; vector<vector<P>> edges;vector<int> targets;vector<State> starts;vector<P>front;int nn=32;long long iter=0;chrono::steady_clock::time_point clock_start;
int add(U v){auto it=ids.find(v);if(it!=ids.end())return it->second;int z=vals.size();ids[v]=z;vals.push_back(v);edges.emplace_back();return z;}
int edge(int z,int a,int b){if(a>b)swap(a,b);P p={a,b};auto it=find(edges[z].begin(),edges[z].end(),p);if(it!=edges[z].end())return it-edges[z].begin();edges[z].push_back(p);return edges[z].size()-1;}
bool build(State&s){vector<int>status(vals.size()),wire(vals.size(),-1),dep(vals.size());s.live.clear();s.c.g.clear();s.c.o.clear();for(int i=0;i<nn;i++){wire[i]=i;status[i]=2;}
 auto rec=[&](auto&&self,int z)->bool{if(status[z]==1)return false;if(status[z]==2)return true;if(s.choice[z]<0||s.choice[z]>=int(edges[z].size()))return false;status[z]=1;auto[a,b]=edges[z][s.choice[z]];if(!self(self,a)||!self(self,b))return false;status[z]=2;wire[z]=nn+s.c.g.size();s.c.g.push_back({wire[a],wire[b]});dep[z]=1+max(dep[a],dep[b]);s.live.push_back(z);return true;};
 s.dep=0;for(int z:targets){if(!rec(rec,z))return false;s.c.o.push_back(wire[z]);s.dep=max(s.dep,dep[z]);}s.count=s.c.g.size();return true;}
void offer(const State&s,const char*method,int parent){for(auto[g,d]:front)if(g<=s.count&&d<=s.dep)return;front.erase(remove_if(front.begin(),front.end(),[&](P x){return s.count<=x.first&&s.dep<=x.second;}),front.end());front.push_back({s.count,s.dep});cout<<"{\"method\":\""<<method<<"\",\"parent_index\":"<<parent<<",\"iteration\":"<<iter<<",\"elapsed\":"<<chrono::duration<double>(chrono::steady_clock::now()-clock_start).count()<<",\"XOR\":"<<s.count<<",\"depth\":"<<s.dep<<",\"circuit\":{\"inputs\":32,\"gates\":[";bool first=true;for(auto[a,b]:s.c.g){if(!first)cout<<',';first=false;cout<<"[\"XOR\","<<a<<','<<b<<']';}cout<<"],\"outputs\":[";first=true;for(int x:s.c.o){if(!first)cout<<',';first=false;cout<<x;}cout<<"]}}"<<endl;}
int main(int argc,char**argv){rng.seed(stoull(argv[1]));double seconds=stod(argv[2]);int expand=stoi(argv[4]);clock_start=chrono::steady_clock::now();ifstream in(argv[3]);int ns;in>>ns;for(int i=0;i<32;i++)add(U(1)<<i);vector<vector<pair<int,int>>> choices;
 for(int k=0;k<ns;k++){int n,g,o;in>>n>>g>>o;vector<int>w(32);iota(w.begin(),w.end(),0);vector<pair<int,int>> ch;for(int i=0;i<g;i++){int a,b;in>>a>>b;a=w[a];b=w[b];int z=add(vals[a]^vals[b]);int e=edge(z,a,b);ch.push_back({z,e});w.push_back(z);}vector<int> out;for(int i=0;i<o;i++){int x;in>>x;out.push_back(w[x]);}if(k==0)targets=out;else if(targets!=out)return 3;choices.push_back(ch);}
 // Optional associativity closure adds bridge signals near original decompositions.
 if(expand){int old=vals.size();for(int z=32;z<old;z++){auto es=edges[z];for(auto[a,b]:es)for(int sw=0;sw<2;sw++){if(sw)swap(a,b);if(a>=32){auto aes=edges[a];for(auto[c,d]:aes){int u=add(vals[b]^vals[c]);if(vals[u]&&u!=z){edge(u,b,c);edge(z,u,d);}int v=add(vals[b]^vals[d]);if(vals[v]&&v!=z){edge(v,b,d);edge(z,v,c);}}}}}}
 // All binary identities among known vectors, including cross-start cancellation.
 int K=vals.size();for(int a=0;a<K;a++)for(int b=a+1;b<K;b++){auto it=ids.find(vals[a]^vals[b]);if(it!=ids.end()&&it->second>=32&&vals[a]&&vals[b])edge(it->second,a,b);}
 vector<int> defaultc(K,-1),depth(K,999);for(int i=0;i<32;i++)depth[i]=0;for(int round=0;round<40;round++){bool change=false;for(int z=32;z<K;z++)for(int e=0;e<int(edges[z].size());e++){auto[a,b]=edges[z][e];int d=1+max(depth[a],depth[b]);if(d<depth[z]){depth[z]=d;defaultc[z]=e;change=true;}}if(!change)break;}
 for(auto ch:choices){State s;s.choice=defaultc;for(auto[z,e]:ch)s.choice[z]=e;if(!build(s))return 4;starts.push_back(s);front.push_back({s.count,s.dep});}
 cerr<<"library "<<K<<" edges ";int ec=0;for(auto e:edges)ec+=e.size();cerr<<ec<<endl;
 int chain=0;while(chrono::duration<double>(chrono::steady_clock::now()-clock_start).count()<seconds){int parent=chain%starts.size();State s=starts[parent];int limit=5+rng()%10; if(rng()%2)limit=max(5,s.dep-int(rng()%3));double penalty=4+(rng()%40);double temp=0.02+(rng()%100)/100.0;double score=s.count+penalty*max(0,s.dep-limit);int accepted=0;
 for(int step=0;step<20000;step++){iter++;if(iter%1000==0&&chrono::duration<double>(chrono::steady_clock::now()-clock_start).count()>=seconds)break;State t=s;int changes=1+(rng()%15==0?1+rng()%3:0);for(int j=0;j<changes;j++){int z=s.live[rng()%s.live.size()];if(edges[z].size()>1)t.choice[z]=rng()%edges[z].size();}if(!build(t))continue;double ns=t.count+penalty*max(0,t.dep-limit);double temperature=temp*(1.0-double(step)/22000);if(ns<=score||double(rng()>>11)/9007199254740992.0<exp((score-ns)/temperature)){s=move(t);score=ns;accepted++;offer(s,"semantic-egraph-anneal",parent);}}
 if(chain%10==0)cerr<<"chain "<<chain<<" iter "<<iter<<" last "<<s.count<<'/'<<s.dep<<" accepts "<<accepted<<endl;chain++;}
 cerr<<"done iterations "<<iter<<endl;}
