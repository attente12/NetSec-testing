<!-- 本组件包含用户编辑自身信息，管理员用户编辑他人信息的功能 -->
<template>
    <div class="edit_info_container" @click="closeEditInfo">
        <div class="user_profile_form" @click.stop>
            <span class="close_icon" @click="closeEditInfo">X</span>
            <h3>请输入新的个人信息</h3>

            <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" @submit.prevent="handleSubmit">
                <el-form-item v-if="isAdmin" label="用户名" prop="username">
                    <el-input v-model="form.username" placeholder="请输入用户名" clearable />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                    <el-input v-model="form.email" :placeholder="isAdmin ? '请输入邮箱' : '请输入邮箱（留空不修改）'" clearable />
                </el-form-item>

                <el-form-item :label="isAdmin ? '密码' : '新密码'" prop="password">
                    <el-input v-model="form.password" type="password"
                        :placeholder="isAdmin ? '请输入新密码' : '请输入新密码（留空不修改）'" show-password clearable />
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
export default {
    name: "EditInfo",
    props: {
        // 关闭编辑信息组件的事件
        isAdmin: {
            type: Boolean,
            default: false
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
        submitForm() {
            console.log("提交的表单数据：", this.$refs.formRef.model);
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
    }
}

</script>

<style scoped>
@import url('./style.css');
</style>