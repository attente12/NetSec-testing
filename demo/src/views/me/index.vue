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

                <div class="my_button" @click="showAndCloseEditInfo"><span>编辑个人信息</span><span>></span></div>
                <div class="my_button" v-if="isAdmin" @click="showAndCloseUserManager">
                    <span>管理其他用户</span><span>{{ showUserManager ? '-' : '+' }}</span>
                </div>
                <div class="my_button"><span>反馈</span><span>?</span></div>
                <div class="my_button" @click="exit"><span>退出登录</span><span>..</span></div>
            </div>
        </main>
        <user-table v-if="showUserManager" @adminAdd="showAdminAdd" @editting="getEdittingUser"></user-table>
        <edit-info v-if="showEditInfo" :isAdmin="editAdminFlag" :currentInfo="whoIsEditted"
            @iClose="showAndCloseEditInfo"></edit-info>
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
            username: "",
            email: "",
            isAdmin: true,
            showEditInfo: false,
            showUserManager: false,
            editAdminFlag: false,
            whoIsEditted: {}
        };
    },
    methods: {
        showAndCloseEditInfo() {
            // 触发编辑信息组件的显示
            this.whoIsEditted = {};
            this.showEditInfo = !this.showEditInfo;
            this.editAdminFlag = false; // 重置管理员编辑标志
        },
        showAndCloseUserManager() {
            // 触发编辑信息组件的显示
            this.showUserManager = !this.showUserManager;
        },
        showAdminAdd() {
            this.editAdminFlag = true;
            this.showEditInfo = true;
        },
        getInfo() {
            this.username = getCookie('username') || 'Joe';
            this.email = getCookie('email') || 'okjoe@qq.com';
            this.isAdmin = getCookie('role') === 'admin';
        },
        getEdittingUser(user) {
            this.whoIsEditted = user;
            this.showEditInfo = true;
            this.editAdminFlag = true; // 设置为管理员编辑状态
        },
        exit() {
            deleteAllCookies();
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