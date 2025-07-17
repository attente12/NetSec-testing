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
                        <p>用户类型：{{ userType }}</p>
                    </span>
                </div>

                <div class="my_button" @click="showAndCloseEditInfo"><span>编辑个人信息</span><span>></span></div>
                <div class="my_button" v-if="isAdmin"><span>管理其他用户</span><span>></span></div>
                <div class="my_button"><span>反馈</span><span>></span></div>
                <div class="my_button"><span>退出登录</span><span>...</span></div>
            </div>
        </main>

        <edit-info v-if="showEditInfo" @IClose="showAndCloseEditInfo"></edit-info>
    </div>
</template>
<script>
import EditInfo from '../../components/editInfo/index.vue';

export default {
    name: "MeIndex",
    components: {
        EditInfo
    },
    data() {
        return {
            username: "Joe",
            email: "joeyes@1100.com",
            userType: "普通用户",
            isAdmin: false,
            showEditInfo: false
        };
    },
    methods: {
        showAndCloseEditInfo() {
            // 触发编辑信息组件的显示
            this.showEditInfo = !this.showEditInfo;
        }
    },
}
</script>
<style scoped>
@import './style.css';
</style>