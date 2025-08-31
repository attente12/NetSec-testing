<template>
    <el-container>
        <el-header style="text-align: center;"><h1>{{ reportName }} Linux安全策略核查</h1></el-header>

        <el-main>
            <h2>服务器基本信息</h2>
            <el-table :data="[serverInfo]" style="width: 100%">
                <el-table-column prop="hostname" label="主机名"></el-table-column>
                <el-table-column prop="arch" label="操作系统位数"></el-table-column>
                <el-table-column prop="cpu" label="CPU型号"></el-table-column>
                <el-table-column prop="cpuPhysical" label="CPU个数"></el-table-column>
                <el-table-column prop="cpuCore" label="CPU核数"></el-table-column>
                <el-table-column prop="free" label="共计内存/G"></el-table-column>
                <el-table-column prop="productName" label="硬件型号"></el-table-column>
                <el-table-column prop="version" label="系统版本"></el-table-column>
                <el-table-column prop="ping" label="联网检测"></el-table-column>
            </el-table>

            <h2>用户信息</h2>
            <el-table :data="users" style="width: 100%" row-key="uid">
                <el-table-column prop="name" label="用户"></el-table-column>
                <el-table-column prop="passwd" label="密码状态" :formatter="formatPasswd"></el-table-column>
                <!-- Add more columns, using custom formatters or scoped slots for complex rendering -->
            </el-table>
        </el-main>
    </el-container>
</template>

<script>
    export default {
        name: 'SecurityCheck',
        data() {
            return {
                reportName: 'YourServerName',
                serverInfo: {
                    hostname: 'Server1',
                    arch: '64-bit',
                    cpu: 'Intel Xeon',
                    cpuPhysical: 1,
                    cpuCore: 1,
                    free: 64,
                    productName: "VMware Virtual Platform",
                    version: "Your System Version",
                    ping: "true"
                },
                users: [
                    {
                        uid: 1,
                        name: 'User1',
                        passwd: 'PS',
                        // Add more user properties as needed
                    },
                    // Add more users as needed
                ]
            };
        },
        methods: {
            formatPasswd(row, column, value) {
                // Customize this method to return formatted password status
                return value === 'PS' ? '正常' : '异常';
            },
        },
    };
</script>

<style>
    /* Add CSS styling as needed */
</style>
