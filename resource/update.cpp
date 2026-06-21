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
    double shift, error_coef, kdist, dist_coef;
    if(newver){
        shift=-1.555;
        error_coef=pixel/15.604;
        dist_coef=391.857;
        kdist=dist*dist_coef;
    }
    else{
        shift=-1.5366;
        error_coef=pixel/47.739;
        dist_coef=185.468;
        kdist=dist*dist_coef;
    }
    double xdist=kdist/pixel;
    double error_dist2=dist_coef*error_dist/dist/xdist;
    double error_pf=sqrt(error_coef*error_coef+error_dist2*error_dist2+error_pfmeasure*error_pfmeasure);

    info[19]=error;
    info[20]=error_coef;
    info[21]=error_dist2;
    info[22]=error_pfmeasure;

    double xvec1=x2-x1;
    double zvec1=z2-z1;
    double nxvec=xvec1*cos(shift)-zvec1*sin(shift);
    double nzvec=xvec1*sin(shift)+zvec1*cos(shift);
    x2=x1+nxvec;
    z2=z1+nzvec;
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
int village_grid(int x, int z, int grid_within, int prev_layout, Result* res, int ncand, Result* gridres, double* info){
    int grid_x;
    int grid_z;
    int chunk_x=(x<0) ? (x-15)/16 : x/16;
    int chunk_z=(z<0) ? (z-15)/16 : z/16;
    if(prev_layout){
        grid_x=(chunk_x<0) ? (chunk_x-26)/27 : chunk_x/27;
        grid_z=(chunk_z<0) ? (chunk_z-26)/27 : chunk_z/27;
    }
    else{
        grid_x=(chunk_x<0) ? (chunk_x-33)/34 : chunk_x/34;
        grid_z=(chunk_z<0) ? (chunk_z-33)/34 : chunk_z/34;
    }
    int size=(grid_within*2+1);
    int size2=size*size;
    int minx=grid_x-grid_within;
    int minz=grid_z-grid_within;

    vector<double> prob(size2,0);
    vector<double> xmean(size2,0);
    vector<double> zmean(size2,0);

    for(int i=0 ; i<ncand ; i++){
        int curx=res[i].x;
        int curz=res[i].z;
        if(prev_layout){
            if(((curx%27)+27)%27<=17 && ((curz%27)+27)%27<=17){
                int curgridx=(curx<0) ? (curx-26)/27 : curx/27;
                curgridx -= minx;
                int curgridz=(curz<0) ? (curz-26)/27 : curz/27;
                curgridz -= minz;
                int ind=curgridx*size+curgridz;
                prob[ind] += res[i].prob;
                xmean[ind] += res[i].prob*(curx*16+4);
                zmean[ind] += res[i].prob*(curz*16+4);
            }
        }
        else{
            if(((curx%34)+34)%34<=27 && ((curz%34)+34)%34<=27){
                int curgridx=(curx<0) ? (curx-33)/34 : curx/34;
                curgridx -= minx;
                int curgridz=(curz<0) ? (curz-33)/34 : curz/34;
                curgridz -= minz;
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
            gridres[ngrid].x=round(xmean[i]/prob[i]);
            gridres[ngrid].z=round(zmean[i]/prob[i]);
            gridres[ngrid].ratio=i;
            ngrid=ngrid+1;
        }
    }

    sort(gridres, gridres+ngrid, [](const Result& a, const Result& b) {
        return a.prob > b.prob;
    }); 

    return(ngrid);
}

extern "C" __declspec(dllexport)
int prob_within3(int x1, int z1, int str_within, int pc2c, Result* res, int lencand, Result* withinres, double* info){
    int cx1=(x1<0) ? (x1-15)/16 : x1/16;
    int cz1=(z1<0) ? (z1-15)/16 : z1/16;
    int chunk_within=ceil(str_within/16);
    int mx=cx1-chunk_within;
    int Mx=cx1+chunk_within;
    int mz=cz1-chunk_within;
    int Mz=cz1+chunk_within;
    int size1=chunk_within*2+1;
    int size2=size1*size1;

    /* grid */
    vector<double> prob(size2,0);
    for(int i=0 ; i<lencand ; i++){
        int indx=res[i].x-mx;
        int indz=res[i].z-mz;
        int ind=indx*size1+indz;
        prob[ind]=res[i].prob;
    }

    double sumprob=0;
    for(int i=0 ; i<size2 ; i++){sumprob += prob[i];}
    info[5]=sumprob;

    /* within */
    vector<int> xr;
    vector<int> zr;
    int dc=ceil(sqrt(pc2c));
    for(int i=-1*dc ; i<(dc+1) ; i++){
        for(int j=-1*dc ; j<(dc+1) ; j++){
            if(i*i+j*j <= pc2c){
                xr.push_back(i);
                zr.push_back(j);
            }
        }
    }

    int lenxr=xr.size();;
    info[6]=lenxr;

    /* calculate */
    int maxind=-1;
    double maxvalue=-1;
    int ncheck=min(lencand,100);

    info[7]=ncheck;

    for(int i=0 ; i<ncheck ; i++){
        double curprob=0.0;
        int cur_x=res[i].x;
        int cur_z=res[i].z;
        for(int i=0 ; i<lenxr ; i++){
            info[7]=i;
            int new_x=cur_x+xr[i];
            int new_z=cur_z+zr[i];
            if(new_x>=mx && new_x<=Mx && new_z>=mz && new_z<=Mz){
                int indx=new_x-mx;
                int indz=new_z-mz;
                int ind=indx*size1+indz;
                curprob += prob[ind];
            }
        }

        withinres[i].prob=curprob;
        if(curprob>maxvalue){
            maxind=i;
            maxvalue=curprob;
        }
    }

    return(maxind);
}

extern "C" __declspec(dllexport)
double angle_dif_cal(double x1, double z1, double x2, double z2, double strx, double strz){
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

    double xvec1=xeye-a;
    double zvec1=zeye-b;
    double xvec2=strx-a;
    double zvec2=strz-b;

    double dist1=sqrt(xvec1*xvec1+zvec1*zvec1);
    double dist2=sqrt(xvec2*xvec2+zvec2*zvec2);
    double denom=xvec1*xvec2+zvec1*zvec2;

    double val=denom/(dist1*dist2);
    if(val>1.0){val=1.0;}
    if(val<-1.0){val=-1.0;}
    double angledif=acos(val);

    return(angledif);
}

extern "C" __declspec(dllexport)
double if_vil_prob(int x, int z, int prev_layout, Result* res, int lencand, double* info){
    double prob_in=0.0;
    double prob_not=0.0;
    double base_prob, likelihood;
    int gridx, gridz, cur_gridx, cur_gridz, curx, curz;
    int found=0;

    if(prev_layout){
        base_prob=1.0/18.0/18.0*0.267;
        gridx=(x<0) ? (x-26)/27 : x/27;
        gridz=(z<0) ? (z-26)/27 : z/27;
    }
    else{
        base_prob=1.0/28.0/28.0*0.267;
        gridx=(x<0) ? (x-33)/34 : x/34;
        gridz=(z<0) ? (z-33)/34 : z/34;
    }
    info[4]=base_prob;

    for(int i=0 ; i<lencand ; i++){
        curx=res[i].x;
        curz=res[i].z;
        if(found==0 && curx==x && curz==z){
            found=1;
            likelihood=res[i].ratio+(1-res[i].ratio)*base_prob;
            prob_in += res[i].prob*likelihood;
        }
        else if(res[i].ratio>0){
            if(prev_layout){
                cur_gridx=(curx<0) ? (curx-26)/27 : curx/27;
                cur_gridz=(curz<0) ? (curz-26)/27 : curz/27;
            }
            else{
                cur_gridx=(curx<0) ? (curx-33)/34 : curx/34;
                cur_gridz=(curz<0) ? (curz-33)/34 : curz/34;
            }
            if(cur_gridx==gridx && cur_gridz==gridz){
                likelihood=(1-res[i].ratio)*base_prob;
            }
            else{
                likelihood=base_prob;
            }
            prob_not += res[i].prob*likelihood;
        }
        else{
            prob_not += res[i].prob*base_prob;
        }
    }

    info[5]=prob_in;
    info[6]=prob_not;
    double res_prob;
    if(prob_in+prob_not==0){res_prob=0;}
    else{res_prob=prob_in/(prob_in+prob_not);}

    return(res_prob);
}