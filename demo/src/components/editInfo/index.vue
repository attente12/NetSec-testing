<template>
    <form action="">
        新用户名：<input type="text">
        新的邮箱：<input type="text">
        旧的密码：<input type="password">
        新的密码：<input type="password">
        确认新的密码：<input type="password">
        <button>提交</button>
        <button>取消</button>
    </form>
</template>
<script>
export default {
    name: "EditInfo",
    data() {
        return {
            username: "",
            email: "",
            oldPassword: "",
            newPassword: "",
            confirmPassword: ""
        };
    },
    methods: {
        submitForm() {
            // 提交表单逻辑
        },
        cancel() {
            // 取消编辑逻辑
        }
    }
}

</script>