<template>
  <div class="vulnerability-container">
    <!-- 左侧资产组列表 -->
    <div class="ip-list">
      <div class="menu-header">
        <span class="title">资产</span>
        <el-badge
            :value="assets.length"
            class="asset-count"
            type="primary">
        </el-badge>
        <el-button
            type="primary"
            icon="el-icon-plus"
            size="mini"
            circle
            class="add-group-btn"
            @click="addGroupDialogVisible = true"
            title="新增资产组">
        </el-button>
      </div>

      <div class="group-container">
        <el-collapse v-model="expandedGroups">
          <!-- 渲染每个资产组 -->
          <el-collapse-item
              v-for="group in assetGroups"
              :key="group.id"
              :name="group.id"
              class="group-item">
            <template slot="title">
              <div class="group-title">
                <span class="group-name" :title="group.name">{{ group.name }}</span>
                <span class="group-count">({{ groupedAssets[group.id]?.assets.length || 0 }})</span>
                <div class="group-actions" @click.stop>
                  <el-button
                      type="text"
                      icon="el-icon-edit"
                      size="mini"
                      @click="showEditGroupDialog(group)"
                      title="修改组名">
                  </el-button>
                  <el-button
                      type="text"
                      icon="el-icon-plus"
                      size="mini"
                      @click="showMoveAssetDialog(group)"
                      title="添加资产到此组"
                      v-if="ungroupedAssets.length > 0">
                  </el-button>
                  <el-button
                      type="text"
                      icon="el-icon-delete"
                      size="mini"
                      @click="handleDeleteGroup(group)"
                      title="删除资产组"
                      v-if="group.id !== null">
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 资产列表 -->
            <div class="assets-list">
              <div
                  v-for="asset in groupedAssets[group.id]?.assets || []"
                  :key="asset.ip"
                  :class="['asset-item', { active: currentIp === asset.ip }]"
                  @click="handleSelect(asset.ip)">
                <div class="asset-info">
                  <i class="el-icon-monitor"></i>
                  <span class="asset-ip" :title="asset.ip">{{ asset.ip }}</span>
<!--                  <div class="asset-status">-->
<!--                    <el-tag-->
<!--                        :type="asset.alive ? 'success' : 'danger'"-->
<!--                        size="mini"-->
<!--                        style="width: 30px; display: inline-block; text-align: center; margin-left: 0px;margin-right: 0px;">-->
<!--                      {{ asset.alive ? '在线' : '离线' }}-->
<!--                    </el-tag>-->
<!--                  </div>-->
                </div>
                <div class="asset-actions" @click.stop>
                  <el-dropdown @command="(groupId) => moveAssetToGroup(asset.ip, groupId)" v-if="assetGroups.filter(g => g.id !== group.id).length > 0">
                    <el-button type="text" icon="el-icon-rank" size="mini" title="移动到其他组"></el-button>
                    <el-dropdown-menu slot="dropdown">
                      <el-dropdown-item
                          v-for="targetGroup in assetGroups.filter(g => g.id !== group.id)"
                          :key="targetGroup.id"
                          :command="targetGroup.id">
                        {{ targetGroup.name }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </el-dropdown>
                </div>
              </div>

              <!-- 空状态 -->
              <div v-if="!groupedAssets[group.id]?.assets.length" class="empty-group">
                <el-empty description="暂无资产" :image-size="60"></el-empty>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <!-- 右侧详情内容 -->
    <div class="content-area" v-if="currentAsset">
      <!-- 添加打印按钮 -->
      <div class="export-section" style="margin-bottom: 20px; text-align: right;">
        <el-button
            type="primary"
            icon="el-icon-printer"
            @click="exportPdf"
            :loading="pdfExporting"
            size="medium">
          {{ pdfExporting ? '导出中...' : '导出PDF报告' }}
        </el-button>
      </div>
      <!--      <el-button type="primary" icon="el-icon-printer" @click="exportPdf" :loading="pdfExporting">-->
      <!--        导出PDF报告-->
      <!--      </el-button>-->
      <div class="ip-header">
        <h2>资产信息</h2>
        <div class="asset-info">
          <div class="info-item">
            <span class="label">IP地址：</span>
            <span class="value">{{ currentAsset.ip }}</span>
          </div>
          <div class="info-item" v-if="currentAsset.serverinfo">
            <span class="label">主机名：</span>
            <span class="value">{{ currentAsset.serverinfo.hostname }}</span>
          </div>
          <div class="info-item" v-if="currentAsset.serverinfo">
            <span class="label">操作系统：</span>
            <span class="value">{{ currentAsset.serverinfo.osName }}</span>
            <!--            <span class="value">{{ currentAsset.serverinfo.osName }} {{ // currentAsset.serverinfo.version }}</span>-->
          </div>
          <div class="info-item" v-if="currentAsset.serverinfo">
            <span class="label">主机架构：</span>
            <span class="value">{{ currentAsset.serverinfo.arch }}</span>
          </div>
          <div class="info-item" v-if="currentAsset.serverinfo">
            <span class="label">CPU：</span>
            <span class="value">{{ currentAsset.serverinfo.cpu }}</span>
            <!--            <span class="value">{{ currentAsset.serverinfo.cpu }} ({{ currentAsset.serverinfo.cpuPhysical }}物理核, {{ currentAsset.serverinfo.cpuCore }}逻辑核)</span>-->
          </div>
          <div class="info-item" v-if="currentAsset.serverinfo">
            <span class="label">硬件型号：</span>
            <span class="value">{{ currentAsset.serverinfo.ProductName }}</span>
          </div>
          <!--          <div class="info-item" v-if="currentAsset.serverinfo">-->
          <!--            <span class="label">空闲内存：</span>-->
          <!--            <span class="value">{{ currentAsset.serverinfo.free }}</span>-->
          <!--          </div>-->
          <!--          <div class="info-item" v-if="currentAsset.serverinfo">-->
          <!--            <span class="label">互联网连接：</span>-->
          <!--            <span class="value">{{ currentAsset.serverinfo.isInternet === 'true' ? '已连接' : '未连接' }}</span>-->
          <!--          </div>-->
          <div class="info-item">
            <span class="label">开放端口：</span>
            <span class="value">{{ formatOpenPorts }}</span>
          </div>
        </div>
      </div>

      <!-- 基线检测信息 -->
      <div class="baseline-section" v-if="currentAsset.baseline_summary">
<!--        <h2>-->
<!--          基线检测-->
<!--          <el-tooltip content="查看详细信息" placement="top">-->
<!--            <i class="el-icon-view baseline-info-icon" @click="showBaselineDetails"></i>-->
<!--          </el-tooltip>-->
<!--        </h2>-->
        <h2>
          基线检测
          <el-tooltip content="查看详细信息" placement="top">
            <i class="el-icon-view baseline-info-icon" @click="showBaselineDetails2"></i>
          </el-tooltip>
        </h2>
        <div class="baseline-info">
          <div class="baseline-summary">
            <div class="compliance-dashboard" style="margin-right: 30px">
              <div class="compliance-label" style="text-align: center; margin-bottom: 10px; font-weight: bold; color: #333;">不合格/已检测项数</div>
              <el-progress type="dashboard" :percentage="currentAsset.baseline_summary.non_compliance_rate" :color="'#F56C6C'" :stroke-width="10">
                <template v-slot:default>
                  <div class="progress-content">
                    <span class="rate">{{ currentAsset.baseline_summary.non_compliance_rate }}%</span>
                  </div>
                </template>
              </el-progress>
            </div>

            <div class="compliance-dashboard">
              <div class="compliance-label" style="text-align: center; margin-bottom: 10px; font-weight: bold; color: #333;">不合格/总项数</div>
              <el-progress type="dashboard" :percentage="currentAsset.baseline_summary.non_compliance_rate_to_initial_checks" :color="'#F56C6C'" :stroke-width="10">
                <template v-slot:default>
                  <div class="progress-content">
                    <span class="rate">{{ currentAsset.baseline_summary.non_compliance_rate_to_initial_checks }}%</span>
                  </div>
                </template>
              </el-progress>
            </div>

            <div class="baseline-stats">
              <div class="stat-item">
                <div class="item-header">总检测项数</div>
                <div class="item-value" style="color: #303133;">{{ currentAsset.baseline_summary.total_checks }}</div>
              </div>
              <div class="stat-item">
                <div class="item-header">合格项数</div>
                <div class="item-value" style="color: #67C23A;">{{ currentAsset.baseline_summary.compliant_items }}</div>
              </div>
              <div class="stat-item">
                <div class="item-header">待检测项数</div>
                <div class="item-value" style="color: #E6A23C;">{{ currentAsset.baseline_summary.pending_items }}</div>
              </div>
              <div class="stat-item">
                <div class="item-header">不合格项数</div>
                <div class="item-value" style="color: #F56C6C;">{{ currentAsset.baseline_summary.non_compliant_items }}</div>
              </div>
            </div>
          </div>
          <!-- 未检查项展示 -->
          <div class="undo-items-section" v-if="currentAsset.undo_baseline && currentAsset.undo_baseline.length > 0">
            <el-collapse v-model="activeBaselineUndoItems" accordion>
              <el-collapse-item name="undo">
                <template slot="title">
        <span class="undo-title">
          <i class="el-icon-warning-outline"></i>
          未检查项 ({{ currentAsset.undo_baseline.length }}项)
        </span>
                </template>
                <div class="undo-content">
                  <el-table
                      :data="currentAsset.undo_baseline"
                      border
                      stripe
                      :header-cell-style="{ backgroundColor: '#f5f7fa' }">
                    <el-table-column prop="item_id" label="项目ID" width="80"></el-table-column>
                    <el-table-column prop="description" label="检查项" width="200"></el-table-column>
                    <el-table-column prop="basis" label="检查依据"></el-table-column>
                  </el-table>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>
      <!-- 等保测评信息 -->
      <!--      <div class="baseline-section" v-if="currentAsset.baseline_summary">-->
      <!--        <h2>-->
      <!--          等级保护测评-->
      <!--          <el-tooltip content="查看详细信息" placement="top">-->
      <!--            <i class="el-icon-view baseline-info-icon" @click="showClassifyProtectDetails"></i>-->
      <!--          </el-tooltip>-->
      <!--        </h2>-->
      <!--        <div class="baseline-info">-->
      <!--          <div class="baseline-summary">-->
      <!--            <div class="compliance-dashboard">-->
      <!--&lt;!&ndash;              <div class="compliance-label" style="text-align: center; margin-bottom: 10px; font-weight: bold; color: #333;">合规率</div>&ndash;&gt;-->
      <!--&lt;!&ndash;              <el-progress type="dashboard" :percentage="currentAsset.baseline_summary.compliance_rate" :color="'#67C23A'" :stroke-width="10">&ndash;&gt;-->
      <!--&lt;!&ndash;                <template v-slot:default>&ndash;&gt;-->
      <!--&lt;!&ndash;                  <div class="progress-content">&ndash;&gt;-->
      <!--&lt;!&ndash;                    <span class="rate">{{ currentAsset.baseline_summary.compliance_rate }}%</span>&ndash;&gt;-->
      <!--&lt;!&ndash;                  </div>&ndash;&gt;-->
      <!--&lt;!&ndash;                </template>&ndash;&gt;-->
      <!--&lt;!&ndash;              </el-progress>&ndash;&gt;-->
      <!--            </div>-->
      <!--          </div>-->
      <!--        </div>-->
      <!--      </div>-->
      <!-- 等保测评信息 -->
      <div class="baseline-section" v-if="currentAsset.level3_baseline_summary">
        <h2>
          等级保护测评
          <el-tooltip content="查看详细信息" placement="top">
            <i class="el-icon-view baseline-info-icon" @click="showClassifyProtectDetails2"></i>
          </el-tooltip>
        </h2>
        <div class="baseline-info">
          <!-- 等保得分显示区域 -->
          <div class="level-score-section" v-if="typeof currentAsset.M !== 'undefined'">
            <div class="score-header">
              <i class="el-icon-trophy"></i>
              <span>等保测评得分</span>
            </div>
            <div class="score-display-inline">
              <div class="score-circle-small" :class="getScoreGradeClass(currentAsset.M)">
                <!--                <span class="score-number-small">{{ currentAsset.M }}</span>-->
                <span class="score-number-small">{{ formattedM }}</span>

                <span class="score-unit-small">分</span>
              </div>
              <div class="score-grade-inline">
                <el-tag :type="getScoreTagType(currentAsset.M)" size="medium">
                  {{ getScoreGrade(currentAsset.M) }}
                </el-tag>
                <div class="score-progress-inline">
                  <el-progress
                      :percentage="currentAsset.M"
                      :color="getScoreProgressColor(currentAsset.M)"
                      :stroke-width="8"
                      :show-text="false">
                  </el-progress>
                </div>
              </div>
            </div>
          </div>
          <div class="baseline-summary">
            <div class="compliance-dashboard" style="margin-right: 30px">
              <div class="compliance-label" style="text-align: center; margin-bottom: 10px; font-weight: bold; color: #333;">不合格/已检测项数</div>
              <el-progress type="dashboard" :percentage="currentAsset.level3_baseline_summary.non_compliance_rate" :color="getLevel3ComplianceColor" :stroke-width="10">
                <template v-slot:default>
                  <div class="progress-content">
                    <span class="rate">{{ currentAsset.level3_baseline_summary.non_compliance_rate }}%</span>
                  </div>
                </template>
              </el-progress>
            </div>
            <div class="compliance-dashboard">
              <div class="compliance-label" style="text-align: center; margin-bottom: 10px; font-weight: bold; color: #333;">不合格/总项数</div>
              <el-progress type="dashboard" :percentage="currentAsset.level3_baseline_summary.non_compliance_rate_to_initial_checks" :color="getLevel3ComplianceColor" :stroke-width="10">
                <template v-slot:default>
                  <div class="progress-content">
                    <span class="rate">{{ currentAsset.level3_baseline_summary.non_compliance_rate_to_initial_checks }}%</span>
                  </div>
                </template>
              </el-progress>
            </div>

            <div class="baseline-stats">
              <div class="stat-item">
                <div class="item-header">总检测项数</div>
                <div class="item-value" style="color: #303133;">{{ currentAsset.level3_baseline_summary.total_checks }}</div>
              </div>
              <div class="stat-item">
                <div class="item-header">合格项数</div>
                <div class="item-value" style="color: #67C23A;">{{ currentAsset.level3_baseline_summary.compliant_items }}</div>
              </div>
              <div class="stat-item">
                <div class="item-header">部分合格项数</div>
                <div class="item-value" style="color: #E6A23C;">{{ currentAsset.level3_baseline_summary.pending_items }}</div>
              </div>
              <div class="stat-item">
                <div class="item-header">不合格项数</div>
                <div class="item-value" style="color: #F56C6C;">{{ currentAsset.level3_baseline_summary.non_compliant_items }}</div>
              </div>
            </div>
          </div>

          <!-- 未检查项展示 -->
          <div class="undo-items-section" v-if="currentAsset.undo_level3_baseline && currentAsset.undo_level3_baseline.length > 0">
            <el-collapse v-model="activeUndoItems" accordion>
              <el-collapse-item name="undo">
                <template slot="title">
            <span class="undo-title">
              <i class="el-icon-warning-outline"></i>
              未检查项 ({{ currentAsset.undo_level3_baseline.length }}项)
            </span>
                </template>
                <div class="undo-content">
                  <el-table
                      :data="currentAsset.undo_level3_baseline"
                      border
                      stripe
                      :header-cell-style="{ backgroundColor: '#f5f7fa' }">
                    <el-table-column prop="item_id" label="项目ID" width="80"></el-table-column>
                    <el-table-column prop="description" label="检查项" width="200"></el-table-column>
                    <!--                    <el-table-column prop="important_level" label="重要级别" width="100">-->
                    <!--                      <template slot-scope="scope">-->
                    <!--                        <el-tag :type="getLevel3ImportanceLevelType(scope.row.important_level)">-->
                    <!--                          {{ getLevel3ImportanceLevel(scope.row.important_level) }}-->
                    <!--                        </el-tag>-->
                    <!--                      </template>-->
                    <!--                    </el-table-column>-->
                    <el-table-column prop="basis" label="检查依据"></el-table-column>
                  </el-table>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>

      <!-- 软件资产部分 -->
      <div class="ports-section">
        <h2>软件资产</h2>
        <div v-for="(ports, type) in groupedPorts" :key="type" class="port-group">
          <h3 class="group-title">{{ type }}</h3>
          <el-table
              :data="ports"
              border
              stripe
              :header-cell-style="{ backgroundColor: '#f5f7fa' }">
            <el-table-column prop="port" label="端口" width="80"></el-table-column>
            <el-table-column prop="protocol" label="协议" width="80"></el-table-column>
            <el-table-column prop="service_name" label="服务名称" width="120"></el-table-column>
            <el-table-column prop="product" label="产品" width="150">
              <template slot-scope="scope">
                {{ scope.row.product || '未识别' }}
              </template>
            </el-table-column>
            <el-table-column prop="version" label="版本" width="150">
              <template slot-scope="scope">
                {{ scope.row.version || '未识别' }}
              </template>
            </el-table-column>
            <!--            <el-table-column prop="product" label="产品" width="150"></el-table-column>-->
            <!--            <el-table-column prop="version" label="版本" width="150"></el-table-column>-->
            <el-table-column prop="status" label="状态" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.status === 'open' ? 'success' : 'danger'">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 风险部分 -->
      <div class="weak-password-section" v-if="weakPasswordPorts.length > 0">
        <h2>风险</h2>
        <el-table
            :data="weakPasswordPorts"
            border
            stripe
            :header-cell-style="{ backgroundColor: '#f5f7fa' }">
          <!--          <el-table-column prop="product" label="产品" width="150">-->
          <!--            <template slot-scope="scope">-->
          <!--              <span style="color: #F56C6C; font-weight: bold;">{{ scope.row.product }}</span>-->
          <!--            </template>-->
          <!--          </el-table-column>-->
          <el-table-column prop="product" label="产品" width="150">
            <template slot-scope="scope">
              <span v-if="scope.row.product" style="color: #F56C6C; font-weight: bold;">
                {{ scope.row.product }}
              </span>
              <span v-else>未识别</span>
            </template>
          </el-table-column>
          <el-table-column prop="port" label="端口" width="80"></el-table-column>
          <el-table-column prop="protocol" label="协议" width="80"></el-table-column>
          <el-table-column prop="service_name" label="服务名称" width="120"></el-table-column>
          <el-table-column prop="software_type" label="软件类型" width="120"></el-table-column>
          <el-table-column prop="weak_username" label="账号" width="120">
            <template slot-scope="scope">
              <span style="color: #F56C6C; font-weight: bold;">{{ scope.row.weak_username }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="weak_password" label="结果" width="120">
            <span style="color: #F56C6C; font-weight: bold;">存在弱密码</span>
          </el-table-column>
          <el-table-column prop="verify_time" label="检测时间" width="180"></el-table-column>
          <!--          <el-table-column prop="verify_time" label="验证时间" width="180"></el-table-column>-->
          <!--          <el-table-column prop="weak_password" label="弱密码" width="120">-->
          <!--            <template slot-scope="scope">-->
          <!--              <span style="color: #F56C6C; font-weight: bold;">{{ scope.row.weak_password }}</span>-->
          <!--            </template>-->
          <!--          </el-table-column>-->
          <!--          <el-table-column prop="verify_time" label="验证时间" width="180"></el-table-column>-->
        </el-table>
      </div>

      <h2 class="flex justify-between items-center">
        <span style="font-size: 18px;">资产漏洞信息</span>
        <div class="chart-toggle">
          <el-radio-group v-model="displayType" size="small">
            <el-radio-button label="assetType">按资产类型分布</el-radio-button>
            <el-radio-button label="vulType">按漏洞类型分布</el-radio-button>
          </el-radio-group>
        </div>
      </h2>

      <!-- 资产类型视图 -->
      <template v-if="displayType === 'assetType'">
        <!-- 饼图 -->
        <el-card class="chart-section">
          <div slot="header" class="clearfix">
            <span>漏洞资产类型分布</span>
          </div>
          <div class="pie-chart" ref="pieChart" style="width: 100%; height: 300px;"></div>
        </el-card>

        <!-- 主机漏洞表格 -->
        <div class="table-section" v-if="currentAsset.host_vulnerabilities && currentAsset.host_vulnerabilities.length > 0">
          <h3><strong>系统漏洞</strong></h3>
          <el-table
              :data="currentAsset.host_vulnerabilities"
              border
              stripe
              :header-cell-style="{ backgroundColor: '#f5f7fa' }"
          >
            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>
            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>
            <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>
            <el-table-column prop="cvss" label="风险等级" width="120">
              <template slot-scope="scope">
                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="summary" label="漏洞描述"></el-table-column>
            <el-table-column prop="vulExist" label="是否存在" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">
                  {{ scope.row.vulExist }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="scan_time" label="检测时间"></el-table-column>
          </el-table>
        </div>

        <!-- 端口漏洞分组表格 -->
        <div class="table-section" v-if="Object.keys(groupedPortVulnerabilities).length > 0">
          <h3><strong>软件资产漏洞</strong></h3>
          <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"
               :key="type"
               class="vulnerability-group">
            <h4 class="group-title">{{ type }}</h4>
            <el-table
                :data="vulnerabilities"
                border
                stripe
                :header-cell-style="{ backgroundColor: '#f5f7fa' }"
            >
              <el-table-column prop="port_id" label="端口" width="70"></el-table-column>
              <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>
              <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>
              <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>
              <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>
              <el-table-column prop="cvss" label="风险等级" width="120">
                <template slot-scope="scope">
                  <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="summary" label="漏洞描述"></el-table-column>
              <el-table-column prop="vulExist" label="是否存在" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">
                    {{ scope.row.vulExist }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="scan_time" label="检测时间"></el-table-column>
            </el-table>
          </div>
        </div>
      </template>

      <!-- 漏洞类型视图 -->
      <template v-else>
        <!-- 漏洞类型饼图 -->
        <el-card class="chart-section">
          <div slot="header" class="clearfix">
            <span>漏洞类型分布</span>
          </div>
          <div class="pie-chart" ref="vulTypePieChart" style="width: 100%; height: 300px;"></div>
        </el-card>

        <!-- 按漏洞类型分组的表格 -->
        <!--        <div class="table-section" v-if="Object.keys(groupedVulTypeVulnerabilities).length > 0">-->
        <!--          <h3><strong>漏洞详情</strong></h3>-->
        <!--          <div v-for="(vulnerabilities, type) in groupedVulTypeVulnerabilities"-->
        <!--               :key="type"-->
        <!--               class="vulnerability-group">-->
        <!--            <h4 class="group-title">{{ type }}</h4>-->
        <!--            <el-table-->
        <!--                :data="vulnerabilities"-->
        <!--                border-->
        <!--                stripe-->
        <!--                :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
        <!--            >-->
        <!--              <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
        <!--              <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
        <!--              <el-table-column prop="softwareType" label="资产类型" width="150"></el-table-column>-->
        <!--              <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>-->
        <!--              <el-table-column prop="cvss" label="风险等级" width="120">-->
        <!--                <template slot-scope="scope">-->
        <!--                  <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
        <!--                </template>-->
        <!--              </el-table-column>-->
        <!--              <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
        <!--              <el-table-column prop="vulExist" label="是否存在" width="100">-->
        <!--                <template slot-scope="scope">-->
        <!--                  <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
        <!--                    {{ scope.row.vulExist }}-->
        <!--                  </el-tag>-->
        <!--                </template>-->
        <!--              </el-table-column>-->
        <!--            </el-table>-->
        <!--          </div>-->
        <!--        </div>-->
        <div class="table-section" v-if="Object.keys(groupedVulTypeVulnerabilities).length > 0">
          <h3><strong>漏洞详情</strong></h3>
          <div v-for="(vulnerabilities, type) in groupedVulTypeVulnerabilities"
               :key="type"
               class="vulnerability-group">
            <h4 class="group-title">{{ type }}</h4>
            <el-table
                :data="vulnerabilities"
                border
                stripe
                :header-cell-style="{ backgroundColor: '#f5f7fa' }"
            >
              <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>
              <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>
              <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>
              <el-table-column prop="softwareType" label="资产类型" width="120"></el-table-column>
              <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>
              <el-table-column prop="cvss" label="风险等级" width="120">
                <template slot-scope="scope">
                  <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="summary" label="漏洞描述"></el-table-column>
              <el-table-column prop="vulExist" label="是否存在" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">
                    {{ scope.row.vulExist }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="scan_time" label="检测时间"></el-table-column>
            </el-table>
          </div>
        </div>
      </template>
    </div>
    <el-dialog
        title="基线检测详细信息"
        :visible.sync="baselineDialogVisible"
        width="70%"
        :before-close="handleBaselineDialogClose">
      <div v-if="baselineDetails.length" class="baseline-details-content">
        <el-table
            :data="baselineDetails"
            border
            stripe
            :header-cell-style="{ backgroundColor: '#f5f7fa' }">
          <el-table-column label="合规状态" width="100">
            <template slot-scope="scope">
              <el-tag v-if="scope.row.IsComply === 'true'" type="success">通过</el-tag>
              <el-tag v-else-if="scope.row.IsComply === 'pending'" type="warning">待检查</el-tag>
              <el-tag v-else type="danger">不通过</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="检查项" width="200"></el-table-column>
          <!--          <el-table-column prop="importantLevel" label="重要级别" width="100">-->
          <!--            <template slot-scope="scope">-->
          <!--              <el-tag :type="getImportanceLevelType(scope.row.importantLevel)">-->
          <!--                {{ getImportanceLevel(scope.row.importantLevel) }}-->
          <!--              </el-tag>-->
          <!--            </template>-->
          <!--          </el-table-column>-->
          <el-table-column prop="basis" label="检查依据" width="200"></el-table-column>
          <el-table-column prop="result" label="检查结果"></el-table-column>
          <el-table-column label="建议" width="350">
            <template slot-scope="scope">
              <span v-if="scope.row.IsComply === 'true'">-</span>
              <span v-else>{{ scope.row.recommend }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else class="baseline-details-loading">
        <el-empty description="暂无数据" v-if="!baselineDetailsLoading"></el-empty>
        <div v-else class="loading-container">
          <el-loading type="primary" v-loading="baselineDetailsLoading"></el-loading>
        </div>
      </div>
    </el-dialog>

    <el-dialog
        title="等保测评详细信息"
        :visible.sync="classifyDialogVisible"
        width="70%"
        :before-close="handleClassifyDialogClose">
      <div v-if="classifyDetails.length" class="baseline-details-content">
        <el-table
            :data="classifyDetails"
            border
            stripe
            :header-cell-style="{ backgroundColor: '#f5f7fa' }">
          <el-table-column label="合规状态" width="100">
            <template slot-scope="scope">
              <el-tag v-if="scope.row.IsComply === 'true'" type="success">通过</el-tag>
              <el-tag v-else-if="scope.row.IsComply === 'pending'" type="warning">待检查</el-tag>
              <el-tag v-else type="danger">不通过</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="检查项" width="200"></el-table-column>
          <!--          <el-table-column prop="importantLevel" label="重要级别" width="100">-->
          <!--            <template slot-scope="scope">-->
          <!--              <el-tag :type="getImportanceLevelType(scope.row.importantLevel)">-->
          <!--                {{ getImportanceLevel(scope.row.importantLevel) }}-->
          <!--              </el-tag>-->
          <!--            </template>-->
          <!--          </el-table-column>-->
          <el-table-column prop="basis" label="检查依据" width="200"></el-table-column>
          <el-table-column prop="result" label="检查结果"></el-table-column>
          <el-table-column label="建议" width="350">
            <template slot-scope="scope">
              <span v-if="scope.row.IsComply === 'true'">-</span>
              <span v-else>{{ scope.row.recommend }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else class="baseline-details-loading">
        <el-empty description="暂无数据" v-if="!classifyDetailsLoading"></el-empty>
        <div v-else class="loading-container">
          <el-loading type="primary" v-loading="classifyDetailsLoading"></el-loading>
        </div>
      </div>
    </el-dialog>

    <!-- 新增资产组对话框 -->
    <el-dialog
        title="新增资产组"
        :visible.sync="addGroupDialogVisible"
        width="400px"
        :before-close="handleAddGroupDialogClose">
      <el-form :model="newGroupForm" :rules="addGroupRules" ref="addGroupForm" label-width="80px">
        <el-form-item label="组名称" prop="group_name">
          <el-input v-model="newGroupForm.group_name" placeholder="请输入资产组名称" maxlength="50" show-word-limit></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
              v-model="newGroupForm.description"
              type="textarea"
              placeholder="请输入描述（可选）"
              maxlength="200"
              show-word-limit
              :rows="3">
          </el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="addGroupDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddGroup" :loading="addGroupLoading">确定</el-button>
      </div>
    </el-dialog>

    <!-- 修改资产组名称对话框 -->
    <el-dialog
        title="修改资产组名称"
        :visible.sync="editGroupDialogVisible"
        width="400px"
        :before-close="handleEditGroupDialogClose">
      <el-form :model="editGroupForm" :rules="editGroupRules" ref="editGroupForm" label-width="80px">
        <el-form-item label="新名称" prop="new_name">
          <el-input v-model="editGroupForm.new_name" placeholder="请输入新的资产组名称" maxlength="50" show-word-limit></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="editGroupDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditGroup" :loading="editGroupLoading">确定</el-button>
      </div>
    </el-dialog>

    <!-- 批量移动资产对话框 -->
    <el-dialog
        :title="`添加资产到 ${currentOperatingGroup?.name}`"
        :visible.sync="moveAssetDialogVisible"
        width="500px"
        :before-close="handleMoveAssetDialogClose">
      <div class="move-asset-content">
        <div class="selection-header">
          <span>选择要添加到该组的未分组资产：</span>
          <div class="selection-actions">
            <el-button type="text" size="small" @click="selectAllAssets">全选</el-button>
            <el-button type="text" size="small" @click="clearAssetSelection">清空</el-button>
          </div>
        </div>
        <el-checkbox-group v-model="moveAssetForm.selectedAssets">
          <div v-for="asset in ungroupedAssets" :key="asset.ip" class="asset-checkbox">
            <el-checkbox :label="asset.ip">
              <span class="asset-ip">{{ asset.ip }}</span>
              <el-tag
                  :type="asset.alive ? 'success' : 'danger'"
                  size="mini"
                  class="asset-status-tag">
                {{ asset.alive ? '在线' : '离线' }}
              </el-tag>
            </el-checkbox>
          </div>
        </el-checkbox-group>
        <div v-if="ungroupedAssets.length === 0" class="no-assets">
          <el-empty description="暂无未分组的资产" :image-size="80"></el-empty>
        </div>
      </div>
      <div slot="footer">
        <el-button @click="moveAssetDialogVisible = false">取消</el-button>
        <el-button
            type="primary"
            @click="handleMoveAssets"
            :loading="moveAssetLoading"
            :disabled="moveAssetForm.selectedAssets.length === 0">
          确定移动 ({{ moveAssetForm.selectedAssets.length }})
        </el-button>
      </div>
    </el-dialog>
  </div>

</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'VulnerabilityTable',
  data() {
    return {
      currentIp: '',
      pieChart: null,
      vulTypePieChart: null,
      displayType: 'assetType',
      assets: [

      ],
      // vulTypes: [
      //   "Buffer Overflow", "File Upload Vulnerability", "Code Injection",
      //   "SQL Injection", "Cross-Site Scripting (XSS)", "Privilege Escalation",
      //   "Denial of Service (DoS)", "Authentication Bypass", "Path Traversal",
      //   "Information Disclosure", "Cross-Site Request Forgery (CSRF)",
      //   "XML External Entity (XXE)", "Remote Code Execution (RCE)",
      //   "Session Hijacking", "Unauthorized Access"
      // ],
      vulTypes: [
        "缓冲区溢出",
        "文件上传漏洞",
        "代码注入",
        "SQL 注入",
        "跨站脚本攻击 (XSS)",
        "权限提升",
        "拒绝服务攻击 (DoS)",
        "身份验证绕过",
        "路径遍历",
        "信息泄露",
        "跨站请求伪造 (CSRF)",
        "XML 外部实体注入 (XXE)",
        "远程代码执行 (RCE)",
        "会话劫持",
        "未经授权的访问"
      ],
      // 新增端口信息的软件类型分类
      softwareTypes: [
        "系统工具", "Web应用", "中间件", "数据库", "操作系统", "未知类型"
      ],
      baselineDialogVisible: false,
      baselineDetails: [],
      baselineDetailsLoading: false,
      classifyDialogVisible: false,
      classifyDetails: [],
      classifyDetailsLoading: false,
      activeUndoItems: '', // 控制等保未检测项折叠面板的展开状态

      // 新增资产组相关数据
      assetGroups: [],

      // 对话框显示控制
      addGroupDialogVisible: false,
      editGroupDialogVisible: false,
      moveAssetDialogVisible: false,

      // 加载状态
      addGroupLoading: false,
      editGroupLoading: false,
      moveAssetLoading: false,

      // 表单数据
      newGroupForm: {
        group_name: '',
        description: ''
      },
      editGroupForm: {
        id: null,
        new_name: ''
      },
      moveAssetForm: {
        targetGroupId: null,
        selectedAssets: []
      },

      // 当前操作的资产组
      currentOperatingGroup: null,

      // 折叠面板展开状态
      expandedGroups: [],

      // 表单验证规则
      addGroupRules: {
        group_name: [
          { required: true, message: '请输入资产组名称', trigger: 'blur' },
          { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
        ]
      },
      editGroupRules: {
        new_name: [
          { required: true, message: '请输入新的资产组名称', trigger: 'blur' },
          { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
        ]
      },
      pdfExporting: false, // PDF导出加载状态
      pdfBaselineDetails: [], // PDF导出时的基线检测详细数据
      pdfClassifyDetails: [], // PDF导出时的等保测评详细数据

    }
  },
  computed: {
    formattedM() {
      return Number(this.currentAsset.M).toFixed(2);
    },
    currentAsset() {
      return this.assets.find(asset => asset.ip === this.currentIp);
    },

    // 按组分组的资产
    groupedAssets() {
      const groups = {};

      // 初始化所有资产组
      this.assetGroups.forEach(group => {
        groups[group.id] = {
          ...group,
          assets: []
        };
      });

      // 分配资产到对应组
      this.assets.forEach(asset => {
        const groupId = asset.group_id;
        if (groups[groupId]) {
          groups[groupId].assets.push(asset);
        }
      });

      return groups;
    },

    // 未分组的资产
    ungroupedAssets() {
      return this.assets.filter(asset => asset.group_id === null);
    },

    groupedPortVulnerabilities() {
      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {
        return {};
      }

      // 创建一个按指定顺序的空对象
      const orderedGroups = {};
      this.softwareTypes.forEach(type => {
        orderedGroups[type] = [];
      });

      // 填充数据
      this.currentAsset.port_vulnerabilities.forEach(vuln => {
        const type = vuln.softwareType || '未知类型';
        if (this.softwareTypes.includes(type)) {
          orderedGroups[type].push(vuln);
        } else {
          // 对于不在预定义列表中的类型，归为未知类型
          orderedGroups['未知类型'].push(vuln);
        }
      });

      // 过滤掉空数组，只返回有数据的分组
      return Object.fromEntries(
          Object.entries(orderedGroups).filter(([, vulns]) => vulns.length > 0)
      );
    },
    vulnerabilityTypeStats() {
      const stats = {
        '操作系统': 0,
        'Web应用': 0,
        '系统工具': 0,
        '中间件': 0,
        '未知类型': 0
      };

      if (this.currentAsset?.host_vulnerabilities) {
        this.currentAsset.host_vulnerabilities.forEach(vuln => {
          // 只统计"是否存在"为"存在"的漏洞
          if (vuln.vulExist === '存在') {
            const type = vuln.softwareType || '未知类型';
            if (Object.hasOwn(stats, type)) {
              stats[type]++;
            } else {
              stats['未知类型']++;
            }
          }
        });
      }

      if (this.currentAsset?.port_vulnerabilities) {
        this.currentAsset.port_vulnerabilities.forEach(vuln => {
          // 只统计"是否存在"为"存在"的漏洞
          if (vuln.vulExist === '存在') {
            const type = vuln.softwareType || '未知类型';
            if (Object.hasOwn(stats, type)) {
              stats[type]++;
            } else {
              stats['未知类型']++;
            }
          }
        });
      }

      return stats;
    },

    // 修改按漏洞类型统计的计算属性
    vulTypeStats() {
      const stats = {};

      // 初始化所有漏洞类型的计数为0
      this.vulTypes.forEach(type => {
        stats[type] = 0;
      });

      // 统计主机漏洞
      if (this.currentAsset?.host_vulnerabilities) {
        this.currentAsset.host_vulnerabilities.forEach(vuln => {
          // 只统计"是否存在"为"存在"的漏洞
          if (vuln.vulExist === '存在' && vuln.vulType) {
            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;
          }
        });
      }

      // 统计端口漏洞
      if (this.currentAsset?.port_vulnerabilities) {
        this.currentAsset.port_vulnerabilities.forEach(vuln => {
          // 只统计"是否存在"为"存在"的漏洞
          if (vuln.vulExist === '存在' && vuln.vulType) {
            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;
          }
        });
      }

      // 只返回数量大于0的类型
      return Object.fromEntries(
          Object.entries(stats).filter(([, count]) => count > 0)
      );
    },

// 更新 groupedVulTypeVulnerabilities 计算属性
    groupedVulTypeVulnerabilities() {
      // 创建一个按指定顺序的空对象
      const orderedGroups = {};
      this.vulTypes.forEach(type => {
        orderedGroups[type] = [];
      });

      // 添加未分类类别
      orderedGroups['未分类'] = [];

      // 合并主机漏洞和端口漏洞
      const allVulnerabilities = [
        ...(this.currentAsset?.host_vulnerabilities || []),
        ...(this.currentAsset?.port_vulnerabilities || [])
      ]; // 显示所有漏洞，包括"存在"和"不存在"的

      // 按漏洞类型分组
      allVulnerabilities.forEach(vuln => {
        const type = vuln.vulType || '未分类';
        if (this.vulTypes.includes(type)) {
          orderedGroups[type].push(vuln);
        } else {
          // 如果不在列表中，添加到"未分类"
          orderedGroups['未分类'].push(vuln);
        }
      });

      // 过滤掉空数组，只返回有数据的分组
      return Object.fromEntries(
          Object.entries(orderedGroups).filter(([, vulns]) => vulns.length > 0)
      );
    },

    // 新增：提取开放端口展示在资产信息中
    formatOpenPorts() {
      if (!this.currentAsset || !this.currentAsset.ports) {
        return '无';
      }
      return this.currentAsset.ports
          .filter(port => port.status === 'open')
          .map(port => `${port.port}`)
          .join(', ');
    },
    // 新增：按软件类型分组端口信息
    groupedPorts() {
      if (!this.currentAsset || !this.currentAsset.ports) {
        return {};
      }

      // 创建一个按指定顺序的空对象
      const orderedGroups = {};
      this.softwareTypes.forEach(type => {
        orderedGroups[type] = [];
      });

      // 填充数据
      this.currentAsset.ports.forEach(port => {
        const type = port.software_type || '未知类型';
        if (this.softwareTypes.includes(type)) {
          orderedGroups[type].push(port);
        } else {
          // 对于不在预定义列表中的类型，归为未知类型
          orderedGroups['未知类型'].push(port);
        }
      });

      // 过滤掉空数组，只返回有数据的分组
      return Object.fromEntries(
          Object.entries(orderedGroups).filter(([, ports]) => ports.length > 0)
      );
    },
    weakPasswordPorts() {
      if (!this.currentAsset || !this.currentAsset.ports) {
        return [];
      }
      return this.currentAsset.ports.filter(port =>
          port.weak_username && port.weak_password && port.verify_time
      );
    },
    // 新增：获取合规率颜色
    getComplianceColor() {
      if (!this.currentAsset || !this.currentAsset.baseline_summary) {
        return '#F56C6C';
      }
      const rate = this.currentAsset.baseline_summary.compliance_rate;
      if (rate < 30) return '#F56C6C';
      if (rate < 60) return '#E6A23C';
      return '#67C23A';
    },
    // 获取等保合规率颜色
    getLevel3ComplianceColor() {
      if (!this.currentAsset || !this.currentAsset.level3_baseline_summary) {
        return '#F56C6C';
      }
      // const rate = this.currentAsset.level3_baseline_summary.compliance_rate;
      // if (rate < 30) return '#F56C6C';
      // if (rate < 60) return '#E6A23C';
      // return '#67C23A';
      return '#F56C6C';
    }
  },
  methods: {
    showClassifyProtectDetails2(){
      this.$nextTick(() => {
        // 传递当前查看的IP到POC验证页面
        this.$router.push({
          path: '/classifyProtect',
          query: { ip: this.currentAsset.ip }
        });
      });
    },
    showBaselineDetails2(){
      this.$nextTick(() => {
        // 传递当前查看的IP到POC验证页面
        this.$router.push({
          path: '/baseCheck',
          query: { ip: this.currentAsset.ip }
        });
      });
    },
    // 导出PDF报告
    // 改进的寻找最佳分页点方法，防止表格行被分割
    findOptimalBreakPoint(canvas, startY, maxHeight, canvasWidth) {
      const ctx = canvas.getContext('2d');
      const imageData = ctx.getImageData(0, startY, canvasWidth, maxHeight);
      const data = imageData.data;

      // 至少保留70%的页面高度
      const minHeight = Math.max(50, maxHeight * 0.7);

      // 从底部向上扫描，寻找合适的分页点
      for (let y = Math.floor(maxHeight) - 1; y >= minHeight; y--) {
        // 检查是否为表格行边界
        if (this.isTableRowBoundary(data, y, canvasWidth, maxHeight)) {
          return y;
        }

        // 检查是否为空白行
        if (this.isRowEmpty(data, y, canvasWidth)) {
          // 确保有足够的空白区域
          let emptyRowCount = 0;
          for (let checkY = y; checkY >= Math.max(0, y - 10) && checkY < maxHeight; checkY--) {
            if (this.isRowEmpty(data, checkY, canvasWidth)) {
              emptyRowCount++;
            } else {
              break;
            }
          }

          if (emptyRowCount >= 3) {
            return y - emptyRowCount + 1;
          }
        }
      }

      // 如果没找到合适的分页点，寻找表格外的安全区域
      for (let y = Math.floor(maxHeight) - 20; y >= minHeight; y--) {
        if (this.isSafeBreakPoint(data, y, canvasWidth, maxHeight)) {
          return y;
        }
      }

      // 最后的备选方案
      return Math.floor(maxHeight * 0.9);
    },

// 检测是否为表格行边界
    isTableRowBoundary(imageData, rowIndex, width, maxHeight) {
      // 检查当前行和上下几行的特征
      const checkRange = 3;

      // 检查当前行是否有表格边框特征
      const currentRowBorderPixels = this.countBorderPixels(imageData, rowIndex, width);

      // 检查上面几行
      let aboveBorderCount = 0;
      for (let i = 1; i <= checkRange; i++) {
        const checkY = rowIndex - i;
        if (checkY >= 0) {
          const borderPixels = this.countBorderPixels(imageData, checkY, width);
          if (borderPixels > width * 0.1) { // 如果有超过10%的像素是边框色
            aboveBorderCount++;
          }
        }
      }

      // 检查下面几行
      let belowBorderCount = 0;
      for (let i = 1; i <= checkRange; i++) {
        const checkY = rowIndex + i;
        if (checkY < maxHeight) {
          const borderPixels = this.countBorderPixels(imageData, checkY, width);
          if (borderPixels > width * 0.1) {
            belowBorderCount++;
          }
        }
      }

      // 如果当前行有明显的水平边框，且上下行的边框较少，认为是表格行边界
      return currentRowBorderPixels > width * 0.15 &&
          aboveBorderCount <= 1 &&
          belowBorderCount <= 1;
    },

// 计算行中边框像素的数量
    countBorderPixels(imageData, rowIndex, width) {
      const rowStart = rowIndex * width * 4;
      const rowEnd = rowStart + width * 4;
      let borderPixels = 0;

      for (let i = rowStart; i < rowEnd; i += 4) {
        const r = imageData[i];
        const g = imageData[i + 1];
        const b = imageData[i + 2];

        // 检测边框颜色（深灰色或黑色）
        if ((r < 100 && g < 100 && b < 100) || // 深色边框
            (Math.abs(r - 221) < 10 && Math.abs(g - 221) < 10 && Math.abs(b - 221) < 10)) { // 浅灰色边框 (#ddd)
          borderPixels++;
        }
      }

      return borderPixels;
    },

// 检查是否为安全的分页点
    isSafeBreakPoint(imageData, rowIndex, width, maxHeight) {
      // 检查当前行及周围行的内容密度
      const checkRange = 5;
      let totalContentPixels = 0;
      let totalPixels = 0;

      for (let y = Math.max(0, rowIndex - checkRange);
           y <= Math.min(maxHeight - 1, rowIndex + checkRange); y++) {
        const rowStart = y * width * 4;
        const rowEnd = rowStart + width * 4;

        for (let i = rowStart; i < rowEnd; i += 4) {
          const r = imageData[i];
          const g = imageData[i + 1];
          const b = imageData[i + 2];

          totalPixels++;

          // 非白色像素视为内容
          if (r < 250 || g < 250 || b < 250) {
            totalContentPixels++;
          }
        }
      }

      // 如果内容密度很低，认为是安全的分页点
      const contentDensity = totalContentPixels / totalPixels;
      return contentDensity < 0.05;
    },

// 检查是否为空白行（保持原有逻辑）
    isRowEmpty(imageData, rowIndex, width) {
      const rowStart = rowIndex * width * 4;
      const rowEnd = rowStart + width * 4;

      for (let i = rowStart; i < rowEnd; i += 4) {
        const r = imageData[i];
        const g = imageData[i + 1];
        const b = imageData[i + 2];

        // 检查是否为白色或接近白色
        if (r < 250 || g < 250 || b < 250) {
          return false;
        }
      }
      return true;
    },
    // 改进的createMultiPagePdf方法
    async createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight) {
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;

      const pageHeight = pdfHeight - 50; // 为页码和边距留出更多空间
      const ratio = pdfWidth / imgWidth;
      const scaledWidth = pdfWidth;
      const scaledHeight = imgHeight * ratio;

      // 计算实际像素对应的PDF高度
      const pixelRatio = scaledHeight / imgHeight;
      const pageHeightInPixels = pageHeight / pixelRatio;

      let currentY = 0;
      let pageIndex = 0;
      const pages = [];

      // 第一步：生成所有页面内容
      while (currentY < imgHeight) {
        if (pageIndex > 0) {
          pdf.addPage();
        }

        // 计算当前页要显示的内容高度（像素）
        let remainingHeight = imgHeight - currentY;
        let currentPageContentHeight = Math.min(pageHeightInPixels, remainingHeight);

        // 如果不是最后一页，需要寻找合适的分页点
        if (remainingHeight > pageHeightInPixels) {
          const optimalHeight = this.findOptimalBreakPoint(
              canvas,
              currentY,
              currentPageContentHeight,
              imgWidth
          );

          // 确保分页点不会太小
          if (optimalHeight > pageHeightInPixels * 0.5) {
            currentPageContentHeight = optimalHeight;
          }
        }

        // 创建当前页的canvas
        const pageCanvas = document.createElement('canvas');
        const pageCtx = pageCanvas.getContext('2d');

        pageCanvas.width = imgWidth;
        pageCanvas.height = currentPageContentHeight;

        // 绘制当前页内容
        pageCtx.fillStyle = '#ffffff';
        pageCtx.fillRect(0, 0, imgWidth, currentPageContentHeight);

        pageCtx.drawImage(
            canvas,
            0, currentY, imgWidth, currentPageContentHeight,
            0, 0, imgWidth, currentPageContentHeight
        );

        // 转换为图片并添加到PDF
        const pageImgData = pageCanvas.toDataURL('image/png');
        const pageScaledHeight = currentPageContentHeight * pixelRatio;

        pdf.addImage(
            pageImgData,
            'PNG',
            0,
            25, // 顶部留出更多边距
            scaledWidth,
            pageScaledHeight
        );

        // 存储页面信息
        pages.push({
          pageNumber: pageIndex + 1,
          scaledHeight: pageScaledHeight
        });

        currentY += currentPageContentHeight;
        pageIndex++;

        // 防止无限循环
        if (pageIndex > 50) {
          console.warn('PDF页数过多，强制结束');
          break;
        }
      }

      const totalPages = pageIndex;

      // 第二步：为每页添加页码
      for (let i = 0; i < totalPages; i++) {
        pdf.setPage(i + 1);

        // 设置页码文本样式
        pdf.setFontSize(10);
        pdf.setTextColor(102, 102, 102);

        // 计算页码文本
        const pageText = `${i + 1}/${totalPages}`;

        // 计算文本宽度以实现居中
        const textWidth = pdf.getTextWidth(pageText);
        const xPosition = (pdfWidth - textWidth) / 2;

        // 在页面底部添加页码
        const yPosition = pdfHeight - 15;

        pdf.text(pageText, xPosition, yPosition);
      }
    },

    async exportPdf() {
      if (!this.currentAsset) {
        this.$message.warning('请先选择一个资产');
        return;
      }

      this.pdfExporting = true;

      try {
        // 获取详细的基线检测和等保测评数据
        await this.fetchDetailedDataForPdf();

        // 动态导入库
        const jsPDF = (await import('jspdf')).default;
        const html2canvas = (await import('html2canvas')).default;

        // 创建临时的打印内容容器
        const printContent = this.createPrintContent();
        document.body.appendChild(printContent);

        // 等待内容渲染完成
        await this.$nextTick();
        await new Promise(resolve => setTimeout(resolve, 1500));

        // 转换为canvas - 使用更高精度设置
        const canvas = await html2canvas(printContent, {
          scale: 1.5, // 降低scale避免内存问题
          useCORS: true,
          allowTaint: true,
          backgroundColor: '#ffffff',
          width: printContent.scrollWidth,
          height: printContent.scrollHeight,
          scrollX: 0,
          scrollY: 0,
          windowWidth: printContent.scrollWidth,
          windowHeight: printContent.scrollHeight
        });

        // 移除临时容器
        document.body.removeChild(printContent);

        // 创建PDF
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();

        // 使用改进的分页逻辑
        await this.createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight);

        // 保存PDF
        const fileName = `资产安全报告_${this.currentAsset.ip}_${new Date().toISOString().split('T')[0]}.pdf`;
        pdf.save(fileName);

        this.$message.success('PDF报告导出成功');

      } catch (error) {
        console.error('PDF导出失败:', error);
        this.$message.error('PDF导出失败，请重试');
      } finally {
        this.pdfExporting = false;
      }
    },

    // 获取详细数据用于PDF导出
    async fetchDetailedDataForPdf() {
      try {
        // 并行获取基线检测详细信息和等保测评详细信息
        const [baselineResponse, classifyResponse] = await Promise.all([
          fetch(`/api/userinfo?ip=${this.currentAsset.ip}`),
          fetch(`/api/level3Userinfo?ip=${this.currentAsset.ip}`)
        ]);

        // 处理基线检测数据
        if (baselineResponse.ok) {
          const baselineData = await baselineResponse.json();
          this.pdfBaselineDetails = baselineData.checkResults || [];
        }

        // 处理等保测评数据
        if (classifyResponse.ok) {
          const classifyData = await classifyResponse.json();
          this.pdfClassifyDetails = classifyData.checkResults || [];
        }
      } catch (error) {
        console.error('获取详细数据失败:', error);
        // 即使获取详细数据失败，也继续生成PDF
        this.pdfBaselineDetails = [];
        this.pdfClassifyDetails = [];
      }
    },


    // 检查行是否适合作为分页点
    isRowSuitableForBreak(imageData, rowIndex, width) {
      const rowStart = rowIndex * width * 4;
      const rowEnd = rowStart + width * 4;

      let nonWhitePixels = 0;
      let totalPixels = width;

      for (let i = rowStart; i < rowEnd; i += 4) {
        const r = imageData[i];
        const g = imageData[i + 1];
        const b = imageData[i + 2];

        // 检查是否为非白色像素
        if (r < 240 || g < 240 || b < 240) {
          nonWhitePixels++;
        }
      }

      // 如果非白色像素比例很小，认为适合分页
      return (nonWhitePixels / totalPixels) < 0.1;
    },

    // 创建打印内容
    createPrintContent() {
      const printDiv = document.createElement('div');
      printDiv.style.cssText = `
      position: absolute;
      top: -10000px;
      left: -10000px;
      width: 800px;
      background: white;
      padding: 20px;
      font-family: 'Microsoft YaHei', Arial, sans-serif;
      line-height: 1.8;
      color: #333;
      box-sizing: border-box;
      overflow: visible;
    `;

      printDiv.innerHTML = this.generatePrintHTML();

      // 确保表格和内容正确渲染
      const tables = printDiv.querySelectorAll('table');
      tables.forEach(table => {
        table.style.tableLayout = 'fixed';
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.marginBottom = '20px';
        table.style.pageBreakInside = 'avoid';

        // 确保单元格内容不会被截断
        const cells = table.querySelectorAll('td, th');
        cells.forEach(cell => {
          cell.style.wordWrap = 'break-word';
          cell.style.wordBreak = 'break-all';
          cell.style.overflow = 'visible';
          cell.style.whiteSpace = 'normal';
          cell.style.padding = '8px';
          cell.style.lineHeight = '1.6';
        });
      });

      // 为每个主要区块添加分页控制
      const sections = printDiv.querySelectorAll('div[style*="margin-bottom: 25px"]');
      sections.forEach(section => {
        section.style.pageBreakInside = 'avoid';
        section.style.marginBottom = '30px';
      });

      // 为标题添加适当的间距
      const headings = printDiv.querySelectorAll('h2, h3');
      headings.forEach(heading => {
        heading.style.pageBreakAfter = 'avoid';
        heading.style.marginTop = '25px';
        heading.style.marginBottom = '15px';
      });

      return printDiv;
    },

    // 生成打印HTML内容
    generatePrintHTML() {
      return `
      <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #333; font-size: 24px; margin: 0;">资产安全检测报告</h1>
        <p style="color: #666; margin: 10px 0;">生成时间：${new Date().toLocaleString()}</p>
      </div>

      ${this.generateAssetInfoHTML()}
      ${this.generateBaselineHTML()}
      ${this.generateLevel3BaselineHTML()}
      ${this.generatePortsHTML()}
      ${this.generateRisksHTML()}
      ${this.generateVulnerabilitiesHTML()}
    `;
    },

    // 生成资产信息HTML
    generateAssetInfoHTML() {
      const asset = this.currentAsset;

      return `
      <div style="margin-bottom: 25px;">
        <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">资产信息</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold;">IP地址</td>
            <td style="padding: 8px; border: 1px solid #ddd; width: 25%;">${asset.ip}</td>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold;">主机名</td>
            <td style="padding: 8px; border: 1px solid #ddd; width: 25%;">${asset.serverinfo?.hostname || '未知'}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">操作系统</td>
            <td style="padding: 8px; border: 1px solid #ddd;">${asset.serverinfo?.osName || '未知'}</td>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">主机架构</td>
            <td style="padding: 8px; border: 1px solid #ddd;">${asset.serverinfo?.arch || '未知'}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">CPU</td>
            <td style="padding: 8px; border: 1px solid #ddd;">${asset.serverinfo?.cpu || '未知'}</td>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">硬件型号</td>
            <td style="padding: 8px; border: 1px solid #ddd;">${asset.serverinfo?.ProductName || '未知'}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">开放端口</td>
            <td style="padding: 8px; border: 1px solid #ddd;" colspan="3">${this.formatOpenPorts}</td>
          </tr>
        </table>
      </div>
    `;
    },

    // 生成基线检测HTML
    generateBaselineHTML() {
      const asset = this.currentAsset;
      if (!asset.baseline_summary) return '';

      let html = `
      <div style="margin-bottom: 25px;">
        <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">基线检测</h2>
        <div style="display: flex; align-items: center; margin-top: 15px;">
          <div style="text-align: center; margin-right: 30px;">
            <div style="font-weight: bold; margin-bottom: 5px;">不合格/已检测项数</div>
            <div style="font-size: 24px; color: #F56C6C; font-weight: bold;">${asset.baseline_summary.non_compliance_rate}%</div>
          </div>
          <div style="text-align: center; margin-right: 30px;">
            <div style="font-weight: bold; margin-bottom: 5px;">不合格/总项数</div>
            <div style="font-size: 24px; color: #F56C6C; font-weight: bold;">${asset.baseline_summary.non_compliance_rate_to_initial_checks}%</div>
          </div>
          <table style="flex: 1; border-collapse: collapse;">
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; text-align: center; font-weight: bold;">总检测项数</td>
              <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; text-align: center; font-weight: bold;">合格项数</td>
              <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; text-align: center; font-weight: bold;">待检测项数</td>
              <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; text-align: center; font-weight: bold;">不合格项数</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">${asset.baseline_summary.total_checks}</td>
              <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #67C23A;">${asset.baseline_summary.compliant_items}</td>
              <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #E6A23C;">${asset.baseline_summary.pending_items}</td>
              <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #F56C6C;">${asset.baseline_summary.non_compliant_items}</td>
            </tr>
          </table>
        </div>
    `;

      // 添加基线检测详细信息
      if (this.pdfBaselineDetails && this.pdfBaselineDetails.length > 0) {
        html += `
        <div style="margin-top: 20px;">
          <h3 style="color: #606266; font-size: 14px; margin: 10px 0; padding-left: 10px; border-left: 3px solid #409EFF;">基线检测详细信息</h3>
          <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
            <thead>
              <tr style="background: #f5f7fa;">
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 8%;">合规状态</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 25%;">检查项</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 20%;">检查依据</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 25%;">检查结果</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 22%;">建议</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 22%;">检测时间</th>
              </tr>
            </thead>
            <tbody>
      `;

        this.pdfBaselineDetails.forEach(item => {
          const statusColor = item.IsComply === 'true' ? '#67C23A' :
              item.IsComply === 'pending' ? '#E6A23C' : '#F56C6C';
          const statusText = item.IsComply === 'true' ? '通过' :
              item.IsComply === 'pending' ? '待检查' : '不通过';
          const suggestion = item.IsComply === 'true' ? '-' : (item.recommend || '-');

          html += `
          <tr>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${statusColor}; font-weight: bold;">${statusText}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.description || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.basis || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.result || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${suggestion}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.check_time}</td>
          </tr>
        `;
        });

        html += `
            </tbody>
          </table>
        </div>
      `;
      }
      // 添加基线未检查项列表
      if (asset.undo_baseline && asset.undo_baseline.length > 0) {
        html += `
        <div style="margin-top: 20px;">
          <h3 style="color: #E6A23C; font-size: 14px; margin: 10px 0; padding-left: 10px; border-left: 3px solid #E6A23C;">未检查项 (${asset.undo_baseline.length}项)</h3>
          <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
            <thead>
              <tr style="background: #f5f7fa;">
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 10%;">项目ID</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 35%;">检查项</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 55%;">检查依据</th>
              </tr>
            </thead>
            <tbody>
      `;

        asset.undo_baseline.forEach(item => {
          html += `
          <tr>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${item.item_id || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.description || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.basis || '-'}</td>
          </tr>
        `;
        });

        html += `
            </tbody>
          </table>
        </div>
      `;
      }

      html += '</div>';
      return html;
    },

    // 生成等保测评HTML
    generateLevel3BaselineHTML() {
      const asset = this.currentAsset;
      if (!asset.level3_baseline_summary) return '';

      let html = `
      <div style="margin-bottom: 25px;">
        <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">等级保护测评</h2>
        ${typeof asset.M !== 'undefined' ? `
          <div style="background: #f5f7fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            <div style="display: flex; align-items: center;">
              <div style="margin-right: 20px;">
                <strong>等保测评得分：</strong>
                <span style="font-size: 20px; color: ${this.getScoreProgressColor(asset.M)}; font-weight: bold;">${Number(asset.M).toFixed(2)}分</span>
                <span style="margin-left: 10px; padding: 3px 8px; background: ${this.getScoreProgressColor(asset.M)}; color: white; border-radius: 3px; font-size: 12px;">${this.getScoreGrade(asset.M)}</span>
              </div>
            </div>
          </div>
        ` : ''}
        <div style="display: flex; align-items: center; margin-top: 15px;">
          <div style="text-align: center; margin-right: 30px;">
            <div style="font-weight: bold; margin-bottom: 5px;">不合格/已检测项数</div>
            <div style="font-size: 24px; color: #F56C6C; font-weight: bold;">${asset.level3_baseline_summary.non_compliance_rate}%</div>
          </div>
          <div style="text-align: center; margin-right: 30px;">
            <div style="font-weight: bold; margin-bottom: 5px;">不合格/总项数</div>
            <div style="font-size: 24px; color: #F56C6C; font-weight: bold;">${asset.level3_baseline_summary.non_compliance_rate_to_initial_checks}%</div>
          </div>
          <table style="flex: 1; border-collapse: collapse;">
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; text-align: center; font-weight: bold;">总检测项数</td>
              <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; text-align: center; font-weight: bold;">合格项数</td>
              <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; text-align: center; font-weight: bold;">部分合格项数</td>
              <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; text-align: center; font-weight: bold;">不合格项数</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">${asset.level3_baseline_summary.total_checks}</td>
              <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #67C23A;">${asset.level3_baseline_summary.compliant_items}</td>
              <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #E6A23C;">${asset.level3_baseline_summary.pending_items}</td>
              <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #F56C6C;">${asset.level3_baseline_summary.non_compliant_items}</td>
            </tr>
          </table>
        </div>
    `;



      // 添加等保测评详细信息
      if (this.pdfClassifyDetails && this.pdfClassifyDetails.length > 0) {
        html += `
        <div style="margin-top: 20px;">
          <h3 style="color: #606266; font-size: 14px; margin: 10px 0; padding-left: 10px; border-left: 3px solid #409EFF;">等保测评详细信息</h3>
          <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
            <thead>
              <tr style="background: #f5f7fa;">
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 8%;">合规状态</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 25%;">检查项</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 20%;">检查依据</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 25%;">检查结果</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 22%;">建议</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 22%;">检测时间</th>
              </tr>
            </thead>
            <tbody>
      `;

        this.pdfClassifyDetails.forEach(item => {
          const statusColor = item.IsComply === 'true' ? '#67C23A' :
              item.IsComply === 'pending' ? '#E6A23C' : '#F56C6C';
          const statusText = item.IsComply === 'true' ? '通过' :
              item.IsComply === 'pending' ? '待检查' : '不通过';
          const suggestion = item.IsComply === 'true' ? '-' : (item.recommend || '-');

          html += `
          <tr>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${statusColor}; font-weight: bold;">${statusText}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.description || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.basis || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.result || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${suggestion}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.check_time}</td>
          </tr>
        `;
        });

        html += `
            </tbody>
          </table>
        </div>
      `;
      }
      // 添加未检查项列表
      if (asset.undo_level3_baseline && asset.undo_level3_baseline.length > 0) {
        html += `
        <div style="margin-top: 20px;">
          <h3 style="color: #E6A23C; font-size: 14px; margin: 10px 0; padding-left: 10px; border-left: 3px solid #E6A23C;">未检查项 (${asset.undo_level3_baseline.length}项)</h3>
          <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
            <thead>
              <tr style="background: #f5f7fa;">
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 10%;">项目ID</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 35%;">检查项</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center; width: 55%;">检查依据</th>
              </tr>
            </thead>
            <tbody>
      `;

        asset.undo_level3_baseline.forEach(item => {
          html += `
          <tr>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${item.item_id || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.description || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.basis || '-'}</td>
          </tr>
        `;
        });

        html += `
            </tbody>
          </table>
        </div>
      `;
      }
      html += '</div>';
      return html;
    },

    // 生成端口信息HTML
    generatePortsHTML() {
      const asset = this.currentAsset;
      if (!asset.ports || asset.ports.length === 0) return '';

      const groupedPorts = this.groupedPorts;
      let html = `
      <div style="margin-bottom: 25px;">
        <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">软件资产</h2>
    `;

      Object.entries(groupedPorts).forEach(([type, ports]) => {
        html += `
        <div style="margin-bottom: 20px;">
          <h3 style="color: #606266; font-size: 14px; margin: 10px 0; padding-left: 10px; border-left: 3px solid #409EFF;">${type}</h3>
          <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
            <thead>
              <tr style="background: #f5f7fa;">
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">端口</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">协议</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">服务名称</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">产品</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">版本</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">状态</th>
              </tr>
            </thead>
            <tbody>
      `;

        ports.forEach(port => {
          html += `
          <tr>
            <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${port.port}</td>
            <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${port.protocol}</td>
            <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${port.service_name}</td>
            <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${port.product || '未识别'}</td>
            <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${port.version || '未识别'}</td>
            <td style="padding: 6px; border: 1px solid #ddd; text-align: center; color: ${port.status === 'open' ? '#67C23A' : '#F56C6C'};">${port.status}</td>
          </tr>
        `;
        });

        html += `
            </tbody>
          </table>
        </div>
      `;
      });

      html += '</div>';
      return html;
    },

    // 生成风险信息HTML
    generateRisksHTML() {
      const weakPorts = this.weakPasswordPorts;
      if (weakPorts.length === 0) return '';

      let html = `
      <div style="margin-bottom: 25px;">
        <h2 style="color: #F56C6C; font-size: 18px; border-bottom: 2px solid #F56C6C; padding-bottom: 5px;">风险</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
          <thead>
            <tr style="background: #f5f7fa;">
              <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">产品</th>
              <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">端口</th>
              <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">协议</th>
              <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">服务名称</th>
              <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">软件类型</th>
              <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">账号</th>
              <th style="padding: 6px; border: 1px solid #ddd; text-align: center;">结果</th>
              <th style="padding: 4px; border: 1px solid #ddd; text-align: center;">检测时间</th>
            </tr>
          </thead>
          <tbody>
    `;

      weakPorts.forEach(port => {
        html += `
        <tr>
          <td style="padding: 6px; border: 1px solid #ddd; text-align: center; color: #F56C6C; font-weight: bold;">${port.product || '未识别'}</td>
          <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${port.port}</td>
          <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${port.protocol}</td>
          <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${port.service_name}</td>
          <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${port.software_type}</td>
          <td style="padding: 6px; border: 1px solid #ddd; text-align: center; color: #F56C6C; font-weight: bold;">${port.weak_username}</td>
          <td style="padding: 6px; border: 1px solid #ddd; text-align: center; color: #F56C6C; font-weight: bold;">存在弱密码</td>
          <td style="padding: 4px; border: 1px solid #ddd; text-align: center;">${port.verify_time}</td>
        </tr>
      `;
      });

      html += `
          </tbody>
        </table>
      </div>
    `;

      return html;
    },

    // 生成漏洞信息HTML
    generateVulnerabilitiesHTML() {
      const asset = this.currentAsset;
      let html = `
      <div style="margin-bottom: 25px;">
        <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">资产漏洞信息</h2>
    `;

      // 系统漏洞
      if (asset.host_vulnerabilities && asset.host_vulnerabilities.length > 0) {
        html += `
        <div style="margin-bottom: 20px;">
          <h3 style="color: #606266; font-size: 14px; margin: 10px 0; padding-left: 10px; border-left: 3px solid #409EFF;">系统漏洞</h3>
          <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
            <thead>
              <tr style="background: #f5f7fa;">
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center;">漏洞ID</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center;">漏洞名称</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center;">漏洞类型</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center;">风险等级</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center;">是否存在</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center;">漏洞描述</th>
                <th style="padding: 5px; border: 1px solid #ddd; text-align: center;">检测时间</th>
              </tr>
            </thead>
            <tbody>
      `;

        asset.host_vulnerabilities.forEach(vuln => {
          const riskColor = this.getCvssType(vuln.cvss) === 'danger' ? '#F56C6C' :
              this.getCvssType(vuln.cvss) === 'warning' ? '#E6A23C' : '#67C23A';
          const existColor = vuln.vulExist === '存在' ? '#F56C6C' : '#67C23A';

          html += `
          <tr>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${vuln.vuln_id}</td>
            <td style="padding: 5px; border: 1px solid #ddd;">${vuln.vuln_name}</td>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${vuln.vulType}</td>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${riskColor};">${this.getRiskLevel(vuln.cvss)}</td>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${existColor};">${vuln.vulExist}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${vuln.summary}</td>
            <td style="padding: 5px; border: 1px solid #ddd;">${vuln.scan_time}</td>
          </tr>
        `;
        });

        html += `
            </tbody>
          </table>
        </div>
      `;
      }

      // 软件资产漏洞
      const groupedPortVulns = this.groupedPortVulnerabilities;
      if (Object.keys(groupedPortVulns).length > 0) {
        html += `<h3 style="color: #606266; font-size: 14px; margin: 10px 0; padding-left: 10px; border-left: 3px solid #409EFF;">软件资产漏洞</h3>`;

        Object.entries(groupedPortVulns).forEach(([type, vulns]) => {
          html += `
          <div style="margin-bottom: 15px;">
            <h4 style="color: #909399; font-size: 12px; margin: 5px 0;">${type}</h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 10px;">
              <thead>
                <tr style="background: #f5f7fa;">
                  <th style="padding: 4px; border: 1px solid #ddd; text-align: center;">端口</th>
                  <th style="padding: 4px; border: 1px solid #ddd; text-align: center;">服务</th>
                  <th style="padding: 4px; border: 1px solid #ddd; text-align: center;">漏洞ID</th>
                  <th style="padding: 4px; border: 1px solid #ddd; text-align: center;">漏洞名称</th>
                  <th style="padding: 4px; border: 1px solid #ddd; text-align: center;">风险等级</th>
                  <th style="padding: 4px; border: 1px solid #ddd; text-align: center;">是否存在</th>
                  <th style="padding: 4px; border: 1px solid #ddd; text-align: center;">检测时间</th>
                </tr>
              </thead>
              <tbody>
        `;

          vulns.forEach(vuln => {
            const riskColor = this.getCvssType(vuln.cvss) === 'danger' ? '#F56C6C' :
                this.getCvssType(vuln.cvss) === 'warning' ? '#E6A23C' : '#67C23A';
            const existColor = vuln.vulExist === '存在' ? '#F56C6C' : '#67C23A';

            html += `
            <tr>
              <td style="padding: 4px; border: 1px solid #ddd; text-align: center;">${vuln.port_id}</td>
              <td style="padding: 4px; border: 1px solid #ddd; text-align: center;">${vuln.service_name}</td>
              <td style="padding: 4px; border: 1px solid #ddd; text-align: center;">${vuln.vuln_id}</td>
              <td style="padding: 4px; border: 1px solid #ddd;">${vuln.vuln_name}</td>
              <td style="padding: 4px; border: 1px solid #ddd; text-align: center; color: ${riskColor};">${this.getRiskLevel(vuln.cvss)}</td>
              <td style="padding: 4px; border: 1px solid #ddd; text-align: center; color: ${existColor};">${vuln.vulExist}</td>
              <td style="padding: 4px; border: 1px solid #ddd; ">${vuln.scan_time}</td>
            </tr>
          `;
          });

          html += `
              </tbody>
            </table>
          </div>
        `;
        });
      }

      html += '</div>';
      return html;
    },
    getResults() {
      fetch('/api//assets/full_info')
          .then(response => response.json())
          .then(data => {
            this.assets = data;
            // 如果当前选中的IP不在新数据中，重置选择
            if (this.currentIp && !this.assets.find(asset => asset.ip === this.currentIp)) {
              this.currentIp = this.assets.length > 0 ? this.assets[0].ip : '';
            }
          })
          .catch(error => {
            console.error('Error:', error);
            this.$message.error('获取资产信息失败');
          });
    },

    // 获取资产组列表
    async getAssetGroups() {
      try {
        const response = await fetch('/api/asset_group/list');
        if (!response.ok) {
          throw new Error('获取资产组列表失败');
        }
        const data = await response.json();
        this.assetGroups = data;

        // 默认展开所有组
        this.expandedGroups = data.map(group => group.id);
      } catch (error) {
        console.error('获取资产组列表失败:', error);
        this.$message.error('获取资产组列表失败');
      }
    },

    // 根据group_id获取资产组名称
    getAssetGroupName(groupId) {
      const group = this.assetGroups.find(g => g.id === groupId);
      return group ? group.name : '未知分组';
    },

    // 新增资产组
    async handleAddGroup() {
      if (!this.$refs.addGroupForm) return;

      try {
        const valid = await this.$refs.addGroupForm.validate();
        if (!valid) return;
      } catch {
        return;
      }

      this.addGroupLoading = true;

      try {
        const response = await fetch('/api/asset_group', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.newGroupForm)
        });

        if (response.ok) {
          this.$message.success('资产组创建成功');
          this.addGroupDialogVisible = false;
          await this.getAssetGroups();
          await this.getResults();
        } else {
          const errorData = await response.json().catch(() => ({}));
          this.$message.error(errorData.message || '创建失败');
        }
      } catch (error) {
        console.error('创建资产组失败:', error);
        this.$message.error('创建资产组失败');
      } finally {
        this.addGroupLoading = false;
      }
    },

    // 关闭新增对话框
    handleAddGroupDialogClose() {
      this.addGroupDialogVisible = false;
      this.newGroupForm = { group_name: '', description: '' };
      if (this.$refs.addGroupForm) {
        this.$refs.addGroupForm.resetFields();
      }
    },

    // 修改资产组名称
    showEditGroupDialog(group) {
      this.editGroupForm.id = group.id;
      this.editGroupForm.new_name = group.name;
      this.editGroupDialogVisible = true;
    },

    async handleEditGroup() {
      if (!this.$refs.editGroupForm) return;

      try {
        const valid = await this.$refs.editGroupForm.validate();
        if (!valid) return;
      } catch {
        return;
      }

      this.editGroupLoading = true;

      try {
        const response = await fetch(`/api/asset_group/${this.editGroupForm.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ new_name: this.editGroupForm.new_name })
        });

        if (response.ok) {
          this.$message.success('资产组名称修改成功');
          this.editGroupDialogVisible = false;
          await this.getAssetGroups();
        } else {
          const errorData = await response.json().catch(() => ({}));
          this.$message.error(errorData.message || '修改失败');
        }
      } catch (error) {
        console.error('修改资产组失败:', error);
        this.$message.error('修改资产组失败');
      } finally {
        this.editGroupLoading = false;
      }
    },

    // 关闭编辑对话框
    handleEditGroupDialogClose() {
      this.editGroupDialogVisible = false;
      this.editGroupForm = { id: null, new_name: '' };
      if (this.$refs.editGroupForm) {
        this.$refs.editGroupForm.resetFields();
      }
    },

    // 删除资产组
    async handleDeleteGroup(group) {
      const hasAssets = this.groupedAssets[group.id]?.assets.length > 0;

      if (hasAssets) {
        try {
          await this.$confirm(
              `资产组 "${group.name}" 下还有 ${this.groupedAssets[group.id].assets.length} 个资产，是否一并删除这些资产？`,
              '删除确认',
              {
                type: 'warning',
                distinguishCancelAndClose: true,
                confirmButtonText: '删除组和资产',
                cancelButtonText: '仅删除组',
                showClose: true,  // 显示关闭按钮
                closeOnClickModal: false,  // 点击遮罩不关闭
                closeOnPressEscape: true,  // 按ESC键关闭
                showCancelButton: true,  // 确保显示取消按钮
              }
          );

          await this.deleteGroup(group.id, true);
        } catch (action) {
          if (action === 'cancel') {
            await this.deleteGroup(group.id, false);
          }
        }
      } else {
        try {
          await this.$confirm(`确定要删除资产组 "${group.name}" 吗？`,
              '删除确认',
              {
                type: 'warning',
                confirmButtonText: '确定删除',
                cancelButtonText: '取消',
                showClose: true,  // 显示关闭按钮
                closeOnClickModal: false,  // 点击遮罩不关闭
                closeOnPressEscape: true,  // 按ESC键关闭
                showCancelButton: true,  // 确保显示取消按钮
              }
          );
          await this.deleteGroup(group.id, false);
        } catch {
          // 用户取消
        }
      }
    },

    async deleteGroup(groupId, deleteAssets) {
      try {
        const url = deleteAssets
            ? `/api/asset_group/${groupId}?delete_assets=true`
            : `/api/asset_group/${groupId}`;

        const response = await fetch(url, {
          method: 'DELETE'
        });

        if (response.ok) {
          this.$message.success('资产组删除成功');
          await this.getAssetGroups();
          await this.getResults();

          // 如果当前选中的资产被删除了，重置选择
          if (deleteAssets && !this.assets.find(asset => asset.ip === this.currentIp)) {
            this.currentIp = this.assets.length > 0 ? this.assets[0].ip : '';
          }
        } else {
          const errorData = await response.json().catch(() => ({}));
          this.$message.error(errorData.message || '删除失败');
        }
      } catch (error) {
        console.error('删除资产组失败:', error);
        this.$message.error('删除资产组失败');
      }
    },

    // 移动资产到指定组
    showMoveAssetDialog(targetGroup) {
      this.currentOperatingGroup = targetGroup;
      this.moveAssetForm.targetGroupId = targetGroup.id;
      this.moveAssetForm.selectedAssets = [];
      this.moveAssetDialogVisible = true;
    },

    // 全选资产
    selectAllAssets() {
      this.moveAssetForm.selectedAssets = this.ungroupedAssets.map(asset => asset.ip);
    },

    // 清空选择
    clearAssetSelection() {
      this.moveAssetForm.selectedAssets = [];
    },

    async handleMoveAssets() {
      if (this.moveAssetForm.selectedAssets.length === 0) {
        this.$message.warning('请选择要移动的资产');
        return;
      }

      this.moveAssetLoading = true;

      try {
        const promises = this.moveAssetForm.selectedAssets.map(assetIp =>
            fetch(`/api/asset/${assetIp}/group`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ group_id: this.moveAssetForm.targetGroupId })
            })
        );

        const results = await Promise.all(promises);
        const successCount = results.filter(r => r.ok).length;

        if (successCount === this.moveAssetForm.selectedAssets.length) {
          this.$message.success(`成功移动 ${successCount} 个资产`);
        } else {
          this.$message.warning(`成功移动 ${successCount} 个资产，${this.moveAssetForm.selectedAssets.length - successCount} 个失败`);
        }

        this.moveAssetDialogVisible = false;
        await this.getResults();
      } catch (error) {
        console.error('移动资产失败:', error);
        this.$message.error('移动资产失败');
      } finally {
        this.moveAssetLoading = false;
      }
    },

    // 关闭移动资产对话框
    handleMoveAssetDialogClose() {
      this.moveAssetDialogVisible = false;
      this.moveAssetForm.selectedAssets = [];
      this.currentOperatingGroup = null;
    },

    // 单个资产移动
    async moveAssetToGroup(assetIp, targetGroupId) {
      try {
        const response = await fetch(`/api/asset/${assetIp}/group`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ group_id: targetGroupId })
        });

        if (response.ok) {
          this.$message.success('资产移动成功');
          await this.getResults();
        } else {
          const errorData = await response.json().catch(() => ({}));
          this.$message.error(errorData.message || '移动失败');
        }
      } catch (error) {
        console.error('移动资产失败:', error);
        this.$message.error('移动资产失败');
      }
    },
    handleSelect(ip) {
      this.currentIp = ip;
      this.displayType = 'assetType';
      // 检查图表实例是否存在
      if (!this.pieChart || !this.pieChart.isDisposed()) {
        this.initCharts();  // 不存在或已销毁:初始化
      } else {
        this.updateCharts(); // 否则直接更新数据
      }
    },
    getCvssType(score) {
      score = parseFloat(score);
      if (score >= 7.0) return 'danger';
      if (score >= 4.0) return 'warning';
      if (score >= 0.0) return 'success';
      return 'info';
    },
    getRiskLevel(score) {
      score = parseFloat(score);
      if (score >= 7.0) return '高风险';
      if (score >= 4.0) return '中风险';
      if (score >= 0.0) return '低风险';
      return '未知';
    },
    // 新增：格式化进度条
    format() {
      return '';
    },
    async initCharts() {
      await this.$nextTick();

      // 初始化资产类型饼图
      if (this.$refs.pieChart) {
        if (this.pieChart) {
          this.pieChart.dispose();
        }
        this.pieChart = echarts.init(this.$refs.pieChart);
      }

      // 初始化漏洞类型饼图
      if (this.$refs.vulTypePieChart) {
        if (this.vulTypePieChart) {
          this.vulTypePieChart.dispose();
        }
        this.vulTypePieChart = echarts.init(this.$refs.vulTypePieChart);
      }

      window.addEventListener('resize', () => {
        this.pieChart && this.pieChart.resize();
        this.vulTypePieChart && this.vulTypePieChart.resize();
      });

      this.updateCharts();
    },
    updateCharts() {
      if (this.displayType === 'assetType') {
        this.updateAssetPieChart();
      } else {
        this.updateVulTypePieChart();
      }
    },
    updateAssetPieChart() {
      if (!this.pieChart) return;

      const stats = this.vulnerabilityTypeStats;
      const data = Object.entries(stats)
          .filter(([, value]) => value > 0)
          .map(([name, value]) => ({
            name,
            value
          }));

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 'right',
          top: 'middle',
          data: data.map(item => item.name)
        },
        series: [{
          name: '存在漏洞的资产类型分布', // 更新名称以反映只显示存在的漏洞
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}个'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: true
          },
          data: data
        }]
      };

      this.pieChart.setOption(option);
    },

    // 更新漏洞类型饼图
    updateVulTypePieChart() {
      if (!this.vulTypePieChart) return;

      const stats = this.vulTypeStats;
      const data = Object.entries(stats)
          .map(([name, value]) => ({
            name,
            value
          }));

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 'right',
          top: 'middle',
          data: data.map(item => item.name)
        },
        series: [{
          name: '存在漏洞的类型分布', // 更新名称以反映只显示存在的漏洞
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}个'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: true
          },
          data: data
        }]
      };

      this.vulTypePieChart.setOption(option);
    },
    // 显示基线检测详细信息对话框
    showBaselineDetails() {
      if (!this.currentAsset) return;

      this.baselineDialogVisible = true;
      this.baselineDetailsLoading = true;
      this.baselineDetails = [];

      // 调用API获取详细信息
      fetch(`/api/userinfo?ip=${this.currentAsset.ip}`)
          .then(response => response.json())
          .then(data => {
            if (data && data.checkResults) {
              this.baselineDetails = data.checkResults;
            }
            this.baselineDetailsLoading = false;
          })
          .catch(error => {
            console.error('获取基线检测详细信息失败:', error);
            this.baselineDetailsLoading = false;
          });
    },

    // 关闭基线检测详细信息对话框
    handleBaselineDialogClose() {
      this.baselineDialogVisible = false;
    },

    showClassifyProtectDetails() {
      if (!this.currentAsset) return;

      this.classifyDialogVisible = true;
      this.classifyDetailsLoading = true;
      this.classifyDetails = [];

      // 调用API获取详细信息
      fetch(`/api/level3Userinfo?ip=${this.currentAsset.ip}`)
          .then(response => response.json())
          .then(data => {
            if (data && data.checkResults) {
              this.classifyDetails = data.checkResults;
            }
            this.classifyDetailsLoading = false;
          })
          .catch(error => {
            console.error('获取基线检测详细信息失败:', error);
            this.classifyDetailsLoading = false;
          });
    },
    // 关闭基线检测详细信息对话框
    handleClassifyDialogClose() {
      this.classifyDialogVisible = false;
    },

    // 获取重要级别对应的类型
    getImportanceLevelType(level) {
      level = parseInt(level, 10);
      switch (level) {
        case 1: return 'warning';
        case 2: return 'danger';
        default: return 'info';
      }
    },

    // 获取重要级别对应的文本
    getImportanceLevel(level) {
      level = parseInt(level, 10);
      switch (level) {
        case 1: return '一般';
        case 2: return '重要';
        default: return '未知';
      }
    },
    // 获取等保重要级别对应的类型
    getLevel3ImportanceLevelType(level) {
      level = parseInt(level, 10);
      switch (level) {
        case 1: return 'info';
        case 2: return 'warning';
        case 3: return 'danger';
        default: return 'info';
      }
    },

// 获取等保重要级别对应的文本
    getLevel3ImportanceLevel(level) {
      level = parseInt(level, 10);
      switch (level) {
        case 1: return '低';
        case 2: return '中';
        case 3: return '高';
        default: return '未知';
      }
    },
    // 获取得分等级
    getScoreGrade(score) {
      if (score >= 90) return '优秀';
      if (score >= 80) return '良好';
      if (score >= 70) return '合格';
      if (score >= 60) return '基本符合';
      return '不符合';
    },

// 获取得分标签类型
    getScoreTagType(score) {
      if (score >= 60) return 'success';
      // if (score >= 80) return 'primary';
      // if (score >= 70) return 'warning';
      // if (score >= 60) return 'info';
      return 'danger';
    },

// 获取得分圆圈样式类名
    getScoreGradeClass(score) {
      if (score >= 60) return 'excellent';
      // if (score >= 80) return 'good';
      // if (score >= 70) return 'qualified';
      // if (score >= 60) return 'basic';
      return 'unqualified';
    },

// 获取进度条颜色
    getScoreProgressColor(score) {
      if (score >= 60) return '#67C23A';
      // if (score >= 80) return '#409EFF';
      // if (score >= 70) return '#E6A23C';
      // if (score >= 60) return '#909399';
      return '#F56C6C';
    }
  },
  watch: {
    currentAsset() {
      this.$nextTick(() => {
        this.updateCharts();
      });
    },
    displayType() {
      this.$nextTick(() => {
        this.initCharts();
      });
    },
  },
  created() {
    this.getResults();
    this.getAssetGroups();
  },
  mounted() {
    if (this.assets.length > 0) {
      this.currentIp = this.assets[0].ip;
    }
    this.initCharts();
  },
  beforeDestroy() {
    if (this.pieChart) {
      this.pieChart.dispose();
      this.pieChart = null;
    }
    if (this.vulTypePieChart) {
      this.vulTypePieChart.dispose();
      this.vulTypePieChart = null;
    }
  },

}
</script>

<style scoped>
.vulnerability-container {
  display: flex;
  height: 100%;
  min-height: 600px;
  background-color: #fff;
}

.ip-list {
  width: 250px;
  border-right: 1px solid #e6e6e6;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.menu-header {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #e6e6e6;
  background-color: #fff;
  flex-shrink: 0;
}

.menu-header .title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.menu-header .asset-count {
  margin-left: 10px;
}

.add-group-btn {
  margin-left: auto;
}

.group-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.group-item {
  border: none;
  margin-bottom: 5px;
}

.group-title {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0 10px;
  min-height: 40px;
}

/*
.group-name {
  font-weight: 600;
  color: #303133;
  flex: 1;
  font-size: 14px;
}
*/
.group-name {
  font-weight: 600;
  max-width: 110px;
  color: #303133;
  flex: 1;
  font-size: 14px;

  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  vertical-align: middle;
}


.group-count {
  color: #909399;
  font-size: 12px;
  margin-left: 5px;
  margin-right: 10px;
}

.group-actions {
  margin-left: auto;
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.3s;
}

.group-title:hover .group-actions {
  opacity: 1;
}

.group-actions .el-button {
  padding: 4px;
  margin: 0;
  min-width: auto;
  border: none;
}

.group-actions .el-button:hover {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.assets-list {
  padding-left: 15px;
  padding-right: 10px;
}

.asset-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  margin: 2px 0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.asset-item:hover {
  background-color: #ecf5ff;
  transform: translateX(2px);
}

.asset-item.active {
  background-color: #409EFF;

  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

/* 确保选中状态下的IP地址文字颜色保持黑色 */
.asset-item.active .asset-ip {
  color: #303133 !important;
}

/* 确保选中状态下的图标颜色保持原样 */
.asset-item.active .asset-info i {
  color: #909399 !important;
}

.asset-item.active .asset-status .el-tag {

}

.asset-info {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.asset-info i {
  margin-right: 8px;
  color: #909399;
  font-size: 14px;
}

/* 只修改右侧内容区域(.ip-header)内的资产信息布局 */
.ip-header .asset-info {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  /* 使用网格布局，每行两列 */
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 20px; /* 行间距10px，列间距20px */
}

.asset-item.active .asset-info i {
  color: rgba(255, 255, 255, 0.8);
}

.asset-ip {
  margin-right: 3px;
  font-size: 13px;
  font-weight: 500;
  flex: 1;

  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;  /*  新增：确保文本能省略 */
  max-width: 200px;        /*  新增：限制最大宽度 */
  vertical-align: middle;  /* （可选）对齐优化 */
}

/*
.asset-ip {
  margin-right: 10px;
  font-size: 13px;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

 */

.asset-status {
  margin-left: auto;
  margin-right: 8px;
}

.asset-status .el-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 2px;
}

.asset-actions {
  opacity: 0;
  transition: opacity 0.3s;
}

.asset-item:hover .asset-actions {
  opacity: 1;
}

.asset-actions .el-button {
  padding: 2px;
  margin: 0;
  font-size: 12px;
}

.empty-group {
  text-align: center;
  padding: 20px 10px;
}

.empty-group .el-empty {
  padding: 10px;
}

.content-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.empty-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.ip-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.ip-header h2 {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 15px 0;
}

.chart-toggle {
  margin-right: 20px;
  margin-top: 15px;
}

.chart-section {
  margin: 20px 0;
  padding: 0;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.pie-chart {
  width: 100%;
  height: 400px;
}

.asset-info {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.info-item {
  line-height: 28px;
  display: flex;
}

.info-item .label {
  color: #606266;
  width: 80px;
  text-align: right;
  margin-right: 15px;
  flex-shrink: 0;
}

.info-item .value {
  color: #303133;
  flex: 1;
  /* 防止长文本溢出 */
  word-break: break-all;
  overflow-wrap: break-word;
}



.table-section {
  margin-bottom: 30px;
}

.table-section h3 {
  margin: 15px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.el-tag {
  width: 65px;
  text-align: center;
}

.el-table .cell {
  text-align: center;
}

.el-table .el-table__row td:nth-child(4) .cell {
  text-align: left;
}

.vulnerability-group {
  margin-bottom: 20px;
}

.group-title {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
  margin: 10px 0;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
}

.port-group {
  margin-bottom: 20px;
}

.ports-section {
  margin-bottom: 30px;
}

.ports-section h2, .baseline-section h2 {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.weak-password-section {
  margin-bottom: 30px;
}

.weak-password-section h2 {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.baseline-section {
  margin-bottom: 30px;
}

.baseline-info {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 20px;
}

.baseline-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.progress-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.progress-content .rate {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.progress-content .label {
  font-size: 14px;
  color: #606266;
  margin-top: 5px;
}

.baseline-stats {
  display: flex;
  flex: 1;
  justify-content: space-around;
  margin-left: 30px;
}

.stat-item {
  text-align: center;
  padding: 0 15px;
}

.item-header {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.item-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.compliance-details {
  margin-top: 20px;
}

.detail-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.detail-label {
  width: 70px;
  margin-right: 15px;
}

.detail-progress {
  flex: 1;
}

.detail-numbers {
  width: 80px;
  text-align: right;
  color: #606266;
  font-size: 14px;
  margin-left: 15px;
}

.compliance-dashboard {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.compliance-label {
  font-size: 16px;
  color: #333;
  font-weight: bold;
  margin-bottom: 10px;
}

.baseline-info-icon {
  cursor: pointer;
  margin-left: 10px;
  color: #409EFF;
  font-size: 16px;
}

.baseline-info-icon:hover {
  color: #66b1ff;
}

.baseline-details-content {
  max-height: 600px;
  overflow-y: auto;
}

.baseline-details-loading {
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.el-table .cell {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 23px;
}

.undo-items-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.undo-title {
  color: #E6A23C;
  font-weight: 500;
  font-size: 14px;
}

.undo-title i {
  margin-right: 5px;
}

.undo-content {
  padding: 10px 0;
}

.el-collapse {
  border: none;
}

.el-collapse-item__header {
  background-color: transparent;
  border: none;
  padding: 0;
  height: auto;
  line-height: normal;
}

.el-collapse-item__content {
  padding: 10px 0;
  background-color: transparent;
  border: none;
}

.el-collapse-item__arrow {
  margin-right: 8px;
}

.level-score-section {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border: 2px solid #e1e6ff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.score-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.score-header i {
  margin-right: 8px;
  color: #FFD700;
  font-size: 18px;
}

.score-display-inline {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-circle-small {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.score-circle-small.excellent {
  background: linear-gradient(135deg, #67C23A, #85ce61);
  border: 3px solid #67C23A;
}

.score-circle-small.good {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  border: 3px solid #409EFF;
}

.score-circle-small.qualified {
  background: linear-gradient(135deg, #E6A23C, #ebb563);
  border: 3px solid #E6A23C;
}

.score-circle-small.basic {
  background: linear-gradient(135deg, #909399, #a6a9ad);
  border: 3px solid #909399;
}

.score-circle-small.unqualified {
  background: linear-gradient(135deg, #F56C6C, #f78989);
  border: 3px solid #F56C6C;
}

.score-number-small {
  font-size: 24px;
  font-weight: bold;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  line-height: 1;
}

.score-unit-small {
  font-size: 12px;
  color: white;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.score-grade-inline {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
}

.score-grade-inline .el-tag {
  align-self: flex-start;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 16px;
  line-height: 1.4;
  display: inline-flex;
  align-items: center;
  height: auto;
}

.baseline-summary {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
  margin-top: 10px;
}

/* 对话框相关样式 */
.move-asset-content {
  max-height: 400px;
  overflow-y: auto;
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.selection-actions {
  display: flex;
  gap: 10px;
}

.asset-checkbox {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s;
}

.asset-checkbox:hover {
  background-color: #f5f7fa;
}

.asset-checkbox:last-child {
  border-bottom: none;
}

.asset-checkbox .el-checkbox {
  flex: 1;
  display: flex;
  align-items: center;
}

.asset-checkbox .asset-ip {
  margin-left: 8px;
  font-weight: 500;
}

.asset-status-tag {
  margin-left: 10px;
}

.no-assets {
  text-align: center;
  padding: 40px 20px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .ip-list {
    width: 220px;
  }
}

@media (max-width: 768px) {
  .vulnerability-container {
    flex-direction: column;
  }

  .ip-list {
    width: 100%;
    max-height: 300px;
    overflow-y: auto;
  }

  .score-display-inline {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .score-grade-inline {
    width: 100%;
  }

  .baseline-stats {
    flex-wrap: wrap;
    margin-left: 0;
    margin-top: 20px;
  }

  .stat-item {
    flex: 1;
    min-width: calc(50% - 10px);
    margin-bottom: 15px;
  }
}

/* 滚动条样式 */
.group-container::-webkit-scrollbar,
.move-asset-content::-webkit-scrollbar,
.content-area::-webkit-scrollbar {
  width: 6px;
}

.group-container::-webkit-scrollbar-track,
.move-asset-content::-webkit-scrollbar-track,
.content-area::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.group-container::-webkit-scrollbar-thumb,
.move-asset-content::-webkit-scrollbar-thumb,
.content-area::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.group-container::-webkit-scrollbar-thumb:hover,
.move-asset-content::-webkit-scrollbar-thumb:hover,
.content-area::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

</style>