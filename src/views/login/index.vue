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
                <el-form-item v-if="!isLogin && isVerify" label="验证码" prop="code">
                    <el-input v-model="form.code" placeholder="请输入验证码"></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button v-if="!isVerify" type="primary" @click="handleSubmit" :loading="loading"
                        class="submit-btn">
                        {{ isLogin ? '登录' : '获取验证码' }}
                    </el-button>
                    <el-button v-else type="primary" @click="codeVerify" :loading="loading" class="submit-btn">
                        注册
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
import { setCookie } from '@/utils/cookie';

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
            isVerify: false,
            loading: false,
            form: {
                username: '',
                email: '',
                password: '',
                confirmPassword: '',
                code: '',
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

    methods: {
        toggleAuthMode() {
            this.isLogin = !this.isLogin;
            this.$refs.authForm.resetFields();
        },
        async userLogin() {
            this.loading = true;
            try {
                const res = await this.$axios.post('/userLogin', {
                    username: this.form.username,
                    password: this.form.password,
                });
                setCookie('userToken', res.token, 1);
                setCookie('username', this.form.username, 1);
                setCookie('email', res.email, 1);
                setCookie('role', res.role, 1);
                setCookie('id', res.id, 1);

                this.$router.push({ path: '/indexPage' });
            } catch (error) {
                this.loading = false;
                console.error(error);
                alert('登录失败，请检查用户名和密码是否正确');
            }
        },
        async codeVerify() {
            try {
                const res = await this.$axios.post('/verify', {
                    email: this.form.email,
                    username: this.form.username,
                    password: this.form.password,
                    code: this.form.code,
                });
                if (res.status !== '200') return alert('验证码错误或已过期，请重新注册');
                alert('注册成功，请登录');
                this.loading = false;
                this.isVerify = false;
                this.form.code = '';
                this.isLogin = true;

            } catch (error) {
                this.loading = false;
                console.error(error);
                alert(error.response.data.message || '验证码错误或已过期，请重新注册');
                this.isVerify = false;
                this.form.code = '';
            }
        },
        async userRegister() {
            this.loading = true;
            try {
                const res = await this.$axios.post('/register', {
                    username: this.form.username,
                    email: this.form.email,
                    password: this.form.password,
                });
                console.log(res);
                this.loading = false;
                this.isVerify = true;
            } catch (error) {
                this.loading = false;
                console.error(error);
                alert(error.response.data.message || '注册失败，请稍后再试');
            }
        },
        handleSubmit() {
            this.$refs.authForm.validate((valid) => {
                if (valid) {
                    if (this.isLogin) {
                        this.userLogin();
                    } else {
                        this.userRegister();
                    }
                } else {
                    this.$message.error('请检查表单填写是否正确');
                }
            });
        },
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
};
</script>

<style scoped>
@import url('./style.css');
</style>