# Distributed under the MIT license, see LICENSE
import os # 用于程序暂停
import requests  # 用于向网页发送GET请求
import time  # 用于设置延时
import getpass  # 用于避免密码的直接输出
from progress.spinner import Spinner  # 用于说明检测状态
import yaml  # 用于加载配置
import pickle  # 用户持久化文件
from termcolor import cprint, colored  # 用于使输出的字符附带颜色的样式
import logging  # 用于日志记录
import logging.handlers  # 用于日志处理器
import sys  # 用于获取系统信息
import traceback  # 用于异常追踪
import msvcrt  # 用于Windows系统下的非阻塞式输入检测
from termcolor import colored
# 配置文件和凭据文件路径
config_file_path = 'config.yml'
network_credentials_file_name = 'network_credentials.pkl'
network_credentials_file_path = os.path.expanduser('~') + os.sep + network_credentials_file_name

# 日志文件路径
log_file_path = 'zhku_connector.log'


def setup_logger():
    """
    配置日志记录器，设置不同级别的日志输出到控制台和文件
    
    :return: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger('zhku_connector')
    logger.setLevel(logging.DEBUG)  # 设置记录器级别为DEBUG，捕获所有级别的日志
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建控制台处理器，只显示INFO及以上级别的日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 创建文件处理器，记录DEBUG及以上级别的日志
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # 将处理器添加到记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# 初始化日志记录器
logger = setup_logger()


def get_config():
    """
    获取配置信息
    
    :return: 配置信息字典，如果配置文件不存在则返回None
    """
    try:
        logger.debug(f'尝试从 {config_file_path} 读取配置')
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
            logger.debug('配置文件读取成功')
            return config
    except Exception as e:
        logger.warning(f'读取配置文件失败: {e}')
        logger.debug(f'异常详情: {traceback.format_exc()}')
        return None


def remember_login(i_user: dict, i_setting: dict):
    """
    保存登录信息，包括用户ID和密码，还有登录的功能设置
    
    :param i_user: 用户信息字典
    :param i_setting: 设置信息字典
    :return: 是否保存成功
    """
    try:
        logger.debug(f'尝试保存登录信息到 {network_credentials_file_path}')
        with open(network_credentials_file_path, 'wb') as f:
            pickle.dump({'login_info': i_user, 'setting_info': i_setting}, f)
            logger.debug('登录信息保存成功')
            return True
    except Exception as e:
        logger.error(f'保存登录信息失败: {e}')
        logger.debug(f'异常详情: {traceback.format_exc()}')
        return False


def get_remembered_credentials():
    """
    获取已保存的登录信息
    
    :return: 登录信息字典，如果没有保存则返回None
    """
    try:
        logger.debug(f'尝试从 {network_credentials_file_path} 读取登录信息')
        with open(network_credentials_file_path, 'rb') as f:
            credentials = pickle.load(f)
            logger.debug('登录信息读取成功')
            return credentials
    except Exception as e:
        logger.debug(f'读取登录信息失败: {e}')
        return None


def remove_remembered_credentials():
    """
    删除已经保存的登录信息
    
    :return: 是否删除成功
    """
    try:
        logger.debug(f'尝试删除登录信息文件: {network_credentials_file_path}')
        os.remove(network_credentials_file_path)
        logger.info('登录信息已成功删除')
        return True
    except Exception as e:
        logger.error(f'删除登录信息失败: {e}')
        logger.debug(f'异常详情: {traceback.format_exc()}')
        return False


class Connector:
    config = get_config()
    agent_header = {
        'pc': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
        },
        'mobile': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) '
                          'AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
    }

    def __init__(self):
        # 添加对config为None的检查
        if Connector.config is None:
            # 设置默认值
            self.printable = True
            self.detect_captive_portal_url = "http://www.gstatic.com/generate_204"
            self.captive_portal = "http://172.31.255.1/drcom/login?callback=dr1003&DDDDD={user_id}&upass={password}&0MKKey=123456&R1=0&R2=&R3=0&R6=0&para=00&v6ip=&terminal_type=1&lang=zh-cn&jsVersion=4.2&v=2579&lang=zh"
        else:
            # 使用配置文件中的值
            self.printable = Connector.config.get('printable', True)
            self.detect_captive_portal_url = Connector.config.get('detect_captive_portal_url', "http://www.gstatic.com/generate_204")
            self.captive_portal = Connector.config.get('login_page', "http://172.31.255.1/drcom/login?callback=dr1003&DDDDD={user_id}&upass={password}&0MKKey=123456&R1=0&R2=&R3=0&R6=0&para=00&v6ip=&terminal_type=1&lang=zh-cn&jsVersion=4.2&v=2579&lang=zh")
        
        self.agent = 'pc'
        self.is_auto_login = True
        self.user_id = ''
        self.password = ''
        self.remember = ''

    @staticmethod
    def print_welcome_banner():
        """ 启动横幅

        :return: 包含字符画的横幅
        """
        # 添加对config为None的检查
        version = Connector.config.get('current_version', '1.0.0') if Connector.config else '1.0.0'
        logger.debug(f'当前版本: {version}')
        banner = f'''
                
        ██   ███   ▄█   ▄                                             
        █ █  █  █  ██    █                                            
        █▄▄█ █ ▀ ▄ ██ █   █                                           
        █  █ █  ▄▀ ▐█ █   █                                           
        █ ███    ▐ █▄ ▄█                                           
        █            ▀▀▀                                            
        ▀                                                            
        ▄█▄    ████▄    ▄      ▄   ▄███▄   ▄█▄      ▄▄▄▄▀ ████▄ █▄▄▄▄ 
        █▀ ▀▄  █   █     █      █  █▀   ▀  █▀ ▀▄ ▀▀▀ █    █   █ █  ▄▀ 
        █   ▀  █   █ ██   █ ██   █ ██▄▄    █   ▀     █    █   █ █▀▀▌  
        █▄  ▄▀ ▀████ █ █  █ █ █  █ █▄   ▄▀ █▄  ▄▀   █     ▀████ █  █  
        ▀███▀        █  █ █ █  █ █ ▀███▀   ▀███▀   ▀              █   
                    █   ██ █   ██                               ▀    
                                                                    

        ::ZHKU connector::            [version {version}]    
        '''
        # cprint(banner, 'green')
        print(colored(banner, color='cyan'))
        
        # 添加对config为None的检查
        github = Connector.config.get('home_page', 'https://github.com/abiua/ZHKU-Connector') if Connector.config else 'https://github.com/Jin-Cheng-Ming/ZHKU-Connector'
        last_update = Connector.config.get('last_update', '未知') if Connector.config else '未知'
        logger.debug(f'项目主页: {github}, 最后更新: {last_update}')
        info = f'''
        - Original author: Jin-Cheng Ming
        - github: 'https://github.com/Jin-Cheng-Ming/ZHKU-Connector'
        - Fork author: Abiua
        - github: {github}
        - last update: {last_update}
        '''
        cprint(info, 'dark_grey')

    def detect_captive_portal(self):
        """
        尝试访问一个不会返回实际内容的URL，如果网络正常，应该返回204 No Content。
        如果返回其他状态码或者重定向，可能意味着存在Captive Portal。
        """
        try:
            logger.debug(f"尝试访问检测URL: {self.detect_captive_portal_url}")
            response = requests.get(self.detect_captive_portal_url, allow_redirects=False)

            if response.status_code == 204:
                # 正常情况，没有Captive Portal
                logger.debug("网络连接正常，状态码: 204")
                return False
            elif response.is_redirect:
                # 检测到重定向，可能是Captive Portal
                self.captive_portal = response.headers.get('Location')
                logger.info(f"检测到重定向，可能存在Captive Portal: {self.captive_portal}")
                return True
            else:
                # 其他未知情况
                logger.warning(f"未知网络状态，状态码: {response.status_code}")
                return None
        except requests.RequestException as e:
            # 网络错误或其他异常
            logger.error(f"网络请求错误: {e}")
            return None

    def account_input(self):
        """ 设置登录相关信息
        包括登录地址，账号和密码

        :return: 登录相关信息。hostname：登录地址；user_id：账号；password：密码；
        """
        logger.info('请求用户输入登录信息')
        # 确保user_id直接存储为字符串而不是元组
        self.user_id = input(f'请输入账号：').strip()
        logger.debug(f'用户输入账号: {self.user_id}')
        self.password = getpass.getpass(f'请输入密码：')
        logger.debug('用户已输入密码（已隐藏）')

    def login(self):
        """ 登录

        :return: 是否登录成功
        """
        # 设置登录状态
        login_result_status = False
        logger.info(f'用户 [{self.user_id}] 正在登录中……')
        
        # 构建包含账号密码的完整URL
        login_url = self.captive_portal.format(user_id=self.user_id, password=self.password)
        logger.debug(f'构建登录URL: {login_url.replace(self.password, "******")}')  # 隐藏密码
        
        try:
            # 使用GET请求方式登录
            logger.debug(f'使用 {self.agent} 代理头发送GET请求')
            response = requests.get(login_url, headers=Connector.agent_header[self.agent], allow_redirects=False)
            
            # 检查登录状态码
            if response.status_code == 200:
                login_result_status = True
                logger.info('登录请求发送成功')
            else:
                logger.error(f'登录请求失败，状态码: {response.status_code}')
                print(colored(f'登录请求失败，状态码: {response.status_code}', 'red'))  # 保留彩色输出
            
            return login_result_status
        except Exception as ex:
            error_msg = f'登录请求出错，请检查网络环境是否正确: {ex}'
            logger.error(error_msg)
            logger.debug(f'异常详情: {traceback.format_exc()}')
            print(error_msg)  # 保留控制台输出
            return None

    def remember_me(self):
        logger.info('询问用户是否保存登录信息')
        print('保存登录信息，下次启动程序可以自动登录。')
        is_remember_input = input('记住登录信息吗？ Y）同意-默认  N）不同意/清除：')
        is_remember_login = len(is_remember_input) == 0 or any(res in is_remember_input for res in ['y', 'Y'])
        if is_remember_login:
            logger.debug(f'用户选择保存登录信息: {self.user_id}')
            login_info = {
                'hostname': self.captive_portal,
                'user_id': self.user_id,
                'password': self.password
            }
            setting_info = {
                'user_agent': self.agent,
                'auto_login': self.is_auto_login,
            }
            if remember_login(login_info, setting_info):
                logger.info('登录信息已成功保存')
                print('登录信息已保存在本地')
            else:
                logger.error('登录信息保存失败')
                print('保存失败，请稍后重试')
        else:
            logger.info('用户选择不保存登录信息')

    def auto_login(self):
        logger.info('启动自动登录监测服务')
        spinner = Spinner('网络已连通 ')
        while True:
            # 互联网连接异常
            logger.debug('执行网络状态检测')
            captive = self.detect_captive_portal()
            if captive or captive is None:
                spinner = Spinner('\r')
                logger.warning('检测到网络异常，需要重新登录')
                print('强制主页，登录以继续，将执行自动登录')
                # 执行登录校园网方法 获取登录状态
                login_status = self.login()
                if login_status is True:
                    logger.info('自动登录成功')
                    print('自动登录成功')
                else:
                    logger.error('自动登录失败')
                    print('自动登录失败')
                spinner = Spinner('网络已连通 ')
            # 间隔5秒执行监测
            for i in range(5):
                spinner.next()
                time.sleep(1)


    def run(self):
        # 欢迎
        logger.info('启动ZHKU校园网连接器')
        self.print_welcome_banner()
        try:
            logger.debug('检测网络连接状态')
            code = requests.get(self.detect_captive_portal_url, allow_redirects=False).status_code
        except Exception as e:
            error_msg = '无网络连接，请检查网络连接状态后重试'
            logger.error(f'{error_msg}: {e}')
            logger.debug(f'异常详情: {traceback.format_exc()}')
            print(error_msg)
            os.system("pause")
            return
            
        # 获取本地记录，如果有则在等待一定时间过后自动使用
        logger.debug('尝试获取已保存的登录信息')
        credentials = get_remembered_credentials()
        if credentials:
            logger.info(f'找到已保存的登录信息: 用户 [{credentials["login_info"]["user_id"]}]')
            print('保存有登录信息' + colored(f'[{credentials["login_info"]["user_id"]}]', 'light_cyan') + 
                  '，等待5秒自动使用此配置')
            print('按回车键清除记录并重新输入...')
            
            # 实现5秒倒计时，同时监听用户输入
            use_saved_config = True
            for i in range(5, 0, -1):
                print(f'\r自动使用配置倒计时: {i}秒...', end='', flush=True)
                # 使用msvcrt模块检测输入，Windows系统专用
                start_time = time.time()
                while time.time() - start_time < 1:  # 每秒检查多次键盘输入
                    if msvcrt.kbhit():  # 检查是否有键盘输入
                        key = msvcrt.getch()  # 获取按下的键
                        if key == b'\r' or key == b'\n':  # 检查是否为回车键
                            use_saved_config = False
                            print('\n用户取消了自动登录')
                            break
                    time.sleep(0.1)  # 短暂休眠，减少CPU使用
                
                if not use_saved_config:  # 如果用户取消了，跳出倒计时循环
                    break
            
            print()  # 换行
            
            if use_saved_config:
                # 倒计时结束，使用保存的配置
                logger.info('使用已保存的登录信息')
                print('使用已保存的登录配置')
                self.user_id = credentials['login_info']['user_id']
                self.password = credentials['login_info']['password']
                self.agent = credentials['setting_info']['user_agent']
            else:
                # 用户按了回车，清除配置
                logger.info('用户选择清除已保存的登录信息')
                remove_remembered_credentials()
                print('本地记录已清除，请重新输入登录信息')
                self.account_input()
        else:
            logger.info('未找到已保存的登录信息，需要用户输入')
            self.account_input()

        # 网络情况检查
        if code is not None and code != 204:
            logger.warning('网络连接异常，尝试登录校园网')
            print("未连接到互联网，检测登录主页中......")
            login_status = self.login()
            if login_status is not True:
                logger.error('登录失败，需要重新输入登录信息')
                print('登录失败，请检查登录信息是否正确并重新输入')
                self.account_input()
                while self.login() is not True:
                    logger.error('登录再次失败，需要重新输入登录信息')
                    print('登录失败，请检查登录信息是否正确并重新输入')
                    self.account_input()

        logger.info('账号登录正常')
        print('账号登录正常')
        if self.remember != 'use_last':
            logger.debug('询问用户是否保存登录信息')
            self.remember_me()

        self.auto_login()


if __name__ == '__main__':
    connector = Connector()
    connector.run()