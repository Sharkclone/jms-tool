@echo off
REM JMS Tool - ban app-mode cho PC Windows.
REM Bam dup file nay: tu chay bridge (neu chua chay) roi mo tool trong cua so app cua Chrome
REM (cua so rieng, khong thanh dia chi, co icon tren taskbar - nhin nhu phan mem that).
REM Neu bridge da chay san thi cua so bridge moi se tu tat vi cong 8765 da co nguoi dung.
cd /d %~dp0
start "JMS Tool Bridge" /min py server.py
timeout /t 2 >nul
start "" chrome --app=http://localhost:8765 --window-size=1100,850
REM Neu Chrome khong mo len, thay dong tren bang duong dan day du cua chrome.exe, vi du:
REM start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://localhost:8765 --window-size=1100,850
