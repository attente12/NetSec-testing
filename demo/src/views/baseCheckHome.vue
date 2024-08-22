<template>
    <div>
        <el-row>
            <el-col :span="24" style="text-align: center;"><h1 style="color:dimgrey">Linux基线检测</h1></el-col>
        </el-row>
        <el-row>
            <el-col :span="24"><h3 style="color:dimgrey">请输入待检测Linux主机的ip地址和root密码：</h3></el-col>
        </el-row>
        <el-form @submit.prevent="submitForm">
            <el-form-item label="IP 地址:">
                <el-input v-model="ip"></el-input>
            </el-form-item>
            <el-form-item label="root密码:">
                <el-input v-model="pd" show-password></el-input>
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
    export default {
        name: "home",
        data() {
            return {
                ip: '',
                pd: '',
                showModal: false,
                progressBarWidth: 0,
                showButton: false
            };
        },
        methods: {
            submitForm() {
                const payload = {
                    ip: this.ip,
                    pd: this.pd
                };
                console.log("Submitting form...", payload);

                fetch('http://192.168.177.129:8081/login', {
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
    .progress-bar-container .el-progress-bar__inner {
        transition: width 0.1s ease-out;
    /*平滑过渡动画*/
    }
</style>




<!--数据传到后端但没有显示进度条和页面跳转-->
<!--<template>-->
<!--    <div>-->
<!--        <el-form @submit.prevent="submitForm">-->
<!--            <el-form-item label="IP 地址:">-->
<!--                <el-input v-model="ip"></el-input>-->
<!--            </el-form-item>-->
<!--            <el-form-item label="root密码:">-->
<!--                <el-input v-model="pd" show-password></el-input>-->
<!--            </el-form-item>-->
<!--            <el-form-item>-->
<!--                <el-button type="button" @click="submitForm">基线检测</el-button>-->
<!--            </el-form-item>-->
<!--        </el-form>-->

<!--        <el-dialog :visible.sync="showModal" title="进度" width="30%">-->
<!--            <div class="progress-bar-container">-->
<!--                <el-progress :percentage="progressBarWidth"></el-progress>-->
<!--            </div>-->
<!--            <span slot="footer" class="dialog-footer">-->
<!--                <el-button :disabled="!showButton" @click="closeModal">查看结果</el-button>-->
<!--            </span>-->
<!--        </el-dialog>-->
<!--    </div>-->
<!--</template>-->

<!--<script>-->
<!--    export default {-->
<!--        name: "home",-->
<!--        data() {-->
<!--            return {-->
<!--                ip: '',-->
<!--                pd: '',-->
<!--                showModal: false,-->
<!--                progressBarWidth: 0,-->
<!--                showButton: false-->
<!--            };-->
<!--        },-->
<!--        methods: {-->
<!--            submitForm() {-->
<!--                const payload = {-->
<!--                    ip: this.ip,-->
<!--                    pd: this.pd-->
<!--                };-->

<!--                console.log("Submitting form...", payload);-->

<!--                fetch('http://localhost:8081/login', {-->
<!--                    method: 'POST',-->
<!--                    headers: {-->
<!--                        'Content-Type': 'application/json',-->
<!--                    },-->
<!--                    body: JSON.stringify(payload),-->
<!--                })-->
<!--                    .then(response => response.json())-->
<!--                    .then(data => {-->
<!--                        console.log("Response received:", data);-->
<!--                        this.showModal = true;-->
<!--                        this.runProgress();-->
<!--                    })-->
<!--                    .catch((error) => {-->
<!--                        console.error('Error:', error);-->
<!--                    });-->
<!--            },-->
<!--            runProgress() {-->
<!--                let duration = 4000; // 总持续时间(毫秒)-->
<!--                let elapsed = 0; // 已过时间-->
<!--                let intervalTime = 50; // 更新间隔(毫秒)-->

<!--                const interval = setInterval(() => {-->
<!--                    elapsed += intervalTime;-->
<!--                    this.progressBarWidth = (elapsed / duration) * 100;-->
<!--                    console.log("Progress:", this.progressBarWidth);-->

<!--                    if (elapsed >= duration) {-->
<!--                        clearInterval(interval);-->
<!--                        this.showButton = true;-->
<!--                        console.log("Progress complete.");-->
<!--                    }-->
<!--                }, intervalTime);-->
<!--            },-->
<!--            closeModal() {-->
<!--                this.showModal = false;-->
<!--                this.progressBarWidth = 0;-->
<!--                this.showButton = false;-->
<!--                console.log("Closing modal and redirecting.");-->
<!--                this.$router.push('/baseCheck');-->
<!--            }-->
<!--        }-->
<!--    }-->
<!--</script>-->



<!--一个报错的修改版本-->
<!--<template>-->
<!--    <div>-->
<!--        <el-form @submit.prevent="submitForm">-->
<!--            <el-form-item label="IP 地址:">-->
<!--                <el-input v-model="ip"></el-input>-->
<!--            </el-form-item>-->
<!--            <el-form-item label="root密码:">-->
<!--                <el-input v-model="pd" show-password></el-input>-->
<!--            </el-form-item>-->
<!--            <el-form-item>-->
<!--                <el-button type="primary" native-type="submit">基线检测</el-button>-->
<!--            </el-form-item>-->
<!--        </el-form>-->

<!--        <el-dialog :visible.sync="showModal" title="进度" width="30%">-->
<!--            <div class="progress-bar-container">-->
<!--                <el-progress :percentage="progressBarWidth"></el-progress>-->
<!--            </div>-->
<!--            <span slot="footer" class="dialog-footer">-->
<!--                <el-button :disabled="!showButton" @click="closeModal">查看结果</el-button>-->
<!--            </span>-->
<!--        </el-dialog>-->
<!--    </div>-->
<!--</template>-->

<!--<script>-->
<!--    export default {-->
<!--        name: "home",-->
<!--        data() {-->
<!--            return {-->
<!--                ip: '',-->
<!--                pd: '',-->
<!--                showModal: false,-->
<!--                progressBarWidth: 0,-->
<!--                showButton: false-->
<!--            };-->
<!--        },-->
<!--        methods: {-->
<!--            submitForm() {-->
<!--                const payload = {-->
<!--                    ip: this.ip,-->
<!--                    pd: this.pd-->
<!--                };-->

<!--                //测试-->
<!--                console.log("Submitting form...", payload);-->

<!--                fetch('http://localhost:8081/login', {-->
<!--                    method: 'POST',-->
<!--                    headers: {-->
<!--                        'Content-Type': 'application/json',-->
<!--                    },-->
<!--                    body: JSON.stringify(payload),-->
<!--                })-->
<!--                    .then(response => response.json())-->
<!--                    .then(data => {-->
<!--                        //测试-->
<!--                        console.log("Response received:", data);-->

<!--                        console.log(data);-->
<!--                        this.showModal = true;-->
<!--                        this.runProgress();-->
<!--                    })-->
<!--                    .catch((error) => {-->
<!--                        console.error('Error:', error);-->
<!--                    });-->
<!--            },-->
<!--            runProgress() {-->
<!--                let duration = 4000; // 总持续时间(毫秒)-->
<!--                let elapsed = 0; // 已过时间-->
<!--                let intervalTime = 50; // 更新间隔(毫秒)-->

<!--                const interval = setInterval(() => {-->
<!--                    elapsed += intervalTime;-->
<!--                    this.progressBarWidth = (elapsed / duration) * 100;-->
<!--                    //测试-->
<!--                    console.log("Progress:", this.progressBarWidth);-->

<!--                    if (elapsed >= duration) {-->
<!--                        clearInterval(interval);-->
<!--                        this.showButton = true;-->
<!--                        //测试-->
<!--                        console.log("Progress complete.");-->
<!--                    }-->
<!--                }, intervalTime);-->
<!--            },-->
<!--            closeModal() {-->
<!--                this.showModal = false;-->
<!--                this.progressBarWidth = 0;-->
<!--                this.showButton = false;-->
<!--                //测试-->
<!--                console.log("Closing modal and redirecting.");-->
<!--                this.$router.push('/baseCheck');-->
<!--            }-->
<!--        }-->
<!--    }-->
<!--</script>-->




<!--下面是原来没有使用element ui的代码-->
<!--<template>-->
<!--    <div>-->
<!--        <form @submit.prevent="submitForm">-->
<!--            <label for="ip">IP 地址:</label>-->
<!--            <input type="text" id="ip" v-model="ip"><br><br>-->
<!--            <label for="pd">root密码:</label>-->
<!--            <input type="text" id="pd" v-model="pd"><br><br>-->
<!--            <button type="submit">基线检测</button>-->
<!--        </form>-->

<!--        <div v-if="showModal" class="modal">-->
<!--            <div class="progress-bar-container">-->
<!--                <div :style="{ width: progressBarWidth + '%' }" class="progress-bar"></div>-->
<!--            </div>-->
<!--            <button :disabled="!showButton" :class="{ 'disabled-button': !showButton }" @click="closeModal">查看结果</button>-->
<!--        </div>-->
<!--    </div>-->
<!--</template>-->

<!--<script>-->
<!--    export default {-->
<!--        name: "home",-->
<!--        data() {-->
<!--            return {-->
<!--                ip: '',-->
<!--                pd: '',-->
<!--                showModal: false,-->
<!--                progressBarWidth: 0,-->
<!--                showButton: false-->
<!--            };-->
<!--        },-->
<!--        methods: {-->
<!--            submitForm() {-->
<!--                const payload = {-->
<!--                    ip: this.ip,-->
<!--                    pd: this.pd-->
<!--                };-->

<!--                fetch('http://localhost:8081/login', {-->
<!--                    method: 'POST',-->
<!--                    headers: {-->
<!--                        'Content-Type': 'application/json',-->
<!--                    },-->
<!--                    body: JSON.stringify(payload),-->
<!--                })-->
<!--                    .then(response => response.json())-->
<!--                    .then(data => {-->
<!--                        console.log(data);-->
<!--                    })-->
<!--                    .catch((error) => {-->
<!--                        console.error('Error:', error);-->
<!--                    });-->

<!--                // 显示模态框并开始进度条动画-->
<!--                // 显示模态框并开始进度条动画-->
<!--                    this.showModal = true;-->
<!--                    this.progressBarWidth = 0; // 初始化进度条宽度-->
<!--                    let duration = 4000; // 总持续时间(毫秒)-->
<!--                    let elapsed = 0; // 已过时间-->
<!--                    let intervalTime = 50; // 更新间隔(毫秒)-->

<!--                    const interval = setInterval(() => {-->
<!--                        elapsed += intervalTime;-->
<!--                        this.progressBarWidth = (elapsed / duration) * 100;-->
<!--                        if (elapsed >= duration) {-->
<!--                            clearInterval(interval);-->
<!--                            this.showButton = true;-->
<!--                        }-->
<!--                    }, intervalTime);-->
<!--                },-->

<!--            //     this.showModal = true;-->
<!--            //     let seconds = 0;-->
<!--            //     const interval = setInterval(() => {-->
<!--            //         seconds++;-->
<!--            //         this.progressBarWidth = (seconds / 4) * 100;-->
<!--            //         if (seconds >= 4) {-->
<!--            //             clearInterval(interval);-->
<!--            //             this.showButton = true;-->
<!--            //         }-->
<!--            //     }, 1000);-->
<!--            // },-->
<!--            closeModal() {-->
<!--                this.showModal = false;-->
<!--                this.progressBarWidth = 0;-->
<!--                this.showButton = false;-->
<!--                this.$router.push('/baseCheck');-->
<!--            }-->
<!--        }-->
<!--    }-->
<!--</script>-->

<!--<style scoped>-->
<!--    .modal {-->
<!--        position: fixed;-->
<!--        left: 50%;-->
<!--        top: 50%;-->
<!--        transform: translate(-50%, -50%);-->
<!--        background: white;-->
<!--        padding: 20px;-->
<!--        z-index: 1000;-->
<!--        width: 60%; /* 调整模态框宽度以适应更长的进度条 */-->
<!--        display: flex; /* 设置模态框为flex容器 */-->
<!--        flex-direction: column; /* 子元素垂直排列 */-->
<!--        align-items: center; /* 水平居中对齐子元素 */-->
<!--        justify-content: center; /* 垂直居中对齐子元素 */-->
<!--    }-->
<!--    .progress-bar-container {-->
<!--        width: 100%; /* 容器宽度调整为100% */-->
<!--        background: #eee;-->
<!--        margin-bottom: 10px;-->
<!--        height: 10px; /* 调整容器高度为10px，使得进度条看起来更扁 */-->
<!--        border-radius: 5px; /* 可选：添加圆角 */-->
<!--    }-->
<!--    .progress-bar {-->
<!--        height: 100%; /* 进度条高度填满容器 */-->
<!--        background: green;-->
<!--        border-radius: 5px; /* 可选：添加圆角 */-->
<!--    }-->
<!--    button {-->
<!--        margin-top: 20px; /* 在按钮和进度条之间添加一些间隙 */-->
<!--    }-->
<!--    .disabled-button {-->
<!--        opacity: 0.5; /* 设置不透明度为0.5，使按钮看起来更暗 */-->
<!--        cursor: not-allowed; /* 鼠标悬停时显示禁止符号 */-->
<!--    }-->
<!--</style>-->







<!--<template>-->
<!--    <div>-->
<!--        <form @submit.prevent="submitForm">-->
<!--            <label for="ip">IP 地址:</label>-->
<!--            <input type="text" id="ip" v-model="ip"><br><br>-->
<!--            <label for="pd">root密码:</label>-->
<!--            <input type="text" id="pd" v-model="pd"><br><br>-->
<!--            <button type="submit">基线检测</button>-->
<!--        </form>-->

<!--        <div v-if="showModal" class="modal">-->
<!--            <div class="progress-bar-container">-->
<!--                <div :style="{ width: progressBarWidth + '%' }" class="progress-bar"></div>-->
<!--            </div>-->
<!--            <button v-if="showButton" @click="closeModal">查看结果</button>-->
<!--        </div>-->
<!--    </div>-->
<!--</template>-->

<!--<script>-->
<!--    export default {-->
<!--        name: "home",-->
<!--        data() {-->
<!--            return {-->
<!--                ip: '',-->
<!--                pd: '',-->
<!--                showModal: false,-->
<!--                progressBarWidth: 0,-->
<!--                showButton: false-->
<!--            };-->
<!--        },-->
<!--        methods: {-->
<!--            submitForm() {-->
<!--                const payload = {-->
<!--                    ip: this.ip,-->
<!--                    pd: this.pd-->
<!--                };-->

<!--                fetch('http://localhost:8081/login', {-->
<!--                    method: 'POST',-->
<!--                    headers: {-->
<!--                        'Content-Type': 'application/json',-->
<!--                    },-->
<!--                    body: JSON.stringify(payload),-->
<!--                })-->
<!--                    .then(response => response.json())-->
<!--                    .then(data => {-->
<!--                        console.log(data);-->
<!--                    })-->
<!--                    .catch((error) => {-->
<!--                        console.error('Error:', error);-->
<!--                    });-->

<!--                // 显示模态框并开始进度条动画-->
<!--                this.showModal = true;-->
<!--                let seconds = 0;-->
<!--                const interval = setInterval(() => {-->
<!--                    seconds++;-->
<!--                    this.progressBarWidth = (seconds / 4) * 100;-->
<!--                    if (seconds >= 4) {-->
<!--                        clearInterval(interval);-->
<!--                        this.showButton = true;-->
<!--                    }-->
<!--                }, 1000);-->
<!--            },-->
<!--            closeModal() {-->
<!--                this.showModal = false;-->
<!--                this.progressBarWidth = 0;-->
<!--                this.showButton = false;-->
<!--                this.$router.push('/baseCheck');-->
<!--            }-->
<!--        }-->
<!--    }-->
<!--</script>-->

<!--<style scoped>-->
<!--    .modal {-->
<!--        position: fixed;-->
<!--        left: 50%;-->
<!--        top: 50%;-->
<!--        transform: translate(-50%, -50%);-->
<!--        background: white;-->
<!--        padding: 20px;-->
<!--        z-index: 1000;-->
<!--        width: 60%; /* 调整模态框宽度以适应更长的进度条 */-->
<!--        display: flex; /* 设置模态框为flex容器 */-->
<!--        flex-direction: column; /* 子元素垂直排列 */-->
<!--        align-items: center; /* 水平居中对齐子元素 */-->
<!--        justify-content: center; /* 垂直居中对齐子元素 */-->
<!--    }-->
<!--    .progress-bar-container {-->
<!--        width: 100%; /* 容器宽度调整为100% */-->
<!--        background: #eee;-->
<!--        margin-bottom: 10px;-->
<!--        height: 10px; /* 调整容器高度为10px，使得进度条看起来更扁 */-->
<!--        border-radius: 5px; /* 可选：添加圆角 */-->
<!--    }-->
<!--    .progress-bar {-->
<!--        height: 100%; /* 进度条高度填满容器 */-->
<!--        background: green;-->
<!--        border-radius: 5px; /* 可选：添加圆角 */-->
<!--    }-->
<!--    button {-->
<!--        margin-top: 20px; /* 在按钮和进度条之间添加一些间隙 */-->
<!--    }-->
<!--</style>-->





<!--
<template>
    <div>
        <form @submit.prevent="submitForm">
            <label for="ip">ip地址:</label>
            <input type="text" id="ip" v-model="ip"><br><br>
            <label for="pd">性别:</label>
            <input type="text" id="pd" v-model="pd"><br><br>
            <button type="submit">基线检测</button>
        </form>
    </div>
</template>

<script>
    export default {
        name:"home",
        data() {
            return {
                ip: '',
                pd: ''
            };
        },
        methods: {
            submitForm() {
                const payload = {
                    ip: this.ip,
                    pd: this.pd
                };

                fetch('http://localhost:8081/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data);
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    });
                //在这里添加一个弹窗，弹窗显示一个进度条，表示正在进行基线检测，进度条持续六秒，下面有一个查看结果按钮，六秒后点击弹窗中的按钮退出弹窗，继续执行下面的代码
                this.$router.push('/baseCheck');
            }
        }
    }
</script>

&lt;!&ndash; Optional: add styles here &ndash;&gt;
<style scoped>
    /* Your CSS styles */
</style>
-->
