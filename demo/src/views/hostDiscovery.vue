<template>
  <div class="host-discovery">
    <el-card class="search-card">
      <div slot="header" class="card-header">
        <span class="title">主机发现</span>
      </div>

      <el-form :model="searchForm" :rules="rules" ref="searchForm" label-width="100px">
        <el-form-item label="IP/网段" prop="ipInput">
          <el-input v-model="searchForm.ipInput" placeholder="请输入 IP地址 (例如: 192.168.1.120) 或 网段 (例如: 192.168.1.0/24)"
            clearable @keyup.enter.native="handleSearch">
            <el-button slot="append" icon="el-icon-search" @click="handleSearch">搜索</el-button>
          </el-input>
        </el-form-item>
      </el-form>

      <!-- 搜索结果展示 -->
      <div class="result-section" v-loading="loading">
        <div class="result-header" v-if="totalHostsCount > 0">
          <span>发现 {{ totalHostsCount }} 个存活主机</span>

        </div>

        <!-- 按资产组分组展示扫描结果 -->
        <div v-if="Object.keys(groupedHosts).length" class="grouped-hosts">
          <div v-for="(hosts, groupName) in groupedHosts" :key="groupName" class="group-section">
            <div class="group-header" @click="toggleGroupExpanded(groupName)">
              <i :class="groupExpandedState[groupName] ? 'el-icon-arrow-down' : 'el-icon-arrow-right'"
                class="expand-icon">
              </i>
              <el-tag type="info" size="medium">{{ groupName }}</el-tag>
              <span class="group-count">{{ hosts.length }} 台主机</span>
            </div>

            <el-collapse-transition>
              <el-table v-show="groupExpandedState[groupName]" :data="hosts" border size="small"
                style="width: 100%; margin-bottom: 20px;" :header-cell-style="{ background: '#f8f9fa' }">
                <el-table-column prop="ip" label="IP地址" width="180">
                  <template slot-scope="scope">
                    <el-tag size="small">{{ scope.row.ip }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="100">
                  <template>
                    <el-tag type="success" size="small">存活</el-tag>
                  </template>
                </el-table-column>
                <!--                <el-table-column prop="lastSeen" label="发现时间">-->
                <!--                  <template slot-scope="scope">-->
                <!--                    {{ scope.row.lastSeen }}-->
                <!--                  </template>-->
                <!--                </el-table-column>-->
              </el-table>
            </el-collapse-transition>
          </div>
        </div>

        <el-empty v-else-if="!loading && searched" description="未发现存活主机">
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script>
import 'jspdf-autotable'

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
      groupedHosts: {}, // 按资产组分组的主机 { groupName: [hosts] }
      totalHostsCount: 0,
      groupExpandedState: {}, // 各组的展开/折叠状态 { groupName: boolean }
      allHosts: [] // 用于导出PDF和存储到localStorage
    }
  },
  methods: {
    // 加载之前保存的主机发现结果
    loadPreviousResults() {
      const savedData = sessionStorage.getItem('hostdiscoveryjson')
      if (savedData) {
        try {
          const parsedData = JSON.parse(savedData)
          // 处理保存的分组数据
          this.processGroupedData(parsedData.groups)
          this.searched = true // 标记为已搜索状态
          console.log('已加载之前的主机发现结果')
        } catch (error) {
          console.error('加载之前的结果失败:', error)
          // 如果数据损坏，清除该项
          sessionStorage.removeItem('hostdiscoveryjson')
        }
      }
    },
    async handleSearch() {
      this.$refs.searchForm.validate(async (valid) => {
        if (valid) {

          this.loading = true
          this.searched = true
          try {
            const response = await this.$axios.post(
              `/api/host_discovery?network=${this.searchForm.ipInput}`
            )

            // 处理返回的分组数据
            this.processGroupedData(response.data.groups)

            // 保存完整的响应数据到sessionStorage
            sessionStorage.setItem('hostdiscoveryjson', JSON.stringify(response.data))


            const storedIps = sessionStorage.getItem('nmapIps');
            if (storedIps) {
              this.historyIps = JSON.parse(storedIps);
              this.historyIps.forEach(ip => {
                sessionStorage.removeItem(`nmapResults-${ip}`);
              });
            }

            const a = sessionStorage.getItem('hostdiscovery');
            if (a) {
              this.b = JSON.parse(a);
              this.b.forEach(ip => {
                const resultKey = `weakpassword-${ip}`;
                if (sessionStorage.getItem(resultKey) !== null) {
                  sessionStorage.removeItem(resultKey);
                }
              });
            }


            sessionStorage.removeItem(`nmapIps`);


            // 保存所有主机到localStorage
            this.saveHostsToLocalStorage()

            this.$message.success(`发现 ${this.totalHostsCount} 个存活主机`)

          } catch (error) {
            this.$message.error('扫描失败：' + (error.response?.data || error.message))
          } finally {
            this.loading = false
          }
        }
      })
    },

    // 处理分组数据
    processGroupedData(groups) {
      this.groupedHosts = {}
      this.allHosts = []
      this.totalHostsCount = 0

      const currentTime = new Date().toLocaleString()

      groups.forEach(group => {
        const groupName = group.group_name
        const hosts = group.hosts.map(ip => ({
          ip: ip,
          status: '存活',
          lastSeen: currentTime,
          group_id: group.group_id,
          group_name: groupName
        }))

        this.groupedHosts[groupName] = hosts
        this.allHosts.push(...hosts)
        this.totalHostsCount += hosts.length

        // 设置默认展开状态
        this.$set(this.groupExpandedState, groupName, true)
      })

      // 对每个组内的主机按IP排序
      Object.keys(this.groupedHosts).forEach(groupName => {
        this.groupedHosts[groupName].sort((a, b) => {
          const aIp = a.ip.split('.').map(num => parseInt(num, 10))
          const bIp = b.ip.split('.').map(num => parseInt(num, 10))
          for (let i = 0; i < 4; i++) {
            if (aIp[i] !== bIp[i]) {
              return aIp[i] - bIp[i]
            }
          }
          return 0
        })
      })
    },

    // 保存主机数据到localStorage
    saveHostsToLocalStorage() {
      const hostIPs = this.allHosts.map(host => host.ip)
      sessionStorage.setItem('hostdiscovery', JSON.stringify(hostIPs))
    },

    // 切换组展开状态
    toggleGroupExpanded(groupName) {
      this.$set(this.groupExpandedState, groupName, !this.groupExpandedState[groupName])
    },
  },
  mounted() {
    // 检查sessionStorage中是否有之前的主机发现结果
    this.loadPreviousResults()
    // 页面加载时不执行任何数据获取，保持空白状态
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

/* 资产组分组展示样式 */
.grouped-hosts {
  margin-top: 15px;
}

.group-section {
  margin-bottom: 25px;
}

.group-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.group-header:hover {
  background-color: #f0f0f0;
}

.expand-icon {
  margin-right: 8px;
  color: #666;
  transition: transform 0.2s;
  font-size: 14px;
}

.group-count {
  margin-left: 10px;
  color: #666;
  font-size: 14px;
}
</style>