<template>
    <div class="container">
        <el-row>
            <el-col :span="24" style="text-align: center;">
                <h1 style="color:dimgrey">{{ flag ? 'Windows' : 'Linux' }}基线检测</h1>
            </el-col>
        </el-row>
        <el-button type="button" @click="turnFlag">切换到{{ flag ? 'Linux' : 'Windows' }}</el-button>
        <el-row>
            <el-col :span="24">
                <h3 style="color:dimgrey">请输入待检测{{ flag ? 'Windows' : 'Linux' }}主机的ip地址和{{ flag ? '管理员用户名及' : 'root'
                    }}密码：</h3>
            </el-col>
        </el-row>
        <el-form @submit.prevent="submitForm" class="login-form">
            <el-form-item label="IP 地址">
                <el-input v-model="ip" placeholder="请输入服务器IP地址" prefix-icon="el-icon-monitor">
                </el-input>
            </el-form-item>
            <el-form-item v-show="flag" label="管理员账户名（默认为Administer）">
                <el-input v-model="adminName" placeholder="请输入管理员账户名" prefix-icon="el-icon-monitor">
                </el-input>
            </el-form-item>
            <el-form-item v-show="flag" label="管理员密码">
                <el-input v-model="pd" type="password" placeholder="请输入密码" prefix-icon="el-icon-monitor">
                </el-input>
            </el-form-item>
            <el-form-item v-show="!flag" label="root密码">
                <el-input v-model="pd" type="password" placeholder="请输入密码" prefix-icon="el-icon-monitor">
                </el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="button" @click="submitForm">开始检测</el-button>
            </el-form-item>
        </el-form>

        <el-dialog :visible.sync="showModal" title="进度" width="30%">
            <div class="progress-bar-container">
                <el-progress :percentage="progressBarWidth"></el-progress>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button :disabled="!showButton" @click="closeModal">查看结果</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
import { Message } from "element-ui"

export default {
    name: "home",
    data() {
        return {
            flag: true,
            ip: '',
            adminName: '',
            pd: '',
            showModal: false,
            progressBarWidth: 0,
            showButton: false
        };
    },
    methods: {
        //切换Windows或Linux方法
        turnFlag() {
            this.flag = !this.flag
            this.pd = ''
        },

        WindowsSubmitForm() {
            window.alert('ok, 200')
        },
        LinuxSubmitForm() {
            const payload = {
                ip: this.ip,
                pd: this.pd
            };
            console.log("Submitting form...", payload);

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

                    console.log("Response received:", data);
                    // 仅在成功响应时执行UI操作
                    this.progressBarWidth = 0; // 初始化进度为0
                    this.showModal = true;
                    this.runProgress();
                })
                .catch((error) => {
                    console.error('Error:', error);
                    // 显示除500外的其他HTTP错误的错误码
                    alert(`发生错误：${error.message}`);
                });
        },

        submitForm() {
            if (this.flag) {
                this.WindowsSubmitForm()
            } else {
                this.LinuxSubmitForm()
            }
        },

        runProgress() {
            let duration = 4000;
            let elapsed = 0;
            let intervalTime = 100;

            const interval = setInterval(() => {
                elapsed += intervalTime;
                this.progressBarWidth = Math.round((elapsed / duration) * 100); // 四舍五入到整数

                if (elapsed >= duration) {
                    clearInterval(interval);
                    this.progressBarWidth = 100; // 确保最后是100%
                    this.showButton = true;
                }
            }, intervalTime);
        },

        batchExecute() {
            this.$refs.form.validate((valid) => {
                if (!valid) {
                    return;
                }

                if (this.selectedItems.length === 0) {
                    Message.warning('请选择需要批量执行的项目');
                    return;
                }

                this.batchLoading = true;
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
                        this.batchLoading = false;
                        this.dialogVisible = true;
                    })
                    .catch((error) => {
                        this.batchLoading = false;
                        Message.error(error.message);
                    });
            });
        },

        closeModal() {
            this.showModal = false;
            this.progressBarWidth = 0;
            this.showButton = false;
            console.log("Closing modal and redirecting.");
            this.$nextTick(() => {
                this.$router.push('/baseCheck');
            });
        }
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
</style>
