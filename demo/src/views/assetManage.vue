<template>
  <div class="vulnerability-container">
    <div class="ip-list">
      <div class="menu-header">
        <span class="title">资产</span>
        <el-badge
            :value="assets.length"
            class="asset-count"
            type="primary">
        </el-badge>
      </div>
      <el-menu
          :default-active="currentIp"
          class="ip-menu"
          @select="handleSelect">
        <el-menu-item
            v-for="asset in assets"
            :key="asset.ip"
            :index="asset.ip">
          <i class="el-icon-monitor"></i>
          <span>{{ asset.ip }}</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 右侧详情内容 -->
    <div class="content-area" v-if="currentAsset">
      <div class="ip-header">
        <h2>资产信息</h2>
        <div class="asset-info">
          <div class="info-item">
            <span class="label">IP地址：</span>
            <span class="value">{{ currentAsset.ip }}</span>
          </div>
          <div class="info-item">
            <span class="label">操作系统：</span>
            <span class="value">{{ currentAsset.os }}</span>
          </div>
          <div class="info-item">
            <span class="label">开放端口：</span>
            <span class="value">{{ currentAsset.ports }}</span>
          </div>
        </div>
      </div>
      <!-- 前面的代码保持不变，直到漏洞信息标题 -->

      <h2 class="flex justify-between items-center">
        <span style="font-size: 18px;">所含漏洞信息</span>
        <div class="chart-toggle">
          <el-radio-group v-model="displayType" size="small">
            <el-radio-button label="assetType">按资产类型分布</el-radio-button>
            <el-radio-button label="vulType">按漏洞类型分布</el-radio-button>
          </el-radio-group>
        </div>
      </h2>

      <!-- 资产类型视图 -->
      <template v-if="displayType === 'assetType'">
        <!-- 饼图 -->
        <el-card class="chart-section">
          <div slot="header" class="clearfix">
            <span>漏洞资产类型分布</span>
          </div>
          <div class="pie-chart" ref="pieChart" style="width: 100%; height: 300px;"></div>
        </el-card>

        <!-- 主机漏洞表格 -->
        <div class="table-section">
          <h3><strong>系统漏洞</strong></h3>
          <el-table
              :data="currentAsset.host_vulnerabilities"
              border
              stripe
              :header-cell-style="{ backgroundColor: '#f5f7fa' }"
          >
            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>
            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>
            <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>
            <el-table-column prop="cvss" label="风险等级" width="120">
              <template slot-scope="scope">
                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="summary" label="漏洞描述"></el-table-column>
            <el-table-column prop="vulExist" label="是否存在" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">
                  {{ scope.row.vulExist }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 原有的端口漏洞分组表格 -->
        <div class="table-section">
          <h3><strong>软件资产漏洞</strong></h3>
          <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"
               :key="type"
               class="vulnerability-group">
            <h4 class="group-title">{{ type }}</h4>
            <el-table
                :data="vulnerabilities"
                border
                stripe
                :header-cell-style="{ backgroundColor: '#f5f7fa' }"
            >
              <el-table-column prop="port_id" label="端口" width="70"></el-table-column>
              <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>
              <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>
              <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>
              <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>
              <el-table-column prop="cvss" label="风险等级" width="120">
                <template slot-scope="scope">
                  <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="summary" label="漏洞描述"></el-table-column>
              <el-table-column prop="vulExist" label="是否存在" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">
                    {{ scope.row.vulExist }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </template>

      <!-- 漏洞类型视图 -->
      <template v-else>
        <!-- 漏洞类型饼图 -->
        <el-card class="chart-section">
          <div slot="header" class="clearfix">
            <span>漏洞类型分布</span>
          </div>
          <div class="pie-chart" ref="vulTypePieChart" style="width: 100%; height: 300px;"></div>
        </el-card>

        <!-- 按漏洞类型分组的表格 -->
        <div class="table-section">
          <h3><strong>漏洞详情</strong></h3>
          <div v-for="(vulnerabilities, type) in groupedVulTypeVulnerabilities"
               :key="type"
               class="vulnerability-group">
            <h4 class="group-title">{{ type }}</h4>
            <el-table
                :data="vulnerabilities"
                border
                stripe
                :header-cell-style="{ backgroundColor: '#f5f7fa' }"
            >
              <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>
              <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>
              <el-table-column prop="softwareType" label="资产类型" width="150"></el-table-column>
              <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>
              <el-table-column prop="cvss" label="风险等级" width="120">
                <template slot-scope="scope">
                  <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="summary" label="漏洞描述"></el-table-column>
              <el-table-column prop="vulExist" label="是否存在" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">
                    {{ scope.row.vulExist }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'VulnerabilityTable',
  data() {
    return {
      currentIp: '',
      pieChart: null,
      vulTypePieChart: null,
      displayType: 'assetType',
      assets: [
        // {
        //   "host_vulnerabilities": [
        //     {
        //       "cvss": "10.000000",
        //       "softwareType": "操作系统",
        //       "summary": "drivers/media/usb/dvb-usb/technisat-usb2.c in the Linux kernel through 5.2.9 has an out-of-bounds read via crafted USB device traffic (which may be remote via usbip or usbredir).",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2019-15505",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "softwareType": "操作系统",
        //       "summary": "The NFSv2 and NFSv3 server implementations in the Linux kernel through 4.10.13 lack certain checks for the end of a buffer, which allows remote attackers to trigger pointer-arithmetic errors or possibly have unspecified other impact via crafted requests, related to fs/nfsd/nfs3xdr.c and fs/nfsd/nfsxdr.c.",
        //       "vulExist": "存在",
        //       "vulType": "未知类型",
        //       "vuln_id": "CVE-2017-7895",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "softwareType": "操作系统",
        //       "summary": "A heap-based buffer overflow vulnerability was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. A remote attacker could cause a denial of service (system crash) or, possibly execute arbitrary code, when the lbs_ibss_join_existing function is called after a STA connects to an AP.",
        //       "vulExist": "存在",
        //       "vulType": "Denial of Service (DoS)",
        //       "vuln_id": "CVE-2019-14896",
        //       "vuln_name": ""
        //     }
        //   ],
        //   "ip": "10.9.130.193",
        //   "port_vulnerabilities": [
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "A heap overflow flaw was found in the Linux kernel, all versions 3.x.x and 4.x.x before 4.18.0, in Marvell WiFi chip driver. The vulnerability allows a remote attacker to cause a system crash, resulting in a denial of service, or execute arbitrary code. The highest threat with this vulnerability is with the availability of the system. If code execution occurs, the code will run with the permissions of root. This will affect both confidentiality and integrity of files on the system.",
        //       "vulExist": "不存在",
        //       "vulType": "Denial of Service (DoS)",
        //       "vuln_id": "CVE-2019-14901",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "A heap-based buffer overflow vulnerability was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. A remote attacker could cause a denial of service (system crash) or, possibly execute arbitrary code, when the lbs_ibss_join_existing function is called after a STA connects to an AP.",
        //       "vulExist": "存在",
        //       "vulType": "Denial of Service (DoS)",
        //       "vuln_id": "CVE-2019-14896",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "Brackets versions 1.14 and earlier have a command injection vulnerability. Successful exploitation could lead to arbitrary code execution.",
        //       "vulExist": "不存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2019-8255",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175020.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-4210",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175022.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-4211",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175023.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-4212",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "SecureCRT before 8.7.2 allows remote attackers to execute arbitrary code via an Integer Overflow and a Buffer Overflow because a banner can trigger a line number to CSI functions that exceeds INT_MAX.",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2020-12651",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "Adobe Flash Player Desktop Runtime 32.0.0.371 and earlier, Adobe Flash Player for Google Chrome 32.0.0.371 and earlier, and Adobe Flash Player for Microsoft Edge and Internet Explorer 32.0.0.330 and earlier have an use after free vulnerability. Successful exploitation could lead to arbitrary code execution.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-9633",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM Spectrum Copy Data Management 2.2.13 and earlier could allow a remote attacker to execute arbitrary commands on the system, caused by improper validation of user-supplied input by the Spectrum Copy Data Management Admin Console login and uploadcertificate function . A remote attacker could inject arbitrary shell commands which would be executed on the affected system. IBM X-Force ID: 214958.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2021-39065",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM CICS TX Standard and Advanced 11.1 could allow a remote attacker to execute arbitrary commands on the system by sending a specially crafted request. IBM X-Force ID: 227980.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2022-31767",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "A carefully crafted request body can cause a buffer overflow in the mod_lua multipart parser (r:parsebody() called from Lua scripts). The Apache httpd team is not aware of an exploit for the vulnerabilty though it might be possible to craft one. This issue affects Apache HTTP Server 2.4.51 and earlier.",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2021-44790",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP Server 2.4.52 and earlier fails to close inbound connection when errors are encountered discarding the request body, exposing the server to HTTP Request Smuggling",
        //       "vulExist": "存在",
        //       "vulType": "未知类型",
        //       "vuln_id": "CVE-2022-22720",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP Server 2.4.53 and earlier may not send the X-Forwarded-* headers to the origin server based on client side Connection header hop-by-hop mechanism. This may be used to bypass IP based authentication on the origin server/application.",
        //       "vulExist": "存在",
        //       "vulType": "未知类型",
        //       "vuln_id": "CVE-2022-31813",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Out-of-bounds Write vulnerability in mod_sed of Apache HTTP Server allows an attacker to overwrite heap memory with possibly attacker provided data. This issue affects Apache HTTP Server 2.4 version 2.4.52 and prior versions.",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2022-23943",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "In Apache HTTP Server versions 2.4.0 to 2.4.46 a specially crafted SessionHeader sent by an origin server could cause a heap overflow",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2021-26691",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "ap_escape_quotes() may write beyond the end of a buffer when given malicious input. No included modules pass untrusted data to these functions, but third-party / external modules may. This issue affects Apache HTTP Server 2.4.48 and earlier.",
        //       "vulExist": "存在",
        //       "vulType": "Cross-Site Scripting (XSS)",
        //       "vuln_id": "CVE-2021-39275",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP server 2.4.32 to 2.4.44 mod_proxy_uwsgi info disclosure and possible RCE",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-11984",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "6.800000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "A crafted request uri-path can cause mod_proxy to forward the request to an origin server choosen by the remote user. This issue affects Apache HTTP Server 2.4.48 and earlier.",
        //       "vulExist": "存在",
        //       "vulType": "未知类型",
        //       "vuln_id": "CVE-2021-40438",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "6.800000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP Server versions 2.4.0 to 2.4.46 A specially crafted Digest nonce can cause a stack overflow in mod_auth_digest. There is no report of this overflow being exploitable, nor the Apache HTTP Server team could create one, though some particular compiler and/or compilation option might make it possible, with limited consequences anyway due to the size (a single byte) and the value (zero byte) of the overflow",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2020-35452",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "6.400000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP Server 2.4.53 and earlier may crash or disclose information due to a read beyond bounds in ap_strcmp_match() when provided with an extremely large input buffer. While no code distributed with the server can be coerced into such a call, third-party modules or lua scripts that use ap_strcmp_match() may hypothetically be affected.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2022-28615",
        //       "vuln_name": ""
        //     }
        //   ]
        // },
        // {
        //   "host_vulnerabilities": [
        //     {
        //       "cvss": "10.000000",
        //       "softwareType": "操作系统",
        //       "summary": "drivers/media/usb/dvb-usb/technisat-usb2.c in the Linux kernel through 5.2.9 has an out-of-bounds read via crafted USB device traffic (which may be remote via usbip or usbredir).",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2019-15505",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "softwareType": "操作系统",
        //       "summary": "The NFSv2 and NFSv3 server implementations in the Linux kernel through 4.10.13 lack certain checks for the end of a buffer, which allows remote attackers to trigger pointer-arithmetic errors or possibly have unspecified other impact via crafted requests, related to fs/nfsd/nfs3xdr.c and fs/nfsd/nfsxdr.c.",
        //       "vulExist": "存在",
        //       "vulType": "未知类型",
        //       "vuln_id": "CVE-2017-7895",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "softwareType": "操作系统",
        //       "summary": "A heap-based buffer overflow vulnerability was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. A remote attacker could cause a denial of service (system crash) or, possibly execute arbitrary code, when the lbs_ibss_join_existing function is called after a STA connects to an AP.",
        //       "vulExist": "存在",
        //       "vulType": "Denial of Service (DoS)",
        //       "vuln_id": "CVE-2019-14896",
        //       "vuln_name": ""
        //     }
        //   ],
        //   "ip": "10.9.130.192",
        //   "port_vulnerabilities": [
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 21,
        //       "softwareType": "系统工具",
        //       "summary": "A heap overflow flaw was found in the Linux kernel, all versions 3.x.x and 4.x.x before 4.18.0, in Marvell WiFi chip driver. The vulnerability allows a remote attacker to cause a system crash, resulting in a denial of service, or execute arbitrary code. The highest threat with this vulnerability is with the availability of the system. If code execution occurs, the code will run with the permissions of root. This will affect both confidentiality and integrity of files on the system.",
        //       "vulExist": "不存在",
        //       "vulType": "Denial of Service (DoS)",
        //       "vuln_id": "CVE-2019-14901",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "A heap-based buffer overflow vulnerability was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. A remote attacker could cause a denial of service (system crash) or, possibly execute arbitrary code, when the lbs_ibss_join_existing function is called after a STA connects to an AP.",
        //       "vulExist": "存在",
        //       "vulType": "Denial of Service (DoS)",
        //       "vuln_id": "CVE-2019-14896",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175020.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-4210",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175022.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-4211",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175023.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-4212",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "SecureCRT before 8.7.2 allows remote attackers to execute arbitrary code via an Integer Overflow and a Buffer Overflow because a banner can trigger a line number to CSI functions that exceeds INT_MAX.",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2020-12651",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "Adobe Flash Player Desktop Runtime 32.0.0.371 and earlier, Adobe Flash Player for Google Chrome 32.0.0.371 and earlier, and Adobe Flash Player for Microsoft Edge and Internet Explorer 32.0.0.330 and earlier have an use after free vulnerability. Successful exploitation could lead to arbitrary code execution.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-9633",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM Spectrum Copy Data Management 2.2.13 and earlier could allow a remote attacker to execute arbitrary commands on the system, caused by improper validation of user-supplied input by the Spectrum Copy Data Management Admin Console login and uploadcertificate function . A remote attacker could inject arbitrary shell commands which would be executed on the affected system. IBM X-Force ID: 214958.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2021-39065",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "10.000000",
        //       "port_id": 22,
        //       "softwareType": "系统工具",
        //       "summary": "IBM CICS TX Standard and Advanced 11.1 could allow a remote attacker to execute arbitrary commands on the system by sending a specially crafted request. IBM X-Force ID: 227980.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2022-31767",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "A carefully crafted request body can cause a buffer overflow in the mod_lua multipart parser (r:parsebody() called from Lua scripts). The Apache httpd team is not aware of an exploit for the vulnerabilty though it might be possible to craft one. This issue affects Apache HTTP Server 2.4.51 and earlier.",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2021-44790",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP Server 2.4.52 and earlier fails to close inbound connection when errors are encountered discarding the request body, exposing the server to HTTP Request Smuggling",
        //       "vulExist": "存在",
        //       "vulType": "未知类型",
        //       "vuln_id": "CVE-2022-22720",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP Server 2.4.53 and earlier may not send the X-Forwarded-* headers to the origin server based on client side Connection header hop-by-hop mechanism. This may be used to bypass IP based authentication on the origin server/application.",
        //       "vulExist": "存在",
        //       "vulType": "未知类型",
        //       "vuln_id": "CVE-2022-31813",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Out-of-bounds Write vulnerability in mod_sed of Apache HTTP Server allows an attacker to overwrite heap memory with possibly attacker provided data. This issue affects Apache HTTP Server 2.4 version 2.4.52 and prior versions.",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2022-23943",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "In Apache HTTP Server versions 2.4.0 to 2.4.46 a specially crafted SessionHeader sent by an origin server could cause a heap overflow",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2021-26691",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "ap_escape_quotes() may write beyond the end of a buffer when given malicious input. No included modules pass untrusted data to these functions, but third-party / external modules may. This issue affects Apache HTTP Server 2.4.48 and earlier.",
        //       "vulExist": "存在",
        //       "vulType": "Cross-Site Scripting (XSS)",
        //       "vuln_id": "CVE-2021-39275",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "7.500000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP server 2.4.32 to 2.4.44 mod_proxy_uwsgi info disclosure and possible RCE",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2020-11984",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "6.800000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "A crafted request uri-path can cause mod_proxy to forward the request to an origin server choosen by the remote user. This issue affects Apache HTTP Server 2.4.48 and earlier.",
        //       "vulExist": "存在",
        //       "vulType": "未知类型",
        //       "vuln_id": "CVE-2021-40438",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "6.800000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP Server versions 2.4.0 to 2.4.46 A specially crafted Digest nonce can cause a stack overflow in mod_auth_digest. There is no report of this overflow being exploitable, nor the Apache HTTP Server team could create one, though some particular compiler and/or compilation option might make it possible, with limited consequences anyway due to the size (a single byte) and the value (zero byte) of the overflow",
        //       "vulExist": "存在",
        //       "vulType": "Buffer Overflow",
        //       "vuln_id": "CVE-2020-35452",
        //       "vuln_name": ""
        //     },
        //     {
        //       "cvss": "6.400000",
        //       "port_id": 80,
        //       "softwareType": "Web应用",
        //       "summary": "Apache HTTP Server 2.4.53 and earlier may crash or disclose information due to a read beyond bounds in ap_strcmp_match() when provided with an extremely large input buffer. While no code distributed with the server can be coerced into such a call, third-party modules or lua scripts that use ap_strcmp_match() may hypothetically be affected.",
        //       "vulExist": "存在",
        //       "vulType": "Remote Code Execution (RCE)",
        //       "vuln_id": "CVE-2022-28615",
        //       "vuln_name": ""
        //     }
        //   ]
        // }
      ],
      vulTypes: [
        "Buffer Overflow", "File Upload Vulnerability", "Code Injection",
        "SQL Injection", "Cross-Site Scripting (XSS)", "Privilege Escalation",
        "Denial of Service (DoS)", "Authentication Bypass", "Path Traversal",
        "Information Disclosure", "Cross-Site Request Forgery (CSRF)",
        "XML External Entity (XXE)", "Remote Code Execution (RCE)",
        "Session Hijacking", "Unauthorized Access"
      ]
    }
  },
  computed: {
    // 原有的计算属性保持不变
    currentAsset() {
      return this.assets.find(asset => asset.ip === this.currentIp);
    },
    groupedPortVulnerabilities() {
      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {
        return {};
      }
      return this.currentAsset.port_vulnerabilities.reduce((groups, vuln) => {
        const type = vuln.softwareType || '未分类';
        if (!groups[type]) {
          groups[type] = [];
        }
        groups[type].push(vuln);
        return groups;
      }, {});
    },
    vulnerabilityTypeStats() {
      const stats = {
        '操作系统': 0,
        'Web应用': 0,
        '系统工具': 0,
        '中间件': 0,
        '未知类型': 0
      };

      if (this.currentAsset?.host_vulnerabilities) {
        this.currentAsset.host_vulnerabilities.forEach(vuln => {
          const type = vuln.softwareType || '未知类型';
          if (Object.hasOwn(stats, type)) {
            stats[type]++;
          } else {
            stats['未知类型']++;
          }
        });
      }

      if (this.currentAsset?.port_vulnerabilities) {
        this.currentAsset.port_vulnerabilities.forEach(vuln => {
          const type = vuln.softwareType || '未知类型';
          if (Object.hasOwn(stats, type)) {
            stats[type]++;
          } else {
            stats['未知类型']++;
          }
        });
      }

      return stats;
    },
    // 新增：按漏洞类型统计
    vulTypeStats() {
      const stats = {};

      // 初始化所有漏洞类型的计数为0
      this.vulTypes.forEach(type => {
        stats[type] = 0;
      });

      // 统计主机漏洞
      if (this.currentAsset?.host_vulnerabilities) {
        this.currentAsset.host_vulnerabilities.forEach(vuln => {
          if (vuln.vulType) {
            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;
          }
        });
      }

      // 统计端口漏洞
      if (this.currentAsset?.port_vulnerabilities) {
        this.currentAsset.port_vulnerabilities.forEach(vuln => {
          if (vuln.vulType) {
            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;
          }
        });
      }

      // 只返回数量大于0的类型
      return Object.fromEntries(
          Object.entries(stats).filter(([, count]) => count > 0)
      );
    },
    // 新增：按漏洞类型分组的所有漏洞
    groupedVulTypeVulnerabilities() {
      const groups = {};

      // 合并主机漏洞和端口漏洞
      const allVulnerabilities = [
        ...(this.currentAsset?.host_vulnerabilities || []),
        ...(this.currentAsset?.port_vulnerabilities || [])
      ];

      // 按漏洞类型分组
      allVulnerabilities.forEach(vuln => {
        const type = vuln.vulType || '未分类';
        if (!groups[type]) {
          groups[type] = [];
        }
        groups[type].push(vuln);
      });

      return groups;
    }
  },
  methods: {
    getResults() {
      fetch('/api/getAllAssetsVulnData')
          .then(response => response.json())
          .then(data => {
            this.assets = data;
          })
          .catch(error => console.error('Error:', error));
    },
    handleSelect(ip) {
      this.currentIp = ip;
      this.displayType = 'assetType';
      // 检查图表实例是否存在
      if (!this.pieChart || !this.pieChart.isDisposed()) {
        this.initCharts();  // 不存在或已销毁:初始化
      } else {
        this.updateCharts(); // 否则直接更新数据
      }
      // this.updateCharts();
      // this.initCharts();
      // 使用 nextTick 确保 DOM 更新后再初始化图表
      // this.$nextTick(() => {
      //   this.initCharts();  // 改用 initCharts 而不是 updateCharts
      // });
    },
    // handleSelect(ip) {
    //   this.currentIp = ip;
    //   this.displayType ='assetType';
    //   this.updateCharts();
    // },
    getCvssType(score) {
      score = parseFloat(score);
      if (score >= 7.0) return 'danger';
      if (score >= 4.0) return 'warning';
      if (score >= 0.0) return 'success';
      return 'info';
    },
    getRiskLevel(score) {
      score = parseFloat(score);
      if (score >= 7.0) return '高风险';
      if (score >= 4.0) return '中风险';
      if (score >= 0.0) return '低风险';
      return '信息';
    },
    async initCharts() {
      await this.$nextTick();

      // 初始化资产类型饼图
      if (this.$refs.pieChart) {
        if (this.pieChart) {
          this.pieChart.dispose();
        }
        this.pieChart = echarts.init(this.$refs.pieChart);
      }

      // 初始化漏洞类型饼图
      if (this.$refs.vulTypePieChart) {
        if (this.vulTypePieChart) {
          this.vulTypePieChart.dispose();
        }
        this.vulTypePieChart = echarts.init(this.$refs.vulTypePieChart);
      }

      window.addEventListener('resize', () => {
        this.pieChart && this.pieChart.resize();
        this.vulTypePieChart && this.vulTypePieChart.resize();
      });

      this.updateCharts();
    },
    updateCharts() {
      if (this.displayType === 'assetType') {
        this.updateAssetPieChart();
      } else {
        this.updateVulTypePieChart();
      }
    },
    // 原有的资产类型饼图更新方法
    updateAssetPieChart() {
      if (!this.pieChart) return;

      const stats = this.vulnerabilityTypeStats;
      const data = Object.entries(stats)
          .filter(([, value]) => value > 0)
          .map(([name, value]) => ({
            name,
            value
          }));

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 'right',
          top: 'middle',
          data: data.map(item => item.name)
        },
        series: [{
          name: '资产类型分布',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}个'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: true
          },
          data: data
        }]
      };

      this.pieChart.setOption(option);
    },
    // 新增：漏洞类型饼图更新方法
    updateVulTypePieChart() {
      if (!this.vulTypePieChart) return;

      const stats = this.vulTypeStats;
      const data = Object.entries(stats)
          .map(([name, value]) => ({
            name,
            value
          }));

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 'right',
          top: 'middle',
          data: data.map(item => item.name)
        },
        series: [{
          name: '漏洞类型分布',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}个'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: true
          },
          data: data
        }]
      };

      this.vulTypePieChart.setOption(option);
    }
  },
  watch: {
    currentAsset() {
      this.$nextTick(() => {
        this.updateCharts();
      });
    },
    displayType() {
      this.$nextTick(() => {
        this.initCharts();
      });
    }
  },
  // created() {
  //   this.getResults().then(() => {
  //     if (this.assets.length > 0) {
  //       this.currentIp = this.assets[0].ip;
  //       this.displayType = 'assetType';
  //       this.$nextTick(() => {
  //         this.initCharts();
  //       });
  //     }
  //   });
  // },
  created() {
    this.getResults();
  },
  mounted() {
    if (this.assets.length > 0) {
      this.currentIp = this.assets[0].ip;
    }
    this.initCharts();
  },
  beforeDestroy() {
    if (this.pieChart) {
      this.pieChart.dispose();
      this.pieChart = null;
    }
    if (this.vulTypePieChart) {
      this.vulTypePieChart.dispose();
      this.vulTypePieChart = null;
    }
  }
}
</script>

<style scoped>
.vulnerability-container {
  display: flex;
  height: 100%;
  min-height: 600px;
  background-color: #fff;
}

.ip-list {
  width: 180px;
  border-right: 1px solid #e6e6e6;
  background-color: #f5f7fa;
}

.menu-header {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #e6e6e6;
}

.menu-header .title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.menu-header .asset-count {
  margin-left: 10px;
}

.ip-menu {
  border-right: none;
}

.content-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.empty-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.ip-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.ip-header h2 {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 15px 0;
}

.chart-toggle {
  margin-right: 20px;
  margin-top: 15px;
}

.chart-section {
  margin: 20px 0;
  padding: 0;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.pie-chart {
  width: 100%;
  height: 400px;
}

.asset-info {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.info-item {
  line-height: 28px;
  display: flex;
}

.info-item .label {
  color: #606266;
  width: 80px;
  text-align: right;
  margin-right: 15px;
}

.info-item .value {
  color: #303133;
  flex: 1;
}

.table-section {
  margin-bottom: 30px;
}

.table-section h3 {
  margin: 15px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.el-tag {
  width: 65px;
  text-align: center;
}

.el-table .cell {
  text-align: center;
}

.el-table .el-table__row td:nth-child(4) .cell {
  text-align: left;
}

.vulnerability-group {
  margin-bottom: 20px;
}

.group-title {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
  margin: 10px 0;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
}
</style>

<!--没有分两类的方法-->
<!--<template>-->
<!--  <div class="vulnerability-container">-->
<!--    &lt;!&ndash; 左侧IP列表 &ndash;&gt;-->
<!--    <div class="ip-list">-->
<!--      <div class="menu-header">-->
<!--        <span class="title">资产</span>-->
<!--        <el-badge-->
<!--            :value="assets.length"-->
<!--            class="asset-count"-->
<!--            type="primary">-->
<!--        </el-badge>-->
<!--      </div>-->
<!--      <el-menu-->
<!--          :default-active="currentIp"-->
<!--          class="ip-menu"-->
<!--          @select="handleSelect">-->
<!--        <el-menu-item-->
<!--            v-for="asset in assets"-->
<!--            :key="asset.ip"-->
<!--            :index="asset.ip">-->
<!--          <i class="el-icon-monitor"></i>-->
<!--          <span>{{ asset.ip }}</span>-->
<!--        </el-menu-item>-->
<!--      </el-menu>-->
<!--    </div>-->

<!--    &lt;!&ndash; 右侧详情内容 &ndash;&gt;-->
<!--    <div class="content-area" v-if="currentAsset">-->
<!--      <div class="ip-header">-->
<!--        <h2>资产信息</h2>-->
<!--        <div class="asset-info">-->
<!--          <div class="info-item">-->
<!--            <span class="label">IP地址：</span>-->
<!--            <span class="value">{{ currentAsset.ip }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">操作系统：</span>-->
<!--            <span class="value">{{ currentAsset.os }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">开放端口：</span>-->
<!--            <span class="value">{{ currentAsset.ports }}</span>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->

<!--      <h2>漏洞信息</h2>-->
<!--      &lt;!&ndash; 漏洞类型统计饼图 &ndash;&gt;-->
<!--      <el-card class="chart-section">-->
<!--        <div slot="header" class="clearfix">-->
<!--          <span>漏洞类型分布</span>-->
<!--        </div>-->
<!--        <div class="pie-chart" ref="pieChart" style="width: 100%; height: 300px;"></div>-->
<!--      </el-card>-->

<!--      &lt;!&ndash; 主机漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3><strong>系统漏洞</strong></h3>-->
<!--        <el-table-->
<!--            :data="currentAsset.host_vulnerabilities"-->
<!--            border-->
<!--            stripe-->
<!--            :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--        >-->
<!--          <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--          <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--          <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>-->
<!--          <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--          <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                {{ scope.row.vulExist }}-->
<!--              </el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--      </div>-->

<!--      &lt;!&ndash; 端口漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3><strong>软件资产漏洞</strong></h3>-->
<!--        <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"-->
<!--             :key="type"-->
<!--             class="vulnerability-group">-->
<!--          <h4 class="group-title">{{ type }}</h4>-->
<!--          <el-table-->
<!--              :data="vulnerabilities"-->
<!--              border-->
<!--              stripe-->
<!--              :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--          >-->
<!--            <el-table-column prop="port_id" label="端口" width="70"></el-table-column>-->
<!--            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--            <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>-->
<!--            <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--            <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--            <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                  {{ scope.row.vulExist }}-->
<!--                </el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 未选择IP时的提示 &ndash;&gt;-->
<!--    <div class="empty-content" v-else>-->
<!--      <el-empty description="请选择左侧IP地址查看详情"></el-empty>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import * as echarts from 'echarts';-->

<!--export default {-->
<!--  name: 'VulnerabilityTable',-->
<!--  data() {-->
<!--    return {-->
<!--      currentIp: '',-->
<!--      pieChart: null,-->
<!--      assets: []-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    currentAsset() {-->
<!--      return this.assets.find(asset => asset.ip === this.currentIp);-->
<!--    },-->
<!--    groupedPortVulnerabilities() {-->
<!--      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {-->
<!--        return {};-->
<!--      }-->
<!--      return this.currentAsset.port_vulnerabilities.reduce((groups, vuln) => {-->
<!--        const type = vuln.softwareType || '未分类';-->
<!--        if (!groups[type]) {-->
<!--          groups[type] = [];-->
<!--        }-->
<!--        groups[type].push(vuln);-->
<!--        return groups;-->
<!--      }, {});-->
<!--    },-->
<!--    vulnerabilityTypeStats() {-->
<!--      const stats = {-->
<!--        '操作系统': 0,-->
<!--        'Web应用程序': 0,-->
<!--        '系统工具': 0,-->
<!--        '中间件': 0,-->
<!--        '未知类型': 0-->
<!--      };-->

<!--      // 统计主机漏洞-->
<!--      if (this.currentAsset?.host_vulnerabilities) {-->
<!--        this.currentAsset.host_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      // 统计端口漏洞-->
<!--      if (this.currentAsset?.port_vulnerabilities) {-->
<!--        this.currentAsset.port_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      return stats;-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    getResults() {-->
<!--      fetch('/api/getAllAssetsVulnData')-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.assets = data;-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->
<!--    handleSelect(ip) {-->
<!--      this.currentIp = ip;-->
<!--      this.updatePieChart();-->
<!--    },-->
<!--    getCvssType(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return 'danger';-->
<!--      if (score >= 4.0) return 'warning';-->
<!--      if (score >= 0.0) return 'success';-->
<!--      return 'info';-->
<!--    },-->
<!--    getRiskLevel(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return '高风险';-->
<!--      if (score >= 4.0) return '中风险';-->
<!--      if (score >= 0.0) return '低风险';-->
<!--      return '信息';-->
<!--    },-->
<!--    async initPieChart() {-->
<!--      await this.$nextTick();-->
<!--      if (this.$refs.pieChart) {-->
<!--        if (this.pieChart) {-->
<!--          this.pieChart.dispose();-->
<!--        }-->
<!--        this.pieChart = echarts.init(this.$refs.pieChart);-->
<!--        window.addEventListener('resize', () => {-->
<!--          this.pieChart && this.pieChart.resize();-->
<!--        });-->
<!--        this.updatePieChart();-->
<!--      }-->
<!--    },-->
<!--    updatePieChart() {-->
<!--      if (!this.pieChart) {-->
<!--        this.initPieChart();-->
<!--        return;-->
<!--      }-->

<!--      const stats = this.vulnerabilityTypeStats;-->
<!--      const data = Object.entries(stats)-->
<!--          .filter(([, value]) => value > 0) // 只显示数量大于0的类型-->
<!--          .map(([name, value]) => ({-->
<!--            name,-->
<!--            value-->
<!--          }));-->

<!--      const option = {-->
<!--        tooltip: {-->
<!--          trigger: 'item',-->
<!--          formatter: '{a} <br/>{b}: {c} ({d}%)'-->
<!--        },-->
<!--        legend: {-->
<!--          orient: 'vertical',-->
<!--          right: 'right',-->
<!--          top: 'middle',-->
<!--          data: data.map(item => item.name)-->
<!--        },-->
<!--        series: [-->
<!--          {-->
<!--            name: '漏洞类型分布',-->
<!--            type: 'pie',-->
<!--            radius: ['40%', '70%'],-->
<!--            center: ['40%', '50%'],-->
<!--            avoidLabelOverlap: false,-->
<!--            itemStyle: {-->
<!--              borderRadius: 10,-->
<!--              borderColor: '#fff',-->
<!--              borderWidth: 2-->
<!--            },-->
<!--            label: {-->
<!--              show: true,-->
<!--              formatter: '{b}: {c}个'-->
<!--            },-->
<!--            emphasis: {-->
<!--              label: {-->
<!--                show: true,-->
<!--                fontSize: '18',-->
<!--                fontWeight: 'bold'-->
<!--              }-->
<!--            },-->
<!--            labelLine: {-->
<!--              show: true-->
<!--            },-->
<!--            data: data-->
<!--          }-->
<!--        ]-->
<!--      };-->

<!--      this.pieChart.setOption(option);-->
<!--    }-->
<!--  },-->
<!--  created() {-->
<!--    this.getResults();-->
<!--  },-->
<!--  mounted() {-->
<!--    // 默认选中第一个IP-->
<!--    if (this.assets.length > 0) {-->
<!--      this.currentIp = this.assets[0].ip;-->
<!--    }-->
<!--    this.$nextTick(() => {-->
<!--      this.initPieChart();-->
<!--    });-->
<!--  },-->
<!--  beforeDestroy() {-->
<!--    if (this.pieChart) {-->
<!--      this.pieChart.dispose();-->
<!--      this.pieChart = null;-->
<!--    }-->
<!--  },-->
<!--  watch: {-->
<!--    currentAsset() {-->
<!--      this.$nextTick(() => {-->
<!--        this.updatePieChart();-->
<!--      });-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.vulnerability-container {-->
<!--  display: flex;-->
<!--  height: 100%;-->
<!--  min-height: 600px;-->
<!--  background-color: #fff;-->
<!--}-->

<!--.ip-list {-->
<!--  width: 250px;-->
<!--  border-right: 1px solid #e6e6e6;-->
<!--  background-color: #f5f7fa;-->
<!--}-->

<!--.menu-header {-->
<!--  height: 50px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding: 0 20px;-->
<!--  border-bottom: 1px solid #e6e6e6;-->
<!--}-->

<!--.menu-header .title {-->
<!--  font-size: 16px;-->
<!--  font-weight: 600;-->
<!--  color: #303133;-->
<!--}-->

<!--.menu-header .asset-count {-->
<!--  margin-left: 10px;-->
<!--}-->

<!--.ip-menu {-->
<!--  border-right: none;-->
<!--}-->

<!--.content-area {-->
<!--  flex: 1;-->
<!--  padding: 20px;-->
<!--  overflow-y: auto;-->
<!--}-->

<!--.empty-content {-->
<!--  flex: 1;-->
<!--  display: flex;-->
<!--  justify-content: center;-->
<!--  align-items: center;-->
<!--}-->

<!--.ip-header {-->
<!--  margin-bottom: 20px;-->
<!--  padding-bottom: 10px;-->
<!--  border-bottom: 1px solid #ebeef5;-->
<!--}-->

<!--.ip-header h2 {-->
<!--  color: #303133;-->
<!--  font-size: 18px;-->
<!--  font-weight: 600;-->
<!--  margin: 0 0 15px 0;-->
<!--}-->

<!--.asset-info {-->
<!--  padding: 15px;-->
<!--  background-color: #f5f7fa;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.info-item {-->
<!--  line-height: 28px;-->
<!--  display: flex;-->
<!--}-->

<!--.info-item .label {-->
<!--  color: #606266;-->
<!--  width: 80px;-->
<!--  text-align: right;-->
<!--  margin-right: 15px;-->
<!--}-->

<!--.info-item .value {-->
<!--  color: #303133;-->
<!--  flex: 1;-->
<!--}-->

<!--.table-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.table-section h3 {-->
<!--  margin: 15px 0;-->
<!--  color: #303133;-->
<!--  font-size: 16px;-->
<!--  font-weight: 500;-->
<!--}-->

<!--.el-tag {-->
<!--  width: 65px;-->
<!--  text-align: center;-->
<!--}-->

<!--/* 表格内的标签居中显示 */-->
<!--.el-table .cell {-->
<!--  text-align: center;-->
<!--}-->

<!--/* 确保描述列左对齐 */-->
<!--.el-table .el-table__row td:nth-child(4) .cell {-->
<!--  text-align: left;-->
<!--}-->

<!--.vulnerability-group {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.group-title {-->
<!--  color: #606266;-->
<!--  font-size: 14px;-->
<!--  font-weight: 500;-->
<!--  margin: 10px 0;-->
<!--  padding-left: 10px;-->
<!--  border-left: 3px solid #409EFF;-->
<!--}-->

<!--/* 新增的饼图相关样式 */-->
<!--.chart-section {-->
<!--  margin: 20px 0;-->
<!--  padding: 0px;-->
<!--  background-color: #fff;-->
<!--  border-radius: 4px;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);-->
<!--}-->

<!--.chart-section h3 {-->
<!--  margin-bottom: 20px;-->
<!--  color: #303133;-->
<!--}-->

<!--.pie-chart {-->
<!--  width: 100%;-->
<!--  height: 400px;-->
<!--}-->
<!--</style>-->


<!--没有饼状图的代码 -->
<!--<template>-->
<!--  <div class="vulnerability-container">-->
<!--    &lt;!&ndash; 左侧IP列表 &ndash;&gt;-->
<!--    <div class="ip-list">-->
<!--      <div class="menu-header">-->
<!--        <span class="title">资产</span>-->
<!--        <el-badge-->
<!--            :value="assets.length"-->
<!--            class="asset-count"-->
<!--            type="primary">-->
<!--        </el-badge>-->
<!--      </div>-->
<!--      <el-menu-->
<!--          :default-active="currentIp"-->
<!--          class="ip-menu"-->
<!--          @select="handleSelect">-->
<!--        <el-menu-item-->
<!--            v-for="asset in assets"-->
<!--            :key="asset.ip"-->
<!--            :index="asset.ip">-->
<!--          <i class="el-icon-monitor"></i>-->
<!--          <span>{{ asset.ip }}</span>-->
<!--        </el-menu-item>-->
<!--      </el-menu>-->
<!--    </div>-->

<!--    &lt;!&ndash; 右侧详情内容 &ndash;&gt;-->
<!--    <div class="content-area" v-if="currentAsset">-->
<!--      <div class="ip-header">-->
<!--        <h2>资产信息</h2>-->
<!--        <div class="asset-info">-->
<!--          <div class="info-item">-->
<!--            <span class="label">IP地址：</span>-->
<!--            <span class="value">{{ currentAsset.ip }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">操作系统：</span>-->
<!--            <span class="value">{{ currentAsset.os }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">开放端口：</span>-->
<!--            <span class="value">{{ currentAsset.ports }}</span>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->

<!--      &lt;!&ndash; 主机漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3>主机漏洞</h3>-->
<!--        <el-table-->
<!--            :data="currentAsset.host_vulnerabilities"-->
<!--            border-->
<!--            stripe-->
<!--            :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--        >-->
<!--          <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--          <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--          <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--          <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                {{ scope.row.vulExist }}-->
<!--              </el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--      </div>-->

<!--      &lt;!&ndash; 端口漏洞表格 &ndash;&gt;-->
<!--      &lt;!&ndash; 将原来的端口漏洞表格部分替换成以下代码 &ndash;&gt;-->
<!--      &lt;!&ndash; 端口漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3>端口漏洞</h3>-->
<!--        <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"-->
<!--             :key="type"-->
<!--             class="vulnerability-group">-->
<!--          <h4 class="group-title">{{ type }}</h4>-->
<!--          <el-table-->
<!--              :data="vulnerabilities"-->
<!--              border-->
<!--              stripe-->
<!--              :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--          >-->
<!--            <el-table-column prop="port_id" label="端口" width="100"></el-table-column>-->
<!--            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--            <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--            <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--            <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                  {{ scope.row.vulExist }}-->
<!--                </el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 未选择IP时的提示 &ndash;&gt;-->
<!--    <div class="empty-content" v-else>-->
<!--      <el-empty description="请选择左侧IP地址查看详情"></el-empty>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  name: 'VulnerabilityTable',-->
<!--  data() {-->
<!--    return {-->
<!--      currentIp: '',-->
<!--      assets: [-->
<!--        {-->
<!--          "host_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "9.800000",-->
<!--              "softwareType": "操作系统",-->
<!--              "summary": "MongoDB 4.2.7存在权限提升漏洞，攻击者可以通过特定的构造命令绕过认证并获得管理员权限。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2020-12345",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "7.500000",-->
<!--              "softwareType": "操作系统",-->
<!--              "summary": "Windows SMBv3协议存在内存损坏漏洞，允许远程代码执行。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2021-34527",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ],-->
<!--          "ip": "10.8.250.77",-->
<!--          "port_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 8080,-->
<!--              "softwareType": "Web应用程序",-->
<!--              "summary": "Apache Struts 2.3.34 存在远程代码执行漏洞，攻击者可通过恶意请求触发。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-11776",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 804,-->
<!--              "softwareType": "Web应用程序",-->
<!--              "summary": "描述。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-12436",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 808,-->
<!--              "softwareType": "系统工具",-->
<!--              "summary": "Apache Struts 2.3.34 存在远程代码执行漏洞，攻击者可通过恶意请求触发。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-1236",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 80,-->
<!--              "softwareType": "未知类型",-->
<!--              "summary": "描述。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-132",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ]-->
<!--        },-->
<!--        {-->
<!--          "host_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "6.500000",-->
<!--              "softwareType": "操作系统",-->
<!--              "summary": "VMware ESXi 7.0中的特定模块存在拒绝服务漏洞，可能导致虚拟机异常终止。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2022-12345",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ],-->
<!--          "ip": "192.168.1.100",-->
<!--          "port_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "10.000000",-->
<!--              "port_id": 443,-->
<!--              "softwareType": "Web服务器",-->
<!--              "summary": "nginx 1.18.0 存在缓冲区溢出漏洞，允许远程攻击者执行任意代码。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2021-23017",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ]-->
<!--        }-->
<!--      ]-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    currentAsset() {-->
<!--      return this.assets.find(asset => asset.ip === this.currentIp);-->
<!--    },-->
<!--    groupedPortVulnerabilities() {-->
<!--      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {-->
<!--        return {};-->
<!--      }-->
<!--      return this.currentAsset.port_vulnerabilities.reduce((groups, vuln) => {-->
<!--        const type = vuln.softwareType || '未分类';-->
<!--        if (!groups[type]) {-->
<!--          groups[type] = [];-->
<!--        }-->
<!--        groups[type].push(vuln);-->
<!--        return groups;-->
<!--      }, {});-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    getResults() {-->
<!--      fetch('/api/getAllAssetsVulnData')-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.assets = data;-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->
<!--    handleSelect(ip) {-->
<!--      this.currentIp = ip;-->
<!--    },-->
<!--    getCvssType(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return 'danger';-->
<!--      if (score >= 4.0) return 'warning';-->
<!--      if (score >= 0.0) return 'success';-->
<!--      return 'info';-->
<!--    },-->
<!--    getRiskLevel(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return '高风险';-->
<!--      if (score >= 4.0) return '中风险';-->
<!--      if (score >= 0.0) return '低风险';-->
<!--      return '信息';-->
<!--    }-->
<!--  },-->
<!--  created() {-->
<!--    this.getResults();-->
<!--  },-->
<!--  mounted() {-->
<!--    // 默认选中第一个IP-->
<!--    if (this.assets.length > 0) {-->
<!--      this.currentIp = this.assets[0].ip;-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.vulnerability-container {-->
<!--  display: flex;-->
<!--  height: 100%;-->
<!--  min-height: 600px;-->
<!--  background-color: #fff;-->
<!--}-->

<!--.ip-list {-->
<!--  width: 250px;-->
<!--  border-right: 1px solid #e6e6e6;-->
<!--  background-color: #f5f7fa;-->
<!--}-->

<!--.menu-header {-->
<!--  height: 50px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding: 0 20px;-->
<!--  border-bottom: 1px solid #e6e6e6;-->
<!--}-->

<!--.menu-header .title {-->
<!--  font-size: 16px;-->
<!--  font-weight: 600;-->
<!--  color: #303133;-->
<!--}-->

<!--.menu-header .asset-count {-->
<!--  margin-left: 10px;-->
<!--}-->

<!--.ip-menu {-->
<!--  border-right: none;-->
<!--}-->

<!--.content-area {-->
<!--  flex: 1;-->
<!--  padding: 20px;-->
<!--  overflow-y: auto;-->
<!--}-->

<!--.empty-content {-->
<!--  flex: 1;-->
<!--  display: flex;-->
<!--  justify-content: center;-->
<!--  align-items: center;-->
<!--}-->

<!--.ip-header {-->
<!--  margin-bottom: 20px;-->
<!--  padding-bottom: 10px;-->
<!--  border-bottom: 1px solid #ebeef5;-->
<!--}-->

<!--.ip-header h2 {-->
<!--  color: #303133;-->
<!--  font-size: 18px;-->
<!--  font-weight: 600;-->
<!--  margin: 0 0 15px 0;-->
<!--}-->

<!--.asset-info {-->
<!--  padding: 15px;-->
<!--  background-color: #f5f7fa;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.info-item {-->
<!--  line-height: 28px;-->
<!--  display: flex;-->
<!--}-->

<!--.info-item .label {-->
<!--  color: #606266;-->
<!--  width: 80px;-->
<!--  text-align: right;-->
<!--  margin-right: 15px;-->
<!--}-->

<!--.info-item .value {-->
<!--  color: #303133;-->
<!--  flex: 1;-->
<!--}-->

<!--.table-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.table-section h3 {-->
<!--  margin: 15px 0;-->
<!--  color: #303133;-->
<!--  font-size: 16px;-->
<!--  font-weight: 500;-->
<!--}-->

<!--.el-tag {-->
<!--  width: 65px;-->
<!--  text-align: center;-->
<!--}-->

<!--/* 表格内的标签居中显示 */-->
<!--.el-table .cell {-->
<!--  text-align: center;-->
<!--}-->

<!--/* 确保描述列左对齐 */-->
<!--.el-table .el-table__row td:nth-child(4) .cell {-->
<!--  text-align: left;-->
<!--}-->

<!--.vulnerability-group {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.group-title {-->
<!--  color: #606266;-->
<!--  font-size: 14px;-->
<!--  font-weight: 500;-->
<!--  margin: 10px 0;-->
<!--  padding-left: 10px;-->
<!--  border-left: 3px solid #409EFF;-->
<!--}-->
<!--</style>-->

