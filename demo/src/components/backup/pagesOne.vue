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
