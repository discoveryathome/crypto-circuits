#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using namespace std; using U=uint64_t; using G=unordered_map<U,pair<U,U>>;
struct C{G g;vector<U> out;int n;};
struct Eval{int size=10000,dep=10000;double sum=0; G g; unordered_map<U,int>d;};
mt19937_64 rng;
bool leaf(U x){return x&&!(x&(x-1));}
Eval evaluate(C const&c){Eval e;unordered_set<U>active;bool fail=false;auto visit=[&](auto&&self,U x)->int{if(leaf(x))return 0;if(e.d.count(x))return e.d[x];if(!x||active.count(x)||!c.g.count(x)){fail=true;return 10000;}active.insert(x);auto[a,b]=c.g.at(x);int z=1+max(self(self,a),self(self,b));active.erase(x);e.d[x]=z;e.g[x]={a,b};return z;};e.dep=0;for(U o:c.out){int d=visit(visit,o);e.dep=max(e.dep,d);e.sum+=d;}if(!fail)e.size=e.g.size();return e;}
C prune(C c){auto e=evaluate(c);if(e.size<10000)c.g=e.g;return c;}
vector<U>nodes(C const&c){vector<U>v;for(int i=0;i<c.n;i++)v.push_back(U(1)<<i);for(auto [z,ab]:c.g)v.push_back(z);return v;}
C relax(C c){auto v=nodes(c);unordered_map<U,vector<pair<U,U>>>options;for(int i=0;i<v.size();i++)for(int j=0;j<i;j++){U z=v[i]^v[j];if(c.g.count(z))options[z].push_back({v[i],v[j]});}unordered_map<U,int>d;for(int i=0;i<c.n;i++)d[U(1)<<i]=0;G g;bool change=true;while(change){change=false;shuffle(v.begin(),v.end(),rng);for(U z:v)if(!leaf(z)){auto &pp=options[z];shuffle(pp.begin(),pp.end(),rng);for(auto[a,b]:pp)if(d.count(a)&&d.count(b)){int dd=1+max(d[a],d[b]);if(!d.count(z)||dd<d[z]){d[z]=dd;g[z]={a,b};change=true;}}}}c.g=g;return prune(c);}
C mutate(C c,int method){auto v=nodes(c);if(c.g.empty())return c;U y=v[c.n+rng()%c.g.size()];auto [a,b]=c.g[y];
 if(method==0){ // reassociate an expanded cone, retaining shared intermediates
 vector<U>terms={a,b};int expansions=1+rng()%3;for(int k=0;k<expansions;k++){vector<int>eligible;for(int i=0;i<terms.size();i++)if(c.g.count(terms[i]))eligible.push_back(i);if(eligible.empty())break;int ix=eligible[rng()%eligible.size()];auto[p,q]=c.g[terms[ix]];terms.erase(terms.begin()+ix);terms.push_back(p);terms.push_back(q);}
 sort(terms.begin(),terms.end());vector<U>t;for(int i=0;i<terms.size();){int j=i+1;while(j<terms.size()&&terms[j]==terms[i])j++;if((j-i)&1)t.push_back(terms[i]);i=j;}if(t.size()<2)return c;shuffle(t.begin(),t.end(),rng);
 while(t.size()>2){int i=rng()%t.size();U p=t[i];t.erase(t.begin()+i);i=rng()%t.size();U q=t[i];t.erase(t.begin()+i);U z=p^q;if(!z||z==y)return c;if(!leaf(z)&&!c.g.count(z))c.g[z]={p,q};t.push_back(z);}c.g[y]={t[0],t[1]};
 }else if(method==1){ // exact pair substitution including arbitrary existing semantic wires
 shuffle(v.begin(),v.end(),rng);for(U p:v){U q=p^y;if(q&&q!=y&&(leaf(q)||c.g.count(q))&&p!=y){c.g[y]={p,q};break;}}
 }else if(method==2){ // eliminate shared vertex by reexpressing every dependent vertex
 U x=y;vector<U>users;for(auto[z,ab]:c.g)if(ab.first==x||ab.second==x)users.push_back(z);if(find(c.out.begin(),c.out.end(),x)!=c.out.end())return c;shuffle(v.begin(),v.end(),rng);for(U z:users){bool found=false;for(U p:v){U q=z^p;if(p!=x&&q!=x&&p!=z&&q!=z&&q&&(leaf(q)||c.g.count(q))){c.g[z]={p,q};found=true;break;}}if(!found)return c;}c.g.erase(x);
 }else{ // introduce a common pair and consume it wherever exact pair identities permit
 U p=v[rng()%v.size()],q=v[rng()%v.size()],z=p^q;if(!z||leaf(z)||c.g.count(z))return c;c.g[z]={p,q};vector<U>vv=v;shuffle(vv.begin(),vv.end(),rng);int changed=0;for(U t:vv){U r=t^z;if(t!=z&&r&&r!=t&&c.g.count(t)&&(leaf(r)||c.g.count(r))){c.g[t]={z,r};if(++changed>=2+rng()%3)break;}}
 }return c;}
void emit(C const&c,string method,long it,int parent){auto e=evaluate(c);cout<<"{\"method\":\""<<method<<"\",\"iteration\":"<<it<<",\"parent\":"<<parent<<",\"XOR\":"<<e.size<<",\"depth\":"<<e.dep<<",\"circuit\":{\"inputs\":"<<c.n<<",\"gates\":[";unordered_map<U,int>id;for(int i=0;i<c.n;i++)id[U(1)<<i]=i;bool first=true;auto add=[&](auto&&self,U z)->int{if(id.count(z))return id[z];auto[a,b]=c.g.at(z);int aa=self(self,a),bb=self(self,b);int k=id.size();id[z]=k;if(!first)cout<<",";first=false;cout<<"[\"XOR\","<<aa<<","<<bb<<"]";return k;};for(U o:c.out)add(add,o);cout<<"],\"outputs\":[";for(int i=0;i<c.out.size();i++){if(i)cout<<",";cout<<id[c.out[i]];}cout<<"]}}"<<endl;}
int main(int argc,char**argv){rng.seed(stoull(argv[1]));double secs=stod(argv[2]);auto start=chrono::steady_clock::now();vector<C>pool;vector<pair<int,int>>front;for(int f=3;f<argc;f++){ifstream in(argv[f]);C c;int m,k;in>>c.n>>m>>k;vector<U>vals;for(int i=0;i<c.n;i++)vals.push_back(U(1)<<i);for(int i=0;i<m;i++){int a,b;in>>a>>b;U z=vals[a]^vals[b];vals.push_back(z);c.g[z]={vals[a],vals[b]};}for(int i=0;i<k;i++){int o;in>>o;c.out.push_back(vals[o]);}c=prune(c);pool.push_back(c);auto e=evaluate(c);front.push_back({e.size,e.dep});}
 auto offer=[&](C c,string meth,long it,int parent){auto e=evaluate(c);if(e.size>=10000)return;for(auto[a,b]:front)if(a<=e.size&&b<=e.dep)return;front.erase(remove_if(front.begin(),front.end(),[&](auto v){return e.size<=v.first&&e.dep<=v.second;}),front.end());front.push_back({e.size,e.dep});c.g=e.g;emit(c,meth,it,parent);pool.push_back(c);};
 long it=0,accepted=0,invalid=0;int parent=0;C cur=pool[0];Eval old=evaluate(cur);int mode=0;while(chrono::duration<double>(chrono::steady_clock::now()-start).count()<secs){if(it%6000==0){parent=(it==0?0:rng()%pool.size());cur=pool[parent];mode=rng()%4;cur=relax(cur);old=evaluate(cur);offer(cur,"minimum-arrival-relaxation",it,parent);}
 int method=rng()%10;method=method<6?0:method<8?1:method==8?2:3;C next=mutate(cur,method);auto e=evaluate(next);if(e.size>=10000){invalid++;it++;continue;}next.g=e.g;if(it%100==99){next=relax(next);e=evaluate(next);}
 offer(next,"semantic-cone-and-shared-resubstitution",it,parent);
 double dw=mode==0?0.1:mode==1?2.5:mode==2?6:12;auto score=[&](Eval const&x){return x.size+dw*x.dep+0.015*x.sum;};double temp=(mode==0?0.7:1.4)*(1.-(it%6000)/7000.);double delta=score(e)-score(old);int ceiling=parent==0?244:174;
 if(e.size<=ceiling&&(delta<=0||generate_canonical<double,53>(rng)<exp(-delta/temp))){cur=next;old=e;accepted++;}
 if(it%20000==0){cerr<<"iteration="<<it<<" elapsed="<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<" current="<<old.size<<","<<old.dep<<" pool="<<pool.size()<<" accepted="<<accepted<<" invalid="<<invalid<<endl;}
 it++;}
 cerr<<"done iterations="<<it<<" accepted="<<accepted<<" invalid="<<invalid<<endl;
}
