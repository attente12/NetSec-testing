<template>
    <div>
        <main class="main_container">
            <p>您的信息</p>
            <div class="info_container">
                <div class="basic_info">
                    <img class="avatar" src="../../assets/logo.png" alt="头像">
                    <span>
                        <p>用户名：{{ username }}</p>
                        <p>邮箱：{{ email }}</p>
                        <p>用户类型：{{ isAdmin ? '管理员' : '普通用户' }}</p>
                    </span>
                </div>

                <div class="my_button" @click="showEditInfo">
                    <span>编辑个人信息</span><span>></span>
                </div>
                <div class="my_button" v-if="isAdmin" @click="showAndCloseUserManager">
                    <span>管理其他用户</span><span>{{ showUserManager ? '-' : '+' }}</span>
                </div>
                <div class="my_button"><span>反馈</span><span>?</span></div>
                <div class="my_button" @click="exit"><span>退出登录</span><span>..</span></div>
            </div>
        </main>
        <user-table v-if="showUserManager" @adminAdd="showAdminAdd" @editting="getEdittingUser"></user-table>
        <edit-info v-if="editInfoFlag" :isAdmin="editAdminFlag" :currentInfo="whoIsEditted"
            @iClose="closeEditInfo"></edit-info>
    </div>
</template>
<script>
import EditInfo from '../../components/editInfo/index.vue';
import UserTable from '../../components/userTable/index.vue';
import { deleteAllCookies, getCookie } from '@/utils/cookie.js';

export default {
    name: "MeIndex",
    components: {
        EditInfo,
        UserTable
    },
    data() {
        return {
            userid: "",
            username: "",
            email: "",
            isAdmin: true,
            editInfoFlag: false,
            showUserManager: false,
            editAdminFlag: false,
            whoIsEditted: {}
        };
    },
    methods: {
        showEditInfo() {
            this.editInfoFlag = true;
            this.whoIsEditted = {
                userid: this.userid,
                username: this.username,
                email: this.email
            };
        },
        closeEditInfo() {
            this.editInfoFlag = false;
            this.whoIsEditted = {};
        },
        showAndCloseUserManager() {
            // 触发编辑信息组件的显示
            this.showUserManager = !this.showUserManager;
        },
        showAdminAdd() {
            console.log('管理员添加新用户');
            this.editAdminFlag = true;
            this.editInfoFlag = true;
        },
        getInfo() {
            this.userid = getCookie('id') || '';
            this.username = getCookie('username') || 'Joe';
            this.email = getCookie('email') || 'okjoe@qq.com';
            this.isAdmin = getCookie('role') === 'admin';
        },
        getEdittingUser(user) {
            console.log('获取正在编辑的用户信息:', user);
            this.whoIsEditted = user;
            this.editInfoFlag = true;
            this.editAdminFlag = true; // 设置为管理员编辑状态
        },
        exit() {
            deleteAllCookies();
            sessionStorage.clear();
            this.$router.push({ name: 'login' });
        }
    },
    mounted() {
        this.getInfo();
    }
}
</script>
<style scoped>
@import './style.css';
</style>