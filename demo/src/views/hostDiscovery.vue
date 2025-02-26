

<!-- HostDiscovery.vue -->
<template>
  <div class="host-discovery">
    <el-card class="search-card">
      <div slot="header" class="card-header">
        <span class="title">主机发现</span>
      </div>

      <el-form :model="searchForm" :rules="rules" ref="searchForm" label-width="100px">
        <el-form-item label="IP/网段" prop="ipInput">
          <el-input
              v-model="searchForm.ipInput"
              placeholder="请输入IP地址或网段(例如: 192.168.1.0/24)"
              clearable
              @keyup.enter.native="handleSearch">
            <el-button slot="append" icon="el-icon-search" @click="handleSearch">搜索</el-button>
          </el-input>
        </el-form-item>
      </el-form>

      <!-- 搜索结果展示 -->
      <div class="result-section" v-loading="loading">
        <div class="result-header" v-if="hostList.length">
          <span>发现 {{ hostList.length }} 个存活主机</span>
          <!--          <el-button type="text" icon="el-icon-download" @click="exportResults">-->
          <!--            导出结果-->
          <!--          </el-button>-->
        </div>

        <el-table
            v-if="hostList.length"
            :data="hostList"
            border
            style="width: 100%"
            :header-cell-style="{ background: '#f5f7fa' }">
          <el-table-column prop="ip" label="IP地址" width="180">
            <template slot-scope="scope">
              <el-tag size="medium">{{ scope.row.ip }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template>
              <el-tag type="success" size="small">存活</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="lastSeen" label="发现时间">
            <template slot-scope="scope">
              {{ scope.row.lastSeen }}
            </template>
          </el-table-column>
        </el-table>

        <el-empty
            v-else-if="!loading && searched"
            description="未发现存活主机">
        </el-empty>
      </div>
    </el-card>

    <!-- 所有存活主机列表卡片 -->
    <el-card class="all-hosts-card">
      <div slot="header" class="card-header">
        <span class="title" style="margin-right: 12px;">所有存活主机列表</span>
        <el-button
            type="default"
            plain
            size="small"
            icon="el-icon-refresh"
            @click="fetchAllAliveHosts"
            style="background: white; border-color: #eee;"
        >刷新</el-button>
      </div>

      <!--      <div slot="header" class="card-header">-->
<!--        <span class="title">所有存活主机列表</span>-->
<!--        <el-button type="primary" size="small" icon="el-icon-refresh" @click="fetchAllAliveHosts">刷新</el-button>-->
<!--      </div>-->

      <div class="result-section" v-loading="allHostsLoading">
        <div class="result-header" v-if="allHostsList.length">
          <span>当前共有 {{ allHostsList.length }} 个存活主机</span>
          <el-button type="text" icon="el-icon-download" @click="exportAllHostsResults">
            导出结果
          </el-button>
        </div>

        <el-table
            v-if="allHostsList.length"
            :data="allHostsList"
            border
            style="width: 100%"
            :header-cell-style="{ background: '#f5f7fa' }">
          <el-table-column prop="ip" label="IP地址" width="180">
            <template slot-scope="scope">
              <el-tag size="medium">{{ scope.row.ip }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template>
              <el-tag type="success" size="small">存活</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
            v-else-if="!allHostsLoading"
            description="当前没有存活主机记录">
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HostDiscovery',
  data() {
    // IP地址/网段验证规则
    const validateIP = (rule, value, callback) => {
      const ipRegex = /^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/
      if (!value) {
        callback(new Error('请输入IP地址或网段'))
      } else if (!ipRegex.test(value)) {
        callback(new Error('请输入正确的IP地址或网段格式'))
      } else {
        callback()
      }
    }

    return {
      searchForm: {
        ipInput: ''
      },
      rules: {
        ipInput: [
          { required: true, trigger: 'blur', validator: validateIP }
        ]
      },
      loading: false,
      searched: false,
      hostList: [],
      // 新增字段：所有存活主机列表相关
      allHostsList: [],
      allHostsLoading: false
    }
  },
  methods: {
    handleSearch() {
      this.$refs.searchForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          this.searched = true
          try {


            // 错误的写法，当network为10.9.130.0/24会将请求变成/api/host_discovery?network=10.9.130.0%2F24
            // const response = await axios.post(
            //     `/api/host_discovery?network=${encodeURIComponent(this.searchForm.ipInput)}` // 将 network 作为 URL 参数
            // )
            //正确的写法
            const response = await axios.post(
                '/api/host_discovery?network=' + this.searchForm.ipInput // 将 network 作为 URL 参数
            )

            //后端写的不在请求体中 在url中
            // const response = await axios.post(
            //     '/api/host_discovery', {
            //       network: this.searchForm.ipInput
            //     }
            // )

            // 处理返回的数据格式
            this.hostList = response.data.alive_hosts.map(ip => ({
              ip,
              lastSeen: new Date().toLocaleString()
            }))
          } catch (error) {
            this.$message.error('搜索失败：' + (error.response?.data?.message || error.message))
          } finally {
            this.loading = false
          }
        }
      })
    },
    exportResults() {
      const data = this.hostList.map(host => ({
        IP地址: host.ip,
        状态: '存活',
        发现时间: host.lastSeen
      }))

      // 创建CSV内容
      const csvContent = [
        Object.keys(data[0]).join(','),
        ...data.map(row => Object.values(row).join(','))
      ].join('\n')

      // 创建下载链接
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `主机扫描结果_${new Date().toLocaleDateString()}.csv`
      link.click()
    },
    // 获取所有存活主机列表
    async fetchAllAliveHosts() {
      this.allHostsLoading = true
      try {
        const response = await axios.get('/api/getAliveHosts')
        // 处理返回的数据格式
        this.allHostsList = response.data.alive_hosts.map(ip => ({
          ip
        }))
        this.$message.success('获取存活主机列表成功');
      } catch (error) {
        this.$message.error('获取存活主机列表失败：' + (error.response?.data?.message || error.message))
      } finally {
        this.allHostsLoading = false
      }
    },
    // 导出所有存活主机列表
    exportAllHostsResults() {
      const data = this.allHostsList.map(host => ({
        IP地址: host.ip,
        状态: '存活'
      }))

      // 创建CSV内容
      const csvContent = [
        Object.keys(data[0]).join(','),
        ...data.map(row => Object.values(row).join(','))
      ].join('\n')

      // 创建下载链接
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `所有存活主机列表_${new Date().toLocaleDateString()}.csv`
      link.click()
    }
  },
  mounted() {
    this.fetchAllAliveHosts()
  }
}
</script>

<style scoped>
.host-discovery {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.result-section {
  margin-top: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 0 10px;
}

.el-table {
  margin-top: 15px;
}

.el-tag {
  margin-right: 5px;
}
</style>

<!--&lt;!&ndash; HostDiscovery.vue &ndash;&gt;-->
<!--<template>-->
<!--  <div class="host-discovery">-->
<!--    <el-card class="search-card">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span class="title">主机发现</span>-->
<!--      </div>-->

<!--      <el-form :model="searchForm" :rules="rules" ref="searchForm" label-width="100px">-->
<!--        <el-form-item label="IP/网段" prop="ipInput">-->
<!--          <el-input-->
<!--              v-model="searchForm.ipInput"-->
<!--              placeholder="请输入IP地址或网段(例如: 192.168.1.0/24)"-->
<!--              clearable-->
<!--              @keyup.enter.native="handleSearch">-->
<!--            <el-button slot="append" icon="el-icon-search" @click="handleSearch">搜索</el-button>-->
<!--          </el-input>-->
<!--        </el-form-item>-->
<!--      </el-form>-->

<!--      &lt;!&ndash; 搜索结果展示 &ndash;&gt;-->
<!--      <div class="result-section" v-loading="loading">-->
<!--        <div class="result-header" v-if="hostList.length">-->
<!--          <span>发现 {{ hostList.length }} 个存活主机</span>-->
<!--&lt;!&ndash;          <el-button type="text" icon="el-icon-download" @click="exportResults">&ndash;&gt;-->
<!--&lt;!&ndash;            导出结果&ndash;&gt;-->
<!--&lt;!&ndash;          </el-button>&ndash;&gt;-->
<!--        </div>-->

<!--        <el-table-->
<!--            v-if="hostList.length"-->
<!--            :data="hostList"-->
<!--            border-->
<!--            style="width: 100%"-->
<!--            :header-cell-style="{ background: '#f5f7fa' }">-->
<!--          <el-table-column prop="ip" label="IP地址" width="180">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag size="medium">{{ scope.row.ip }}</el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="status" label="状态" width="100">-->
<!--            <template>-->
<!--              <el-tag type="success" size="small">存活</el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="lastSeen" label="发现时间">-->
<!--            <template slot-scope="scope">-->
<!--              {{ scope.row.lastSeen }}-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->

<!--        <el-empty-->
<!--            v-else-if="!loading && searched"-->
<!--            description="未发现存活主机">-->
<!--        </el-empty>-->
<!--      </div>-->
<!--    </el-card>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios'-->

<!--export default {-->
<!--  name: 'HostDiscovery',-->
<!--  data() {-->
<!--    // IP地址/网段验证规则-->
<!--    const validateIP = (rule, value, callback) => {-->
<!--      const ipRegex = /^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/-->
<!--      if (!value) {-->
<!--        callback(new Error('请输入IP地址或网段'))-->
<!--      } else if (!ipRegex.test(value)) {-->
<!--        callback(new Error('请输入正确的IP地址或网段格式'))-->
<!--      } else {-->
<!--        callback()-->
<!--      }-->
<!--    }-->

<!--    return {-->
<!--      searchForm: {-->
<!--        ipInput: ''-->
<!--      },-->
<!--      rules: {-->
<!--        ipInput: [-->
<!--          { required: true, trigger: 'blur', validator: validateIP }-->
<!--        ]-->
<!--      },-->
<!--      loading: false,-->
<!--      searched: false,-->
<!--      hostList: []-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    handleSearch() {-->
<!--      this.$refs.searchForm.validate(async (valid) => {-->
<!--        if (valid) {-->
<!--          this.loading = true-->
<!--          this.searched = true-->
<!--          try {-->


<!--            // 错误的写法，当network为10.9.130.0/24会将请求变成/api/host_discovery?network=10.9.130.0%2F24-->
<!--            // const response = await axios.post(-->
<!--            //     `/api/host_discovery?network=${encodeURIComponent(this.searchForm.ipInput)}` // 将 network 作为 URL 参数-->
<!--            // )-->
<!--            //正确的写法-->
<!--            const response = await axios.post(-->
<!--                '/api/host_discovery?network=' + this.searchForm.ipInput // 将 network 作为 URL 参数-->
<!--            )-->

<!--            //后端写的不在请求体中 在url中-->
<!--            // const response = await axios.post(-->
<!--            //     '/api/host_discovery', {-->
<!--            //       network: this.searchForm.ipInput-->
<!--            //     }-->
<!--            // )-->

<!--            // 处理返回的数据格式-->
<!--            this.hostList = response.data.alive_hosts.map(ip => ({-->
<!--              ip,-->
<!--              lastSeen: new Date().toLocaleString()-->
<!--            }))-->
<!--          } catch (error) {-->
<!--            this.$message.error('搜索失败：' + (error.response?.data?.message || error.message))-->
<!--          } finally {-->
<!--            this.loading = false-->
<!--          }-->
<!--        }-->
<!--      })-->
<!--    },-->
<!--    exportResults() {-->
<!--      const data = this.hostList.map(host => ({-->
<!--        IP地址: host.ip,-->
<!--        状态: '存活',-->
<!--        发现时间: host.lastSeen-->
<!--      }))-->

<!--      // 创建CSV内容-->
<!--      const csvContent = [-->
<!--        Object.keys(data[0]).join(','),-->
<!--        ...data.map(row => Object.values(row).join(','))-->
<!--      ].join('\n')-->

<!--      // 创建下载链接-->
<!--      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })-->
<!--      const link = document.createElement('a')-->
<!--      link.href = URL.createObjectURL(blob)-->
<!--      link.download = `主机扫描结果_${new Date().toLocaleDateString()}.csv`-->
<!--      link.click()-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.host-discovery {-->
<!--  padding: 20px;-->
<!--}-->

<!--.search-card {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.card-header {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--}-->

<!--.title {-->
<!--  font-size: 18px;-->
<!--  font-weight: bold;-->
<!--}-->

<!--.result-section {-->
<!--  margin-top: 20px;-->
<!--}-->

<!--.result-header {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  margin-bottom: 15px;-->
<!--  padding: 0 10px;-->
<!--}-->

<!--.el-table {-->
<!--  margin-top: 15px;-->
<!--}-->

<!--.el-tag {-->
<!--  margin-right: 5px;-->
<!--}-->
<!--</style>-->