@echo off
echo ==============================================================
echo   APLIKASI AUDIT KODING INA-CBG / iDRG 2025
echo   Berjalan di mode Jaringan Lokal (Intranet) - 100%% GRATIS
echo ==============================================================
echo.

:: Get local IP address using PowerShell
for /f "tokens=*" %%a in ('powershell -command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback' }).IPAddress | Select-Object -First 1"') do set LOCAL_IP=%%a

echo Aplikasi sedang dijalankan...
echo.
echo --------------------------------------------------------------
echo Buka alamat ini di browser Komputer Anda:
echo http://localhost:5000
echo.
echo Buka alamat ini di Komputer Lintas Jaringan/Teman Kantor Anda:
echo http://%LOCAL_IP%:5000
echo --------------------------------------------------------------
echo.
echo Biarkan jendela hitam ini tetap terbuka selama aplikasi digunakan.
echo Tekan Ctrl+C lalu Y untuk menutup aplikasi.
echo.

python app.py
pause
