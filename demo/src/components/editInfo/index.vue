<!-- 本组件包含用户编辑自身信息，管理员用户编辑他人信息的功能 -->
<template>
    <div class="edit_info_container" @click="closeEditInfo">
        <div class="user_profile_form" @click.stop>
            <span class="close_icon" @click="closeEditInfo">X</span>
            <h3>请输入新的个人信息</h3>

            <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" @submit.prevent="handleSubmit">
                <el-form-item v-if="isAdmin && !currentInfo.username" label="用户名" prop="username">
                    <el-input v-model="form.username" placeholder="请输入用户名" clearable />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                    <el-input v-model="form.email"
                        :placeholder="isAdmin && !currentInfo.username ? '请输入邮箱' : '请输入邮箱（留空不修改）'" clearable />
                </el-form-item>

                <el-form-item :label="isAdmin && !currentInfo.username ? '密码' : '新密码'" prop="password">
                    <el-input v-model="form.password" type="password"
                        :placeholder="isAdmin && !currentInfo.username ? '请输入新密码' : '请输入新密码（留空不修改）'" show-password
                        clearable />
                </el-form-item>

                <el-form-item label="确认密码" prop="confirmPassword">
                    <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" show-password
                        clearable />
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" @click="submitForm">提交</el-button>
                    <el-button @click="resetForm">重置</el-button>
                </el-form-item>
            </el-form>
        </div>

    </div>

</template>
<script>

import { setCookie, getCookie } from '@/utils/cookie'


export default {
    name: "EditInfo",
    props: {
        // 关闭编辑信息组件的事件
        isAdmin: {
            type: Boolean,
            default: false
        },
        currentInfo: {
            type: Object,
            default: () => ({})
        }
    },
    data() {
        const validateConfirmPassword = (rule, value, callback) => {
            if (value && value !== this.form.password) {
                callback(new Error('两次输入的密码不一致'));
            } else {
                callback();
            }
        };
        return {
            form: {
                userid: '',
                username: "",
                email: "",
                password: "",
                confirmPassword: ""
            },
            rules: {
                email: [
                    { message: '请输入邮箱', trigger: 'blur' },
                    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] },
                ],
                password: [
                    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
                ],
                confirmPassword: [
                    { validator: validateConfirmPassword, trigger: 'blur' },
                ],
            }
        };
    },
    methods: {
        initForm() {
            this.form.userid = this.currentInfo.id || this.currentInfo.userid || '';
            this.form.username = this.currentInfo.username || '';
            this.form.email = this.currentInfo.email || '';
        },
        async editCurrentUser() {
            if (!this.form.email && !this.form.password) {
                return alert("请至少修改邮箱或密码");
            }
            if (!this.form.password && this.form.email === this.currentInfo.email) {
                return alert("请至少修改邮箱或密码");
            }
            try {
                const res = await this.$axios.put('/updateUser', {
                    userid: parseInt(this.form.userid),
                    email: this.form.email,
                    password: this.form.password,
                });
                if (this.currentInfo.email === getCookie('email')) {
                    // 更新cookie中的email
                    setCookie('email', this.form.email, 1);
                }


                alert(res.message || '用户信息更新成功');
                window.location.reload(); // 刷新页面以应用更改
            } catch (error) {
                return alert(error || "更新用户信息失败，请稍后再试");
            }
        },
        async addUser() {
            try {
                const res = await this.$axios.post('/createUser', {
                    username: this.form.username,
                    email: this.form.email,
                    password: this.form.password,
                });
                alert(res.message || '用户添加成功');
            } catch (error) {
                return alert("添加用户失败，请稍后再试");
            }
        },
        submitForm() {
            if (this.isAdmin && !this.currentInfo.username) {
                this.addUser()
            } else {
                this.editCurrentUser();
            }
        },
        resetForm() {
            this.$refs.formRef.resetFields();
            this.form.password = '';
            this.form.confirmPassword = '';
        },
        closeEditInfo() {
            // 关闭编辑信息组件
            this.$emit('iClose');
        }
    },
    mounted() {
        this.initForm();
    }
}

</script>

<style scoped>
@import url('./style.css');
</style>