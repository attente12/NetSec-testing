#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random
import string
from collections import OrderedDict

#自动安装库的功能所需要的库
import subprocess
import sys
import importlib

class DemoPOC:
    appName = ''              # 漏洞影响的应用或组件名称
    appVersion = ''           # 漏洞影响版本
    install_requires = []     # 你可以在这里添加其他需要的库
    CVE_ID = ""               #CVE编号
    Vul_name = ""             #漏洞名称
    Type = ""                 #漏洞类型
    Description = ""          #漏洞描述
    Script_type = "python"    #POC类型（暂时只支持python）
    Script = "xxx.py"         #POC文件名（包含后缀）
    Vul_Date = ""             # 漏洞公开日期


    def __init__(self, url, ip, port):
        self.url = url
        self.ip = ip
        self.port = port



    def check_and_install_dependencies(self):
        """检查并安装所需的库"""
        missing_packages = []
        for package in self.install_requires:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"Missing packages: {missing_packages}. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
                print(f"Successfully installed: {missing_packages}")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to install required packages: {e}")
                return False
        return True

    def random_str(self, length):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    #所需用到的配置信息
    def _options(self):
        """定义POC运行时所需的选项"""
        o = OrderedDict()
        o['user'] = ''  #支持认证的账号
        o['pwd'] = ''   #支持认证的密码
        return o

    def get_option(self, key):
        """从options中获取选项值"""
        if key in self.options:
            return self.options[key]  # 返回选项的值
        else:
            raise KeyError(f"Option '{key}' not found in available options.")

    #（重写）结合漏洞细节，需要重写部分内容。
    #建议：尽量添加调试信息，如请求超时等。
    def _exploit(self, param=''):
        user = self.get_option('user')
        pwd = self.get_option('pwd')
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = 'a=b'
        result = {}
        try:
            res = requests.post(self.url, headers=headers, data=payload)
            #res = requests.post(f'{self.url}/checkValid', headers=headers, data=payload, auth=(user, pwd))
            result['ExploitResponse'] = res.text
            return res.text
        except requests.RequestException as e:
            result['Error'] = f"[ERROR] Request failed: {e}"    #错误的调试信息放在result[ERROR]里
            return result

    def _verify(self):
        self.check_and_install_dependencies()    #在提示无对应库时，单独运行此行代码。
        result = {}
        flag = self.random_str(6)
        param = f'echo {flag}'      #需要远程执行的命令
        try:
            # 调用 _exploit 并获取返回结果
            res = self._exploit(param)
            if isinstance(res, dict) and 'Error' in res:
                result.update(res)  # 传递 _exploit 中的错误信息
            elif res and flag in res:
                result['VerifyInfo'] = f"[!] Vulnerability found at {self.url}"     #（必需）验证漏洞存在一定要有带[!]的信息返回。
            else:
                result['VerifyInfo'] = "[SAFE] No vulnerability found."
        except Exception as e:
            result['Error'] = f"[ERROR] Error during POC execution: {str(e)}"
        return result
