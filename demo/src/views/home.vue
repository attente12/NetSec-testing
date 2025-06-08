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

    <!-- 使用手册区域 -->
    <div class="manual-section">
      <el-card shadow="hover" class="manual-card">
        <div class="manual-header">
          <i class="el-icon-document"></i>
          <h2>使用手册</h2>
        </div>
        <div class="manual-content">
          <div class="manual-description">
            <p>为便于用户快速上手平台各项功能，我们提供了详细的使用手册和相关模板文件，助力您高效开展安全测试工作。</p>
          </div>
          <div class="manual-items">
            <div class="manual-item">
              <div class="manual-item-icon">
                <i class="el-icon-document-copy"></i>
              </div>
              <div class="manual-item-content">
                <h4>POC脚本模板</h4>
                <p>包含常见漏洞的POC脚本编写模板，便于安全人员快速开发自定义POC</p>
                <el-button type="primary" size="small" icon="el-icon-download" @click="downloadFile('/poc_helper.pdf')">
                  下载模板
                </el-button>
              </div>
            </div>

            <!-- 新增的CVE库使用手册下载模块 -->
            <div class="manual-item">
              <div class="manual-item-icon">
                <i class="el-icon-document"></i>
              </div>
              <div class="manual-item-content">
                <h4>CVE库使用手册</h4>
                <p>详细介绍CVE库的使用方法、CVE漏洞库界面各个字段的含义</p>
                <el-button type="primary" size="small" icon="el-icon-download" @click="downloadFile('/CVE-Search_helper.pdf')">
                  下载手册
                </el-button>
              </div>
            </div>

            <div class="manual-item">
              <div class="manual-item-icon">
                <i class="el-icon-document"></i>
              </div>
              <div class="manual-item-content">
                <h4>三级等保说明</h4>
                <p>介绍三级等保各检测项的内容和建议</p>
                <el-button type="primary" size="small" icon="el-icon-download" @click="downloadFile('/level3_protection_description.pdf')">
                  下载手册
                </el-button>
              </div>
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
    downloadFile(filePath) {
      // 创建一个链接，指向文件路径
      const link = document.createElement('a');
      link.href = filePath;

      // 设置下载的文件名
      const fileName = filePath.split('/').pop();
      link.download = fileName;

      // 模拟点击链接进行下载
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // 显示下载成功提示
      this.$message({
        message: '文件下载已开始',
        type: 'success',
        duration: 2000
      });
    }
  },
  created() {

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

/* 使用手册样式 */
.manual-section {
  margin-bottom: 30px;
}

.manual-card {
  border-radius: 8px;
  overflow: hidden;
}

.manual-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.manual-header i {
  font-size: 24px;
  color: #409EFF;
  margin-right: 10px;
}

.manual-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.manual-description {
  margin-bottom: 20px;
}

.manual-description p {
  font-size: 16px;
  line-height: 1.8;
  color: #606266;
}

.manual-items {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.manual-item {
  display: flex;
  padding: 20px;
  border-radius: 8px;
  background-color: #f5f7fa;
  transition: all 0.3s;
  border-left: 4px solid #409EFF;
}

.manual-item:hover {
  background-color: #eef5fe;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.manual-item-icon {
  margin-right: 15px;
  flex-shrink: 0;
}

.manual-item-icon i {
  font-size: 28px;
  color: #409EFF;
}

.manual-item-content h4 {
  margin: 0 0 10px;
  font-size: 18px;
  color: #303133;
}

.manual-item-content p {
  margin: 0 0 15px;
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

  .manual-items {
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


<!--&lt;!&ndash; HomePage.vue &ndash;&gt;-->
<!--<template>-->
<!--  <div class="home-container">-->
<!--    &lt;!&ndash; 顶部欢迎区域 &ndash;&gt;-->
<!--    <div class="welcome-section">-->
<!--      <h1 class="welcome-title">-->
<!--        网络安全测试平台-->
<!--        <span class="sub-title">保障网络安全，从资产管理到风险评估，一站式解决方案</span>-->
<!--      </h1>-->
<!--    </div>-->

<!--    &lt;!&ndash; 平台简介区域 &ndash;&gt;-->
<!--    <div class="platform-intro">-->
<!--      <el-card shadow="hover" class="intro-card">-->
<!--        <div class="intro-header">-->
<!--          <i class="el-icon-lock"></i>-->
<!--          <h2>平台简介</h2>-->
<!--        </div>-->
<!--        <div class="intro-content">-->
<!--          <p>在数字化时代，网络安全风险无处不在。我们的<strong>网络安全测试平台</strong>，集<strong>资产清点、安全基线检测、弱口令检测、安全风险评估、安全等级保护测评、测试报告输出</strong>于一体，旨在为企业提供全方位、智能化的安全检测服务，助力提升网络安全防护能力。</p>-->

<!--        </div>-->
<!--      </el-card>-->
<!--    </div>-->

<!--    &lt;!&ndash; 功能模块区域 &ndash;&gt;-->
<!--    <div class="features-section">-->
<!--      <div class="section-header">-->
<!--        <i class="el-icon-s-grid"></i>-->
<!--        <h2>核心功能</h2>-->
<!--      </div>-->
<!--      <div class="features-grid">-->
<!--        <div class="feature-card"-->
<!--             v-for="(feature, index) in features"-->
<!--             :key="index"-->
<!--             @click="navigateToFeature(feature.path)"-->
<!--             :style="{ animationDelay: index * 0.1 + 's' }">-->
<!--          <el-card shadow="hover" :body-style="{ padding: '0px' }">-->
<!--            <div class="feature-icon" :style="{ background: feature.gradient || 'linear-gradient(135deg, #409EFF, #67C23A)' }">-->
<!--              <i :class="feature.icon"></i>-->
<!--            </div>-->
<!--            <div class="feature-content">-->
<!--              <h3>{{ feature.title }}</h3>-->
<!--              <p>{{ feature.description }}</p>-->
<!--            </div>-->
<!--          </el-card>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 功能详情区域 &ndash;&gt;-->
<!--    <div class="feature-details">-->
<!--      <el-card shadow="hover" class="details-card">-->
<!--        <div class="details-header">-->
<!--          <i class="el-icon-s-opportunity"></i>-->
<!--          <h2>功能详情</h2>-->
<!--        </div>-->
<!--        <div class="details-content">-->
<!--          <div class="detail-item" v-for="(item, index) in featureDetails" :key="index">-->
<!--            <div class="detail-icon">-->
<!--              <i class="el-icon-check"></i>-->
<!--            </div>-->
<!--            <div class="detail-text">-->
<!--              <h4>{{ item.title }}</h4>-->
<!--              <p>{{ item.description }}</p>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->
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
<!--        { label: '系统状态', value: '正常', icon: 'el-icon-success' },-->
<!--        { label: '待处理', value: '5', icon: 'el-icon-bell' }-->
<!--      ],-->
<!--      features: [-->
<!--        {-->
<!--          title: '资产管理',-->
<!--          description: '网络设备与系统资产管理',-->
<!--          icon: 'el-icon-collection',-->
<!--          path: '/assetManage',-->
<!--          gradient: 'linear-gradient(135deg, #1890FF, #36CBCB)',-->
<!--          stats: {-->
<!--            percentage: 95,-->
<!--            label: '覆盖率',-->
<!--            color: '#1890FF'-->
<!--          }-->
<!--        },-->
<!--        {-->
<!--          title: '基线检测',-->
<!--          description: '系统配置安全基线检测与评估',-->
<!--          icon: 'el-icon-aim',-->
<!--          path: '/baseCheckHome',-->
<!--          gradient: 'linear-gradient(135deg, #67C23A, #95DE64)',-->
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
<!--          path: '/weakPasswordDetect',-->
<!--          gradient: 'linear-gradient(135deg, #409EFF, #85A5FF)',-->
<!--          stats: {-->
<!--            percentage: 92,-->
<!--            label: '安全度',-->
<!--            color: '#409EFF'-->
<!--          }-->
<!--        },-->
<!--        {-->
<!--          title: '安全风险评估',-->
<!--          description: '系统漏洞扫描与评估',-->
<!--          icon: 'el-icon-discover',-->
<!--          path: '/pocScanner',-->
<!--          gradient: 'linear-gradient(135deg, #E6A23C, #F5C842)',-->
<!--          stats: {-->
<!--            percentage: 76,-->
<!--            label: '漏洞率',-->
<!--            color: '#E6A23C'-->
<!--          }-->
<!--        },-->
<!--        {-->
<!--          title: '等级保护测评',-->
<!--          description: '等级保护合规性评估',-->
<!--          icon: 'el-icon-trophy',-->
<!--          path: '/classifyProtect',-->
<!--          gradient: 'linear-gradient(135deg, #F56C6C, #FF9F7F)',-->
<!--          stats: {-->
<!--            percentage: 88,-->
<!--            label: '达标率',-->
<!--            color: '#67C23A'-->
<!--          }-->
<!--        },-->
<!--      ],-->
<!--      featureDetails: [-->
<!--        {-->
<!--          title: '资产清点',-->
<!--          description: '全面盘点企业的主机及关键资产，构建细粒度资产信息库，提供可视化"概览视图"与"分级视图"，帮助用户快速掌握资产情况，确保安全检测范围的完整性。'-->
<!--        },-->
<!--        {-->
<!--          title: '安全基线检测',-->
<!--          description: '依据多项权威安全标准（如等保三级、安全基线规范等），对系统配置、弱密码等关键安全项进行深入核查，确保系统符合行业安全要求。'-->
<!--        },-->
<!--        {-->
<!--          title: '弱口令检测',-->
<!--          description: '智能化扫描各类应用（如SSH、Tomcat、Mysql、Redis等）弱口令，支持自定义口令字典，精准识别易被攻击的账号，提高密码安全性。'-->
<!--        },-->
<!--        {-->
<!--          title: '安全风险评估',-->
<!--          description: '遵循GB/T 20984-2022《信息安全技术信息安全风险评估方法》，结合漏洞扫描、端口探测、服务识别等技术，对信息系统的脆弱性进行全面评估。'-->
<!--        },-->
<!--        {-->
<!--          title: '安全等级保护测评',-->
<!--          description: '基于GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》，对信息系统进行等级划分，对比安全技术要求，提供安全加固建议，确保符合等级保护要求。'-->
<!--        },-->
<!--        {-->
<!--          title: '测试报告输出',-->
<!--          description: '自动生成安全测试报告，包括资产概览、安全检测结果、风险分析与整改建议，并支持PDF格式导出，助力企业制定精准的安全防护策略。'-->
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

<!--  },-->
<!--  created() {-->

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
<!--  text-align: center;-->
<!--  padding: 40px 0;-->
<!--  background: linear-gradient(135deg, #409EFF, #67C23A);-->
<!--  border-radius: 8px;-->
<!--  color: white;-->
<!--  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.welcome-title {-->
<!--  font-size: 32px;-->
<!--  margin-bottom: 0;-->
<!--  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);-->
<!--}-->

<!--.welcome-title .sub-title {-->
<!--  display: block;-->
<!--  font-size: 18px;-->
<!--  font-weight: normal;-->
<!--  margin-top: 15px;-->
<!--  opacity: 0.9;-->
<!--}-->

<!--/* 平台简介样式 */-->
<!--.platform-intro {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.intro-card {-->
<!--  border-radius: 8px;-->
<!--  overflow: hidden;-->
<!--}-->

<!--.intro-header {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.intro-header i {-->
<!--  font-size: 24px;-->
<!--  color: #409EFF;-->
<!--  margin-right: 10px;-->
<!--}-->

<!--.intro-header h2 {-->
<!--  margin: 0;-->
<!--  font-size: 22px;-->
<!--  color: #303133;-->
<!--}-->

<!--.intro-content p {-->
<!--  font-size: 16px;-->
<!--  line-height: 1.8;-->
<!--  color: #606266;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.stats-container {-->
<!--  margin-top: 30px;-->
<!--}-->

<!--.stat-box {-->
<!--  background-color: #f5f7fa;-->
<!--  border-radius: 8px;-->
<!--  padding: 20px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);-->
<!--  transition: all 0.3s;-->
<!--}-->

<!--.stat-box:hover {-->
<!--  transform: translateY(-5px);-->
<!--  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.stat-box i {-->
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

<!--/* 功能模块样式 */-->
<!--.section-header {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.section-header i {-->
<!--  font-size: 24px;-->
<!--  color: #409EFF;-->
<!--  margin-right: 10px;-->
<!--}-->

<!--.section-header h2 {-->
<!--  margin: 0;-->
<!--  font-size: 22px;-->
<!--  color: #303133;-->
<!--}-->

<!--.features-section {-->
<!--  margin-bottom: 30px;-->
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
<!--  height: 100px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  justify-content: center;-->
<!--  border-radius: 8px 8px 0 0;-->
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
<!--  color: #606266;-->
<!--  margin: 0;-->
<!--  height: 40px;-->
<!--  font-size: 14px;-->
<!--  overflow: hidden;-->
<!--  text-overflow: ellipsis;-->
<!--  display: -webkit-box;-->
<!--  -webkit-line-clamp: 2;-->
<!--  -webkit-box-orient: vertical;-->
<!--}-->

<!--/* 功能详情样式 */-->
<!--.feature-details {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.details-card {-->
<!--  border-radius: 8px;-->
<!--  overflow: hidden;-->
<!--}-->

<!--.details-header {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.details-header i {-->
<!--  font-size: 24px;-->
<!--  color: #409EFF;-->
<!--  margin-right: 10px;-->
<!--}-->

<!--.details-header h2 {-->
<!--  margin: 0;-->
<!--  font-size: 22px;-->
<!--  color: #303133;-->
<!--}-->

<!--.details-content {-->
<!--  display: grid;-->
<!--  grid-template-columns: repeat(2, 1fr);-->
<!--  gap: 30px;-->
<!--}-->

<!--.detail-item {-->
<!--  display: flex;-->
<!--  padding: 15px;-->
<!--  border-radius: 8px;-->
<!--  background-color: #f5f7fa;-->
<!--  transition: all 0.3s;-->
<!--}-->

<!--.detail-item:hover {-->
<!--  background-color: #eef5fe;-->
<!--  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);-->
<!--}-->

<!--.detail-icon {-->
<!--  margin-right: 15px;-->
<!--  width: 24px;-->
<!--  height: 24px;-->
<!--  background-color: #409EFF;-->
<!--  border-radius: 50%;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  justify-content: center;-->
<!--  flex-shrink: 0;-->
<!--}-->

<!--.detail-icon i {-->
<!--  font-size: 14px;-->
<!--  color: white;-->
<!--}-->

<!--.detail-text h4 {-->
<!--  margin: 0 0 8px;-->
<!--  font-size: 16px;-->
<!--  color: #303133;-->
<!--}-->

<!--.detail-text p {-->
<!--  margin: 0;-->
<!--  font-size: 14px;-->
<!--  color: #606266;-->
<!--  line-height: 1.6;-->
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

<!--  .details-content {-->
<!--    grid-template-columns: 1fr;-->
<!--  }-->
<!--}-->

<!--@media screen and (max-width: 1000px) {-->
<!--  .features-grid {-->
<!--    grid-template-columns: repeat(2, 1fr);-->
<!--  }-->
<!--}-->

<!--@media screen and (max-width: 768px) {-->
<!--  .features-grid {-->
<!--    grid-template-columns: 1fr;-->
<!--  }-->

<!--  .welcome-title {-->
<!--    font-size: 26px;-->
<!--  }-->

<!--  .welcome-title .sub-title {-->
<!--    font-size: 16px;-->
<!--  }-->
<!--}-->
<!--</style>-->

