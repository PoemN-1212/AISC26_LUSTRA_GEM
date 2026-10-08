@echo off
chcp 65001 >nul
:: Kiem tra quyen Administrator
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Dang mo cua so xac nhan Administrator (UAC)...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ====================================================================
echo  DANG CHUYEN FILE BO NHO DEM (PAGEFILE.SYS) TU O C: SANG O D:
echo ====================================================================
echo.

:: 1. Tat quan ly Pagefile tu dong tren toan bo he thong
echo [1/3] Tat che do tu dong dat pagefile tren o C...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-CimInstance -Query 'Select * from Win32_ComputerSystem' -Property @{AutomaticManagedPagefile=$False}"

:: 2. Thiet lap Registry de chi dung pagefile tren o D:
echo [2/3] Cau hinh Pagefile tren o D: (D:\pagefile.sys)...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v PagingFiles /t REG_MULTI_SZ /d "D:\pagefile.sys 0 0" /f

:: 3. Thong bao hoan tat
echo [3/3] Cau hinh thanh cong!
echo.
echo ====================================================================
echo  HOAN TAT CAI DAT!
echo  - O D: se quan ly bo nho dem (D:\pagefile.sys).
echo  - O C: se khong con bi ngat 16 GB bo nho dem nua.
echo.
echo  * QUAN TRONG: Ban chi can KHOI DONG LAI MAY (Restart Windows)
echo    de he thong giai phong hoan toan 16 GB file pagefile.sys tren o C!
echo ====================================================================
echo.
pause
