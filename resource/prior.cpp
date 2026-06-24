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

extern "C" __declspec(dllexport)
int calculate_prior(int x1, int z1, int str_within, int prev_layout, int simul, double* vilprob, int nvilprob, Result* res, double* info, double* distprob, int ndistprob){
    int cur_x=(x1<0) ? (x1-15)/16 : x1/16;
    int cur_z=(z1<0) ? (z1-15)/16 : z1/16;
    int ncand=0;
    double sumprob=0;

    for(int i=(cur_x-str_within) ; i<(cur_x+str_within) ; i++){
        int mi1=((i%200)+200)%200;
        int mi2_pprev=((i%40)+40)%40;
        int mi2_prev=((i%27)+27)%27;
        int mi2_new=((i%34)+34)%34;
        for(int j=(cur_z-str_within) ; j<(cur_z+str_within) ; j++){
            double cur_prob_vil=0;
            double cur_prob_sca=0;
            int mj1=((j%200)+200)%200;
            if(mi1>=50 && mi1<=150 && mj1>=50 && mj1<=150){cur_prob_sca=0.0000245074;}
            if(prev_layout==2){
                int mj2=((j%40)+40)%40;
                if(mi2_pprev<=28 && mj2<=28){
                    int cur_dist=round(sqrt(i*i+j*j));
                    if(cur_dist<nvilprob){cur_prob_vil=vilprob[cur_dist];}
                }
            }
            else if(prev_layout==1){
                int mj2=((j%27)+27)%27;
                if(mi2_prev<=17 && mj2<=17){
                    int cur_dist=round(sqrt(i*i+j*j));
                    if(cur_dist<nvilprob){cur_prob_vil=vilprob[cur_dist];}
                }
            }
            else{
                int mj2=((j%34)+34)%34;
                if(mi2_new<=27 && mj2<=27){
                    int cur_dist=round(sqrt(i*i+j*j));
                    if(cur_dist<nvilprob){cur_prob_vil=vilprob[cur_dist];}
                }
            }
            double cur_prob=cur_prob_vil+cur_prob_sca;
            if(cur_prob>0){
                int dist_int=round(sqrt((i-cur_x)*(i-cur_x)+(j-cur_z)*(j-cur_z)));
                double dist_coef=0.0001;
                if(dist_int<ndistprob){dist_coef=distprob[dist_int];}
                res[ncand].prob=cur_prob*dist_coef;
                res[ncand].ratio=cur_prob_vil/cur_prob;
                res[ncand].x=i;
                res[ncand].z=j;

                sumprob += res[ncand].prob;
                ncand++;
            }
        }
    }

    double uniform_prob = 1.0/(double)ncand;
    double xvilprob=0, xmean=0, zmean=0;
    if(simul==0){
        for(int i=0 ; i<ncand ; i++){res[i].prob=uniform_prob;}
    }
    else{
        for(int i=0 ; i<ncand ; i++){res[i].prob /= sumprob;}
    }

    /* calculating info */
    for(int i=0 ; i<ncand ; i++){
        xvilprob += res[i].prob*res[i].ratio;
        xmean += (res[i].x*16+4)*res[i].prob;
        zmean += (res[i].z*16+4)*res[i].prob;
    }
    
    info[1]=xmean;
    info[2]=zmean;

    return(ncand);
}