#include <windows.h>
#include <wchar.h>

static void say(const wchar_t *s) {
    DWORD n; WriteConsoleW(GetStdHandle(STD_OUTPUT_HANDLE), s, (DWORD)wcslen(s), &n, NULL);
}

int wmain(void) {
    wchar_t dir[MAX_PATH * 2], py[MAX_PATH * 2], app[MAX_PATH * 2], models[MAX_PATH * 2], cmd[MAX_PATH * 6];
    DWORD len = GetModuleFileNameW(NULL, dir, MAX_PATH * 2);
    if (!len) return 1;
    wchar_t *slash = wcsrchr(dir, L'\\');
    if (slash) *slash = 0;
    swprintf(py, MAX_PATH * 2, L"%ls\\_internal\\runtime\\python.exe", dir);
    swprintf(app, MAX_PATH * 2, L"%ls\\_internal\\runtime\\app.zip", dir);
    swprintf(models, MAX_PATH * 2, L"%ls\\_internal\\models", dir);
    SetConsoleTitleW(L"圖片簡報轉可編輯PPT（本機版）");
    if (GetFileAttributesW(py) == INVALID_FILE_ATTRIBUTES || GetFileAttributesW(app) == INVALID_FILE_ATTRIBUTES) {
        MessageBoxW(NULL,
            L"找不到程式檔案。\n\n請先在壓縮檔上按右鍵 →「解壓縮全部」，再到解壓後的資料夾執行。\n若已解壓仍出現本訊息，可能是防毒軟體移除了「_internal」裡的檔案，請截圖給 Claude。",
            L"圖片簡報轉可編輯PPT", MB_ICONWARNING | MB_OK);
        return 1;
    }
    SetEnvironmentVariableW(L"S2P_MODEL_DIR", models);
    SetEnvironmentVariableW(L"HF_HUB_OFFLINE", L"1");
    SetEnvironmentVariableW(L"GRADIO_ANALYTICS_ENABLED", L"False");
    SetEnvironmentVariableW(L"PYTHONUTF8", L"1");
    SetEnvironmentVariableW(L"PYTHONIOENCODING", L"utf-8");
    SetEnvironmentVariableW(L"PYTHONNOUSERSITE", L"1");
    swprintf(cmd, MAX_PATH * 6, L"\"%ls\" -m s2p_app", py);
    STARTUPINFOW si; PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof si); si.cb = sizeof si; ZeroMemory(&pi, sizeof pi);
    if (!CreateProcessW(py, cmd, NULL, NULL, TRUE, 0, NULL, dir, &si, &pi)) {
        say(L"\n  無法啟動程式，請把這個視窗截圖給 Claude。\n  按 Enter 關閉。");
        getwchar();
        return 1;
    }
    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 0; GetExitCodeProcess(pi.hProcess, &code);
    CloseHandle(pi.hProcess); CloseHandle(pi.hThread);
    if (code != 0) {
        say(L"\n  程式發生錯誤，請把這個視窗截圖給 Claude。\n  按 Enter 關閉。");
        getwchar();
    }
    return (int)code;
}
