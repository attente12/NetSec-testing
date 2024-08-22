<template>
    <div>
        <el-row :gutter="20">
            <el-col :span="8" v-for="(item, index) in paginatedData" :key="index">
                <el-card>
                    <h4>{{ item.title }}</h4>
                    <div>{{ item.summary }}</div>
                    <el-tag v-for="tag in item.tags" :key="tag">{{ tag }}</el-tag>
                    <!-- More content here -->
                </el-card>
            </el-col>
        </el-row>
        <el-pagination
                layout="prev, pager, next"
                :total="data.length"
                :page-size="pageSize"
                @current-change="handlePageChange">
        </el-pagination>
    </div>
</template>

<script>
    export default {
        name:'pageOne',
        data() {
            return {
                // Mock data for the vulnerabilities cards
                data: [
                    {
                        id: 1,
                        title: 'Wordpress插件Elementor XSS漏洞 (CVE-xxxx-xxxx)',
                        summary: 'Elementor存在一个XSS漏洞，更新插件版本...',
                        tags: ['Elementor', 'XSS'],
                        severity: 'High',
                        dateReported: '2022-01-15'
                    },
                    {
                        id: 2,
                        title: 'Webmin远程命令执行漏洞(CVE-2019-15107)',
                        summary: 'Webmin是一个用于管理类Unix系统的管理配置工具，具有Web页面。在其找回密码页面中，存在一处无需权限的命令注入漏洞，通过这个漏洞攻击者即可以执行任意系统命令。',
                        tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                        severity: 'Critical',
                        dateReported: '2022-02-20'
                    },
                    {
                        id: 3,
                        title: 'Zabbix SAML身份验证绕过漏洞 (CVE-zzzz-zzzz)',
                        summary: 'Zabbix存在一个影响SAML身份验证的漏洞...',
                        tags: ['Zabbix', 'PATH_DISCLOSURE'],
                        severity: 'Medium',
                        dateReported: '2022-03-10'
                    },
                    {
                        id: 4,
                        title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                        summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                        tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                        severity: 'Critical',
                        dateReported: '2022-02-20'
                    },
                    {
                        id: 5,
                        title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                        summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                        tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                        severity: 'Critical',
                        dateReported: '2022-02-20'
                    },
                    {
                        id: 6,
                        title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                        summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                        tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                        severity: 'Critical',
                        dateReported: '2022-02-20'
                    },
                    {
                        id: 7,
                        title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                        summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                        tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                        severity: 'Critical',
                        dateReported: '2022-02-20'
                    },
                    {
                        id: 8,
                        title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                        summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                        tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                        severity: 'Critical',
                        dateReported: '2022-02-20'
                    },
                    // Add more objects for each card you want to display
                ],
                currentPage: 1,
                pageSize: 6 // Number of cards per page
            };
        },
        computed: {
            paginatedData() {
                let start = (this.currentPage - 1) * this.pageSize;
                let end = start + this.pageSize;
                return this.data.slice(start, end);
            }
        },
        methods: {
            handlePageChange(newPage) {
                this.currentPage = newPage;
            }
        }
    };
</script>

<style scoped>
    .el-row {
        display: flex;
        flex-wrap: wrap;
    }
    .el-col {
        display: flex;
        margin-bottom: 20px;
    }
    .el-card {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    .el-card .el-card__body {
        flex-grow: 1; /* This makes the body of the card fill the space */
    }
</style>



<!--<template>-->
<!--    <div id="content">-->
<!--        <div style="text-align: center;"><h1>{{ Name }}_Linux安全策略核查</h1></div>-->

<!--        <h2 id="info">服务器基本信息</h2>-->
<!--        <table>-->
<!--            <thead>-->
<!--            <tr>-->
<!--                <th>主机名</th>-->
<!--                <th>操作系统位数</th>-->
<!--                <th>CPU型号</th>-->
<!--                <th>CPU个数</th>-->
<!--                <th>CPU核数</th>-->
<!--                <th>共计内存/G</th>-->
<!--                <th>硬件型号</th>-->
<!--                <th>系统版本</th>-->
<!--                <th>联网检测</th>-->
<!--            </tr>-->
<!--            </thead>-->
<!--            <tbody>-->
<!--            <tr>-->
<!--                <td>{{ Info.HostName }}</td>-->
<!--                <td>{{ Info.Arch }}</td>-->
<!--                <td>{{ Info.Cpu }}</td>-->
<!--                <td>{{ Info.CpuPhysical }}</td>-->
<!--                <td>{{ Info.CpuCore }}</td>-->
<!--                <td>{{ Info.Free }}</td>-->
<!--                <td>{{ Info.ProductName }}</td>-->
<!--                <td>{{ Info.Version }}</td>-->
<!--                <td>{{ Info.Ping }}</td>-->
<!--            </tr>-->
<!--            </tbody>-->
<!--        </table>-->

<!--        <h2 id="userinfo">用户信息</h2>-->
<!--        <table>-->
<!--            <thead>-->
<!--            <tr>-->
<!--                <th>用户</th>-->
<!--                <th><a href="#" @click.prevent="showPasswdStatus()">密码状态</a></th>-->
<!--                <th>状态描述</th>-->
<!--                <th>UID</th>-->
<!--                <th>GID</th>-->
<!--                <th>主目录</th>-->
<!--                <th>Bash</th>-->
<!--                <th>可登录</th>-->
<!--                <th>上次修改密码时间</th>-->
<!--                <th><a href="#" @click.prevent="showPasswordExpiryNote()">密码过期的日期</a></th>-->
<!--                <th><a href="#" @click.prevent="showAccountExpiryNote()">账号过期的日期</a></th>-->
<!--                <th>密码最大使用天数</th>-->
<!--            </tr>-->
<!--            </thead>-->
<!--            <tbody>-->
<!--            <tr v-for="user in users" :key="user.uid">-->
<!--                <td>{{ user.name }}</td>-->
<!--                <td :style="{ color: user.passwd === 'PS' ? 'rgb(32, 199, 29)' : 'rgb(255, 0, 0)' }">{{ user.passwd }}</td>-->
<!--                <td>{{ user.remark }}</td>-->
<!--                <td>{{ user.uid }}</td>-->
<!--                <td>{{ user.gid }}</td>-->
<!--                <td>{{ user.pwd }}</td>-->
<!--                <td>{{ user.bash }}</td>-->
<!--                <td :style="{ color: user.login ? 'rgb(32, 199, 29)' : 'rgb(255, 0, 0)' }">{{ user.login ? '是' : '否' }}</td>-->
<!--                <td>{{ user.lastPasswd }}</td>-->
<!--                <td>{{ user.passwdExpired }}</td>-->
<!--                <td>{{ user.userExpired }}</td>-->
<!--                <td>{{ user.maxPasswd }}</td>-->
<!--            </tr>-->
<!--            </tbody>-->
<!--        </table>-->
<!--    </div>-->
<!--</template>-->

<!--<script>-->
<!--    export default {-->
<!--        name: "pagesOne",-->
<!--        data() {-->
<!--            return {-->
<!--                // 在这里定义 Name 和 Info 数据-->
<!--                Name: "Your Name",-->
<!--                Info: {-->
<!--                    HostName: "Your Host Name",-->
<!--                    Arch: "Your Arch",-->
<!--                    Cpu: "Your CPU Model",-->
<!--                    CpuPhysical: "Number of Physical CPUs",-->
<!--                    CpuCore: "Number of CPU Cores",-->
<!--                    Free: "Total Memory",-->
<!--                    ProductName: "Your Hardware Model",-->
<!--                    Version: "Your System Version",-->
<!--                    Ping: "Network Connection Status"-->
<!--                },-->
<!--                users:[-->
<!--                    {-->
<!--                        name:"user",-->
<!--                        passwd:"x",-->
<!--                        remark:"root",-->
<!--                        uid:0,-->
<!--                        gid:0,-->
<!--                        pwd:"/root",-->
<!--                        bash:"/bin/bash",-->
<!--                        login:1,-->
<!--                        lastPasswd:"never",-->
<!--                        passwdExpired:"never",-->
<!--                        userExpired:"never",-->
<!--                        maxPasswd:"99999"-->
<!--                    },-->
<!--                    {-->
<!--                        name:"user2",-->
<!--                        passwd:"x",-->
<!--                        remark:"root2",-->
<!--                        uid:0,-->
<!--                        gid:0,-->
<!--                        pwd:"/root2",-->
<!--                        bash:"/bin/bash",-->
<!--                        login:0,-->
<!--                        lastPasswd:"never",-->
<!--                        passwdExpired:"never",-->
<!--                        userExpired:"never",-->
<!--                        maxPasswd:"99999"-->
<!--                    },-->
<!--                    {-->
<!--                        name:"user3",-->
<!--                        passwd:"x",-->
<!--                        remark:"root2",-->
<!--                        uid:0,-->
<!--                        gid:0,-->
<!--                        pwd:"/root2",-->
<!--                        bash:"/bin/bash",-->
<!--                        login:0,-->
<!--                        lastPasswd:"never",-->
<!--                        passwdExpired:"never",-->
<!--                        userExpired:"never",-->
<!--                        maxPasswd:"99999"-->
<!--                    }-->
<!--                ]-->
<!--            }-->
<!--        }-->
<!--    }-->
<!--</script>-->

<!--<style scoped>-->

<!--</style>-->
