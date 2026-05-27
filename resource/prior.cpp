#include <vector>
#include <cmath>
#include <algorithm>
using namespace std;

struct Result{
    double prob;
    double ratio;
    int x;
    int z;
};
struct Cand{
    int distance;
    int x;
    int z;
    double prob_vil;
    double prob_sca;
};

extern "C" __declspec(dllexport)
int calculate_prior(int x1, int z1, int str_within, int prev_layout, int simul, double* vilprob, int nvilprob, Result* res, double* info){
    int cur_x=x1/16;
    int cur_z=z1/16;
    int ncand=0;

    vector<Cand> cand_list;
    for(int i=(cur_x-str_within) ; i<(cur_x+str_within) ; i++){
        for(int j=(cur_z-str_within) ; j<(cur_z+str_within) ; j++){
            double cur_prob_vil=0;
            double cur_prob_sca=0;
            int mi1=((i%200)+200)%200;
            int mj1=((j%200)+200)%200;
            if(mi1>=50 && mi1<=150 && mj1>=50 && mj1<=150){cur_prob_sca=0.0000245074;}
            if(prev_layout){
                int mi2=((i%27)+27)%27;
                int mj2=((j%27)+27)%27;
                if(mi2<=17 && mj2<=17){
                    int cur_dist=round(sqrt(i*i+j*j));
                    if(cur_dist<nvilprob){cur_prob_vil=vilprob[cur_dist];}
                }
            }
            else{
                int mi2=((i%34)+34)%34;
                int mj2=((j%34)+34)%34;
                if(mi2<=27 && mj2<=27){
                    int cur_dist=round(sqrt(i*i+j*j));
                    if(cur_dist<nvilprob){cur_prob_vil=vilprob[cur_dist];}
                }
            }
            if(cur_prob_vil+cur_prob_sca>0){
                ncand=ncand+1;
                int ci=i*16+2;
                int cj=j*16+2;
                int dist=(ci-x1)*(ci-x1)+(cj-z1)*(cj-z1);
                Cand cur = {dist,i,j,cur_prob_vil,cur_prob_sca};
                cand_list.push_back(cur);
            }
        }
    }

    sort(cand_list.begin(), cand_list.end(), [](const Cand& a, const Cand& b) {
        return a.distance < b.distance;
    });

    double sumprob=0;
    for(int i=0 ; i<ncand ; i++){sumprob=sumprob+cand_list[i].prob_vil+cand_list[i].prob_sca;}

    double no_stronghold=1;
    for(int i=0 ; i<ncand ; i++){
        double cur_prob=(cand_list[i].prob_vil+cand_list[i].prob_sca)/sumprob;
        double ratio=(cand_list[i].prob_vil/sumprob)/cur_prob;
        res[i].prob=no_stronghold*cur_prob;
        res[i].ratio=ratio;
        no_stronghold=no_stronghold*(1-cur_prob);
        res[i].x=cand_list[i].x;
        res[i].z=cand_list[i].z;
    }

    sumprob=0;
    for(int i=0 ; i<ncand ; i++){sumprob=sumprob+res[i].prob;}
    for(int i=0 ; i<ncand ; i++){res[i].prob=res[i].prob/sumprob;}

    /* uniform distribution */
    double uniform_prob=0;
    if(ncand>0){uniform_prob=1.0/(double)ncand;}
    if(simul==0){
        for(int i=0 ; i<ncand ; i++){res[i].prob=uniform_prob;}
    }

    /* calculating info */
    double xvilprob=0;
    for(int i=0 ; i<ncand ; i++){xvilprob=xvilprob+res[i].prob*res[i].ratio;}
    info[0]=xvilprob;

    double xmean=0;
    double zmean=0;
    for(int i=0 ; i<ncand ; i++){
        xmean=xmean+(res[i].x*16+4)*res[i].prob;
        zmean=zmean+(res[i].z*16+4)*res[i].prob;
    }
    info[1]=xmean;
    info[2]=zmean;

    return(ncand);
}