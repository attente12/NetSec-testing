<template>
    <div>
        <div>
            <div>用户名：{{ username }}</div>
            <div>邮箱：{{ email }}</div>
            <div>用户类型：{{ userType }}</div>
            <button>编辑个人信息</button>
            <button>退出登录</button>
        </div>
        <edit-info></edit-info>
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
            email: "joeyess@1100.com",
            userType: "普通用户"
        };
    },
}
</script>
<style scoped>
@import './style.css';
</style>