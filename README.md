# ZHKU校园网自动登录程序

自动检测并登录仲恺农业工程学院校园网（Drcom 认证系统），断线自动重连。

Fork of [ZHKU-Connector](https://github.com/Jin-Cheng-Ming/ZHKU-Connector) by @Jin-Cheng-Ming.

## 快速开始

1. 下载 `dist/` 中的 `.exe` 和 `config.yml`，放在同一文件夹
2. 双击运行 `.exe`，首次使用输入学号和校园网密码
3. 选择记住登录信息，下次启动自动登录

详细说明见 **[使用手册](使用手册.md)**

## 自行打包

Windows 上双击 `打包程序.bat` 或运行 `python build.py`，生成的文件在 `dist/` 目录。

## 开发

```bash
pip install requests progress pyyaml termcolor
python main.py          # 运行
python -m pytest tests/ -v  # 测试
```
