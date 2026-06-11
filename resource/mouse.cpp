#include <windows.h>
#include <thread>
#include <atomic>
#include <cmath>
using namespace std;

atomic<int> sum_move{0};
atomic<int> sum_abs{0};

HWND hidden_hwnd=nullptr;
thread worker_thread;
atomic<int> is_running{0};

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam){
    if(msg==WM_INPUT){
        RAWINPUT raw;
        UINT dwSize=sizeof(raw);
        if(GetRawInputData((HRAWINPUT)lParam, RID_INPUT, &raw, &dwSize, sizeof(RAWINPUTHEADER)) != (UINT)-1){
            if(raw.header.dwType==RIM_TYPEMOUSE){
                int dx = raw.data.mouse.lLastX;
                sum_move += dx;
                sum_abs += abs(dx);
            }
        }
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

void MessagePumpThread(){
    WNDCLASS wc={0};
    wc.lpfnWndProc=WndProc;
    wc.hInstance=GetModuleHandle(NULL);
    wc.lpszClassName=TEXT("RawInputHiddenWnd");
    RegisterClass(&wc);

    hidden_hwnd=CreateWindowEx(0,wc.lpszClassName,TEXT("MsgWnd"),0, 0, 0, 0, 0, HWND_MESSAGE, NULL, wc.hInstance, NULL);

    RAWINPUTDEVICE rid[1];
    rid[0].usUsagePage=0x01;
    rid[0].usUsage=0x02;
    rid[0].dwFlags=RIDEV_INPUTSINK;
    rid[0].hwndTarget=hidden_hwnd;

    RegisterRawInputDevices(rid, 1, sizeof(rid[0]));

    MSG msg;
    while(GetMessage(&msg,NULL,0,0)>0){
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}

extern "C" __declspec(dllexport) 
void start_tracking() {
    if (!is_running) {
        sum_move = 0;
        sum_abs = 0;
        is_running = true;
        worker_thread = std::thread(MessagePumpThread);
    }
}

extern "C" __declspec(dllexport) 
void stop_tracking() {
    if (is_running && hidden_hwnd != nullptr) {
        PostMessage(hidden_hwnd, WM_QUIT, 0, 0);
        if (worker_thread.joinable()) {
            worker_thread.join();
        }
        is_running = false;
        hidden_hwnd = nullptr;
    }
}

extern "C" __declspec(dllexport) 
void get_mouse_data(int* out_move, int* out_abs) {
    *out_move = sum_move.load();
    *out_abs = sum_abs.load();
}

extern "C" __declspec(dllexport) 
void reset_data() {
    sum_move = 0;
    sum_abs = 0;
}