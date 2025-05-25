<template>
    <div class="container">
        <el-card class="box-card">
            <el-row>
                <el-col :span="24">
                    <div class="header">
                        <h1>{{ flag ? 'Windows' : 'Linux' }}基线检测</h1>
                        <p class="subtitle">安全基线检测工具</p>
                    </div>
                </el-col>
            </el-row>

            <el-form @submit.prevent="submitForm" :model="formData" :rules="rules" ref="form" label-width="120px"
                class="login-form">
                <el-form-item label="IP 地址" prop="ip" v-show="!flag">
                    <el-select v-model="formData.ip" placeholder="请选择或输入服务器IP地址" filterable allow-create
                        default-first-option style="width: 100%">
                        <el-option v-for="ip in aliveHosts" :key="ip" :label="ip" :value="ip">
                        </el-option>
                    </el-select>

                    <!-- 新增查看临时结果链接 -->
                    <div class="temp-check-link">
                        <el-link type="primary" :underline="false" @click="handleViewTempResult" icon="el-icon-view">
                            查看该IP最近一次检查结果
                        </el-link>
                    </div>

                </el-form-item>
                <el-form-item v-show="!flag" label="root密码：" prop="pd">
                    <el-input v-model="formData.pd" type="password" placeholder="请输入root密码" prefix-icon="el-icon-lock"
                        show-password>
                    </el-input>
                </el-form-item>

                <!-- 以上为Linux检测登录项 -->
                <!-- 以下为Windows检测登录项 -->

                <el-form-item label="IP 地址：" v-show="flag">
                    <el-input v-model="ip" placeholder="请输入服务器IP地址" prefix-icon="el-icon-monitor">
                    </el-input>
                </el-form-item>
                <el-form-item v-show="flag" label="管理员账户名：">
                    <el-input v-model="adminName" placeholder="请输入管理员账户名" prefix-icon="el-icon-monitor">
                    </el-input>
                </el-form-item>
                <el-form-item v-show="flag" label="管理员密码：">
                    <el-input v-model="pd" type="password" show-password placeholder="请输入密码" prefix-icon="el-icon-lock">
                    </el-input>
                </el-form-item>
                <p class="versionSelector" v-if="isChecked">
                    <span>您的Windows版本为： <span class="winVerText">{{ value }}</span></span>
                </p>

                <el-form-item>

                    <div class="control-bar">
                        <el-checkbox v-if="flag" v-model="isSelectAll" @change="handleCheckAllChangeW"
                            style="margin-right: 15px;">
                            全选检测项目
                        </el-checkbox>
                        <el-checkbox v-else v-model="checkAll" @change="handleCheckAllChange"
                            style="margin-right: 15px;">
                            全选检测项目
                        </el-checkbox>
                        <el-button v-show="!flag" type="primary" @click="LinuxSubmitForm" icon="el-icon-video-play"
                            :loading="loading" :disabled="selectedItems.length === 0">
                            开始检测
                        </el-button>
                        <el-button v-show="flag" type="primary" class="versionSelectBT" @click="WindowsSubmitForm"
                            :disabled="ip && pd && adminName ? null : true">开始检测</el-button>
                    </div>

                    <el-button type="primary" @click="turnFlag">切换到{{ flag ? 'Linux' : 'Windows' }}</el-button>
                </el-form-item>
            </el-form>

        </el-card>

        <el-card class="box-card check-items">
            <div slot="header" class="card-header">

                <span>检测项目选择</span>
                <el-button type="primary" :disabled="isChecked ? null : true"
                    @click="isSelectAll ? checkAll : batchExecuteW" icon="el-icon-video-play" :loading="batchLoading">
                    批量执行
                </el-button>
            </div>

            <div v-if="versionFlag" class="checboxGroupContainer">

                <el-checkbox-group v-model="selectedItemsW" class="checboxGroup" @change="handleCheckedItemsChange">
                    <el-checkbox v-for="item in checkItemsW_" :key="item.id" :label="item.name" />
                </el-checkbox-group>

            </div>

            <el-checkbox-group v-model="selectedItems" v-if="!flag">
                <el-row :gutter="20">
                    <el-col :span="8" v-for="item in checkItems" :key="item.id">
                        <el-checkbox :label="item.id">
                            <el-tooltip :content="item.name" placement="top">
                                <span class="checkbox-label">{{ item.name }}</span>
                            </el-tooltip>
                        </el-checkbox>
                    </el-col>
                </el-row>
            </el-checkbox-group>

        </el-card>

        <el-dialog title="检测完成" :visible.sync="dialogVisible" width="30%" center>
            <span>检测任务已完成，是否查看结果？</span>
            <span slot="footer" class="dialog-footer">
                <el-button @click="dialogVisible = false">取 消</el-button>
                <el-button type="primary" @click="viewResult">查看结果</el-button>
            </span>
        </el-dialog>

        <!-- Popup遮罩层 -->
        <div v-if="showPopup" class="overlay" @click="showPopup = false"></div>
        <div v-if="showPopup" class="popup">
            <Popup :dataFromParent="checkResult"></Popup>
        </div>
    </div>
</template>

<script>
import { Message } from "element-ui"
import Popup from "../components/popup.vue";

export default {
    name: "home",
    components: {
        Popup
    },
    data() {
        return {
            formData: {
                ip: '',
                pd: ''
            },
            aliveHosts: [], // 存储活跃IP列表
            dialogVisible: false,
            loading: false,
            rules: {
                ip: [
                    { required: true, message: '请输入IP地址', trigger: 'blur' },
                    { pattern: /^(\d{1,3}\.){3}\d{1,3}$/, message: 'IP地址格式不正确', trigger: 'blur' }
                ],
                pd: [
                    { required: true, message: '请输入密码', trigger: 'blur' }
                ]
            },
            flag: false,
            versionFlag: false,
            ip: '',
            adminName: '',
            pd: '',
            selectedItems: [],
            selectedItemsW: [],
            progressBarWidth: 0,
            showButton: false,
            checkItems: [
                { id: 1, name: '检查口令生存周期' },
                { id: 2, name: '检查口令最小长度' },
                { id: 3, name: '检查口令过期前警告天数' },
                { id: 4, name: '检查设备密码复杂度策略' },
                { id: 5, name: '检查是否存在空口令账号' },
                { id: 6, name: '检查是否设置除root之外UID为0的用户' },
                { id: 7, name: '检查/etc/csh.cshrc中的用户umask设置' },
                { id: 8, name: '检查/etc/bashrc中的用户umask设置' },
                { id: 9, name: '检查/etc/profile中的用户umask设置' },
                { id: 10, name: '检查/etc/xinetd.conf文件权限' },
                { id: 11, name: '检查/etc/group文件权限' },
                { id: 12, name: '检查/etc/shadow文件权限' },
                { id: 13, name: '检查/etc/services文件权限' },
                { id: 14, name: '检查/etc/security目录权限' },
                { id: 15, name: '检查/etc/passwd文件权限' },
                { id: 16, name: '检查/etc/rc6.d目录权限' },
                { id: 17, name: '检查/etc/rc0.d目录权限' },
                { id: 18, name: '检查/etc/rc1.d目录权限' },
                { id: 19, name: '检查/etc/rc2.d目录权限' },
                { id: 20, name: '检查/etc目录权限' },
                { id: 21, name: '检查/etc/rc4.d目录权限' },
                { id: 22, name: '检查/etc/rc5.d目录权限' },
                { id: 23, name: '检查/etc/rc3.d目录权限' },
                { id: 24, name: '检查/etc/rc.d/init.d目录权限' },
                { id: 25, name: '检查/tmp目录权限' },
                { id: 26, name: '检查/etc/grub.conf文件权限' },
                { id: 27, name: '检查/etc/grub/grub.conf文件权限' },
                { id: 28, name: '检查/etc/lilo.conf文件权限' },
                { id: 29, name: '检查/etc/passwd的文件属性' },
                { id: 30, name: '检查/etc/shadow的文件属性' },
                { id: 31, name: '检查/etc/group的文件属性' },
                { id: 32, name: '检查/etc/gshadow的文件属性' },
                { id: 33, name: '检查用户目录缺省访问权限设置' },
                { id: 34, name: '检查是否设置ssh登录前警告Banner' },
                { id: 35, name: '检查e-ng是否配置远程日志功能' },
                { id: 36, name: '检查rsyslog是否配置远程日志功能' },
                { id: 37, name: '检查syslog是否配置远程日志功能' },
                { id: 38, name: '检查syslog_ng是否配置安全事件日志' },
                { id: 39, name: '检查rsyslog是否配置安全事件日志' },
                { id: 40, name: '检查syslog是否配置安全事件日志' },
                { id: 41, name: '检查/var/log/cron日志文件是否other用户不可写' },
                { id: 42, name: '检查/var/log/secure日志文件是否other用户不可写' },
                { id: 43, name: '检查/var/log/messages日志文件是否other用户不可写' },
                { id: 44, name: '检查/var/log/boot.log日志文件是否other用户不可写' },
                { id: 45, name: '检查/var/log/mail日志文件是否other用户不可写' },
                { id: 46, name: '检查/var/log/spooler日志文件是否other用户不可写' },
                { id: 47, name: '检查/var/log/localmessages日志文件是否other用户不可写' },
                { id: 48, name: '检查/var/log/maillog日志文件是否other用户不可写' },
                { id: 49, name: '是否对登录进行日志记录' },
                { id: 50, name: '检查是否配置su命令使用情况记录' },
                { id: 51, name: '检查系统openssh安全配置' },
                { id: 52, name: '检查SNMP服务是否在运行' },
                { id: 53, name: '检查是否已修改snmp默认团体字' },
                { id: 54, name: '是否配置ssh协议' },
                { id: 55, name: '是否禁用telnet协议' },
                { id: 56, name: '检查是否在运行ftp' },
                { id: 57, name: '检查是否禁止root用户登录ftp' },
                { id: 58, name: '检查是否禁止匿名用户登录FTP' },
                { id: 59, name: '检查是否设置命令行界面超时退出' },
                { id: 60, name: '检查是否设置系统引导管理器密码' },
                { id: 61, name: '检查系统coredump设置' },
                { id: 62, name: '检查历史命令设置' },
                { id: 63, name: '检查是否使用PAM认证模块禁止wheel组之外的用户su为root' },
                { id: 64, name: '检查是否对系统账户进行登录限制' },
                { id: 65, name: '检查密码重复使用次数限制' },
                { id: 66, name: '检查账户认证失败次数限制' },
                { id: 67, name: '检查是否关闭绑定多ip功能' },
                { id: 68, name: '检查是否限制远程登录IP范围' },
                { id: 69, name: '检查别名文件' },
                { id: 70, name: '检查重要文件是否存在suid和sgid权限' },
                { id: 71, name: '检查是否配置定时自动屏幕锁定' },
                { id: 72, name: '检查系统内核参数配置' },
                { id: 73, name: '检查是否按组进行账号管理' },
                { id: 74, name: '检查root用户的path环境变量' },
                { id: 75, name: '检查系统是否禁用ctrl+alt+del组合键' },
                { id: 76, name: '检查是否关闭系统信任机制' },
                { id: 77, name: '检查系统磁盘分区使用率' },
                { id: 78, name: '检查是否删除了潜在危险文件' },
                { id: 79, name: '检查是否配置用户所需最小权限' },
                { id: 80, name: '检查是否关闭数据包转发功能' },
                { id: 81, name: '检查是否使用NTP保持时间同步' },
                { id: 82, name: '检查NFS服务设置' },
                { id: 83, name: '检查是否设置ssh成功登陆后Banner' },
                { id: 84, name: '检查FTP用户上传的文件所具有的权限' },
                { id: 85, name: '检查是否更改默认的ftp登陆警告Banner' },
                { id: 86, name: '检查/usr/bin/目录下可执行文件的拥有者属性' },
                { id: 87, name: '检查telnet Banner设置' },
                { id: 88, name: '检查是否限制FTP用户登录后能访问的目录' },
                { id: 89, name: '检查内核版本是否处于CVE-2021-43267漏洞影响版本' }
            ],
            checkItemsW: [
                { id: 1, name: '检查密码长度最小值' },
                { id: 2, name: '检查是否已启用密码复杂性要求' },
                { id: 3, name: '检查是否已禁用来宾 (Guest) 帐户' },
                { id: 4, name: '检查“强制密码历史”个数' },
                { id: 5, name: '检查已启用的本地用户的个数' },
                { id: 6, name: '检查密码最长使用期限' },
                { id: 7, name: '检查密码最长使用期限是否不为0' },
                { id: 8, name: '检查帐户锁定阈值' },
                { id: 9, name: '检查帐户锁定阈值是否不为0' },
                { id: 10, name: '检查“取得文件或其它对象的所有权”的帐户和组' },
                { id: 11, name: '检查可从远端关闭系统的帐户和组' },
                { id: 12, name: '检查是否已禁止 SAM 帐户的匿名枚举' },
                { id: 13, name: '检查是否已禁止 SAM 帐户和共享的匿名枚举' },
                { id: 14, name: '检查可远程访问的注册表路径' },
                { id: 15, name: '检查可匿名访问的共享' },
                { id: 16, name: '检查可匿名访问的命名管道' },
                { id: 17, name: '检查是否只有授权用户或组通过远程桌面服务连接访问远程设备' },
                { id: 18, name: '检查允许本地登录的用户和组' },
                { id: 19, name: '检查应用程序日志文件达到最大大小时的动作' },
                { id: 20, name: '检查应用程序日志文件最大大小' },
                { id: 21, name: '检查“审核对象访问”级别' },
                { id: 22, name: '检查“审核特权使用”级别' },
                { id: 23, name: '检查“审核进程跟踪”级别' },
                { id: 24, name: '检查“审核登录事件”级别' },
                { id: 25, name: '检查“审核目录服务访问”级别' },
                { id: 26, name: '检查“审核系统事件”级别' },
                { id: 27, name: '检查“审核帐户登录事件”级别' },
                { id: 28, name: '检查“审核策略更改”级别' },
                { id: 29, name: '检查“审核帐户管理”级别' },
                { id: 30, name: '检查 Windows 防火墙状态' },
                { id: 31, name: '检查远程桌面 (RDP) 服务端口' },
                { id: 32, name: '检查源路由配置' },
                { id: 33, name: '检查 TCP 连接请求阈值' },
                { id: 34, name: '检查是否已启用 SYN 攻击保护' },
                { id: 35, name: '检查取消尝试响应 SYN 请求之前要重新传输 SYN-ACK 的次数' },
                { id: 36, name: '检查处于SYN_RCVD状态下的TCP连接阈值' },
                { id: 37, name: '检查处于SYN_RCVD状态下，且至少已经进行了一次重新传输的TCP连接阈值' },
                { id: 38, name: '检查是否已删除SNMP服务的默认public团体' },
                { id: 39, name: '检查是否已启用TCP最大传输单元(MTU)大小自动探测' },
                { id: 40, name: '检查Remote Access Connection Manager服务状态' },
                { id: 41, name: '检查Message Queuing服务状态' },
                { id: 42, name: '检查DHCP Server服务状态' },
                { id: 43, name: '检查DHCP Client服务状态' },
                { id: 44, name: '检查Simple Mail Transport Protocol (SMTP)服务状态' },
                { id: 45, name: '检查Windows Internet Name Service (WINS)服务状态' },
                { id: 46, name: '检查Simple TCP/IP Services服务状态' },
                { id: 47, name: '检查Windows 自动登录设置' },
                { id: 48, name: '检查共享文件夹的共享权限' },
                { id: 49, name: '检查所有磁盘分区的文件系统格式' },
                { id: 50, name: '检查是否已对所有驱动器关闭 Windows 自动播放' },
                { id: 51, name: '检查是否已禁用 Windows 硬盘默认共享' },
                { id: 52, name: '检查服务器在暂停会话前所需的空闲时间量' },
                { id: 53, name: '检查是否正确配置 NTP 时间同步服务器' },
                { id: 54, name: '检查是否正确配置 DNS 服务器' },
                { id: 55, name: '检查是否已开启数据DEP功能' },
                { id: 56, name: '检查是否已开启 UAC 安全提示' }
            ],
            checkItemsW_: [],
            value: '',
            valueTemp: '',
            checkResult: {},
            isChecked: false,
            checkAll: false,//linux全选标记
            isSelectAll: false,//windows全选标记
            showPopup: false
        };
    },
    watch: {
        //用于监听版本信息
        value(newValue, oldValue) {
            if (newValue !== '') {
                console.log(oldValue)

                let idArr = []
                switch (newValue) {
                    case 1:
                        this.checkItemsW_ = this.checkItemsW
                        break;
                    case 2:
                        this.checkItemsW_ = this.checkItemsW
                        break;
                    case 3:
                        idArr = [55, 56]
                        this.checkItemsW_ = this.checkItemsW.filter(item => !idArr.includes(item.id));
                        break;
                    case 4:
                        idArr = [47, 55, 56]
                        this.checkItemsW_ = this.checkItemsW.filter(item => !idArr.includes(item.id));
                        break;
                    case 5:
                        idArr = [17, 31, 47, 55, 56]
                        this.checkItemsW_ = this.checkItemsW.filter(item => !idArr.includes(item.id));
                        break;
                    case 6:
                        this.checkItemsW_ = this.checkItemsW
                        break;
                    case 7:
                        this.checkItemsW_ = this.checkItemsW
                        break;
                    case 8:
                        this.checkItemsW_ = this.checkItemsW
                        break;
                    case 9:
                        idArr = [55, 56]
                        this.checkItemsW_ = this.checkItemsW.filter(item => !idArr.includes(item.id));
                        break;
                    case 10:
                        idArr = [55, 56]
                        this.checkItemsW_ = this.checkItemsW.filter(item => !idArr.includes(item.id));
                        break;
                    case 11:
                        idArr = [47, 55, 56]
                        this.checkItemsW_ = this.checkItemsW.filter(item => !idArr.includes(item.id));
                        break;
                    default:
                        break;
                }

                this.versionFlag = true
                this.isSelectAll = true
                this.handleCheckAllChange(true)
            }
        },
    },
    methods: {
        // 获取活跃IP列表
        fetchAliveHosts() {
            fetch('/api/getAliveHosts')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP status ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    this.aliveHosts = data.alive_hosts;
                })
                .catch(error => {
                    Message.error('获取活跃IP列表失败：' + error.message);
                });
        },
        //切换Windows或Linux方法，同时初始化其他指示值
        turnFlag() {
            this.flag = !this.flag
            this.versionFlag = false
            this.value = ''
            this.pd = ''
            this.ip = ''
            this.adminName = ''
            this.isChecked = false
        },

        WindowsSubmitForm() {
            const payload = {
                hostname: this.adminName,
                ip: this.ip,
                pd: this.pd
            };
            console.log("Submitting form...", payload);

            fetch('/api/win_login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            })
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 500) {
                            // 处理特定的500内部错误
                            alert("请求失败，SSH会话无法启动");
                            return null; // 返回null但不结束Promise链，以防止进一步的.then执行
                        }
                        // 对于除500外的其他错误，抛出错误并附带状态码
                        throw new Error(`HTTP status ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // 检查data是否为null来避免执行不需要的代码
                    if (data === null) return;
                    this.checkResult = data
                    this.sendData()
                    if (!this.value) this.value = data.ServerInfo.version
                    // 仅在成功响应时执行UI操作
                    this.versionFlag = true
                    this.isChecked = true
                    return true
                })
                .catch((error) => {
                    console.error('Error:', error);
                    // 显示除500外的其他HTTP错误的错误码
                    alert(`发生错误：${error.message}`);
                });
        },

        //用于组件之间传递数据
        sendData() {
            if (this.isSelectAll) {
                this.$store.commit('updateMessage', this.checkResult)
            } else {
                let idArr = []
                let newres = []
                this.checkItemsW.forEach(element => {
                    if (this.selectedItemsW.includes(element.name)) idArr.push(element.id)

                });
                this.checkResult.Event_result.forEach((element, index) => {
                    if (idArr.includes(index + 1)) {
                        console.log(index)
                        newres.push(element)
                    }
                })
                console.log(newres)

                this.checkResult.Event_result = newres
                this.$store.commit('updateMessage', this.checkResult)
            }
            // 更新共享状态
        },

        LinuxSubmitForm() {
            this.$refs.form.validate((valid) => {
                if (!valid) {
                    return;
                }

                if (this.selectedItems.length === 0) {
                    Message.warning('请选择至少一个检测项目');
                    return;
                }

                this.loading = true;
                //let payload; // 在 if/else 外部声明变量

                // if (this.checkAll) {
                //   payload = {
                //     ip: this.formData.ip,
                //     pd: this.formData.pd
                //   }; // 给变量赋值
                // } else {
                //   payload = {
                //     ip: this.formData.ip,
                //     pd: this.formData.pd,
                //     ids: this.selectedItems
                //   }; // 给变量赋值
                // }
                const payload = {
                    ip: this.formData.ip,
                    pd: this.formData.pd,
                    ids: this.selectedItems
                };

                fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                })
                    .then(response => {
                        if (!response.ok) {
                            if (response.status === 500) {
                                throw new Error("SSH会话无法启动");
                            }
                            throw new Error(`HTTP status ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log(data);
                        this.loading = false;
                        this.dialogVisible = true;
                    })
                    .catch((error) => {
                        this.loading = false;
                        Message.error(error.message);
                    });
            });
        },

        viewResult() {
            this.dialogVisible = false;
            if (this.flag) {
                this.showPopup = true; // 显示PDF相关内容
            } else {
                this.$nextTick(() => {
                    this.$router.push({
                        path: '/tempBaseCheck',  // 改为跳转到新页面
                        query: {
                            ip: this.formData.ip  // 传递检测的IP
                        }
                    });
                });
            }

        },

        checkAllW() {
            if (this.isChecked) {
                this.viewResult();
                return 0
            } else {
                this.submitForm()
                this.viewResult()
            }
        },

        batchExecuteW() {
            if (this.isChecked) {
                this.sendData()
                this.viewResult()
                return 0
            } else {
                this.submitForm()
                this.viewResult()
            }
        },


        // 处理全选复选框变化
        handleCheckAllChange(val) {
            const allItemIds = this.checkItems.map(item => item.id);
            this.selectedItems = val ? allItemIds : [];
        },
        // 处理选中项变化
        handleCheckedItemsChange(value) {
            const checkedCount = value.length;
            this.checkAll = checkedCount === this.checkItems.length;
        },

        handleCheckAllChangeW(val) {
            this.selectedItemsW = val ? this.checkItemsW.map(item => item.name) : [];
            this.isIndeterminate = false; // 取消半选状态
        },

        handleCheckedItemsChangeW(value) {
            const checkedCount = value.length;
            this.isSelectAll = checkedCount === this.checkItemsW.map(item => item.name).length;
            this.isIndeterminate =
                checkedCount > 0 && checkedCount < this.checkItemsW.map(item => item.name).length;
        },

        // closeModal() {
        //     this.showModal = false;
        //     this.progressBarWidth = 0;
        //     this.showButton = false;
        //     this.$nextTick(() => {
        //         this.showPopup = true; // 显示当前ip检测内容
        //     });
        // },

        closePopup(event) {
            if (event.key === 'Escape') {
                this.showPopup = false; // 隐藏PDF相关内容
            }
        },

        handleViewTempResult() {
            if (!this.formData.ip) {
                Message.warning('请先输入服务器IP地址');
                return;
            }

            // 验证IP格式（复用原有规则）
            const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
            if (!ipPattern.test(this.formData.ip.trim())) {
                Message.error('IP地址格式不正确，请检查输入');
                return;
            }

            this.$router.push({
                path: '/tempBaseCheck',
                query: { ip: this.formData.ip }
            });
        },
    },
    created() {
        // 组件创建时获取活跃IP列表
        this.fetchAliveHosts();
    },
    mounted() {
        window.addEventListener('keydown', this.closePopup);
    },
    beforeUnMount() {
        window.removeEventListener('keydown', this.closePopup);
    }
}
</script>

<style scoped>
.container {
    padding: 20px;
}

.box-card {
    margin-bottom: 20px;
}

.header {
    text-align: center;
    margin-bottom: 30px;
}

.header h1 {
    color: #409EFF;
    margin-bottom: 10px;
}

.subtitle {
    color: #909399;
    font-size: 14px;
}

.login-form {
    max-width: 500px;
    margin: 0 auto;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-actions {
    display: flex;
    align-items: center;
}

.check-items {
    margin-top: 30px;
}

.checkbox-label {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: inline-block;
    max-width: 200px;
}

.el-checkbox {
    margin-bottom: 15px;
    width: 100%;
}

.el-row {
    margin-bottom: 20px;
}

.control-bar {
    display: flex;
    align-items: center;
}

.selected-info {
    margin-top: 10px;
    color: #606266;
    font-size: 14px;
}

.temp-check-link {
    margin-top: -8px;
    margin-bottom: -13px;
    font-size: 12px;
    text-align: right;

    .el-link {
        display: inline-flex;
        align-items: center;

        i {
            margin-right: 3px;
            font-size: 14px;
        }
    }
}

.login-form>>>.el-form-item {
    margin-bottom: 18px;
}

.checboxGroupContainer {
    width: 100%;
    display: flex;
    justify-content: center;
}

.checboxGroup {
    width: 98%;
    display: flex;
    box-sizing: border-box;
    flex-wrap: wrap;
}

.checboxGroup>.el-checkbox {
    width: 30%;
    overflow: hidden;
}

.winVerText {
    color: #409EFF;
    font-weight: bold;
}

.popup {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    z-index: 1001;
}

.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
}
</style>
