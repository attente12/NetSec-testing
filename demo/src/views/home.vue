<!-- HomePage.vue -->
<template>
  <div class="home-container">
    <!-- 顶部欢迎区域 -->
    <div class="welcome-section">
      <h1 class="welcome-title">
        网络安全测试平台
        <span class="sub-title">保障网络安全，从资产管理到风险评估，一站式解决方案</span>
      </h1>
    </div>

    <!-- 平台简介区域 -->
    <div class="platform-intro">
      <el-card shadow="hover" class="intro-card">
        <div class="intro-header">
          <i class="el-icon-lock"></i>
          <h2>平台简介</h2>
        </div>
        <div class="intro-content">
          <p>在数字化时代，网络安全风险无处不在。我们的<strong>网络安全测试平台</strong>，集<strong>资产清点、安全基线检测、弱口令检测、安全风险评估、安全等级保护测评、测试报告输出</strong>于一体，旨在为企业提供全方位、智能化的安全检测服务，助力提升网络安全防护能力。</p>

<!--          <div class="stats-container">-->
<!--            <el-row :gutter="20">-->
<!--              <el-col :span="8" v-for="(stat, index) in systemStats" :key="index">-->
<!--                <div class="stat-box">-->
<!--                  <i :class="stat.icon"></i>-->
<!--                  <div class="stat-info">-->
<!--                    <div class="stat-value">{{ stat.value }}</div>-->
<!--                    <div class="stat-label">{{ stat.label }}</div>-->
<!--                  </div>-->
<!--                </div>-->
<!--              </el-col>-->
<!--            </el-row>-->
<!--          </div>-->
        </div>
      </el-card>
    </div>

    <!-- 功能模块区域 -->
    <div class="features-section">
      <div class="section-header">
        <i class="el-icon-s-grid"></i>
        <h2>核心功能</h2>
      </div>
      <div class="features-grid">
        <div class="feature-card"
             v-for="(feature, index) in features"
             :key="index"
             @click="navigateToFeature(feature.path)"
             :style="{ animationDelay: index * 0.1 + 's' }">
          <el-card shadow="hover" :body-style="{ padding: '0px' }">
            <div class="feature-icon" :style="{ background: feature.gradient || 'linear-gradient(135deg, #409EFF, #67C23A)' }">
              <i :class="feature.icon"></i>
            </div>
            <div class="feature-content">
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 功能详情区域 -->
    <div class="feature-details">
      <el-card shadow="hover" class="details-card">
        <div class="details-header">
          <i class="el-icon-s-opportunity"></i>
          <h2>功能详情</h2>
        </div>
        <div class="details-content">
          <div class="detail-item" v-for="(item, index) in featureDetails" :key="index">
            <div class="detail-icon">
              <i class="el-icon-check"></i>
            </div>
            <div class="detail-text">
              <h4>{{ item.title }}</h4>
              <p>{{ item.description }}</p>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  data() {
    return {
      systemInfo: {
        name: '网络安全测试平台',
      },
      systemStats: [
        { label: '今日检测', value: '128', icon: 'el-icon-data-analysis' },
        { label: '系统状态', value: '正常', icon: 'el-icon-success' },
        { label: '待处理', value: '5', icon: 'el-icon-bell' }
      ],
      features: [
        {
          title: '资产管理',
          description: '网络设备与系统资产管理',
          icon: 'el-icon-collection',
          path: '/assetManage',
          gradient: 'linear-gradient(135deg, #1890FF, #36CBCB)',
          stats: {
            percentage: 95,
            label: '覆盖率',
            color: '#1890FF'
          }
        },
        {
          title: '基线检测',
          description: '系统配置安全基线检测与评估',
          icon: 'el-icon-aim',
          path: '/baseCheckHome',
          gradient: 'linear-gradient(135deg, #67C23A, #95DE64)',
          stats: {
            percentage: 85,
            label: '合规率',
            color: '#67C23A'
          }
        },
        {
          title: '弱口令检测',
          description: '系统账号弱口令安全检测',
          icon: 'el-icon-key',
          path: '/weakPasswordDetect',
          gradient: 'linear-gradient(135deg, #409EFF, #85A5FF)',
          stats: {
            percentage: 92,
            label: '安全度',
            color: '#409EFF'
          }
        },
        {
          title: '安全风险评估',
          description: '系统漏洞扫描与评估',
          icon: 'el-icon-discover',
          path: '/pocScanner',
          gradient: 'linear-gradient(135deg, #E6A23C, #F5C842)',
          stats: {
            percentage: 76,
            label: '漏洞率',
            color: '#E6A23C'
          }
        },
        {
          title: '等级保护测评',
          description: '等级保护合规性评估',
          icon: 'el-icon-trophy',
          path: '/classifyProtect',
          gradient: 'linear-gradient(135deg, #F56C6C, #FF9F7F)',
          stats: {
            percentage: 88,
            label: '达标率',
            color: '#67C23A'
          }
        },
      ],
      featureDetails: [
        {
          title: '资产清点',
          description: '全面盘点企业的主机及关键资产，构建细粒度资产信息库，提供可视化"概览视图"与"分级视图"，帮助用户快速掌握资产情况，确保安全检测范围的完整性。'
        },
        {
          title: '安全基线检测',
          description: '依据多项权威安全标准（如等保三级、安全基线规范等），对系统配置、弱密码等关键安全项进行深入核查，确保系统符合行业安全要求。'
        },
        {
          title: '弱口令检测',
          description: '智能化扫描各类应用（如SSH、Tomcat、Mysql、Redis等）弱口令，支持自定义口令字典，精准识别易被攻击的账号，提高密码安全性。'
        },
        {
          title: '安全风险评估',
          description: '遵循GB/T 20984-2022《信息安全技术信息安全风险评估方法》，结合漏洞扫描、端口探测、服务识别等技术，对信息系统的脆弱性进行全面评估。'
        },
        {
          title: '安全等级保护测评',
          description: '基于GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》，对信息系统进行等级划分，对比安全技术要求，提供安全加固建议，确保符合等级保护要求。'
        },
        {
          title: '测试报告输出',
          description: '自动生成安全测试报告，包括资产概览、安全检测结果、风险分析与整改建议，并支持PDF格式导出，助力企业制定精准的安全防护策略。'
        },
      ],
      recentActivities: [
        {
          content: '完成系统漏洞扫描',
          time: '2024-12-06 10:30:00',
          type: 'success'
        },
        {
          content: '发现新的弱口令风险',
          time: '2024-12-06 09:15:00',
          type: 'warning'
        },
        {
          content: '基线检查完成',
          time: '2024-12-06 08:00:00',
          type: 'info'
        }
      ]
    }
  },
  methods: {
    navigateToFeature(path) {
      this.$router.push(path)
    },
    // async fetchSystemInfo() {
    //   try {
    //     const response = await this.$http.get('/api/system/info')
    //     this.systemInfo = response.data
    //   } catch (error) {
    //     this.$message.error('获取系统信息失败')
    //   }
    // },
    // async fetchSystemStats() {
    //   try {
    //     const response = await this.$http.get('/api/system/stats')
    //     this.systemStats = response.data
    //   } catch (error) {
    //     this.$message.error('获取统计信息失败')
    //   }
    // },
    // async fetchRecentActivities() {
    //   try {
    //     const response = await this.$http.get('/api/activities/recent')
    //     this.recentActivities = response.data
    //   } catch (error) {
    //     this.$message.error('获取最近活动失败')
    //   }
    // }
  },
  created() {
    // this.fetchSystemInfo()
    // this.fetchSystemStats()
    // this.fetchRecentActivities()
  }
}
</script>

<style scoped>
.home-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.welcome-section {
  margin-bottom: 30px;
  text-align: center;
  padding: 40px 0;
  background: linear-gradient(135deg, #409EFF, #67C23A);
  border-radius: 8px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.welcome-title {
  font-size: 32px;
  margin-bottom: 0;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

.welcome-title .sub-title {
  display: block;
  font-size: 18px;
  font-weight: normal;
  margin-top: 15px;
  opacity: 0.9;
}

/* 平台简介样式 */
.platform-intro {
  margin-bottom: 30px;
}

.intro-card {
  border-radius: 8px;
  overflow: hidden;
}

.intro-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.intro-header i {
  font-size: 24px;
  color: #409EFF;
  margin-right: 10px;
}

.intro-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.intro-content p {
  font-size: 16px;
  line-height: 1.8;
  color: #606266;
  margin-bottom: 20px;
}

.stats-container {
  margin-top: 30px;
}

.stat-box {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.stat-box i {
  font-size: 36px;
  margin-right: 15px;
  color: #409EFF;
}

.stat-info .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-info .stat-label {
  font-size: 14px;
  color: #909399;
}

/* 功能模块样式 */
.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.section-header i {
  font-size: 24px;
  color: #409EFF;
  margin-right: 10px;
}

.section-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.features-section {
  margin-bottom: 30px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  width: 100%;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s;
  animation: slideIn 0.5s ease-out forwards;
  opacity: 0;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px 8px 0 0;
}

.feature-icon i {
  font-size: 48px;
  color: white;
}

.feature-content {
  padding: 20px;
}

.feature-content h3 {
  margin: 0 0 10px;
  color: #303133;
}

.feature-content p {
  color: #606266;
  margin: 0;
  height: 40px;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 功能详情样式 */
.feature-details {
  margin-bottom: 30px;
}

.details-card {
  border-radius: 8px;
  overflow: hidden;
}

.details-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.details-header i {
  font-size: 24px;
  color: #409EFF;
  margin-right: 10px;
}

.details-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.details-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.detail-item {
  display: flex;
  padding: 15px;
  border-radius: 8px;
  background-color: #f5f7fa;
  transition: all 0.3s;
}

.detail-item:hover {
  background-color: #eef5fe;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.detail-icon {
  margin-right: 15px;
  width: 24px;
  height: 24px;
  background-color: #409EFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.detail-icon i {
  font-size: 14px;
  color: white;
}

.detail-text h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #303133;
}

.detail-text p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式布局 */
@media screen and (max-width: 1400px) {
  .features-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .details-content {
    grid-template-columns: 1fr;
  }
}

@media screen and (max-width: 1000px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media screen and (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
  }

  .welcome-title {
    font-size: 26px;
  }

  .welcome-title .sub-title {
    font-size: 16px;
  }
}
</style>


<!-- 旧版本 没有简介 -->
<!--<template>-->
<!--  <div class="home-container">-->
<!--    &lt;!&ndash; 顶部欢迎区域 &ndash;&gt;-->
<!--    <div class="welcome-section">-->
<!--      <h1 class="welcome-title">-->
<!--        网络安全测试平台-->
<!--      </h1>-->
<!--&lt;!&ndash;      <div class="system-stats">&ndash;&gt;-->
<!--&lt;!&ndash;        <el-row :gutter="20">&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="8" v-for="(stat, index) in systemStats" :key="index">&ndash;&gt;-->
<!--&lt;!&ndash;            <el-card shadow="hover" :body-style="{ padding: '20px' }">&ndash;&gt;-->
<!--&lt;!&ndash;              <div class="stat-item">&ndash;&gt;-->
<!--&lt;!&ndash;                <i :class="stat.icon"></i>&ndash;&gt;-->
<!--&lt;!&ndash;                <div class="stat-info">&ndash;&gt;-->
<!--&lt;!&ndash;                  <div class="stat-value">{{ stat.value }}</div>&ndash;&gt;-->
<!--&lt;!&ndash;                  <div class="stat-label">{{ stat.label }}</div>&ndash;&gt;-->
<!--&lt;!&ndash;                </div>&ndash;&gt;-->
<!--&lt;!&ndash;              </div>&ndash;&gt;-->
<!--&lt;!&ndash;            </el-card>&ndash;&gt;-->
<!--&lt;!&ndash;          </el-col>&ndash;&gt;-->
<!--&lt;!&ndash;        </el-row>&ndash;&gt;-->
<!--&lt;!&ndash;      </div>&ndash;&gt;-->
<!--    </div>-->

<!--    &lt;!&ndash; 功能模块区域 &ndash;&gt;-->
<!--    <div class="features-section">-->
<!--      <div class="features-grid">-->
<!--        <div class="feature-card"-->
<!--             v-for="(feature, index) in features"-->
<!--             :key="index"-->
<!--             @click="navigateToFeature(feature.path)"-->
<!--             :style="{ animationDelay: index * 0.1 + 's' }">-->
<!--          <el-card shadow="hover" :body-style="{ padding: '0px' }">-->
<!--            <div class="feature-icon">-->
<!--              <i :class="feature.icon"></i>-->
<!--            </div>-->
<!--            <div class="feature-content">-->
<!--              <h3>{{ feature.title }}</h3>-->
<!--              <p>{{ feature.description }}</p>-->
<!--&lt;!&ndash;              <div class="feature-stats" v-if="feature.stats">&ndash;&gt;-->
<!--&lt;!&ndash;                <div class="stat-circle">&ndash;&gt;-->
<!--&lt;!&ndash;                  <el-progress type="circle"&ndash;&gt;-->
<!--&lt;!&ndash;                               :percentage="feature.stats.percentage"&ndash;&gt;-->
<!--&lt;!&ndash;                               :color="feature.stats.color">&ndash;&gt;-->
<!--&lt;!&ndash;                  </el-progress>&ndash;&gt;-->
<!--&lt;!&ndash;                  <span class="stat-label">{{ feature.stats.label }}</span>&ndash;&gt;-->
<!--&lt;!&ndash;                </div>&ndash;&gt;-->
<!--&lt;!&ndash;              </div>&ndash;&gt;-->
<!--            </div>-->
<!--          </el-card>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 最近活动区域 &ndash;&gt;-->
<!--&lt;!&ndash;    <div class="recent-activities">&ndash;&gt;-->
<!--&lt;!&ndash;      <el-card class="activity-card">&ndash;&gt;-->
<!--&lt;!&ndash;        <div slot="header">&ndash;&gt;-->
<!--&lt;!&ndash;          <span>最近活动</span>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->
<!--&lt;!&ndash;        <el-timeline>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-timeline-item&ndash;&gt;-->
<!--&lt;!&ndash;              v-for="(activity, index) in recentActivities"&ndash;&gt;-->
<!--&lt;!&ndash;              :key="index"&ndash;&gt;-->
<!--&lt;!&ndash;              :timestamp="activity.time"&ndash;&gt;-->
<!--&lt;!&ndash;              :type="activity.type">&ndash;&gt;-->
<!--&lt;!&ndash;            {{ activity.content }}&ndash;&gt;-->
<!--&lt;!&ndash;          </el-timeline-item>&ndash;&gt;-->
<!--&lt;!&ndash;        </el-timeline>&ndash;&gt;-->
<!--&lt;!&ndash;      </el-card>&ndash;&gt;-->
<!--&lt;!&ndash;    </div>&ndash;&gt;-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  name: 'HomePage',-->
<!--  data() {-->
<!--    return {-->
<!--      systemInfo: {-->
<!--        name: '网络安全测试平台',-->
<!--      },-->
<!--      systemStats: [-->
<!--        { label: '今日检测', value: '128', icon: 'el-icon-data-analysis' },-->
<!--        // { label: '安全事件', value: '12', icon: 'el-icon-warning' },-->
<!--        { label: '系统状态', value: '正常', icon: 'el-icon-success' },-->
<!--        { label: '待处理', value: '5', icon: 'el-icon-bell' }-->
<!--      ],-->
<!--      features: [-->

<!--        {-->
<!--          title: '基线检测',-->
<!--          description: '系统配置安全基线检测与评估',-->
<!--          icon: 'el-icon-aim',-->
<!--          path: '/baseCheckHome',-->
<!--          stats: {-->
<!--            percentage: 85,-->
<!--            label: '合规率',-->
<!--            color: '#67C23A'-->
<!--          }-->
<!--        },-->
<!--        {-->
<!--          title: '安全风险评估',-->
<!--          description: '系统漏洞扫描与评估',-->
<!--          icon: 'el-icon-discover',-->
<!--          path: '/pocScanner',-->
<!--          stats: {-->
<!--            percentage: 76,-->
<!--            label: '漏洞率',-->
<!--            color: '#E6A23C'-->
<!--          }-->
<!--        },-->
<!--        {-->
<!--          title: '弱口令检测',-->
<!--          description: '系统账号弱口令安全检测',-->
<!--          icon: 'el-icon-key',-->
<!--          path: '/weakPasswordDetect',-->
<!--          stats: {-->
<!--            percentage: 92,-->
<!--            label: '安全度',-->
<!--            color: '#409EFF'-->
<!--          }-->
<!--        },-->

<!--        {-->
<!--          title: '等级保护测评',-->
<!--          description: '等级保护合规性评估',-->
<!--          icon: 'el-icon-trophy',-->
<!--          path: '/classifyProtect',-->
<!--          stats: {-->
<!--            percentage: 88,-->
<!--            label: '达标率',-->
<!--            color: '#67C23A'-->
<!--          }-->
<!--        },-->
<!--        {-->
<!--          title: '资产管理',-->
<!--          description: '网络设备与系统资产管理',-->
<!--          icon: 'el-icon-collection',-->
<!--          path: '/assetManage',-->
<!--          stats: {-->
<!--            percentage: 95,-->
<!--            label: '覆盖率',-->
<!--            color: '#1890FF'-->
<!--          }-->
<!--        },-->
<!--      ],-->
<!--      recentActivities: [-->
<!--        {-->
<!--          content: '完成系统漏洞扫描',-->
<!--          time: '2024-12-06 10:30:00',-->
<!--          type: 'success'-->
<!--        },-->
<!--        {-->
<!--          content: '发现新的弱口令风险',-->
<!--          time: '2024-12-06 09:15:00',-->
<!--          type: 'warning'-->
<!--        },-->
<!--        {-->
<!--          content: '基线检查完成',-->
<!--          time: '2024-12-06 08:00:00',-->
<!--          type: 'info'-->
<!--        }-->
<!--      ]-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    navigateToFeature(path) {-->
<!--      this.$router.push(path)-->
<!--    },-->
<!--    async fetchSystemInfo() {-->
<!--      try {-->
<!--        const response = await this.$http.get('/api/system/info')-->
<!--        this.systemInfo = response.data-->
<!--      } catch (error) {-->
<!--        this.$message.error('获取系统信息失败')-->
<!--      }-->
<!--    },-->
<!--    async fetchSystemStats() {-->
<!--      try {-->
<!--        const response = await this.$http.get('/api/system/stats')-->
<!--        this.systemStats = response.data-->
<!--      } catch (error) {-->
<!--        this.$message.error('获取统计信息失败')-->
<!--      }-->
<!--    },-->
<!--    async fetchRecentActivities() {-->
<!--      try {-->
<!--        const response = await this.$http.get('/api/activities/recent')-->
<!--        this.recentActivities = response.data-->
<!--      } catch (error) {-->
<!--        this.$message.error('获取最近活动失败')-->
<!--      }-->
<!--    }-->
<!--  },-->
<!--  created() {-->
<!--    this.fetchSystemInfo()-->
<!--    this.fetchSystemStats()-->
<!--    this.fetchRecentActivities()-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.home-container {-->
<!--  padding: 20px;-->
<!--  background-color: #f5f7fa;-->
<!--  min-height: 100vh;-->
<!--}-->

<!--.welcome-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.welcome-title {-->
<!--  font-size: 28px;-->
<!--  color: #303133;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.welcome-title .sub-title {-->
<!--  font-size: 16px;-->
<!--  color: #909399;-->
<!--  margin-left: 10px;-->
<!--}-->

<!--.stat-item {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--}-->

<!--.stat-item i {-->
<!--  font-size: 36px;-->
<!--  margin-right: 15px;-->
<!--  color: #409EFF;-->
<!--}-->

<!--.stat-info .stat-value {-->
<!--  font-size: 24px;-->
<!--  font-weight: bold;-->
<!--  color: #303133;-->
<!--}-->

<!--.stat-info .stat-label {-->
<!--  font-size: 14px;-->
<!--  color: #909399;-->
<!--}-->

<!--.features-section {-->
<!--  margin-bottom: 30px;-->
<!--  padding: 0 0px;-->
<!--}-->

<!--.features-grid {-->
<!--  display: grid;-->
<!--  grid-template-columns: repeat(5, 1fr);-->
<!--  gap: 20px;-->
<!--  width: 100%;-->
<!--}-->

<!--.feature-card {-->
<!--  cursor: pointer;-->
<!--  transition: all 0.3s;-->
<!--  animation: slideIn 0.5s ease-out forwards;-->
<!--  opacity: 0;-->
<!--}-->

<!--.feature-card:hover {-->
<!--  transform: translateY(-5px);-->
<!--}-->

<!--.feature-icon {-->
<!--  background: linear-gradient(135deg, #409EFF, #67C23A);-->
<!--  height: 120px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  justify-content: center;-->
<!--}-->

<!--.feature-icon i {-->
<!--  font-size: 48px;-->
<!--  color: white;-->
<!--}-->

<!--.feature-content {-->
<!--  padding: 20px;-->
<!--}-->

<!--.feature-content h3 {-->
<!--  margin: 0 0 10px;-->
<!--  color: #303133;-->
<!--}-->

<!--.feature-content p {-->
<!--  color: #909399;-->
<!--  margin: 0 0 15px;-->
<!--  height: 40px;-->
<!--  font-size: 13px;-->
<!--}-->

<!--.feature-stats {-->
<!--  text-align: center;-->
<!--}-->

<!--.stat-circle {-->
<!--  display: inline-block;-->
<!--}-->

<!--.stat-circle .stat-label {-->
<!--  display: block;-->
<!--  margin-top: 10px;-->
<!--  color: #909399;-->
<!--}-->

<!--.activity-card .el-card__header {-->
<!--  padding: 15px 20px;-->
<!--  border-bottom: 1px solid #EBEEF5;-->
<!--  font-size: 16px;-->
<!--  font-weight: bold;-->
<!--}-->

<!--@keyframes slideIn {-->
<!--  from {-->
<!--    opacity: 0;-->
<!--    transform: translateY(20px);-->
<!--  }-->
<!--  to {-->
<!--    opacity: 1;-->
<!--    transform: translateY(0);-->
<!--  }-->
<!--}-->

<!--/* 响应式布局 */-->
<!--@media screen and (max-width: 1400px) {-->
<!--  .features-grid {-->
<!--    grid-template-columns: repeat(3, 1fr);-->
<!--  }-->
<!--}-->

<!--@media screen and (max-width: 768px) {-->
<!--  .features-grid {-->
<!--    grid-template-columns: repeat(1, 1fr);-->
<!--  }-->
<!--}-->
<!--</style>-->





<!--<template>-->
<!--  <div class="home-container">-->
<!--    &lt;!&ndash; 顶部欢迎区域 &ndash;&gt;-->
<!--    <div class="welcome-section">-->
<!--      <h1 class="welcome-title" v-if="systemInfo.name">-->
<!--        {{ systemInfo.name }}-->
<!--&lt;!&ndash;        <span class="sub-title">安全检测与评估平台</span>&ndash;&gt;-->
<!--      </h1>-->
<!--      <div class="system-stats">-->
<!--        <el-row :gutter="20">-->
<!--          <el-col :span="6" v-for="(stat, index) in systemStats" :key="index">-->
<!--            <el-card shadow="hover" :body-style="{ padding: '20px' }">-->
<!--              <div class="stat-item">-->
<!--                <i :class="stat.icon"></i>-->
<!--                <div class="stat-info">-->
<!--                  <div class="stat-value">{{ stat.value }}</div>-->
<!--                  <div class="stat-label">{{ stat.label }}</div>-->
<!--                </div>-->
<!--              </div>-->
<!--            </el-card>-->
<!--          </el-col>-->
<!--        </el-row>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 功能模块区域 &ndash;&gt;-->
<!--    <div class="features-section">-->
<!--      <el-row :gutter="30">-->
<!--        <el-col :span="6" v-for="(feature, index) in features" :key="index">-->
<!--          <div class="feature-card"-->
<!--               @click="navigateToFeature(feature.path)"-->
<!--               :style="{ animationDelay: index * 0.1 + 's' }">-->
<!--            <el-card shadow="hover" :body-style="{ padding: '0px' }">-->
<!--              <div class="feature-icon">-->
<!--                <i :class="feature.icon"></i>-->
<!--              </div>-->
<!--              <div class="feature-content">-->
<!--                <h3>{{ feature.title }}</h3>-->
<!--                <p>{{ feature.description }}</p>-->
<!--                <div class="feature-stats" v-if="feature.stats">-->
<!--                  <div class="stat-circle">-->
<!--                    <el-progress type="circle"-->
<!--                                 :percentage="feature.stats.percentage"-->
<!--                                 :color="feature.stats.color">-->
<!--                    </el-progress>-->
<!--                    <span class="stat-label">{{ feature.stats.label }}</span>-->
<!--                  </div>-->
<!--                </div>-->
<!--              </div>-->
<!--            </el-card>-->
<!--          </div>-->
<!--        </el-col>-->
<!--      </el-row>-->
<!--    </div>-->

<!--    &lt;!&ndash; 最近活动区域 &ndash;&gt;-->
<!--    <div class="recent-activities">-->
<!--      <el-card class="activity-card">-->
<!--        <div slot="header">-->
<!--          <span>最近活动</span>-->
<!--        </div>-->
<!--        <el-timeline>-->
<!--          <el-timeline-item-->
<!--              v-for="(activity, index) in recentActivities"-->
<!--              :key="index"-->
<!--              :timestamp="activity.time"-->
<!--              :type="activity.type">-->
<!--            {{ activity.content }}-->
<!--          </el-timeline-item>-->
<!--        </el-timeline>-->
<!--      </el-card>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  name: 'HomePage',-->
<!--  data() {-->
<!--    return {-->
<!--      systemInfo: {-->
<!--        name: '网络安全测试平台',-->
<!--      },-->
<!--      systemStats: [-->
<!--        { label: '今日检测', value: '128', icon: 'el-icon-data-analysis' },-->
<!--        { label: '安全事件', value: '12', icon: 'el-icon-warning' },-->
<!--        { label: '系统状态', value: '正常', icon: 'el-icon-success' },-->
<!--        { label: '待处理', value: '5', icon: 'el-icon-bell' }-->
<!--      ],-->
<!--      features: [-->
<!--        {-->
<!--          title: '基线检测',-->
<!--          description: '系统配置安全基线检测与评估',-->
<!--          icon: 'el-icon-aim',-->
<!--          path: '/baseCheck',-->
<!--          stats: {-->
<!--            percentage: 85,-->
<!--            label: '合规率',-->
<!--            color: '#67C23A'-->
<!--          }-->
<!--        },-->
<!--        {-->
<!--          title: '弱口令检测',-->
<!--          description: '系统账号弱口令安全检测',-->
<!--          icon: 'el-icon-key',-->
<!--          path: '/password',-->
<!--          stats: {-->
<!--            percentage: 92,-->
<!--            label: '安全度',-->
<!--            color: '#409EFF'-->
<!--          }-->
<!--        },-->
<!--        {-->
<!--          title: '漏洞扫描',-->
<!--          description: '系统漏洞扫描与评估',-->
<!--          icon: 'el-icon-discover',-->
<!--          path: '/vulnerability',-->
<!--          stats: {-->
<!--            percentage: 76,-->
<!--            label: '修复率',-->
<!--            color: '#E6A23C'-->
<!--          }-->
<!--        },-->
<!--        {-->
<!--          title: '等级保护测评',-->
<!--          description: '等级保护合规性评估',-->
<!--          icon: 'el-icon-trophy',-->
<!--          path: '/grade',-->
<!--          stats: {-->
<!--            percentage: 88,-->
<!--            label: '达标率',-->
<!--            color: '#67C23A'-->
<!--          },-->
<!--        },-->
<!--        {-->
<!--          title: '等级保护测评',-->
<!--          description: '等级保护合规性评估',-->
<!--          icon: 'el-icon-trophy',-->
<!--          path: '/grade',-->
<!--          stats: {-->
<!--            percentage: 88,-->
<!--            label: '达标率',-->
<!--            color: '#67C23A'-->
<!--          },-->
<!--        }-->
<!--      ],-->
<!--      recentActivities: [-->
<!--        {-->
<!--          content: '完成系统漏洞扫描',-->
<!--          time: '2024-12-06 10:30:00',-->
<!--          type: 'success'-->
<!--        },-->
<!--        {-->
<!--          content: '发现新的弱口令风险',-->
<!--          time: '2024-12-06 09:15:00',-->
<!--          type: 'warning'-->
<!--        },-->
<!--        {-->
<!--          content: '基线检查完成',-->
<!--          time: '2024-12-06 08:00:00',-->
<!--          type: 'info'-->
<!--        }-->
<!--      ]-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    navigateToFeature(path) {-->
<!--      this.$router.push(path)-->
<!--    },-->
<!--    async fetchSystemInfo() {-->
<!--      try {-->
<!--        const response = await this.$http.get('/api/system/info')-->
<!--        this.systemInfo = response.data-->
<!--      } catch (error) {-->
<!--        this.$message.error('获取系统信息失败')-->
<!--      }-->
<!--    },-->
<!--    async fetchSystemStats() {-->
<!--      try {-->
<!--        const response = await this.$http.get('/api/system/stats')-->
<!--        this.systemStats = response.data-->
<!--      } catch (error) {-->
<!--        this.$message.error('获取统计信息失败')-->
<!--      }-->
<!--    },-->
<!--    async fetchRecentActivities() {-->
<!--      try {-->
<!--        const response = await this.$http.get('/api/activities/recent')-->
<!--        this.recentActivities = response.data-->
<!--      } catch (error) {-->
<!--        this.$message.error('获取最近活动失败')-->
<!--      }-->
<!--    }-->
<!--  },-->
<!--  created() {-->
<!--    this.fetchSystemInfo()-->
<!--    this.fetchSystemStats()-->
<!--    this.fetchRecentActivities()-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.home-container {-->
<!--  padding: 20px;-->
<!--  background-color: #f5f7fa;-->
<!--  min-height: 100vh;-->
<!--}-->

<!--.welcome-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.welcome-title {-->
<!--  font-size: 28px;-->
<!--  color: #303133;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.welcome-title .sub-title {-->
<!--  font-size: 16px;-->
<!--  color: #909399;-->
<!--  margin-left: 10px;-->
<!--}-->

<!--.stat-item {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--}-->

<!--.stat-item i {-->
<!--  font-size: 36px;-->
<!--  margin-right: 15px;-->
<!--  color: #409EFF;-->
<!--}-->

<!--.stat-info .stat-value {-->
<!--  font-size: 24px;-->
<!--  font-weight: bold;-->
<!--  color: #303133;-->
<!--}-->

<!--.stat-info .stat-label {-->
<!--  font-size: 14px;-->
<!--  color: #909399;-->
<!--}-->

<!--.features-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.feature-card {-->
<!--  cursor: pointer;-->
<!--  transition: all 0.3s;-->
<!--  animation: slideIn 0.5s ease-out forwards;-->
<!--  opacity: 0;-->
<!--}-->

<!--.feature-card:hover {-->
<!--  transform: translateY(-5px);-->
<!--}-->

<!--.feature-icon {-->
<!--  background: linear-gradient(135deg, #409EFF, #67C23A);-->
<!--  height: 120px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  justify-content: center;-->
<!--}-->

<!--.feature-icon i {-->
<!--  font-size: 48px;-->
<!--  color: white;-->
<!--}-->

<!--.feature-content {-->
<!--  padding: 20px;-->
<!--}-->

<!--.feature-content h3 {-->
<!--  margin: 0 0 10px;-->
<!--  color: #303133;-->
<!--}-->

<!--.feature-content p {-->
<!--  color: #909399;-->
<!--  margin: 0 0 15px;-->
<!--  height: 40px;-->
<!--}-->

<!--.feature-stats {-->
<!--  text-align: center;-->
<!--}-->

<!--.stat-circle {-->
<!--  display: inline-block;-->
<!--}-->

<!--.stat-circle .stat-label {-->
<!--  display: block;-->
<!--  margin-top: 10px;-->
<!--  color: #909399;-->
<!--}-->

<!--.activity-card .el-card__header {-->
<!--  padding: 15px 20px;-->
<!--  border-bottom: 1px solid #EBEEF5;-->
<!--  font-size: 16px;-->
<!--  font-weight: bold;-->
<!--}-->

<!--@keyframes slideIn {-->
<!--  from {-->
<!--    opacity: 0;-->
<!--    transform: translateY(20px);-->
<!--  }-->
<!--  to {-->
<!--    opacity: 1;-->
<!--    transform: translateY(0);-->
<!--  }-->
<!--}-->

<!--/* 响应式布局 */-->
<!--@media screen and (max-width: 1200px) {-->
<!--  .el-col {-->
<!--    width: 50% !important;-->
<!--  }-->
<!--}-->

<!--@media screen and (max-width: 768px) {-->
<!--  .el-col {-->
<!--    width: 100% !important;-->
<!--  }-->
<!--}-->
<!--</style>-->


<!--<template>-->
<!--  <div class="vulnerability-container">-->
<!--    <div class="ip-list">-->
<!--      <div class="menu-header">-->
<!--        <span class="title">资产</span>-->
<!--        <el-badge-->
<!--            :value="assets.length"-->
<!--            class="asset-count"-->
<!--            type="primary">-->
<!--        </el-badge>-->
<!--      </div>-->
<!--      <el-menu-->
<!--          :default-active="currentIp"-->
<!--          class="ip-menu"-->
<!--          @select="handleSelect">-->
<!--        <el-menu-item-->
<!--            v-for="asset in assets"-->
<!--            :key="asset.ip"-->
<!--            :index="asset.ip">-->
<!--          <i class="el-icon-monitor"></i>-->
<!--          <span>{{ asset.ip }}</span>-->
<!--        </el-menu-item>-->
<!--      </el-menu>-->
<!--    </div>-->

<!--    &lt;!&ndash; 右侧详情内容 &ndash;&gt;-->
<!--    <div class="content-area" v-if="currentAsset">-->
<!--      <div class="ip-header">-->
<!--        <h2>资产信息</h2>-->
<!--        <div class="asset-info">-->
<!--          <div class="info-item">-->
<!--            <span class="label">IP地址：</span>-->
<!--            <span class="value">{{ currentAsset.ip }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">操作系统：</span>-->
<!--            <span class="value">{{ currentAsset.os }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">开放端口：</span>-->
<!--            <span class="value">{{ currentAsset.ports }}</span>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->
<!--    &lt;!&ndash; 前面的代码保持不变，直到漏洞信息标题 &ndash;&gt;-->

<!--    <h2 class="flex justify-between items-center">-->
<!--      <span>漏洞信息</span>-->
<!--      <div class="chart-toggle">-->
<!--        <el-radio-group v-model="displayType" size="small">-->
<!--          <el-radio-button label="assetType">按资产类型分布</el-radio-button>-->
<!--          <el-radio-button label="vulType">按漏洞类型分布</el-radio-button>-->
<!--        </el-radio-group>-->
<!--      </div>-->
<!--    </h2>-->

<!--    &lt;!&ndash; 资产类型视图 &ndash;&gt;-->
<!--    <template v-if="displayType === 'assetType'">-->
<!--      &lt;!&ndash; 饼图 &ndash;&gt;-->
<!--      <el-card class="chart-section">-->
<!--        <div slot="header" class="clearfix">-->
<!--          <span>漏洞资产类型分布</span>-->
<!--        </div>-->
<!--        <div class="pie-chart" ref="pieChart" style="width: 100%; height: 300px;"></div>-->
<!--      </el-card>-->

<!--      &lt;!&ndash; 主机漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3><strong>系统漏洞</strong></h3>-->
<!--        <el-table-->
<!--            :data="currentAsset.host_vulnerabilities"-->
<!--            border-->
<!--            stripe-->
<!--            :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--        >-->
<!--          <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--          <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--          <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>-->
<!--          <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--          <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                {{ scope.row.vulExist }}-->
<!--              </el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--      </div>-->

<!--      &lt;!&ndash; 原有的端口漏洞分组表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3><strong>软件资产漏洞</strong></h3>-->
<!--        <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"-->
<!--             :key="type"-->
<!--             class="vulnerability-group">-->
<!--          <h4 class="group-title">{{ type }}</h4>-->
<!--          <el-table-->
<!--              :data="vulnerabilities"-->
<!--              border-->
<!--              stripe-->
<!--              :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--          >-->
<!--            <el-table-column prop="port_id" label="端口" width="70"></el-table-column>-->
<!--            <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>-->
<!--            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--            <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>-->
<!--            <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--            <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--            <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                  {{ scope.row.vulExist }}-->
<!--                </el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--        </div>-->
<!--      </div>-->
<!--    </template>-->

<!--    &lt;!&ndash; 漏洞类型视图 &ndash;&gt;-->
<!--    <template v-else>-->
<!--      &lt;!&ndash; 漏洞类型饼图 &ndash;&gt;-->
<!--      <el-card class="chart-section">-->
<!--        <div slot="header" class="clearfix">-->
<!--          <span>漏洞类型分布</span>-->
<!--        </div>-->
<!--        <div class="pie-chart" ref="vulTypePieChart" style="width: 100%; height: 300px;"></div>-->
<!--      </el-card>-->

<!--      &lt;!&ndash; 按漏洞类型分组的表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3><strong>漏洞详情</strong></h3>-->
<!--        <div v-for="(vulnerabilities, type) in groupedVulTypeVulnerabilities"-->
<!--             :key="type"-->
<!--             class="vulnerability-group">-->
<!--          <h4 class="group-title">{{ type }}</h4>-->
<!--          <el-table-->
<!--              :data="vulnerabilities"-->
<!--              border-->
<!--              stripe-->
<!--              :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--          >-->
<!--            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--            <el-table-column prop="softwareType" label="资产类型" width="150"></el-table-column>-->
<!--            <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>-->
<!--            <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--            <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--            <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                  {{ scope.row.vulExist }}-->
<!--                </el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--        </div>-->
<!--      </div>-->
<!--    </template>-->
<!--  </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import * as echarts from 'echarts';-->

<!--export default {-->
<!--  name: 'VulnerabilityTable',-->
<!--  data() {-->
<!--    return {-->
<!--      currentIp: '',-->
<!--      pieChart: null,-->
<!--      vulTypePieChart: null,-->
<!--      displayType: 'assetType',-->
<!--      assets: [-->
<!--        // {-->
<!--        //   "host_vulnerabilities": [-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "softwareType": "操作系统",-->
<!--        //       "summary": "drivers/media/usb/dvb-usb/technisat-usb2.c in the Linux kernel through 5.2.9 has an out-of-bounds read via crafted USB device traffic (which may be remote via usbip or usbredir).",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2019-15505",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "softwareType": "操作系统",-->
<!--        //       "summary": "The NFSv2 and NFSv3 server implementations in the Linux kernel through 4.10.13 lack certain checks for the end of a buffer, which allows remote attackers to trigger pointer-arithmetic errors or possibly have unspecified other impact via crafted requests, related to fs/nfsd/nfs3xdr.c and fs/nfsd/nfsxdr.c.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "未知类型",-->
<!--        //       "vuln_id": "CVE-2017-7895",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "softwareType": "操作系统",-->
<!--        //       "summary": "A heap-based buffer overflow vulnerability was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. A remote attacker could cause a denial of service (system crash) or, possibly execute arbitrary code, when the lbs_ibss_join_existing function is called after a STA connects to an AP.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Denial of Service (DoS)",-->
<!--        //       "vuln_id": "CVE-2019-14896",-->
<!--        //       "vuln_name": ""-->
<!--        //     }-->
<!--        //   ],-->
<!--        //   "ip": "10.9.130.193",-->
<!--        //   "port_vulnerabilities": [-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "A heap overflow flaw was found in the Linux kernel, all versions 3.x.x and 4.x.x before 4.18.0, in Marvell WiFi chip driver. The vulnerability allows a remote attacker to cause a system crash, resulting in a denial of service, or execute arbitrary code. The highest threat with this vulnerability is with the availability of the system. If code execution occurs, the code will run with the permissions of root. This will affect both confidentiality and integrity of files on the system.",-->
<!--        //       "vulExist": "不存在",-->
<!--        //       "vulType": "Denial of Service (DoS)",-->
<!--        //       "vuln_id": "CVE-2019-14901",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "A heap-based buffer overflow vulnerability was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. A remote attacker could cause a denial of service (system crash) or, possibly execute arbitrary code, when the lbs_ibss_join_existing function is called after a STA connects to an AP.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Denial of Service (DoS)",-->
<!--        //       "vuln_id": "CVE-2019-14896",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "Brackets versions 1.14 and earlier have a command injection vulnerability. Successful exploitation could lead to arbitrary code execution.",-->
<!--        //       "vulExist": "不存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2019-8255",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175020.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-4210",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175022.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-4211",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175023.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-4212",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "SecureCRT before 8.7.2 allows remote attackers to execute arbitrary code via an Integer Overflow and a Buffer Overflow because a banner can trigger a line number to CSI functions that exceeds INT_MAX.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2020-12651",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "Adobe Flash Player Desktop Runtime 32.0.0.371 and earlier, Adobe Flash Player for Google Chrome 32.0.0.371 and earlier, and Adobe Flash Player for Microsoft Edge and Internet Explorer 32.0.0.330 and earlier have an use after free vulnerability. Successful exploitation could lead to arbitrary code execution.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-9633",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM Spectrum Copy Data Management 2.2.13 and earlier could allow a remote attacker to execute arbitrary commands on the system, caused by improper validation of user-supplied input by the Spectrum Copy Data Management Admin Console login and uploadcertificate function . A remote attacker could inject arbitrary shell commands which would be executed on the affected system. IBM X-Force ID: 214958.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2021-39065",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM CICS TX Standard and Advanced 11.1 could allow a remote attacker to execute arbitrary commands on the system by sending a specially crafted request. IBM X-Force ID: 227980.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2022-31767",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "A carefully crafted request body can cause a buffer overflow in the mod_lua multipart parser (r:parsebody() called from Lua scripts). The Apache httpd team is not aware of an exploit for the vulnerabilty though it might be possible to craft one. This issue affects Apache HTTP Server 2.4.51 and earlier.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2021-44790",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP Server 2.4.52 and earlier fails to close inbound connection when errors are encountered discarding the request body, exposing the server to HTTP Request Smuggling",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "未知类型",-->
<!--        //       "vuln_id": "CVE-2022-22720",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP Server 2.4.53 and earlier may not send the X-Forwarded-* headers to the origin server based on client side Connection header hop-by-hop mechanism. This may be used to bypass IP based authentication on the origin server/application.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "未知类型",-->
<!--        //       "vuln_id": "CVE-2022-31813",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Out-of-bounds Write vulnerability in mod_sed of Apache HTTP Server allows an attacker to overwrite heap memory with possibly attacker provided data. This issue affects Apache HTTP Server 2.4 version 2.4.52 and prior versions.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2022-23943",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "In Apache HTTP Server versions 2.4.0 to 2.4.46 a specially crafted SessionHeader sent by an origin server could cause a heap overflow",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2021-26691",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "ap_escape_quotes() may write beyond the end of a buffer when given malicious input. No included modules pass untrusted data to these functions, but third-party / external modules may. This issue affects Apache HTTP Server 2.4.48 and earlier.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Cross-Site Scripting (XSS)",-->
<!--        //       "vuln_id": "CVE-2021-39275",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP server 2.4.32 to 2.4.44 mod_proxy_uwsgi info disclosure and possible RCE",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-11984",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "6.800000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "A crafted request uri-path can cause mod_proxy to forward the request to an origin server choosen by the remote user. This issue affects Apache HTTP Server 2.4.48 and earlier.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "未知类型",-->
<!--        //       "vuln_id": "CVE-2021-40438",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "6.800000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP Server versions 2.4.0 to 2.4.46 A specially crafted Digest nonce can cause a stack overflow in mod_auth_digest. There is no report of this overflow being exploitable, nor the Apache HTTP Server team could create one, though some particular compiler and/or compilation option might make it possible, with limited consequences anyway due to the size (a single byte) and the value (zero byte) of the overflow",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2020-35452",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "6.400000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP Server 2.4.53 and earlier may crash or disclose information due to a read beyond bounds in ap_strcmp_match() when provided with an extremely large input buffer. While no code distributed with the server can be coerced into such a call, third-party modules or lua scripts that use ap_strcmp_match() may hypothetically be affected.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2022-28615",-->
<!--        //       "vuln_name": ""-->
<!--        //     }-->
<!--        //   ]-->
<!--        // },-->
<!--        // {-->
<!--        //   "host_vulnerabilities": [-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "softwareType": "操作系统",-->
<!--        //       "summary": "drivers/media/usb/dvb-usb/technisat-usb2.c in the Linux kernel through 5.2.9 has an out-of-bounds read via crafted USB device traffic (which may be remote via usbip or usbredir).",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2019-15505",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "softwareType": "操作系统",-->
<!--        //       "summary": "The NFSv2 and NFSv3 server implementations in the Linux kernel through 4.10.13 lack certain checks for the end of a buffer, which allows remote attackers to trigger pointer-arithmetic errors or possibly have unspecified other impact via crafted requests, related to fs/nfsd/nfs3xdr.c and fs/nfsd/nfsxdr.c.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "未知类型",-->
<!--        //       "vuln_id": "CVE-2017-7895",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "softwareType": "操作系统",-->
<!--        //       "summary": "A heap-based buffer overflow vulnerability was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. A remote attacker could cause a denial of service (system crash) or, possibly execute arbitrary code, when the lbs_ibss_join_existing function is called after a STA connects to an AP.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Denial of Service (DoS)",-->
<!--        //       "vuln_id": "CVE-2019-14896",-->
<!--        //       "vuln_name": ""-->
<!--        //     }-->
<!--        //   ],-->
<!--        //   "ip": "10.9.130.192",-->
<!--        //   "port_vulnerabilities": [-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 21,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "A heap overflow flaw was found in the Linux kernel, all versions 3.x.x and 4.x.x before 4.18.0, in Marvell WiFi chip driver. The vulnerability allows a remote attacker to cause a system crash, resulting in a denial of service, or execute arbitrary code. The highest threat with this vulnerability is with the availability of the system. If code execution occurs, the code will run with the permissions of root. This will affect both confidentiality and integrity of files on the system.",-->
<!--        //       "vulExist": "不存在",-->
<!--        //       "vulType": "Denial of Service (DoS)",-->
<!--        //       "vuln_id": "CVE-2019-14901",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "A heap-based buffer overflow vulnerability was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. A remote attacker could cause a denial of service (system crash) or, possibly execute arbitrary code, when the lbs_ibss_join_existing function is called after a STA connects to an AP.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Denial of Service (DoS)",-->
<!--        //       "vuln_id": "CVE-2019-14896",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175020.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-4210",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175022.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-4211",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM Spectrum Protect Plus 10.1.0 and 10.1.5 could allow a remote attacker to execute arbitrary code on the system. By using a specially crafted HTTP command, an attacker could exploit this vulnerability to execute arbitrary command on the system. IBM X-Force ID: 175023.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-4212",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "SecureCRT before 8.7.2 allows remote attackers to execute arbitrary code via an Integer Overflow and a Buffer Overflow because a banner can trigger a line number to CSI functions that exceeds INT_MAX.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2020-12651",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "Adobe Flash Player Desktop Runtime 32.0.0.371 and earlier, Adobe Flash Player for Google Chrome 32.0.0.371 and earlier, and Adobe Flash Player for Microsoft Edge and Internet Explorer 32.0.0.330 and earlier have an use after free vulnerability. Successful exploitation could lead to arbitrary code execution.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-9633",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM Spectrum Copy Data Management 2.2.13 and earlier could allow a remote attacker to execute arbitrary commands on the system, caused by improper validation of user-supplied input by the Spectrum Copy Data Management Admin Console login and uploadcertificate function . A remote attacker could inject arbitrary shell commands which would be executed on the affected system. IBM X-Force ID: 214958.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2021-39065",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "10.000000",-->
<!--        //       "port_id": 22,-->
<!--        //       "softwareType": "系统工具",-->
<!--        //       "summary": "IBM CICS TX Standard and Advanced 11.1 could allow a remote attacker to execute arbitrary commands on the system by sending a specially crafted request. IBM X-Force ID: 227980.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2022-31767",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "A carefully crafted request body can cause a buffer overflow in the mod_lua multipart parser (r:parsebody() called from Lua scripts). The Apache httpd team is not aware of an exploit for the vulnerabilty though it might be possible to craft one. This issue affects Apache HTTP Server 2.4.51 and earlier.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2021-44790",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP Server 2.4.52 and earlier fails to close inbound connection when errors are encountered discarding the request body, exposing the server to HTTP Request Smuggling",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "未知类型",-->
<!--        //       "vuln_id": "CVE-2022-22720",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP Server 2.4.53 and earlier may not send the X-Forwarded-* headers to the origin server based on client side Connection header hop-by-hop mechanism. This may be used to bypass IP based authentication on the origin server/application.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "未知类型",-->
<!--        //       "vuln_id": "CVE-2022-31813",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Out-of-bounds Write vulnerability in mod_sed of Apache HTTP Server allows an attacker to overwrite heap memory with possibly attacker provided data. This issue affects Apache HTTP Server 2.4 version 2.4.52 and prior versions.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2022-23943",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "In Apache HTTP Server versions 2.4.0 to 2.4.46 a specially crafted SessionHeader sent by an origin server could cause a heap overflow",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2021-26691",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "ap_escape_quotes() may write beyond the end of a buffer when given malicious input. No included modules pass untrusted data to these functions, but third-party / external modules may. This issue affects Apache HTTP Server 2.4.48 and earlier.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Cross-Site Scripting (XSS)",-->
<!--        //       "vuln_id": "CVE-2021-39275",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "7.500000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP server 2.4.32 to 2.4.44 mod_proxy_uwsgi info disclosure and possible RCE",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2020-11984",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "6.800000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "A crafted request uri-path can cause mod_proxy to forward the request to an origin server choosen by the remote user. This issue affects Apache HTTP Server 2.4.48 and earlier.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "未知类型",-->
<!--        //       "vuln_id": "CVE-2021-40438",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "6.800000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP Server versions 2.4.0 to 2.4.46 A specially crafted Digest nonce can cause a stack overflow in mod_auth_digest. There is no report of this overflow being exploitable, nor the Apache HTTP Server team could create one, though some particular compiler and/or compilation option might make it possible, with limited consequences anyway due to the size (a single byte) and the value (zero byte) of the overflow",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Buffer Overflow",-->
<!--        //       "vuln_id": "CVE-2020-35452",-->
<!--        //       "vuln_name": ""-->
<!--        //     },-->
<!--        //     {-->
<!--        //       "cvss": "6.400000",-->
<!--        //       "port_id": 80,-->
<!--        //       "softwareType": "Web应用",-->
<!--        //       "summary": "Apache HTTP Server 2.4.53 and earlier may crash or disclose information due to a read beyond bounds in ap_strcmp_match() when provided with an extremely large input buffer. While no code distributed with the server can be coerced into such a call, third-party modules or lua scripts that use ap_strcmp_match() may hypothetically be affected.",-->
<!--        //       "vulExist": "存在",-->
<!--        //       "vulType": "Remote Code Execution (RCE)",-->
<!--        //       "vuln_id": "CVE-2022-28615",-->
<!--        //       "vuln_name": ""-->
<!--        //     }-->
<!--        //   ]-->
<!--        // }-->
<!--      ],-->
<!--      vulTypes: [-->
<!--        "Buffer Overflow", "File Upload Vulnerability", "Code Injection",-->
<!--        "SQL Injection", "Cross-Site Scripting (XSS)", "Privilege Escalation",-->
<!--        "Denial of Service (DoS)", "Authentication Bypass", "Path Traversal",-->
<!--        "Information Disclosure", "Cross-Site Request Forgery (CSRF)",-->
<!--        "XML External Entity (XXE)", "Remote Code Execution (RCE)",-->
<!--        "Session Hijacking", "Unauthorized Access"-->
<!--      ]-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    // 原有的计算属性保持不变-->
<!--    currentAsset() {-->
<!--      return this.assets.find(asset => asset.ip === this.currentIp);-->
<!--    },-->
<!--    groupedPortVulnerabilities() {-->
<!--      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {-->
<!--        return {};-->
<!--      }-->
<!--      return this.currentAsset.port_vulnerabilities.reduce((groups, vuln) => {-->
<!--        const type = vuln.softwareType || '未分类';-->
<!--        if (!groups[type]) {-->
<!--          groups[type] = [];-->
<!--        }-->
<!--        groups[type].push(vuln);-->
<!--        return groups;-->
<!--      }, {});-->
<!--    },-->
<!--    vulnerabilityTypeStats() {-->
<!--      const stats = {-->
<!--        '操作系统': 0,-->
<!--        'Web应用程序': 0,-->
<!--        '系统工具': 0,-->
<!--        '中间件': 0,-->
<!--        '未知类型': 0-->
<!--      };-->

<!--      if (this.currentAsset?.host_vulnerabilities) {-->
<!--        this.currentAsset.host_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      if (this.currentAsset?.port_vulnerabilities) {-->
<!--        this.currentAsset.port_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      return stats;-->
<!--    },-->
<!--    // 新增：按漏洞类型统计-->
<!--    vulTypeStats() {-->
<!--      const stats = {};-->

<!--      // 初始化所有漏洞类型的计数为0-->
<!--      this.vulTypes.forEach(type => {-->
<!--        stats[type] = 0;-->
<!--      });-->

<!--      // 统计主机漏洞-->
<!--      if (this.currentAsset?.host_vulnerabilities) {-->
<!--        this.currentAsset.host_vulnerabilities.forEach(vuln => {-->
<!--          if (vuln.vulType) {-->
<!--            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      // 统计端口漏洞-->
<!--      if (this.currentAsset?.port_vulnerabilities) {-->
<!--        this.currentAsset.port_vulnerabilities.forEach(vuln => {-->
<!--          if (vuln.vulType) {-->
<!--            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      // 只返回数量大于0的类型-->
<!--      return Object.fromEntries(-->
<!--          Object.entries(stats).filter(([, count]) => count > 0)-->
<!--      );-->
<!--    },-->
<!--    // 新增：按漏洞类型分组的所有漏洞-->
<!--    groupedVulTypeVulnerabilities() {-->
<!--      const groups = {};-->

<!--      // 合并主机漏洞和端口漏洞-->
<!--      const allVulnerabilities = [-->
<!--        ...(this.currentAsset?.host_vulnerabilities || []),-->
<!--        ...(this.currentAsset?.port_vulnerabilities || [])-->
<!--      ];-->

<!--      // 按漏洞类型分组-->
<!--      allVulnerabilities.forEach(vuln => {-->
<!--        const type = vuln.vulType || '未分类';-->
<!--        if (!groups[type]) {-->
<!--          groups[type] = [];-->
<!--        }-->
<!--        groups[type].push(vuln);-->
<!--      });-->

<!--      return groups;-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    getResults() {-->
<!--      fetch('/api/getAllAssetsVulnData')-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.assets = data;-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->
<!--    handleSelect(ip) {-->
<!--      this.currentIp = ip;-->
<!--      this.displayType = 'assetType';-->
<!--      // 检查图表实例是否存在-->
<!--      if (!this.pieChart || !this.pieChart.isDisposed()) {-->
<!--        this.initCharts();  // 不存在或已销毁:初始化-->
<!--      } else {-->
<!--        this.updateCharts(); // 否则直接更新数据-->
<!--      }-->
<!--      // this.updateCharts();-->
<!--      // this.initCharts();-->
<!--      // 使用 nextTick 确保 DOM 更新后再初始化图表-->
<!--      // this.$nextTick(() => {-->
<!--      //   this.initCharts();  // 改用 initCharts 而不是 updateCharts-->
<!--      // });-->
<!--    },-->
<!--    // handleSelect(ip) {-->
<!--    //   this.currentIp = ip;-->
<!--    //   this.displayType ='assetType';-->
<!--    //   this.updateCharts();-->
<!--    // },-->
<!--    getCvssType(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return 'danger';-->
<!--      if (score >= 4.0) return 'warning';-->
<!--      if (score >= 0.0) return 'success';-->
<!--      return 'info';-->
<!--    },-->
<!--    getRiskLevel(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return '高风险';-->
<!--      if (score >= 4.0) return '中风险';-->
<!--      if (score >= 0.0) return '低风险';-->
<!--      return '信息';-->
<!--    },-->
<!--    async initCharts() {-->
<!--      await this.$nextTick();-->

<!--      // 初始化资产类型饼图-->
<!--      if (this.$refs.pieChart) {-->
<!--        if (this.pieChart) {-->
<!--          this.pieChart.dispose();-->
<!--        }-->
<!--        this.pieChart = echarts.init(this.$refs.pieChart);-->
<!--      }-->

<!--      // 初始化漏洞类型饼图-->
<!--      if (this.$refs.vulTypePieChart) {-->
<!--        if (this.vulTypePieChart) {-->
<!--          this.vulTypePieChart.dispose();-->
<!--        }-->
<!--        this.vulTypePieChart = echarts.init(this.$refs.vulTypePieChart);-->
<!--      }-->

<!--      window.addEventListener('resize', () => {-->
<!--        this.pieChart && this.pieChart.resize();-->
<!--        this.vulTypePieChart && this.vulTypePieChart.resize();-->
<!--      });-->

<!--      this.updateCharts();-->
<!--    },-->
<!--    updateCharts() {-->
<!--      if (this.displayType === 'assetType') {-->
<!--        this.updateAssetPieChart();-->
<!--      } else {-->
<!--        this.updateVulTypePieChart();-->
<!--      }-->
<!--    },-->
<!--    // 原有的资产类型饼图更新方法-->
<!--    updateAssetPieChart() {-->
<!--      if (!this.pieChart) return;-->

<!--      const stats = this.vulnerabilityTypeStats;-->
<!--      const data = Object.entries(stats)-->
<!--          .filter(([, value]) => value > 0)-->
<!--          .map(([name, value]) => ({-->
<!--            name,-->
<!--            value-->
<!--          }));-->

<!--      const option = {-->
<!--        tooltip: {-->
<!--          trigger: 'item',-->
<!--          formatter: '{a} <br/>{b}: {c} ({d}%)'-->
<!--        },-->
<!--        legend: {-->
<!--          orient: 'vertical',-->
<!--          right: 'right',-->
<!--          top: 'middle',-->
<!--          data: data.map(item => item.name)-->
<!--        },-->
<!--        series: [{-->
<!--          name: '资产类型分布',-->
<!--          type: 'pie',-->
<!--          radius: ['40%', '70%'],-->
<!--          center: ['40%', '50%'],-->
<!--          avoidLabelOverlap: false,-->
<!--          itemStyle: {-->
<!--            borderRadius: 10,-->
<!--            borderColor: '#fff',-->
<!--            borderWidth: 2-->
<!--          },-->
<!--          label: {-->
<!--            show: true,-->
<!--            formatter: '{b}: {c}个'-->
<!--          },-->
<!--          emphasis: {-->
<!--            label: {-->
<!--              show: true,-->
<!--              fontSize: '18',-->
<!--              fontWeight: 'bold'-->
<!--            }-->
<!--          },-->
<!--          labelLine: {-->
<!--            show: true-->
<!--          },-->
<!--          data: data-->
<!--        }]-->
<!--      };-->

<!--      this.pieChart.setOption(option);-->
<!--    },-->
<!--    // 新增：漏洞类型饼图更新方法-->
<!--    updateVulTypePieChart() {-->
<!--      if (!this.vulTypePieChart) return;-->

<!--      const stats = this.vulTypeStats;-->
<!--      const data = Object.entries(stats)-->
<!--          .map(([name, value]) => ({-->
<!--            name,-->
<!--            value-->
<!--          }));-->

<!--      const option = {-->
<!--        tooltip: {-->
<!--          trigger: 'item',-->
<!--          formatter: '{a} <br/>{b}: {c} ({d}%)'-->
<!--        },-->
<!--        legend: {-->
<!--          orient: 'vertical',-->
<!--          right: 'right',-->
<!--          top: 'middle',-->
<!--          data: data.map(item => item.name)-->
<!--        },-->
<!--        series: [{-->
<!--          name: '漏洞类型分布',-->
<!--          type: 'pie',-->
<!--          radius: ['40%', '70%'],-->
<!--          center: ['40%', '50%'],-->
<!--          avoidLabelOverlap: false,-->
<!--          itemStyle: {-->
<!--            borderRadius: 10,-->
<!--            borderColor: '#fff',-->
<!--            borderWidth: 2-->
<!--          },-->
<!--          label: {-->
<!--            show: true,-->
<!--            formatter: '{b}: {c}个'-->
<!--          },-->
<!--          emphasis: {-->
<!--            label: {-->
<!--              show: true,-->
<!--              fontSize: '18',-->
<!--              fontWeight: 'bold'-->
<!--            }-->
<!--          },-->
<!--          labelLine: {-->
<!--            show: true-->
<!--          },-->
<!--          data: data-->
<!--        }]-->
<!--      };-->

<!--      this.vulTypePieChart.setOption(option);-->
<!--    }-->
<!--  },-->
<!--  watch: {-->
<!--    currentAsset() {-->
<!--      this.$nextTick(() => {-->
<!--        this.updateCharts();-->
<!--      });-->
<!--    },-->
<!--    displayType() {-->
<!--      this.$nextTick(() => {-->
<!--        this.initCharts();-->
<!--      });-->
<!--    }-->
<!--  },-->
<!--  // created() {-->
<!--  //   this.getResults().then(() => {-->
<!--  //     if (this.assets.length > 0) {-->
<!--  //       this.currentIp = this.assets[0].ip;-->
<!--  //       this.displayType = 'assetType';-->
<!--  //       this.$nextTick(() => {-->
<!--  //         this.initCharts();-->
<!--  //       });-->
<!--  //     }-->
<!--  //   });-->
<!--  // },-->
<!--  created() {-->
<!--    this.getResults();-->
<!--  },-->
<!--  mounted() {-->
<!--    if (this.assets.length > 0) {-->
<!--      this.currentIp = this.assets[0].ip;-->
<!--    }-->
<!--    this.initCharts();-->
<!--  },-->
<!--  beforeDestroy() {-->
<!--    if (this.pieChart) {-->
<!--      this.pieChart.dispose();-->
<!--      this.pieChart = null;-->
<!--    }-->
<!--    if (this.vulTypePieChart) {-->
<!--      this.vulTypePieChart.dispose();-->
<!--      this.vulTypePieChart = null;-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.vulnerability-container {-->
<!--  display: flex;-->
<!--  height: 100%;-->
<!--  min-height: 600px;-->
<!--  background-color: #fff;-->
<!--}-->

<!--.ip-list {-->
<!--  width: 250px;-->
<!--  border-right: 1px solid #e6e6e6;-->
<!--  background-color: #f5f7fa;-->
<!--}-->

<!--.menu-header {-->
<!--  height: 50px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding: 0 20px;-->
<!--  border-bottom: 1px solid #e6e6e6;-->
<!--}-->

<!--.menu-header .title {-->
<!--  font-size: 16px;-->
<!--  font-weight: 600;-->
<!--  color: #303133;-->
<!--}-->

<!--.menu-header .asset-count {-->
<!--  margin-left: 10px;-->
<!--}-->

<!--.ip-menu {-->
<!--  border-right: none;-->
<!--}-->

<!--.content-area {-->
<!--  flex: 1;-->
<!--  padding: 20px;-->
<!--  overflow-y: auto;-->
<!--}-->

<!--.empty-content {-->
<!--  flex: 1;-->
<!--  display: flex;-->
<!--  justify-content: center;-->
<!--  align-items: center;-->
<!--}-->

<!--.ip-header {-->
<!--  margin-bottom: 20px;-->
<!--  padding-bottom: 10px;-->
<!--  border-bottom: 1px solid #ebeef5;-->
<!--}-->

<!--.ip-header h2 {-->
<!--  color: #303133;-->
<!--  font-size: 18px;-->
<!--  font-weight: 600;-->
<!--  margin: 0 0 15px 0;-->
<!--}-->

<!--.chart-toggle {-->
<!--  margin-right: 20px;-->
<!--}-->

<!--.chart-section {-->
<!--  margin: 20px 0;-->
<!--  padding: 0;-->
<!--  background-color: #fff;-->
<!--  border-radius: 4px;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);-->
<!--}-->

<!--.pie-chart {-->
<!--  width: 100%;-->
<!--  height: 400px;-->
<!--}-->

<!--.asset-info {-->
<!--  padding: 15px;-->
<!--  background-color: #f5f7fa;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.info-item {-->
<!--  line-height: 28px;-->
<!--  display: flex;-->
<!--}-->

<!--.info-item .label {-->
<!--  color: #606266;-->
<!--  width: 80px;-->
<!--  text-align: right;-->
<!--  margin-right: 15px;-->
<!--}-->

<!--.info-item .value {-->
<!--  color: #303133;-->
<!--  flex: 1;-->
<!--}-->

<!--.table-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.table-section h3 {-->
<!--  margin: 15px 0;-->
<!--  color: #303133;-->
<!--  font-size: 16px;-->
<!--  font-weight: 500;-->
<!--}-->

<!--.el-tag {-->
<!--  width: 65px;-->
<!--  text-align: center;-->
<!--}-->

<!--.el-table .cell {-->
<!--  text-align: center;-->
<!--}-->

<!--.el-table .el-table__row td:nth-child(4) .cell {-->
<!--  text-align: left;-->
<!--}-->

<!--.vulnerability-group {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.group-title {-->
<!--  color: #606266;-->
<!--  font-size: 14px;-->
<!--  font-weight: 500;-->
<!--  margin: 10px 0;-->
<!--  padding-left: 10px;-->
<!--  border-left: 3px solid #409EFF;-->
<!--}-->
<!--</style>-->


<!--<template>-->
<!--  <div class="vulnerability-container">-->
<!--    &lt;!&ndash; 左侧IP列表 &ndash;&gt;-->
<!--    <div class="ip-list">-->
<!--      <div class="menu-header">-->
<!--        <span class="title">资产</span>-->
<!--        <el-badge-->
<!--            :value="assets.length"-->
<!--            class="asset-count"-->
<!--            type="primary">-->
<!--        </el-badge>-->
<!--      </div>-->
<!--      <el-menu-->
<!--          :default-active="currentIp"-->
<!--          class="ip-menu"-->
<!--          @select="handleSelect">-->
<!--        <el-menu-item-->
<!--            v-for="asset in assets"-->
<!--            :key="asset.ip"-->
<!--            :index="asset.ip">-->
<!--          <i class="el-icon-monitor"></i>-->
<!--          <span>{{ asset.ip }}</span>-->
<!--        </el-menu-item>-->
<!--      </el-menu>-->
<!--    </div>-->

<!--    &lt;!&ndash; 右侧详情内容 &ndash;&gt;-->
<!--    <div class="content-area" v-if="currentAsset">-->
<!--      <div class="ip-header">-->
<!--        <h2>资产信息</h2>-->
<!--        <div class="asset-info">-->
<!--          <div class="info-item">-->
<!--            <span class="label">IP地址：</span>-->
<!--            <span class="value">{{ currentAsset.ip }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">操作系统：</span>-->
<!--            <span class="value">{{ currentAsset.os }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">开放端口：</span>-->
<!--            <span class="value">{{ currentAsset.ports }}</span>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->

<!--      &lt;!&ndash; 漏洞类型统计饼图 &ndash;&gt;-->
<!--      <el-card class="chart-section">-->
<!--        <div slot="header" class="clearfix">-->
<!--          <span>漏洞类型分布</span>-->
<!--        </div>-->
<!--        <div class="pie-chart" ref="pieChart" style="width: 100%; height: 400px;"></div>-->
<!--      </el-card>-->

<!--      &lt;!&ndash; 主机漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3>主机漏洞</h3>-->
<!--        <el-table-->
<!--            :data="currentAsset.host_vulnerabilities"-->
<!--            border-->
<!--            stripe-->
<!--            :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--        >-->
<!--          <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--          <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--          <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--          <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                {{ scope.row.vulExist }}-->
<!--              </el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--      </div>-->

<!--      &lt;!&ndash; 端口漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3>端口漏洞</h3>-->
<!--        <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"-->
<!--             :key="type"-->
<!--             class="vulnerability-group">-->
<!--          <h4 class="group-title">{{ type }}</h4>-->
<!--          <el-table-->
<!--              :data="vulnerabilities"-->
<!--              border-->
<!--              stripe-->
<!--              :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--          >-->
<!--            <el-table-column prop="port_id" label="端口" width="100"></el-table-column>-->
<!--            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--            <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--            <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--            <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                  {{ scope.row.vulExist }}-->
<!--                </el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 未选择IP时的提示 &ndash;&gt;-->
<!--    <div class="empty-content" v-else>-->
<!--      <el-empty description="请选择左侧IP地址查看详情"></el-empty>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import * as echarts from 'echarts';-->

<!--export default {-->
<!--  name: 'VulnerabilityTable',-->
<!--  data() {-->
<!--    return {-->
<!--      currentIp: '',-->
<!--      pieChart: null,-->
<!--      assets: [-->
<!--        {-->
<!--          "host_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "9.800000",-->
<!--              "softwareType": "操作系统",-->
<!--              "summary": "MongoDB 4.2.7存在权限提升漏洞，攻击者可以通过特定的构造命令绕过认证并获得管理员权限。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2020-12345",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "7.500000",-->
<!--              "softwareType": "操作系统",-->
<!--              "summary": "Windows SMBv3协议存在内存损坏漏洞，允许远程代码执行。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2021-34527",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ],-->
<!--          "ip": "10.8.250.77",-->
<!--          "port_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 8080,-->
<!--              "softwareType": "Web应用程序",-->
<!--              "summary": "Apache Struts 2.3.34 存在远程代码执行漏洞，攻击者可通过恶意请求触发。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-11776",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 804,-->
<!--              "softwareType": "Web应用程序",-->
<!--              "summary": "描述。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-12436",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 808,-->
<!--              "softwareType": "系统工具",-->
<!--              "summary": "Apache Struts 2.3.34 存在远程代码执行漏洞，攻击者可通过恶意请求触发。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-1236",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 80,-->
<!--              "softwareType": "未知类型",-->
<!--              "summary": "描述。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-132",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ]-->
<!--        },-->
<!--        {-->
<!--          "host_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "6.500000",-->
<!--              "softwareType": "操作系统",-->
<!--              "summary": "VMware ESXi 7.0中的特定模块存在拒绝服务漏洞，可能导致虚拟机异常终止。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2022-12345",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ],-->
<!--          "ip": "192.168.1.100",-->
<!--          "port_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "10.000000",-->
<!--              "port_id": 443,-->
<!--              "softwareType": "Web服务器",-->
<!--              "summary": "nginx 1.18.0 存在缓冲区溢出漏洞，允许远程攻击者执行任意代码。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2021-23017",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ]-->
<!--        }-->
<!--      ]-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    currentAsset() {-->
<!--      return this.assets.find(asset => asset.ip === this.currentIp);-->
<!--    },-->
<!--    groupedPortVulnerabilities() {-->
<!--      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {-->
<!--        return {};-->
<!--      }-->
<!--      return this.currentAsset.port_vulnerabilities.reduce((groups, vuln) => {-->
<!--        const type = vuln.softwareType || '未分类';-->
<!--        if (!groups[type]) {-->
<!--          groups[type] = [];-->
<!--        }-->
<!--        groups[type].push(vuln);-->
<!--        return groups;-->
<!--      }, {});-->
<!--    },-->
<!--    vulnerabilityTypeStats() {-->
<!--      const stats = {-->
<!--        '操作系统': 0,-->
<!--        'Web应用程序': 0,-->
<!--        '系统工具': 0,-->
<!--        '中间件': 0,-->
<!--        '未知类型': 0-->
<!--      };-->

<!--      // 统计主机漏洞-->
<!--      if (this.currentAsset?.host_vulnerabilities) {-->
<!--        this.currentAsset.host_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      // 统计端口漏洞-->
<!--      if (this.currentAsset?.port_vulnerabilities) {-->
<!--        this.currentAsset.port_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      return stats;-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    getResults() {-->
<!--      fetch('/api/getAllAssetsVulnData')-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.assets = data;-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->
<!--    handleSelect(ip) {-->
<!--      this.currentIp = ip;-->
<!--      this.updatePieChart();-->
<!--    },-->
<!--    getCvssType(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return 'danger';-->
<!--      if (score >= 4.0) return 'warning';-->
<!--      if (score >= 0.0) return 'success';-->
<!--      return 'info';-->
<!--    },-->
<!--    getRiskLevel(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return '高风险';-->
<!--      if (score >= 4.0) return '中风险';-->
<!--      if (score >= 0.0) return '低风险';-->
<!--      return '信息';-->
<!--    },-->
<!--    async initPieChart() {-->
<!--      await this.$nextTick();-->
<!--      if (this.$refs.pieChart) {-->
<!--        if (this.pieChart) {-->
<!--          this.pieChart.dispose();-->
<!--        }-->
<!--        this.pieChart = echarts.init(this.$refs.pieChart);-->
<!--        window.addEventListener('resize', () => {-->
<!--          this.pieChart && this.pieChart.resize();-->
<!--        });-->
<!--        this.updatePieChart();-->
<!--      }-->
<!--    },-->
<!--    updatePieChart() {-->
<!--      if (!this.pieChart) {-->
<!--        this.initPieChart();-->
<!--        return;-->
<!--      }-->

<!--      const stats = this.vulnerabilityTypeStats;-->
<!--      const data = Object.entries(stats)-->
<!--          .filter(([, value]) => value > 0) // 只显示数量大于0的类型-->
<!--          .map(([name, value]) => ({-->
<!--            name,-->
<!--            value-->
<!--          }));-->

<!--      const option = {-->
<!--        tooltip: {-->
<!--          trigger: 'item',-->
<!--          formatter: '{a} <br/>{b}: {c} ({d}%)'-->
<!--        },-->
<!--        legend: {-->
<!--          orient: 'vertical',-->
<!--          right: 'right',-->
<!--          top: 'middle',-->
<!--          data: data.map(item => item.name)-->
<!--        },-->
<!--        series: [-->
<!--          {-->
<!--            name: '漏洞类型分布',-->
<!--            type: 'pie',-->
<!--            radius: ['40%', '70%'],-->
<!--            center: ['40%', '50%'],-->
<!--            avoidLabelOverlap: false,-->
<!--            itemStyle: {-->
<!--              borderRadius: 10,-->
<!--              borderColor: '#fff',-->
<!--              borderWidth: 2-->
<!--            },-->
<!--            label: {-->
<!--              show: true,-->
<!--              formatter: '{b}: {c}个'-->
<!--            },-->
<!--            emphasis: {-->
<!--              label: {-->
<!--                show: true,-->
<!--                fontSize: '18',-->
<!--                fontWeight: 'bold'-->
<!--              }-->
<!--            },-->
<!--            labelLine: {-->
<!--              show: true-->
<!--            },-->
<!--            data: data-->
<!--          }-->
<!--        ]-->
<!--      };-->

<!--      this.pieChart.setOption(option);-->
<!--    }-->
<!--  },-->
<!--  created() {-->
<!--    this.getResults();-->
<!--  },-->
<!--  mounted() {-->
<!--    // 默认选中第一个IP-->
<!--    if (this.assets.length > 0) {-->
<!--      this.currentIp = this.assets[0].ip;-->
<!--    }-->
<!--    this.$nextTick(() => {-->
<!--      this.initPieChart();-->
<!--    });-->
<!--  },-->
<!--  beforeDestroy() {-->
<!--    if (this.pieChart) {-->
<!--      this.pieChart.dispose();-->
<!--      this.pieChart = null;-->
<!--    }-->
<!--  },-->
<!--  watch: {-->
<!--    currentAsset() {-->
<!--      this.$nextTick(() => {-->
<!--        this.updatePieChart();-->
<!--      });-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.vulnerability-container {-->
<!--  display: flex;-->
<!--  height: 100%;-->
<!--  min-height: 600px;-->
<!--  background-color: #fff;-->
<!--}-->

<!--.ip-list {-->
<!--  width: 250px;-->
<!--  border-right: 1px solid #e6e6e6;-->
<!--  background-color: #f5f7fa;-->
<!--}-->

<!--.menu-header {-->
<!--  height: 50px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding: 0 20px;-->
<!--  border-bottom: 1px solid #e6e6e6;-->
<!--}-->

<!--.menu-header .title {-->
<!--  font-size: 16px;-->
<!--  font-weight: 600;-->
<!--  color: #303133;-->
<!--}-->

<!--.menu-header .asset-count {-->
<!--  margin-left: 10px;-->
<!--}-->

<!--.ip-menu {-->
<!--  border-right: none;-->
<!--}-->

<!--.content-area {-->
<!--  flex: 1;-->
<!--  padding: 20px;-->
<!--  overflow-y: auto;-->
<!--}-->

<!--.empty-content {-->
<!--  flex: 1;-->
<!--  display: flex;-->
<!--  justify-content: center;-->
<!--  align-items: center;-->
<!--}-->

<!--.ip-header {-->
<!--  margin-bottom: 20px;-->
<!--  padding-bottom: 10px;-->
<!--  border-bottom: 1px solid #ebeef5;-->
<!--}-->

<!--.ip-header h2 {-->
<!--  color: #303133;-->
<!--  font-size: 18px;-->
<!--  font-weight: 600;-->
<!--  margin: 0 0 15px 0;-->
<!--}-->

<!--.asset-info {-->
<!--  padding: 15px;-->
<!--  background-color: #f5f7fa;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.info-item {-->
<!--  line-height: 28px;-->
<!--  display: flex;-->
<!--}-->

<!--.info-item .label {-->
<!--  color: #606266;-->
<!--  width: 80px;-->
<!--  text-align: right;-->
<!--  margin-right: 15px;-->
<!--}-->

<!--.info-item .value {-->
<!--  color: #303133;-->
<!--  flex: 1;-->
<!--}-->

<!--.table-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.table-section h3 {-->
<!--  margin: 15px 0;-->
<!--  color: #303133;-->
<!--  font-size: 16px;-->
<!--  font-weight: 500;-->
<!--}-->

<!--.el-tag {-->
<!--  width: 65px;-->
<!--  text-align: center;-->
<!--}-->

<!--/* 表格内的标签居中显示 */-->
<!--.el-table .cell {-->
<!--  text-align: center;-->
<!--}-->

<!--/* 确保描述列左对齐 */-->
<!--.el-table .el-table__row td:nth-child(4) .cell {-->
<!--  text-align: left;-->
<!--}-->

<!--.vulnerability-group {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.group-title {-->
<!--  color: #606266;-->
<!--  font-size: 14px;-->
<!--  font-weight: 500;-->
<!--  margin: 10px 0;-->
<!--  padding-left: 10px;-->
<!--  border-left: 3px solid #409EFF;-->
<!--}-->

<!--/* 新增的饼图相关样式 */-->
<!--.chart-section {-->
<!--  margin: 10px 0;-->
<!--  padding: 20px;-->
<!--  background-color: #fff;-->
<!--  border-radius: 4px;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);-->
<!--}-->

<!--.chart-section h3 {-->
<!--  margin-bottom: 20px;-->
<!--  color: #303133;-->
<!--}-->

<!--.pie-chart {-->
<!--  width: 100%;-->
<!--  height: 400px;-->
<!--}-->
<!--</style>-->