# 使用手册：POC脚本模板

此脚本是一个用于验证和利用漏洞的POC模板。用户可以使用它来验证特定的Web应用是否存在该漏洞，并尝试读取受影响应用的敏感文件。以下是如何使用这个POC脚本的详细说明。

## 1. 前提要求

```python
import requests
import subprocess
import sys
import importlib
```

### 1.1 必要的Python版本

此脚本适用于Python 3.x。请确保你的Python环境符合以下要求：

- Python 3.6 或更高版本

### 1.2 安装依赖库

此POC脚本可能依赖一些外部库。在执行前，确保所有必需的库已经安装。如果某些库没有安装，脚本会自动尝试安装缺少的库。

依赖库包括（但不限于）：

- `requests`: 用于发送HTTP请求。

## 2. 配置

### 2.1 配置类属性

```python
class DemoPOC:
    appName = ''              # 漏洞影响的应用或组件名称
    appVersion = ''           # 漏洞影响版本
    install_requires = []     # 你可以在这里添加其他需要的库
    CVE_ID = ""               # CVE编号
    Vul_name = ""             # 漏洞名称
    Type = "Arbitrary File Read" # 漏洞类型
    Description = ""          # 漏洞描述
    Script_type = "python"    # POC类型（暂时只支持python）
    Script = "xxx.py"         # POC文件名（包含后缀）
    Vul_Date = ""             # 漏洞公开日期
```

在脚本中，`DemoPOC`类有几个属性需要配置：

- **appName**: 漏洞影响的应用或组件的名称（可选）。
- **appVersion**: 漏洞影响的版本（可选）。
- **install_requires**: 所需安装的外部库列表。可以根据需要添加。
- **CVE_ID**: 漏洞的CVE编号，格式为`CVE-XXXX-YYYY`（可选）。
- **Vul_name**: 漏洞的名称，如“任意文件读取”。
- **Type**: 漏洞类型，可以修改。
- **Description**: 漏洞的简短描述。
- **Script_type**: 脚本类型，当前只支持Python脚本，保持默认“python”即可。
- **Script**: 脚本文件名，当前模板中默认为“xxx.py”。
- **Vul_Date**: 漏洞公开日期。

### 2.2 配置POC实例化参数

```python
    def __init__(self, url, ip, port):
        self.url = url
        self.ip = ip
        self.port = port
        self.file_path = '/etc/passwd'  # 修改这个路径以读取其他文件
```

在脚本的`DemoPOC`类的构造函数中，你需要提供以下信息：

- **url**: 目标Web应用的UR。
- **ip**: 目标主机的IP地址。
- **port**: 目标Web应用的端口号。

- **self.file_path**：可选项。你可以修改`self.file_path`属性来指定尝试读取的文件路径。你可以更改它为任何你想要尝试读取的文件路径。

例如，修改文件路径：

```python
self.file_path = '/etc/shadow'  # 读取shadow文件
```

## 3. 执行流程

### 3.1 检查并安装依赖

```python
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
```

在开始执行漏洞验证和利用之前，脚本会首先检查是否已经安装了所需的Python库。如果缺少任何依赖，脚本将会尝试自动安装缺失的库。

### 3.2 漏洞利用

```python
def _exploit(self):
    """
    漏洞利用函数，尝试读取指定文件。
    """
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'file': self.file_path}  # 根据目标漏洞调整此payload

    result = {}
    try:
        res = requests.post(self.url, headers=headers, data=payload)
        result['ExploitResponse'] = res.text
        return res.text
    except requests.RequestException as e:
        result['Error'] = f"[ERROR] Request failed: {e}"
        return result
```

执行漏洞利用函数时，脚本会发送HTTP请求到指定的URL，并携带自定义的payload。具体过程如下：

1. 检查依赖库是否安装。
2. 使用`requests`库发送一个POST请求到目标URL，payload中包含文件路径。
3. 根据返回的响应内容判断是否存在漏洞。如果能够成功读取指定的文件（例如`/etc/passwd`），则确认漏洞存在。

### 3.3 漏洞验证

```python
def _verify(self):
    """
    验证函数，检查漏洞是否存在。
    """
    self.check_and_install_dependencies()  # 检查是否安装所需库
    result = {}

    try:
        # 调用 _exploit 并获取返回结果
        res = self._exploit()

        if isinstance(res, dict) and 'Error' in res:
            result.update(res)  # 传递 _exploit 中的错误信息
        elif res and ':/bin/' in res:
            result['VerifyInfo'] = f"[!] Vulnerability found at {self.url}, able to read file: {self.file_path}"
        else:
            result['VerifyInfo'] = "[SAFE] No vulnerability found or file not accessible."
    except Exception as e:
        result['Error'] = f"[ERROR] Error during POC execution: {str(e)}"

    return result
```

如果验证成功，脚本将返回漏洞验证结果。如果文件不可访问或漏洞不存在，将显示相应的安全信息。

规格化的输出格式如下：

|    **场景**    |                       **输出格式示例**                       |                         **说明**                         |
| :------------: | :----------------------------------------------------------: | :------------------------------------------------------: |
|  **漏洞存在**  |              `[!] Vulnerability found at {url}`              |        检测到漏洞时输出，`{url}` 自动替换为实际值        |
| **漏洞不存在** |               `[SAFE] No vulnerability found.`               |                    未检测到漏洞时输出                    |
|  **错误信息**  | `[ERROR] Request failed: Connection refused` `[ERROR] Failed to install packages: {error}` | 网络错误、依赖安装失败或其他异常时输出，包含具体错误原因 |

## 4. 注意事项

1. **仅在授权的环境中使用此POC**：请确保你有权限对目标Web应用进行安全测试。未经授权的安全测试可能是非法的。
2. **payload**：如果需要，你可以根据目标漏洞的特性修改`_exploit()`方法的payload，或者添加更多的依赖库。