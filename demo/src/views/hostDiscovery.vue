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
              placeholder="请输入 IP地址 (例如: 192.168.1.120) 或 网段 (例如: 192.168.1.0/24)"
              clearable
              @keyup.enter.native="handleSearch">
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
              <i
                  :class="groupExpandedState[groupName] ? 'el-icon-arrow-down' : 'el-icon-arrow-right'"
                  class="expand-icon">
              </i>
              <el-tag type="info" size="medium">{{ groupName }}</el-tag>
              <span class="group-count">{{ hosts.length }} 台主机</span>
            </div>

            <el-collapse-transition>
              <el-table
                  v-show="groupExpandedState[groupName]"
                  :data="hosts"
                  border
                  size="small"
                  style="width: 100%; margin-bottom: 20px;"
                  :header-cell-style="{ background: '#f8f9fa' }">
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

        <el-empty
            v-else-if="!loading && searched"
            description="未发现存活主机">
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
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
            const response = await axios.post(
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

<!-- 展示所有主机发现结果的版本 -->
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
<!--              placeholder="请输入 IP地址 (例如: 192.168.1.120) 或 网段 (例如: 192.168.1.0/24)"-->
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
<!--          <div>-->
<!--            <el-button type="text" icon="el-icon-document" @click="exportPDF">-->
<!--              导出PDF-->
<!--            </el-button>-->
<!--          </div>-->
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

<!--    &lt;!&ndash; 主机列表卡片 - 按资产组分组展示 &ndash;&gt;-->
<!--    <el-card class="all-hosts-card">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span class="title" style="margin-right: 12px;">主机列表</span>-->
<!--        <el-button-->
<!--            type="default"-->
<!--            plain-->
<!--            size="small"-->
<!--            icon="el-icon-refresh"-->
<!--            @click="fetchHostsAndGroups"-->
<!--            style="background: white; border-color: #eee;"-->
<!--        >刷新</el-button>-->
<!--      </div>-->
<!--      <div class="result-section" v-loading="allHostsLoading">-->
<!--        <div class="result-header" v-if="Object.keys(groupedHosts).length">-->
<!--          <span>当前共有 {{ totalHostsCount }} 个主机</span>-->
<!--        </div>-->

<!--        &lt;!&ndash; 按资产组分组展示 &ndash;&gt;-->
<!--        <div v-if="Object.keys(groupedHosts).length" class="grouped-hosts">-->
<!--          <div v-for="(hosts, groupName) in groupedHosts" :key="groupName" class="group-section">-->
<!--            <div class="group-header" @click="toggleGroupExpanded(groupName)">-->
<!--              <i-->
<!--                  :class="groupExpandedState[groupName] ? 'el-icon-arrow-down' : 'el-icon-arrow-right'"-->
<!--                  class="expand-icon">-->
<!--              </i>-->
<!--              <el-tag type="info" size="medium">{{ groupName }}</el-tag>-->
<!--              <span class="group-count">{{ hosts.length }} 台主机</span>-->
<!--            </div>-->

<!--            <el-collapse-transition>-->
<!--              <el-table-->
<!--                  v-show="groupExpandedState[groupName]"-->
<!--                  :data="hosts"-->
<!--                  border-->
<!--                  size="small"-->
<!--                  style="width: 100%; margin-bottom: 20px;"-->
<!--                  :header-cell-style="{ background: '#f8f9fa' }">-->
<!--                <el-table-column prop="ip" label="IP地址" width="180">-->
<!--                  <template slot-scope="scope">-->
<!--                    <el-tag size="small">{{ scope.row.ip }}</el-tag>-->
<!--                  </template>-->
<!--                </el-table-column>-->
<!--                <el-table-column prop="alive" label="状态" width="100">-->
<!--                  <template slot-scope="scope">-->
<!--                    <el-tag-->
<!--                        :type="scope.row.alive ? 'success' : 'danger'"-->
<!--                        size="small">-->
<!--                      {{ scope.row.alive ? '存活' : '离线' }}-->
<!--                    </el-tag>-->
<!--                  </template>-->
<!--                </el-table-column>-->
<!--              </el-table>-->
<!--            </el-collapse-transition>-->
<!--          </div>-->
<!--        </div>-->

<!--        <el-empty-->
<!--            v-else-if="!allHostsLoading"-->
<!--            description="当前没有主机记录">-->
<!--        </el-empty>-->
<!--      </div>-->
<!--    </el-card>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios'-->
<!--import jsPDF from 'jspdf'-->
<!--import 'jspdf-autotable'-->

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
<!--      hostList: [],-->
<!--      // 修改后的字段：主机列表和资产组相关-->
<!--      allHostsList: [],-->
<!--      allHostsLoading: false,-->
<!--      assetGroups: {},  // 资产组映射 { id: name }-->
<!--      groupedHosts: {}, // 按资产组分组的主机 { groupName: [hosts] }-->
<!--      totalHostsCount: 0,-->
<!--      groupExpandedState: {} // 各组的展开/折叠状态 { groupName: boolean }-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    handleSearch() {-->
<!--      this.$refs.searchForm.validate(async (valid) => {-->
<!--        if (valid) {-->
<!--          this.loading = true-->
<!--          this.searched = true-->
<!--          try {-->
<!--            const response = await axios.post(-->
<!--                '/api/host_discovery?network=' + this.searchForm.ipInput-->
<!--            )-->
<!--            this.hostList = response.data.alive_hosts.map(ip => ({-->
<!--              ip,-->
<!--              lastSeen: new Date().toLocaleString()-->
<!--            }))-->
<!--          } catch (error) {-->
<!--            this.$message.error('error：' + (error.response.data))-->
<!--          } finally {-->
<!--            this.loading = false-->
<!--          }-->
<!--        }-->
<!--      })-->
<!--    },-->

<!--    // 获取资产组列表-->
<!--    async fetchAssetGroups() {-->
<!--      try {-->
<!--        const response = await axios.get('/api/asset_group/list')-->
<!--        // 构建资产组映射-->
<!--        this.assetGroups = {}-->
<!--        response.data.forEach(group => {-->
<!--          this.assetGroups[group.id] = group.name-->
<!--        })-->
<!--      } catch (error) {-->
<!--        console.error('获取资产组失败:', error)-->
<!--        this.$message.error('获取资产组失败：' + (error.response?.data?.message || error.message))-->
<!--      }-->
<!--    },-->

<!--    // 获取主机完整信息-->
<!--    async fetchHostsInfo() {-->
<!--      this.allHostsLoading = true-->
<!--      try {-->
<!--        const response = await axios.get('/api/assets/full_info')-->
<!--        this.allHostsList = response.data.map(host => ({-->
<!--          ip: host.ip,-->
<!--          alive: host.alive,-->
<!--          group_id: host.group_id,-->
<!--          group_name: this.assetGroups[host.group_id] || '未分组'-->
<!--        }))-->

<!--        // 按资产组分组-->
<!--        this.groupHostsByAssetGroup()-->
<!--        this.totalHostsCount = this.allHostsList.length-->

<!--        this.$message.success('获取主机列表成功')-->
<!--      } catch (error) {-->
<!--        this.$message.error('获取主机列表失败：' + (error.response?.data?.message || error.message))-->
<!--      } finally {-->
<!--        this.allHostsLoading = false-->
<!--      }-->
<!--    },-->
<!--    // 改进的切换方法-->
<!--    toggleGroupExpanded(groupName) {-->
<!--      // 使用 Vue.set 确保响应式更新-->
<!--      this.$set(this.groupExpandedState, groupName, !this.groupExpandedState[groupName])-->
<!--    },-->

<!--    // 改进的分组方法-->
<!--    groupHostsByAssetGroup() {-->
<!--      this.groupedHosts = {}-->

<!--      // 先收集所有组名-->
<!--      const allGroups = [...new Set(this.allHostsList.map(host => host.group_name))]-->

<!--      // 初始化展开状态-->
<!--      const newExpandedState = {}-->
<!--      allGroups.forEach(groupName => {-->
<!--        newExpandedState[groupName] = true // 默认展开-->
<!--      })-->

<!--      // 一次性设置展开状态-->
<!--      this.groupExpandedState = newExpandedState-->

<!--      // 分组主机-->
<!--      this.allHostsList.forEach(host => {-->
<!--        const groupName = host.group_name-->
<!--        if (!this.groupedHosts[groupName]) {-->
<!--          this.groupedHosts[groupName] = []-->
<!--        }-->
<!--        this.groupedHosts[groupName].push(host)-->
<!--      })-->

<!--      // 对每个组内的主机按IP排序-->
<!--      Object.keys(this.groupedHosts).forEach(groupName => {-->
<!--        this.groupedHosts[groupName].sort((a, b) => {-->
<!--          const aIp = a.ip.split('.').map(num => parseInt(num, 10))-->
<!--          const bIp = b.ip.split('.').map(num => parseInt(num, 10))-->
<!--          for (let i = 0; i < 4; i++) {-->
<!--            if (aIp[i] !== bIp[i]) {-->
<!--              return aIp[i] - bIp[i]-->
<!--            }-->
<!--          }-->
<!--          return 0-->
<!--        })-->
<!--      })-->
<!--    },-->

<!--    // 获取主机和资产组信息-->
<!--    async fetchHostsAndGroups() {-->
<!--      await this.fetchAssetGroups()-->
<!--      await this.fetchHostsInfo()-->
<!--    },-->

<!--    // 导出PDF函数 - 搜索结果-->
<!--    exportPDF() {-->
<!--      try {-->
<!--        const doc = new jsPDF({-->
<!--          orientation: 'portrait',-->
<!--          unit: 'mm',-->
<!--          format: 'a4'-->
<!--        });-->

<!--        const tableData = this.hostList.map(host => [host.ip, 'Active']);-->

<!--        doc.autoTable({-->
<!--          head: [['IP Address', 'Status']],-->
<!--          body: tableData,-->
<!--          startY: 40,-->
<!--          theme: 'grid',-->
<!--          styles: {-->
<!--            fontSize: 10,-->
<!--            cellPadding: 3,-->
<!--            lineWidth: 0.5,-->
<!--            lineColor: [0, 0, 0]-->
<!--          },-->
<!--          headStyles: {-->
<!--            fillColor: [240, 240, 240],-->
<!--            textColor: [0, 0, 0],-->
<!--            fontStyle: 'bold'-->
<!--          }-->
<!--        });-->

<!--        this.addChineseTextAsImage(doc, '存活主机列表', 105, 20, 18, 'center');-->

<!--        const currentTime = new Date().toLocaleString();-->
<!--        this.addChineseTextAsImage(doc, `打印时间: ${currentTime}`, 105, 30, 10, 'center');-->

<!--        doc.save(`主机扫描结果_${new Date().toLocaleDateString()}.pdf`);-->
<!--      } catch (error) {-->
<!--        console.error('导出PDF出错:', error);-->
<!--        this.$message.error('导出PDF失败: ' + error.message);-->
<!--      }-->
<!--    },-->

<!--    // 辅助方法：将中文文本转为canvas图像，然后添加到PDF-->
<!--    addChineseTextAsImage(doc, text, x, y, fontSize, align) {-->
<!--      const canvas = document.createElement('canvas');-->
<!--      const ctx = canvas.getContext('2d');-->

<!--      const scale = 4;-->

<!--      ctx.font = `${fontSize * scale}px "Microsoft YaHei", SimHei, Arial, sans-serif`;-->

<!--      const textWidth = ctx.measureText(text).width;-->

<!--      canvas.width = textWidth + 40 * scale;-->
<!--      canvas.height = fontSize * 2 * scale;-->

<!--      ctx.scale(scale, scale);-->

<!--      ctx.font = `${fontSize}px "Microsoft YaHei", SimHei, Arial, sans-serif`;-->
<!--      ctx.textBaseline = 'middle';-->

<!--      ctx.fillStyle = 'white';-->
<!--      ctx.fillRect(0, 0, canvas.width / scale, canvas.height / scale);-->

<!--      ctx.fillStyle = 'black';-->

<!--      let textX = 20;-->
<!--      if (align === 'center') {-->
<!--        ctx.textAlign = 'center';-->
<!--        textX = (canvas.width / scale) / 2;-->
<!--      }-->

<!--      ctx.fillText(text, textX, (canvas.height / scale) / 2);-->

<!--      const imgData = canvas.toDataURL('image/png');-->

<!--      let posX = x;-->
<!--      if (align === 'center') {-->
<!--        posX = doc.internal.pageSize.getWidth() / 2;-->
<!--      }-->

<!--      doc.addImage(imgData, 'PNG', posX - (canvas.width / scale / 2) * 0.264583, y - (canvas.height / scale / 2) * 0.264583, (canvas.width / scale) * 0.264583, (canvas.height / scale) * 0.264583);-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchHostsAndGroups()-->
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

<!--/* 新增样式：资产组分组展示 */-->
<!--.grouped-hosts {-->
<!--  margin-top: 15px;-->
<!--}-->

<!--.group-section {-->
<!--  margin-bottom: 25px;-->
<!--}-->

<!--.group-header {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  margin-bottom: 10px;-->
<!--  padding: 10px;-->
<!--  background-color: #fafafa;-->
<!--  border-radius: 4px;-->
<!--  cursor: pointer;-->
<!--  user-select: none;-->
<!--  transition: background-color 0.2s;-->
<!--}-->

<!--.group-header:hover {-->
<!--  background-color: #f0f0f0;-->
<!--}-->

<!--.expand-icon {-->
<!--  margin-right: 8px;-->
<!--  color: #666;-->
<!--  transition: transform 0.2s;-->
<!--  font-size: 14px;-->
<!--}-->

<!--.group-count {-->
<!--  margin-left: 10px;-->
<!--  color: #666;-->
<!--  font-size: 14px;-->
<!--}-->
<!--</style>-->


<!--版本：未展示资产组的版本-->
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
<!--              placeholder="请输入 IP地址 (例如: 192.168.1.120) 或 网段 (例如: 192.168.1.0/24)"-->
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
<!--          <div>-->
<!--            &lt;!&ndash;          <el-button type="text" icon="el-icon-download" @click="exportResults">&ndash;&gt;-->
<!--            &lt;!&ndash;            导出结果&ndash;&gt;-->
<!--            &lt;!&ndash;          </el-button>&ndash;&gt;-->
<!--            <el-button type="text" icon="el-icon-document" @click="exportPDF">-->
<!--              导出PDF-->
<!--            </el-button>-->
<!--          </div>-->
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

<!--    &lt;!&ndash; 所有存活主机列表卡片 &ndash;&gt;-->
<!--    <el-card class="all-hosts-card">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span class="title" style="margin-right: 12px;">所有存活主机列表</span>-->
<!--        <el-button-->
<!--            type="default"-->
<!--            plain-->
<!--            size="small"-->
<!--            icon="el-icon-refresh"-->
<!--            @click="fetchAllAliveHosts"-->
<!--            style="background: white; border-color: #eee;"-->
<!--        >刷新</el-button>-->
<!--      </div>-->
<!--      <div class="result-section" v-loading="allHostsLoading">-->
<!--        <div class="result-header" v-if="allHostsList.length">-->
<!--          <span>当前共有 {{ allHostsList.length }} 个存活主机</span>-->

<!--        </div>-->

<!--        <el-table-->
<!--            v-if="allHostsList.length"-->
<!--            :data="allHostsList"-->
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
<!--        </el-table>-->

<!--        <el-empty-->
<!--            v-else-if="!allHostsLoading"-->
<!--            description="当前没有存活主机记录">-->
<!--        </el-empty>-->
<!--      </div>-->
<!--    </el-card>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios'-->
<!--import jsPDF from 'jspdf'-->
<!--import 'jspdf-autotable'-->

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
<!--      hostList: [],-->
<!--      // 新增字段：所有存活主机列表相关-->
<!--      allHostsList: [],-->
<!--      allHostsLoading: false-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    handleSearch() {-->
<!--      this.$refs.searchForm.validate(async (valid) => {-->
<!--        if (valid) {-->
<!--          this.loading = true-->
<!--          this.searched = true-->
<!--          try {-->

<!--            const response = await axios.post(-->
<!--                '/api/host_discovery?network=' + this.searchForm.ipInput // 将 network 作为 URL 参数-->
<!--            )-->
<!--            // 处理返回的数据格式-->
<!--            this.hostList = response.data.alive_hosts.map(ip => ({-->
<!--              ip,-->
<!--              lastSeen: new Date().toLocaleString()-->
<!--            }))-->
<!--          } catch (error) {-->
<!--            this.$message.error('error：' + (error.response.data))-->
<!--            //this.$message.error('搜索失败：' + (error.response.data?.message || error.message))-->
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
<!--    },-->
<!--    // 获取所有存活主机列表-->
<!--    async fetchAllAliveHosts() {-->
<!--      this.allHostsLoading = true-->
<!--      try {-->
<!--        const response = await axios.get('/api/getAliveHosts')-->
<!--        // 处理返回的数据格式-->
<!--        this.allHostsList = response.data.alive_hosts.map(ip => ({-->
<!--          ip-->
<!--        }))-->
<!--        this.$message.success('获取存活主机列表成功');-->
<!--      } catch (error) {-->
<!--        this.$message.error('获取存活主机列表失败：' + (error.response?.data?.message || error.message))-->
<!--      } finally {-->
<!--        this.allHostsLoading = false-->
<!--      }-->
<!--    },-->
<!--    // 导出所有存活主机列表-->
<!--    exportAllHostsResults() {-->
<!--      const data = this.allHostsList.map(host => ({-->
<!--        IP地址: host.ip,-->
<!--        状态: '存活'-->
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
<!--      link.download = `所有存活主机列表_${new Date().toLocaleDateString()}.csv`-->
<!--      link.click()-->
<!--    },-->

<!--    // 导出PDF函数 - 搜索结果-->
<!--    exportPDF() {-->
<!--      try {-->
<!--        // 创建一个支持中文的PDF-->
<!--        const doc = new jsPDF({-->
<!--          orientation: 'portrait',-->
<!--          unit: 'mm',-->
<!--          format: 'a4'-->
<!--        });-->

<!--        // 获取默认字体，仅用于英文内容-->
<!--        //const defaultFont = doc.getFontList().helvetica;-->

<!--        // 创建表格数据（仅IP地址和存活状态）-->
<!--        const tableData = this.hostList.map(host => [host.ip, 'Active']);-->

<!--        // 首先创建一个简单的表格，包含英文内容-->
<!--        doc.autoTable({-->
<!--          head: [['IP Address', 'Status']],-->
<!--          body: tableData,-->
<!--          startY: 40,-->
<!--          theme: 'grid',-->
<!--          styles: {-->
<!--            fontSize: 10,-->
<!--            cellPadding: 3,-->
<!--            lineWidth: 0.5,-->
<!--            lineColor: [0, 0, 0]-->
<!--          },-->
<!--          headStyles: {-->
<!--            fillColor: [240, 240, 240],-->
<!--            textColor: [0, 0, 0],-->
<!--            fontStyle: 'bold'-->
<!--          }-->
<!--        });-->

<!--        // 手动添加中文标题作为图像-->
<!--        // 在PDF顶部添加中文说明文字（作为图像）-->
<!--        this.addChineseTextAsImage(doc, '存活主机列表', 105, 20, 18, 'center');-->

<!--        // 添加时间-->
<!--        const currentTime = new Date().toLocaleString();-->
<!--        this.addChineseTextAsImage(doc, `打印时间: ${currentTime}`, 105, 30, 10, 'center');-->

<!--        // 保存PDF-->
<!--        doc.save(`主机扫描结果_${new Date().toLocaleDateString()}.pdf`);-->
<!--      } catch (error) {-->
<!--        console.error('导出PDF出错:', error);-->
<!--        this.$message.error('导出PDF失败: ' + error.message);-->
<!--      }-->
<!--    },-->

<!--    // 导出PDF函数 - 所有存活主机-->
<!--    exportAllHostsPDF() {-->
<!--      try {-->
<!--        // 创建一个支持中文的PDF-->
<!--        const doc = new jsPDF({-->
<!--          orientation: 'portrait',-->
<!--          unit: 'mm',-->
<!--          format: 'a4'-->
<!--        });-->

<!--        // 获取默认字体，仅用于英文内容-->
<!--        //const defaultFont = doc.getFontList().helvetica;-->

<!--        // 创建表格数据（仅IP地址和存活状态）-->
<!--        const tableData = this.allHostsList.map(host => [host.ip, 'Active']);-->

<!--        // 首先创建一个简单的表格，包含英文内容-->
<!--        doc.autoTable({-->
<!--          head: [['IP Address', 'Status']],-->
<!--          body: tableData,-->
<!--          startY: 40,-->
<!--          theme: 'grid',-->
<!--          styles: {-->
<!--            fontSize: 10,-->
<!--            cellPadding: 3,-->
<!--            lineWidth: 0.5,-->
<!--            lineColor: [0, 0, 0]-->
<!--          },-->
<!--          headStyles: {-->
<!--            fillColor: [240, 240, 240],-->
<!--            textColor: [0, 0, 0],-->
<!--            fontStyle: 'bold'-->
<!--          }-->
<!--        });-->

<!--        // 手动添加中文标题作为图像-->
<!--        // 在PDF顶部添加中文说明文字（作为图像）-->
<!--        this.addChineseTextAsImage(doc, '存活主机列表', 105, 20, 18, 'center');-->

<!--        // 添加时间-->
<!--        const currentTime = new Date().toLocaleString();-->
<!--        this.addChineseTextAsImage(doc, `打印时间: ${currentTime}`, 105, 30, 10, 'center');-->

<!--        // 保存PDF-->
<!--        doc.save(`所有存活主机列表_${new Date().toLocaleDateString()}.pdf`);-->
<!--      } catch (error) {-->
<!--        console.error('导出PDF出错:', error);-->
<!--        this.$message.error('导出PDF失败: ' + error.message);-->
<!--      }-->
<!--    },-->

<!--    // 辅助方法：将中文文本转为canvas图像，然后添加到PDF（高清版）-->
<!--    addChineseTextAsImage(doc, text, x, y, fontSize, align) {-->
<!--      // 创建一个临时canvas，使用更高的分辨率-->
<!--      const canvas = document.createElement('canvas');-->
<!--      const ctx = canvas.getContext('2d');-->

<!--      // 设置高分辨率倍数-->
<!--      const scale = 4; // 增加4倍分辨率-->

<!--      // 设置字体大小和字体-->
<!--      ctx.font = `${fontSize * scale}px "Microsoft YaHei", SimHei, Arial, sans-serif`;-->

<!--      // 测量文本宽度-->
<!--      const textWidth = ctx.measureText(text).width;-->

<!--      // 设置canvas大小（留出一些额外空间并应用缩放）-->
<!--      canvas.width = textWidth + 40 * scale;-->
<!--      canvas.height = fontSize * 2 * scale;-->

<!--      // 应用缩放以提高清晰度-->
<!--      ctx.scale(scale, scale);-->

<!--      // 重新设置字体（因为canvas resize后会重置字体设置）-->
<!--      ctx.font = `${fontSize}px "Microsoft YaHei", SimHei, Arial, sans-serif`;-->
<!--      ctx.textBaseline = 'middle';-->

<!--      // 清空canvas-->
<!--      ctx.fillStyle = 'white';-->
<!--      ctx.fillRect(0, 0, canvas.width / scale, canvas.height / scale);-->

<!--      // 绘制文本-->
<!--      ctx.fillStyle = 'black';-->

<!--      // 根据对齐方式调整位置-->
<!--      let textX = 20;-->
<!--      if (align === 'center') {-->
<!--        ctx.textAlign = 'center';-->
<!--        textX = (canvas.width / scale) / 2;-->
<!--      }-->

<!--      ctx.fillText(text, textX, (canvas.height / scale) / 2);-->

<!--      // 将canvas转为图像，并添加到PDF-->
<!--      const imgData = canvas.toDataURL('image/png');-->

<!--      // 计算插入位置-->
<!--      let posX = x;-->
<!--      if (align === 'center') {-->
<!--        posX = doc.internal.pageSize.getWidth() / 2;-->
<!--      }-->

<!--      // 插入图片，宽高保持不变（高分辨率但尺寸相同）-->
<!--      doc.addImage(imgData, 'PNG', posX - (canvas.width / scale / 2) * 0.264583, y - (canvas.height / scale / 2) * 0.264583, (canvas.width / scale) * 0.264583, (canvas.height / scale) * 0.264583);-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchAllAliveHosts()-->
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
