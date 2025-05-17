# ZHKU校园网自动登录程序

这是一个用于自动登录仲恺农业工程学院校园网的工具，可以帮助用户自动检测网络状态并进行登录。

## 功能特点

- 自动检测网络状态，当网络断开时自动重新登录
- 支持记住登录信息，下次启动时可以自动使用
- 提供日志记录功能，方便排查问题
- 可配置的登录参数和检测URL

## 使用方法

### 直接运行Python脚本

1. 确保已安装Python 3.6+
2. 安装依赖：`pip install requests progress pyyaml termcolor`
3. 运行主程序：`python main.py`

### 使用打包好的可执行文件

1. 直接双击运行`ZHKU校园网自动登录.exe`文件
2. 按照提示输入账号和密码
3. 程序会自动检测网络状态并进行登录

## 打包为可执行文件

本项目提供了打包脚本，可以将Python程序打包为独立的可执行文件，方便分享给没有Python环境的用户。

### 打包步骤

1. 运行打包脚本：`python build.py`
2. 脚本会自动安装所需的依赖和PyInstaller
3. 打包完成后，可执行文件将位于`dist`目录下
4. 将生成的`ZHKU校园网自动登录.exe`文件和`config.yml`配置文件一起分享给其他用户

### 打包注意事项

- 打包过程需要联网安装依赖
- 打包生成的可执行文件较大（约10-20MB），这是正常的
- 首次运行可能会被杀毒软件拦截，需要添加信任

## 配置文件说明

`config.yml`文件包含程序的配置信息，可以根据需要进行修改：

```yaml
current_version: version_abiu  # 版本号
last_update: 2025-05  # 最后更新时间
home_page: https://github.com/Abiu/ZHKU-Connector  # 项目主页
detect_captive_portal_url: http://www.gstatic.com/generate_204  # 检测URL
login_page: http://172.31.255.1/drcom/login?callback=dr1003&DDDDD={user_id}&upass={password}&0MKKey=123456&R1=0&R2=&R3=0&R6=0&para=00&v6ip=&terminal_type=1&lang=zh-cn&jsVersion=4.2&v=2579&lang=zh  # 登录URL模板
log_level: info  # 日志级别
printable: True  # 是否打印详细信息
```

## 常见问题

1. **打包失败怎么办？**
   - 确保已安装最新版本的pip和setuptools：`pip install --upgrade pip setuptools`
   - 尝试以管理员权限运行打包脚本

2. **程序无法登录怎么办？**
   - 检查账号密码是否正确
   - 检查网络连接是否正常
   - 查看日志文件`zhku_connector.log`获取详细错误信息

3. **打包后的程序运行报错怎么办？**
   - 确保配置文件`config.yml`与可执行文件在同一目录
   - 尝试在命令行中运行可执行文件，查看详细错误信息