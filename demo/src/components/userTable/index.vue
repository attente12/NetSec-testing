<template>
    <div class="table_container">
        <el-table :data="tableData" :row-style="getRowStyle">
            <el-table-column fixed prop="userid" label="userid" width="50" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="email" label="邮箱" width="240" />
            <el-table-column prop="role" label="用户类型" width="120" />
            <el-table-column prop="account_status" label="用户状态" width="120" />
            <el-table-column fixed="right" label="操作" min-width="180">
                <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="handleClick(row)">
                        编辑
                    </el-button>
                    <el-button v-if="row.account_status === 'deleted'" link type="success" size="small"
                        @click="handleRestore(row)">
                        恢复
                    </el-button>
                    <el-button v-if="row.account_status !== 'deleted'" link type="danger" size="small"
                        @click="handleDelete(row)">
                        删除
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
        <el-button class="add_button" @click="addUser">
            添加用户
        </el-button>
    </div>
</template>
<script>

export default {
    name: "UserTable",
    data() {
        return {
            tableData: [
                {
                    userid: '1',
                    username: 'JohnSmith',
                    email: 'LovingKindom@qq.com',
                    role: 'admin',
                    account_status: 'active'
                },
                {
                    userid: '2',
                    username: 'JaneDoe',
                    email: 'JDtheBest@qq.com',
                    role: 'user',
                    account_status: 'active'
                },
                {
                    userid: '3',
                    username: 'BBLiz',
                    email: 'Lizy@qq.com',
                    role: 'user',
                    account_status: 'pending'
                },
                {
                    userid: '4',
                    username: 'TonyStark',
                    email: 'Starkuserid@google.com',
                    role: 'user',
                    account_status: 'active'
                },
                {
                    userid: '5',
                    username: 'HuiCheng',
                    email: 'huiC@qq.com',
                    role: 'user',
                    account_status: 'delete'
                }
            ]
        };
    },
    methods: {
        getRowStyle({ row }) {
            if (row.account_status === 'pending') {
                return { backgroundColor: '#f9f4cc' };
            } else if (row.account_status === 'deleted') {
                return { backgroundColor: '#f3b0a8' };
            }
            return {};
        },
        handleClick() {
            this.$message({
                message: 'Detail clicked!',
                type: 'info'
            });
        },
        async getUsers() {
            try {
                const res = await this.$axios.get('/displayUsers');
                this.tableData = res.users;
            } catch (error) {
                console.error('获取用户数据失败:', error);
                alert('获取用户数据失败，请稍后再试');
            }
        },
        addUser() {
            this.$emit('adminAdd');
        },
        handleDelete(row) {
            this.$confirm(`确定删除用户 ${row.username} 吗？`, '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(async () => {
                try {
                    const res = await this.$axios.delete('/deleteUser', {
                        data: { username: row.username }
                    });
                    alert(res.message || '用户删除成功');
                    this.getUsers();
                } catch (error) {
                    console.error('删除用户失败:', error);
                    alert('删除用户失败，请稍后再试');
                }
            }).catch(() => {
                alert('已取消删除');
            });
        },
    },
    mounted() {
        this.getUsers();
    },
}

</script>

<style scoped>
@import url('./style.css');
</style>