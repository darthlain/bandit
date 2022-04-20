#include <shobjidl_core.h>
#include <shlobj_core.h>
#include <shlobj.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tchar.h>

#pragma comment(lib, "shell32")
#pragma comment(lib, "user32")
#pragma comment(lib, "ole32")

extern "C" __declspec(dllexport) void multiproperties(LPOLESTR*, int);
extern "C" __declspec(dllexport) void rightclickmenu(LPOLESTR, LPOLESTR*, int, HWND);

void multiproperties(LPOLESTR *pszFiles, int num)
{
    LPITEMIDLIST* pidls = (LPITEMIDLIST*)malloc(sizeof(LPITEMIDLIST) * num);
    HRESULT hr;
    IShellFolder* pDesktop;
    IDataObject *pDataObject;

    hr = SHGetDesktopFolder(&pDesktop);

    for (int i = 0; i < num; i++) {

        hr = pDesktop->ParseDisplayName(HWND_DESKTOP, NULL, pszFiles[i],
                NULL, &pidls[i], NULL);
    }

    hr = pDesktop->GetUIObjectOf(HWND_DESKTOP, num, (LPCITEMIDLIST*)pidls,
            IID_IDataObject, NULL, (void**)&pDataObject);
    pDesktop->Release();
    
    for (int i = 0; i < num; i++) {
        SHFree(pidls[i]);
    }

    if (SUCCEEDED(hr)) {
        hr = SHMultiFileProperties(pDataObject, 0);
        pDataObject->Release();

        //if (SUCCEEDED(hr)) {
        //    MessageBox(0, _T("Dummy message box"), 0, 0);
        //    Sleep(10000); // Give the system time to show the dialog before exiting
        //}
    }

    free(pidls);
}

void rightclickmenu(LPOLESTR dirname, LPOLESTR *filenames, int num, HWND hwnd)
{
    LPITEMIDLIST        dirpidl;
    LPITEMIDLIST        *itempidls = (LPITEMIDLIST*)malloc(sizeof(LPITEMIDLIST) * num);
    IShellFolder        *pDesktop;
    IShellFolder        *pFolder;
    IContextMenu        *context;
    IContextMenu        *context2;
    IContextMenu        *context3;
    LPCONTEXTMENU       pCM;
    HMENU               hMenu;
    int                 id;
    POINT               pt;
    CMINVOKECOMMANDINFO cmi = {sizeof(CMINVOKECOMMANDINFO)}; // �Ȃ��������SIGSEGV���Ȃ��Ȃ�

    // pDesktop
    SHGetDesktopFolder(&pDesktop);

    // dirpidl
    pDesktop->ParseDisplayName(NULL, NULL, dirname, NULL, &dirpidl, NULL);

    // pFolder
    pDesktop->BindToObject(dirpidl, NULL, IID_IShellFolder, (void**)&pFolder);

    // itempidls
    for (int i = 0; i < num; i++) {
        pFolder->ParseDisplayName(NULL, NULL, filenames[i], NULL, &itempidls[i], NULL);
    }

    // context
    pFolder->GetUIObjectOf(hwnd, num, (LPCITEMIDLIST*)itempidls, IID_IContextMenu, NULL,
                    (void **)&context);

    context->QueryInterface(IID_PPV_ARGS(&context2));
    context->QueryInterface(IID_PPV_ARGS(&context3));

    //pCM
    if      (context3) pCM = context3;
    else if (context2) pCM = context2;
    else               pCM = context;

    // ��������{��
    hMenu = CreatePopupMenu();
    pCM->QueryContextMenu(hMenu, 0, 1, 0x7fff, CMF_EXPLORE);
    GetCursorPos(&pt);
    id = TrackPopupMenu(hMenu, TPM_LEFTALIGN|TPM_RETURNCMD|TPM_RIGHTBUTTON,
            pt.x, pt.y, 0, hwnd, NULL);

    if (hMenu) {

        if (id) {
            cmi.hwnd   = hwnd;
            cmi.lpVerb = MAKEINTRESOURCE(id - 1);
            cmi.nShow  = SW_SHOW;

            pCM->InvokeCommand(&cmi);
        }
        DestroyMenu(hMenu);
    }

    pCM->Release();
    free(itempidls);
}
