#include <windows.h>
#include <vector>
#include <cmath>
using namespace std;

struct Coords{
    int x;
    int y;
    int z;
    int valid;
};

extern "C" __declspec(dllexport)
Coords read_coords(int swidth, int sheight, int* debug){
    Coords result={0,0,0,0};
    vector<int> coords={0,0,0};

    /* Read screen */
    HDC hScreen=GetDC(NULL);
    HDC hMemoryDC=CreateCompatibleDC(hScreen);

    int width=int(max(swidth/3,min(125,swidth)));
    int height=int(sheight/3);

    HBITMAP hBitmap=CreateCompatibleBitmap(hScreen,width,height);
    HGDIOBJ hOldBitmap=SelectObject(hMemoryDC,hBitmap);
    BitBlt(hMemoryDC,0,0,width,height,hScreen,0,0,SRCCOPY);

    BITMAPINFOHEADER bmi={};
    bmi.biSize=sizeof(BITMAPINFOHEADER);
    bmi.biWidth=width;
    bmi.biHeight=-height;
    bmi.biPlanes=1;
    bmi.biBitCount=32;
    bmi.biCompression=BI_RGB;

    vector<BYTE> pixels(width*height*4);
    GetDIBits(hMemoryDC,hBitmap,0,height,pixels.data(),(BITMAPINFO*)&bmi,DIB_RGB_COLORS);

    /* OCR */
    int start_x=0;
    int start_y=0;
    int streak=0;
    int coordindex=0;
    int is_signed=0;

    for(int y=30 ; y<height ; y++){
        for(int x=8 ; x<width ; x++){
            int ind=(y*width+x)*4;
            if(pixels[ind]==255 && pixels[ind+1]==255 & pixels[ind+2]==255){
                if(start_x==0){
                    start_x=x;
                    start_y=y;
                }
                streak=streak+1;
            }
            else if(streak<4){streak=0;}
            else{break;}
        }
        if(streak>=4){break;}
    }

    if(streak>=4){
        int scale=streak/4;
        start_x=start_x+scale*44;
        while(start_x<width){
            int cM=0;
            for(int dy=0 ; dy<7 ; dy++){
                cM=cM*2;
                int current_y=start_y+dy*scale;
                int ind=(current_y*width+start_x)*4;
                if(pixels[ind]==255 && pixels[ind+1]==255 & pixels[ind+2]==255){cM=cM+1;}
            }
            int digit=-1;
            if(cM==62){digit=0;}
            else if(cM==1){digit=1;}
            else if(cM==35){digit=2;}
            else if(cM==34){digit=3;}
            else if(cM==12){digit=4;}
            else if(cM==114){digit=5;}
            else if(cM==30){digit=6;}
            else if(cM==96){digit=7;}
            else if(cM==54){digit=8;}
            else if(cM==48){digit=9;}
            else if(cM==8){is_signed=1;}
            else if(cM==3){
                if(is_signed){coords[coordindex]=coords[coordindex]*-1;}
                coordindex=coordindex+1;
                is_signed=0;
            }
            if(digit!=-1){coords[coordindex]=10*coords[coordindex]+digit;}
            start_x=start_x+scale*6;
        }
        if(is_signed && coordindex<3){coords[coordindex]=coords[coordindex]*-1;}
        result.x=coords[0];
        result.y=coords[1];
        result.z=coords[2];
        result.valid=1;
    }

    /* cleanup memory */
    SelectObject(hMemoryDC, hOldBitmap);
    DeleteObject(hBitmap);
    DeleteDC(hMemoryDC);
    ReleaseDC(NULL, hScreen);
    return(result);
}