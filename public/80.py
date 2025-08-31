#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random
import string
#自动安装库的功能所需要的库
import subprocess
import sys
import importlib
class DemoPOC:
    appName = '通用Web应用'           # 漏洞影响的应用或组件名称
    appVersion = '所有版本'           # 漏洞影响版本
    install_requires = ['requests']   # 你可以在这里添加其他需要的库
    VE_ID = "CVE-20XX-XXXX"         # CVE编号
    Vul_name = "服务器端请求伪造漏洞"  # 漏洞名称
    Type = "SSRF"                    # 漏洞类型
    Description = "该漏洞允许攻击者诱导服务器端应用程序向指定的目标地址发起请求，可能导致内网探测、绕过防火墙、获取内部服务敏感信息等危害"  # 漏洞描述
    Script_type = "python"           # POC类型（暂时只支持python）
    Script = "ssrf_poc.py"           # POC文件名（包含后缀）
    Vul_Date = "2023-01-01"          # 漏洞公开日期

    def __init__(self, url, ip, port):
        self.url = url
        self.ip = ip
        self.port = port

    def random_str(self, length):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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



    def _exploit(self, param=''):
        """漏洞利用逻辑"""
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        """构造潜在的SSRF参数"""
        payload = 'a=b'
        result = {}
        try:
            res = requests.post(self.url, headers=headers, data=payload)
            result['ExploitResponse'] = res.text
            return res.text
        #捕捉网络方面的报错异常
        except requests.RequestException as e:
            result['Error'] = f"[ERROR] Request failed: {e}"
            return result

    def _verify(self):
        """验证漏洞存在"""
        result = {}
        param = ''  # 这里没有执行命令，只是简单的验证，需要用户自己加和payload以某种方式拼接再发送
        try:
            res = self._exploit(param)
            #if判断漏洞是否存在的逻辑需要自己改善
            if res:
                result['VerifyInfo'] = f"[!] Vulnerability found at {self.url}"  # （必需）验证漏洞存在一定要有带[!]的信息返回。
            else:
                result['VerifyInfo'] = "[SAFE] No vulnerability found."
        except Exception as e:
            result['Error'] = f"[ERROR] Error during verification: {e}"
        return result


# 使用示例
if __name__ == '__main__':
    url = 'http://example.com/vulnerable_endpoint'
    poc = DemoPOC(url)

    # 验证漏洞
    verify_result = poc._verify()
    print(verify_result)


