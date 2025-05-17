@echo off
chcp 65001 > nul
echo ===================================
echo  ZHKU校园网自动登录程序打包工具
echo ===================================
echo.
echo 此批处理文件将帮助您将程序打包为可执行文件
echo 打包完成后的文件将位于dist目录中
echo.
echo 按任意键开始打包...
pause > nul

python build.py

echo.
echo 如果打包成功，可执行文件将位于dist目录中
echo 您可以将ZHKU校园网自动登录.exe和config.yml一起分享给其他用户
echo.
pause