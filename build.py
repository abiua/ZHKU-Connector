# -*- coding: utf-8 -*-
"""
打包脚本 - 将ZHKU校园网自动登录程序打包为可执行文件

此脚本使用PyInstaller将Python项目打包成独立的.exe文件，
使其可以在没有Python环境的计算机上运行。
"""

import os
import sys
import subprocess
import shutil

# 检查PyInstaller是否已安装
def check_pyinstaller():
    """检查PyInstaller是否已安装，如果没有则安装"""
    try:
        import PyInstaller
        print("PyInstaller已安装，版本：", PyInstaller.__version__)
        return True
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller安装成功！")
            return True
        except subprocess.CalledProcessError as e:
            print(f"安装PyInstaller失败: {e}")
            return False

# 检查项目依赖是否已安装
def check_dependencies():
    """检查项目所需的依赖是否已安装，如果没有则安装"""
    dependencies = [
        "requests",
        "progress",
        "pyyaml",
        "termcolor"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"{dep} 已安装")
        except ImportError:
            print(f"{dep} 未安装，正在安装...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"{dep} 安装成功！")
            except subprocess.CalledProcessError as e:
                print(f"安装 {dep} 失败: {e}")
                return False
    return True

# 清理之前的构建文件
def clean_build_files():
    """清理之前的构建文件"""
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            shutil.rmtree(dir_name)
    
    spec_file = "main.spec"
    if os.path.exists(spec_file):
        print(f"删除 {spec_file} 文件...")
        os.remove(spec_file)

# 使用PyInstaller打包应用
def build_executable():
    """使用PyInstaller打包应用为可执行文件"""
    print("开始打包应用...")
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--name=ZHKU校园网自动登录",
        "--onefile",  # 打包成单个可执行文件
        "--icon=NONE",  # 如果有图标文件，可以在这里指定
        "--add-data=config.yml;.",  # 添加配置文件
        "main.py"  # 主程序文件
    ]
    
    try:
        subprocess.check_call(cmd)
        print("打包完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False

# 主函数
def main():
    """主函数，执行打包流程"""
    print("=== ZHKU校园网自动登录程序打包工具 ===")
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("PyInstaller安装失败，无法继续打包")
        return
    
    # 检查依赖
    if not check_dependencies():
        print("依赖安装失败，无法继续打包")
        return
    
    # 清理之前的构建文件
    clean_build_files()
    
    # 打包应用
    if build_executable():
        exe_path = os.path.join("dist", "ZHKU校园网自动登录.exe")
        if os.path.exists(exe_path):
            print(f"\n打包成功！可执行文件位于: {os.path.abspath(exe_path)}")
            print("\n您可以将此文件分享给其他用户，他们无需安装Python即可运行。")
        else:
            print("打包似乎成功，但找不到生成的可执行文件。")
    else:
        print("打包失败，请检查错误信息。")

# 程序入口
if __name__ == "__main__":
    main()
    input("\n按任意键退出...")