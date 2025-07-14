<template>
    <div class="auth-container">
        <div id="particles-js" class="particles-background"></div>
        <div class="auth-box">
            <h2>{{ isLogin ? '登录' : '注册' }}</h2>
            <el-form :model="form" :rules="rules" ref="authForm" label-position="top" class="auth-form">
                <el-form-item label="用户名" prop="username">
                    <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
                </el-form-item>
                <el-form-item v-if="!isLogin" label="邮箱" prop="email">
                    <el-input v-model="form.email" placeholder="请输入邮箱"></el-input>
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="form.password" type="password" placeholder="请输入密码"></el-input>
                </el-form-item>
                <el-form-item v-if="!isLogin" label="确认密码" prop="confirmPassword">
                    <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码"></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="handleSubmit" :loading="loading" class="submit-btn">
                        {{ isLogin ? '登录' : '注册' }}
                    </el-button>
                </el-form-item>
            </el-form>
            <div class="toggle-link">
                <span @click="toggleAuthMode">
                    {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
                </span>
            </div>
        </div>
    </div>
</template>

<script>
import 'particles.js';
export default {
    data() {
        const validatePass = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请输入密码'));
            } else {
                if (this.form.confirmPassword !== '') {
                    this.$refs.authForm.validateField('confirmPassword');
                }
                callback();
            }
        };
        const validateConfirmPass = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请再次输入密码'));
            } else if (value !== this.form.password) {
                callback(new Error('两次输入密码不一致'));
            } else {
                callback();
            }
        };
        const validateEmail = (rule, value, callback) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (value === '') {
                callback(new Error('请输入邮箱'));
            } else if (!emailRegex.test(value)) {
                callback(new Error('请输入有效的邮箱地址'));
            } else {
                callback();
            }
        };
        return {
            isLogin: true,
            loading: false,
            form: {
                username: '',
                email: '',
                password: '',
                confirmPassword: '',
            },
            rules: {
                username: [
                    { required: true, message: '请输入用户名', trigger: 'blur' },
                    { min: 3, max: 15, message: '用户名长度在 3 到 15 个字符', trigger: 'blur' },
                ],
                email: [
                    { required: true, validator: validateEmail, trigger: 'blur' },
                ],
                password: [
                    { required: true, validator: validatePass, trigger: 'blur' },
                    { min: 6, message: '密码至少 6 个字符', trigger: 'blur' },
                ],
                confirmPassword: [
                    { required: true, validator: validateConfirmPass, trigger: 'blur' },
                ],
            },
        };
    },
    mounted() {
        // 初始化 particles.js
        window.particlesJS('particles-js', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: '#ffffff' },
                shape: { type: 'circle', stroke: { width: 0, color: '#000000' } },
                opacity: { value: 0.5, random: true },
                size: { value: 3, random: true },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: '#ffffff',
                    opacity: 0.4,
                    width: 1,
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: 'none',
                    random: true,
                    straight: false,
                    out_mode: 'out',
                    bounce: false,
                },
            },
            interactivity: {
                detect_on: 'canvas',
                events: {
                    onhover: { enable: true, mode: 'grab' },
                    onclick: { enable: true, mode: 'push' },
                    resize: true,
                },
                modes: {
                    grab: { distance: 200, line_linked: { opacity: 0.7 } },
                    push: { particles_nb: 4 },
                },
            },
            retina_detect: true,
        });
    },
    methods: {
        toggleAuthMode() {
            this.isLogin = !this.isLogin;
            this.$refs.authForm.resetFields();
        },
        handleSubmit() {
            this.$refs.authForm.validate((valid) => {
                if (valid) {
                    this.loading = true;
                    setTimeout(() => {
                        this.loading = false;
                        this.$message.success(this.isLogin ? '登录成功' : '注册成功');
                    }, 1000);
                }
            });
        },
    },
};
</script>

<style scoped>
@import url('./style.css');
</style>