<template>
    <div>
        <el-row :gutter="20">
            <el-col :span="8" v-for="(item, index) in paginatedData" :key="index">
                <el-card>
                    <h4>{{ item.title }}</h4>
                    <div>{{ item.summary }}</div>
                    <el-tag v-for="tag in item.tags" :key="tag">{{ tag }}</el-tag>
                    <!-- More content here -->
                </el-card>
            </el-col>
        </el-row>
        <el-pagination layout="prev, pager, next" :total="data.length" :page-size="pageSize"
            @current-change="handlePageChange">
        </el-pagination>
    </div>
</template>

<script>
export default {
    name: 'pageOne',
    data() {
        return {
            // Mock data for the vulnerabilities cards
            data: [
                {
                    id: 1,
                    title: 'Wordpress插件Elementor XSS漏洞 (CVE-xxxx-xxxx)',
                    summary: 'Elementor存在一个XSS漏洞，更新插件版本...',
                    tags: ['Elementor', 'XSS'],
                    severity: 'High',
                    dateReported: '2022-01-15'
                },
                {
                    id: 2,
                    title: 'Webmin远程命令执行漏洞(CVE-2019-15107)',
                    summary: 'Webmin是一个用于管理类Unix系统的管理配置工具，具有Web页面。在其找回密码页面中，存在一处无需权限的命令注入漏洞，通过这个漏洞攻击者即可以执行任意系统命令。',
                    tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                    severity: 'Critical',
                    dateReported: '2022-02-20'
                },
                {
                    id: 3,
                    title: 'Zabbix SAML身份验证绕过漏洞 (CVE-zzzz-zzzz)',
                    summary: 'Zabbix存在一个影响SAML身份验证的漏洞...',
                    tags: ['Zabbix', 'PATH_DISCLOSURE'],
                    severity: 'Medium',
                    dateReported: '2022-03-10'
                },
                {
                    id: 4,
                    title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                    summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                    tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                    severity: 'Critical',
                    dateReported: '2022-02-20'
                },
                {
                    id: 5,
                    title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                    summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                    tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                    severity: 'Critical',
                    dateReported: '2022-02-20'
                },
                {
                    id: 6,
                    title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                    summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                    tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                    severity: 'Critical',
                    dateReported: '2022-02-20'
                },
                {
                    id: 7,
                    title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                    summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                    tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                    severity: 'Critical',
                    dateReported: '2022-02-20'
                },
                {
                    id: 8,
                    title: 'F5 BIG-IP未授权RCE漏洞 (CVE-yyyy-yyyy)',
                    summary: 'F5 BIG-IP Control REST存在一个未授权执行...',
                    tags: ['F5 BIG-IP', 'CODE_EXECUTION'],
                    severity: 'Critical',
                    dateReported: '2022-02-20'
                },
                // Add more objects for each card you want to display
            ],
            currentPage: 1,
            pageSize: 6 // Number of cards per page
        };
    },
    computed: {
        paginatedData() {
            let start = (this.currentPage - 1) * this.pageSize;
            let end = start + this.pageSize;
            return this.data.slice(start, end);
        }
    },
    methods: {
        handlePageChange(newPage) {
            this.currentPage = newPage;
        }
    }
};
</script>

<style scoped>
.el-row {
    display: flex;
    flex-wrap: wrap;
}

.el-col {
    display: flex;
    margin-bottom: 20px;
}

.el-card {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.el-card .el-card__body {
    flex-grow: 1;
    /* This makes the body of the card fill the space */
}
</style>