#include <cmath>
#include <vector>
#include <algorithm>
#include <cstdio>

using namespace std;

struct Result{
    double prob;
    double ratio;
    int x;
    int z;
};

extern "C" __declspec(dllexport)
int update_prob(double x1, double z1, double x2, double z2, double error, double* PDF, int npdf, Result* res, int lencand, double* info){
    double a=x1+0.5;
    double b=z1+0.5;
    double xeye1,xeye2,zeye1,zeye2,xeye,zeye;
    if(x1==x2){
        xeye1=x1;
        xeye2=x1;
        zeye1=b+sqrt(143.75);
        zeye2=b-sqrt(143.75);
    }
    else{
        double p=(z2-z1)/(x2-x1);
        double q=z1-p*x1;
        double r=12;
        double denom1=-1*a*a*p*p+2*a*b*p-2*a*p*q-b*b+2*b*q+p*p*r*r-q*q+r*r;
        double denom2=a+b*p-p*q;
        double nom=p*p+1;
        xeye1=(sqrt(denom1)+denom2)/nom;
        xeye2=(-1*sqrt(denom1)+denom2)/nom;
        zeye1=p*xeye1+q;
        zeye2=p*xeye2+q;
    }

    double xdir=x2-x1;
    double zdir=z2-z1;
    double cos1=xdir*(xeye1-a)+zdir*(zeye1-b);
    double cos2=xdir*(xeye2-a)+zdir*(zeye2-b);
    if(cos1>cos2){
        xeye=xeye1;
        zeye=zeye1;
    }
    else{
        xeye=xeye2;
        zeye=zeye2;
    }

    double xvec=xeye-a;
    double zvec=zeye-b;
    double vecdist=sqrt(xvec*xvec+zvec*zvec);

    vector<Result> new_res;
    int ncand=0;

    for(int i=0 ; i<lencand ; i++){
        int posx=res[i].x*16+2;
        int posz=res[i].z*16+2;
        double xvec2=posx-a;
        double zvec2=posz-b;
        double vecdist2=sqrt(xvec2*xvec2+zvec2*zvec2);

        double dot_prod=xvec*xvec2+zvec*zvec2;
        double magnitude=vecdist*vecdist2;

        double angledif=1000;
        double likelihood=0;
        if(magnitude>0){
            double val=dot_prod/magnitude;
            if(val>1.0){val=1.0;}
            if(val<-1.0){val=-1.0;}
            angledif=acos(val);
        }

        int Z=round(1000*angledif/error);
        if(Z<npdf){likelihood=PDF[Z];}
        if(likelihood>0){
            ncand=ncand+1;
            Result cur = {res[i].prob*likelihood,res[i].ratio,res[i].x,res[i].z};
            new_res.push_back(cur);
        }
    }

    sort(new_res.begin(), new_res.end(), [](const Result& a, const Result& b) {
        return a.prob > b.prob;
    });

    double sumprob=0;
    for(int i=0 ; i<ncand ; i++){sumprob=sumprob+new_res[i].prob;}
    info[3]=sumprob;

    if(sumprob>0){
        double xvilprob=0, xmean=0, zmean=0;
        for(int i=0 ; i<ncand ; i++){
            res[i].prob=new_res[i].prob/sumprob;
            res[i].ratio=new_res[i].ratio;
            res[i].x=new_res[i].x;
            res[i].z=new_res[i].z;
            xvilprob=xvilprob+res[i].prob*res[i].ratio;
            xmean=xmean+(res[i].x*16+4)*res[i].prob;
            zmean=zmean+(res[i].z*16+4)*res[i].prob;
        }

        info[0]=xvilprob;
        info[1]=xmean;
        info[2]=zmean;

        return(ncand);
    }
    else{
        info[0]=0;
        info[1]=0;
        info[2]=0;

        return(0);
    }
}

extern "C" __declspec(dllexport)
int update_prob_pf(double x1, double z1, double x2, double z2, double pixel, double error, double error_pfmeasure, double error_dist, int newver, double* PDF, int npdf, Result* res, int lencand, double* info){
    double dist=sqrt((x2-x1)*(x2-x1)+(z2-z1)*(z2-z1));
    double shift, error_coef, kdist;
    if(newver){
        shift=0.196;
        error_coef=pixel/15.604;
        kdist=dist*391.857;
    }
    else{
        shift=0.4032;
        error_coef=pixel/47.739;
        kdist=dist*185.468;
    }
    info[3]=(x2-x1)*(x2-x1)+(z2-z1)*(z2-z1);
    info[4]=dist;
    info[5]=kdist;
    double error_dist2=pixel*error_dist/dist;
    double error_pf=sqrt(error_coef*error_coef+error_dist2*error_dist2+error_pfmeasure*error_pfmeasure);
    info[6]=error_pf;
    info[7]=error_coef;
    info[8]=error_dist2;
    info[9]=error_pfmeasure;

    double xvec1=x2-x1;
    double zvec1=z2-z1;
    double newx1=x1+xvec1*shift/dist;
    double newz1=z1+zvec1*shift/dist; 
    double a=newx1+0.5;
    double b=newz1+0.5;
    double xeye1,xeye2,zeye1,zeye2,xeye,zeye;

    if(newz1==z2){
        xeye1=newx1;
        xeye2=newx1;
        zeye1=newz1+sqrt(143.75);
        zeye2=newz1-sqrt(143.75);
    }
    else{
        double p=(x2-newx1)/(z2-newz1)*-1;
        double q=newz1-p*newx1;
        double r=12;
        double denom1=-1*a*a*p*p+2*a*b*p-2*a*p*q-b*b+2*b*q+p*p*r*r-q*q+r*r;
        double denom2=a+b*p-p*q;
        double nom=p*p+1;
        xeye1=(sqrt(denom1)+denom2)/nom;
        xeye2=(-1*sqrt(denom1)+denom2)/nom;
        zeye1=p*xeye1+q;
        zeye2=p*xeye2+q;
    }

    double xdir=z2-newz1;
    double zdir=newx1-x2;
    double cos1=xdir*(xeye1-a)+zdir*(zeye1-b);
    double cos2=xdir*(xeye2-a)+zdir*(zeye2-b);
    if(cos1>cos2){
        xeye=xeye1;
        zeye=zeye1;
    }
    else{
        xeye=xeye2;
        zeye=zeye2;
    }

    double xvec=xeye-a;
    double zvec=zeye-b;
    double vecdist=sqrt(xvec*xvec+zvec*zvec);

    vector<Result> new_res;
    int ncand=0;

    for(int i=0 ; i<lencand ; i++){
        /* angle */
        int posx=res[i].x*16+2;
        int posz=res[i].z*16+2;
        double xvec2=posx-a;
        double zvec2=posz-b;
        double vecdist2=sqrt(xvec2*xvec2+zvec2*zvec2);

        double dot_prod=xvec*xvec2+zvec*zvec2;
        double magnitude=vecdist*vecdist2;

        double angledif=1000;
        double likelihood=0;
        if(magnitude>0){
            double val=dot_prod/magnitude;
            if(val>1.0){val=1.0;}
            if(val<-1.0){val=-1.0;}
            angledif=acos(val);
        }

        int Z=round(1000*angledif/error);
        if(Z<npdf){likelihood=PDF[Z];}

        /* distance */
        double xpixel=kdist/sqrt((posx-a)*(posx-a)+(posz-b)*(posz-b));
        int Z2=round(1000*abs(xpixel-pixel)/error_pf);
        if(Z2<npdf){likelihood=likelihood*PDF[Z2];}
        else{likelihood=0;}

        if(likelihood>0){
            ncand=ncand+1;
            Result cur = {res[i].prob*likelihood,res[i].ratio,res[i].x,res[i].z};
            new_res.push_back(cur);
        }
    }

    sort(new_res.begin(), new_res.end(), [](const Result& a, const Result& b) {
        return a.prob > b.prob;
    });

    double sumprob=0;
    for(int i=0 ; i<ncand ; i++){sumprob=sumprob+new_res[i].prob;}
    info[3]=sumprob;

    if(sumprob>0){
        double xvilprob=0, xmean=0, zmean=0;
        for(int i=0 ; i<ncand ; i++){
            res[i].prob=new_res[i].prob/sumprob;
            res[i].ratio=new_res[i].ratio;
            res[i].x=new_res[i].x;
            res[i].z=new_res[i].z;
            xvilprob=xvilprob+res[i].prob*res[i].ratio;
            xmean=xmean+(res[i].x*16+4)*res[i].prob;
            zmean=zmean+(res[i].z*16+4)*res[i].prob;
        }

        info[0]=xvilprob;
        info[1]=xmean;
        info[2]=zmean;

        return(ncand);
    }
    else{
        info[0]=0;
        info[1]=0;
        info[2]=0;

        return(0);
    }
}

extern "C" __declspec(dllexport)
double prob_within(int x, int z, int pc2c, Result* res, int lencand){
    double prob=0;
    for(int i=0 ; i<lencand ; i++){
        int dist=(x-res[i].x)*(x-res[i].x)+(z-res[i].z)*(z-res[i].z);
        if(dist <= pc2c){prob=prob+res[i].prob;}
    }
    return(prob);
}

extern "C" __declspec(dllexport)
double prob_within2(int x, int z, int pc, Result* res, int lencand){
    double prob=0;
    for(int i=0 ; i<lencand ; i++){
        int dist=(x-(res[i].x*16+2))*(x-(res[i].x*16+2))+(z-(res[i].z*16+2))*(z-(res[i].z*16+2));
        if(dist <= pc){prob=prob+res[i].prob;}
    }
    return(prob);
}

extern "C" __declspec(dllexport)
int village_grid(int x, int z, int grid_within, int prev_layout, Result* res, int ncand, Result* gridres){
    int grid_x;
    int grid_z;
    if(prev_layout){
        grid_x=int(x/16/27);
        grid_z=int(z/16/27);
    }
    else{
        grid_x=int(x/16/34);
        grid_z=int(z/16/34);
    }
    int size=(grid_within*2+1);
    int size2=size*size;
    int minx=grid_x-grid_within;
    int minz=grid_z-grid_within;

    vector<double> prob(size2,0);
    vector<double> xmean(size2,0);
    vector<double> zmean(size2,0);

    for(int i=0 ; i<ncand ; i++){
        if(prev_layout){
            int curx=res[i].x;
            int curz=res[i].z;
            if(((curx%27)+27)%27<=17 && ((curz%27)+27)%27<=17){
                int curgridx=curx/27-minx;
                int curgridz=curz/27-minz;
                int ind=curgridx*size+curgridz;
                prob[ind] += res[i].prob;
                xmean[ind] += res[i].prob*(curx*16+4);
                zmean[ind] += res[i].prob*(curz*16+4);
            }
        }
    }

    int ngrid=0;
    for(int i=0 ; i<size2 ; i++){
        if(prob[i]>0){
            gridres[ngrid].prob=prob[i];
            gridres[ngrid].x=xmean[i]/prob[i];
            gridres[ngrid].z=zmean[i]/prob[i];
            gridres[ngrid].ratio=1;
            ngrid=ngrid+1;
        }
    }

    sort(gridres, gridres+ngrid, [](const Result& a, const Result& b) {
        return a.prob > b.prob;
    });

    return(ngrid);
}