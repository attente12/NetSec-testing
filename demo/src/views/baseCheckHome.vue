<template>
    <div class="container">
        <el-card class="box-card">
            <el-row>
                <el-col :span="24">
                    <div class="header">
                        <h1>Linux基线检测</h1>
                        <!--            <p class="subtitle">安全基线检测工具</p>-->
                    </div>
                </el-col>
            </el-row>

            <el-form @submit.prevent="submitForm" :model="formData" :rules="rules" ref="form" label-width="120px"
                class="login-form">
                <el-form-item label="IP 地址" prop="ip">
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
                <el-form-item label="root密码" prop="pd">
                    <el-input v-model="formData.pd" type="password" placeholder="请输入root密码" prefix-icon="el-icon-lock"
                        show-password>
                    </el-input>
                </el-form-item>
                <el-form-item>
                    <div class="control-bar">
                        <el-checkbox v-model="checkAll" @change="handleCheckAllChange" style="margin-right: 15px;">
                            全选检测项目
                        </el-checkbox>
                        <el-button type="primary" @click="startCheck" icon="el-icon-video-play" :loading="loading"
                            :disabled="selectedItems.length === 0">
                            开始检测
                        </el-button>
                    </div>
                    <!--          <div class="selected-info" v-if="selectedItems.length > 0">-->
                    <!--            已选择 {{ selectedItems.length }} 项检测项目-->
                    <!--          </div>-->
                </el-form-item>
            </el-form>
        </el-card>

        <el-card class="box-card check-items">
            <div slot="header" class="card-header">
                <span>检测项目选择</span>
            </div>

            <el-checkbox-group v-model="selectedItems" @change="handleCheckedItemsChange">
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
    </div>
</template>

<script>
import { Message } from "element-ui";

export default {
    name: "home",
    data() {
        return {
            formData: {
                ip: '',
                pd: ''
            },
            aliveHosts: [], // 存储活跃IP列表
            selectedItems: [],
            checkAll: false,
            dialogVisible: false,
            loading: false,
            rules: {
                ip: [
                    { required: true, message: '请输入IP地址', trigger: 'blur' },
                    { pattern: /^(\d{1,3}\.){3}\d{1,3}$/, message: '请输入正确的IP地址格式', trigger: 'blur' }
                ],
                pd: [
                    { required: true, message: '请输入密码', trigger: 'blur' }
                ]
            },
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
            ]
        };
    },
    created() {
        // 组件创建时获取活跃IP列表
        this.fetchAliveHosts();
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
        // 开始检测（合并了原来的submitForm和batchExecute方法）
        startCheck() {
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
            this.$nextTick(() => {
                this.$router.push({
                    path: '/tempBaseCheck',  // 改为跳转到新页面
                    query: {
                        ip: this.formData.ip  // 传递检测的IP
                    }
                });
            });
        },
        // viewResult() {
        //   this.dialogVisible = false;
        //   this.$nextTick(() => {
        //     this.$router.push('/baseCheck');
        //   });
        // }
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
</style>
