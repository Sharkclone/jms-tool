@echo off
REM JMS Tool - che do mobile: chay bridge mo ra mang LAN de dien thoai cung WiFi mo duoc.
REM Bridge se tu in dia chi LAN (dang http://<IP-may-tinh>:8765) - mo dia chi do tren dien thoai.
REM CHI DUNG TREN WIFI TIN CAY. Xong viec thi dong cua so bridge nay lai.
cd /d %~dp0
py server.py --host 0.0.0.0
pause
