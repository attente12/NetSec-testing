<template>
  <div class="container">
    <el-card class="box-card">
      <el-row>
        <el-col :span="24">
          <div class="header">
            <h1>Linux等级保护测评</h1>
<!--            <p class="subtitle">安全基线检测工具</p>-->
          </div>
        </el-col>
      </el-row>

      <el-form
          @submit.prevent="submitForm"
          :model="formData"
          :rules="rules"
          ref="form"
          label-width="120px"
          class="login-form">
        <el-form-item label="测评级别" prop="level">
          <el-select
              v-model="formData.level"
              placeholder="请选择测评级别"
              style="width: 100%">
            <el-option
                label="三级等保"
                :value="3">
            </el-option>
            <el-option
                label="二级等保"
                :value="2"
                disabled>
            </el-option>
            <el-option
                label="一级等保"
                :value="1"
                disabled>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="IP 地址" prop="ip">
          <el-select
              v-model="formData.ip"
              placeholder="请选择或输入服务器IP地址"
              filterable
              allow-create
              default-first-option
              style="width: 100%">
            <el-option
                v-for="ip in aliveHosts"
                :key="ip"
                :label="ip"
                :value="ip">
            </el-option>
          </el-select>
          <!-- 新增查看临时结果链接 -->
          <div class="temp-check-link">
            <el-link
                type="primary"
                :underline="false"
                @click="handleViewTempResult"
                icon="el-icon-view">
              查看该IP的最近报告
            </el-link>
          </div>
        </el-form-item>
        <el-form-item label="root密码" prop="pd">
          <el-input
              v-model="formData.pd"
              type="password"
              placeholder="请输入root密码"
              prefix-icon="el-icon-lock"
              show-password>
          </el-input>
        </el-form-item>
        <el-form-item>
          <div class="control-bar">
            <el-checkbox
                v-model="checkAll"
                @change="handleCheckAllChange"
                style="margin-right: 15px;">
              全选检测项目
            </el-checkbox>
            <el-button
                type="primary"
                @click="startCheck"
                icon="el-icon-video-play"
                :loading="loading"
                :disabled="selectedItems.length === 0">
              开始检测
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="box-card check-items">
      <div slot="header" class="card-header">
        <span>检测项目选择</span>
      </div>

      <el-checkbox-group v-model="selectedItems" @change="handleCheckedItemsChange">
        <el-row :gutter="20">
          <el-col :span="8" v-for="item in checkItems" :key="item.id">
            <el-checkbox :label="item.id">
              <el-tooltip :content="item.name" placement="top">
                <span class="checkbox-label">{{ item.name }}</span>
              </el-tooltip>
            </el-checkbox>
          </el-col>
        </el-row>
      </el-checkbox-group>


    </el-card>

    <el-dialog
        title="检测完成"
        :visible.sync="dialogVisible"
        width="30%"
        center>
      <span>检测任务已完成，是否查看结果？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="viewResult">查看结果</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { Message } from "element-ui";

export default {
  name: "home",
  data() {
    return {
      formData: {
        ip: '',
        pd: '',
        level: 3 // 默认选择三级等保
      },
      aliveHosts: [], // 存储活跃IP列表
      selectedItems: [],
      checkAll: false,
      dialogVisible: false,
      loading: false,
      rules: {
        level: [
          { required: true, message: '请选择测评级别', trigger: 'change' }
        ],
        ip: [
          { required: true, message: '请输入IP地址', trigger: 'blur' },
          { pattern: /^(\d{1,3}\.){3}\d{1,3}$/, message: '请输入正确的IP地址格式', trigger: 'blur' }
        ],
        pd: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      checkItems: [
        { id: 1, name: '8.1.3.2.a 应在网络边界或区域之间根据访问控制策略设置访问控制规则，默认情况下除允许通信外受控接口拒绝所有通信' },
        { id: 2, name: '8.1.3.2.b 应删除多余或无效的访问控制规则，优化访问控制列表，并保证访问控制规则数量最小化' },
        { id: 3, name: '8.1.3.2.c 应对源地址、目的地址、源端口、目的端口和协议等进行检查，以允许/拒绝数据包进出。' },
        { id: 4, name: '8.1.3.2.d 应能根据会话状态信息为进出数据流提供明确的允许/拒绝访问能力' },
        { id: 5, name: '8.1.3.2.e 应对进出网络的数据流实现基于应用协议和应用内容的访问控制' },
        { id: 6, name: '8.1.3.3.a 应在关键网络节点处检测、防止或限制从外部发起的网络攻击行为' },
        { id: 7, name: '8.1.3.3.b 应在关键网络节点处检测、防止或限制从内部发起的网络攻击行为' },
        { id: 8, name: '8.1.3.3.c 应采取技术措施对网络行为进行分析实现对网络攻击特别是新型网络攻击行为的分析' },
        { id: 9, name: '8.1.3.3.d 当检测到攻击行为时，记录攻击源IP、攻击类型、攻击目标、攻击时间，在发生严重入侵事件时应提供报警' },
        { id: 10, name: '8.1.3.4.a 应在关键网络节点处对恶意代码进行检测和清除，并维护恶意代码防护机制的升级和更新' },
        { id: 11, name: '8.1.3.4.b 应在关键网络节点处对垃圾邮件进行检测和防护，并维护垃圾邮件防护机制的升级和更新' },
        { id: 12, name: '8.1.3.5.a 应在网络边界、重要网络节点进行安全审计，审计覆盖到每个用户，对重要的用户行为和重要安全事件进行审计' },
        { id: 13, name: '8.1.3.5.b 审计记录应包括事件的日期和时间、用户、事件类型、事件是否成功及其他与审计相关的信息' },
        { id: 14, name: '8.1.3.5.c 应对审计记录进行保护，定期备份，避免受到未预期的删除、修改或覆盖' },
        { id: 15, name: '8.1.3.5.d 应能对远程访问的用户行为、访问互联网的用户行为等单独进行行为审计和数据分析' },
        { id: 16, name: '8.1.4.1.a 应对登录的用户进行身份标识和鉴别，身份标识具有唯一性，身份鉴别信息具有复杂度要求并定期更换' },
        { id: 17, name: '8.1.4.1.b 应具有登录失败处理功能，应配置并启用结束会话、限制非法登录次数和当登录连接超时自动退出等相关措施' },
        { id: 18, name: '8.1.4.1.c 当进行远程管理时，应采取必要措施防止鉴别信息在网络传输过程中被窃听' },
        { id: 19, name: '8.1.4.1.d 应采用口令、密码技术、生物技术等两种或两种以上组合的鉴别技术对用户进行身份鉴别，且其中一种鉴别技术至少应使用密码技术来实现' },
        { id: 20, name: '8.1.4.2.a 应对登录的用户分配账户和权限，确保每个用户拥有唯一身份，并依据职责授予适当权限' },
        { id: 21, name: '8.1.4.2.b 应重命名或删除默认账户，修改默认账户的默认口令' },
        { id: 22, name: '8.1.4.2.c 应及时删除或停用多余的、过期的账户，避免共享账户的存在' },
        { id: 23, name: '8.1.4.2.d 应授予管理用户所需的最小权限，实现管理用户的权限分离' },
        { id: 24, name: '8.1.4.2.e 应由授权主体配置访问控制策略，访问控制策略规定主体对客体的访问规则' },
        { id: 25, name: '8.1.4.2.f 访问控制的粒度应达到主体为用户级或进程级，客体为文件，数据库表级' },
        { id: 26, name: '8.1.4.2.g 应对重要主体和客体设置安全标记，并控制主体对有安全标记信息资源的访问' },
        { id: 27, name: '8.1.4.3.a 应启用安全审计功能，审计覆盖到每个用户，对重要的用户行为和重要安全事件进行审计' },
        { id: 28, name: '8.1.4.3.b 审计记录应包括事件的日期和时间、用户、事件类型，事件是否成功及其他审计相关的信息' },
        { id: 29, name: '8.1.4.3.c 应对审计记录进行保护，定期备份，避免受到未预期的删除、修改或覆盖等' },
        { id: 30, name: '8.1.4.3.d 应对审计进程进行保护，防止未经授权的中断' },
        { id: 31, name: '8.1.4.4.a 应遵循最小安装原则，仅安装需要的组件和应用程序' },
        { id: 32, name: '8.1.4.4.b 应关闭不需要的系统服务、默认共享和高危端口' },
        { id: 33, name: '8.1.4.4.c 应能够检测到对重要节点进行入侵的行为，并在发生严重入侵事件时提供报警' },
        { id: 34, name: '8.1.4.4.d 应采用免受恶意代码攻击的技术措施或主动免疫可信验证机制，及时识别入侵和病毒行为，并将其有效阻断' },
        { id: 35, name: '8.1.4.5.a 应采用校验技术或密码技术保证重要数据在传输过程中的完整性，包括鉴别数据、业务数据、审计数据、配置数据、视频数据、个人信息等' },
        { id: 36, name: '8.1.4.5.b 应采用校验技术或密码技术保证重要数据在存储过程中的完整性，包括鉴别数据、业务数据、审计数据、配置数据、视频数据和个人信息等' },
        { id: 37, name: '8.1.4.5.c 应采用密码技术保证重要数据在传输过程中的保密性，包括但不限于鉴别数据、重要业务数据和重要个人信息等' },
        { id: 38, name: '8.1.4.5.d 应采用密码技术保证重要数据在存储过程中的保密性，包括但不限于鉴别数据、重要业务数据和重要个人信息等' },
        { id: 39, name: '8.1.4.5.e 应提供重要数据的本地数据备份和恢复功能' },
        { id: 40, name: '8.1.4.5.f 应提供重要数据处理系统的热冗余，保证系统的高可用性' },
        { id: 41, name: '8.1.4.5.g 应保证鉴别信息所在的存储空间在被释放或重新分配前得到完全清除' },
        { id: 42, name: '8.1.4.5.h 应保证存有敏感数据的存储空间被释放或重新分配前得到完全清除' },
        { id: 43, name: '8.1.4.6.a 应仅采集和保存业务必需的用户个人信息' },
        { id: 44, name: '8.1.4.6.b 应禁止未授权访问和非法使用用户个人信息' }
      ]
    };
  },
  created() {
    // 组件创建时获取活跃IP列表
    this.fetchAliveHosts();
  },
  methods: {
    // 获取活跃IP列表 - 修改为从localStorage获取
    fetchAliveHosts() {
      try {
        const storedHosts = sessionStorage.getItem('hostdiscovery');
        if (storedHosts) {
          this.aliveHosts = JSON.parse(storedHosts);
        } else {
          this.aliveHosts = [];
          Message.warning('未找到存活主机列表，请先进行主机发现');
        }
      } catch (error) {
        console.error('解析sessionStorage数据失败:', error);
        this.aliveHosts = [];
        Message.error('获取存活主机列表失败');
      }
    },
    // 获取活跃IP列表
    // fetchAliveHosts() {
    //   fetch('/api/getAliveHosts')
    //       .then(response => {
    //         if (!response.ok) {
    //           throw new Error(`HTTP status ${response.status}`);
    //         }
    //         return response.json();
    //       })
    //       .then(data => {
    //         this.aliveHosts = data.alive_hosts;
    //       })
    //       .catch(error => {
    //         Message.error('获取活跃IP列表失败：' + error.message);
    //       });
    // },
    // 处理全选复选框变化
    handleCheckAllChange(val) {
      const allItemIds = this.checkItems.map(item => item.id);
      this.selectedItems = val ? allItemIds : [];
    },
    // 处理选中项变化
    handleCheckedItemsChange(value) {
      const checkedCount = value.length;
      this.checkAll = checkedCount === this.checkItems.length;
    },
    // 开始检测（合并了原来的submitForm和batchExecute方法）
    startCheck() {
      this.$refs.form.validate((valid) => {
        if (!valid) {
          return;
        }

        if (this.selectedItems.length === 0) {
          Message.warning('请选择至少一个检测项目');
          return;
        }

        this.loading = true;
        const payload = {
          //level: this.formData.level, // 添加测评级别到payload
          ip: this.formData.ip,
          pd: this.formData.pd,
          ids: this.selectedItems
        };

        fetch('/api/level3Login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        })
            .then(response => {
              if (!response.ok) {
                if (response.status === 500) {
                  throw new Error("SSH会话无法启动");
                }
                throw new Error(`HTTP status ${response.status}`);
              }
              return response.json();
            })
            .then(data => {
              console.log(data);
              this.loading = false;
              this.dialogVisible = true;
            })
            .catch((error) => {
              this.loading = false;
              Message.error(error.message);
            });
      });
    },
    viewResult() {
      this.dialogVisible = false;
      this.$nextTick(() => {
        this.$router.push({
          path: '/tempClassifyProtect',  // 改为跳转到新页面
          query: {
            //level: this.formData.level, // 传递测评级别
            ip: this.formData.ip  // 传递检测的IP
          }
        });
      });
    },
    handleViewTempResult() {
      if (!this.formData.ip) {
        Message.warning('请先输入服务器IP地址');
        return;
      }

      // 验证IP格式（复用原有规则）
      const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
      if (!ipPattern.test(this.formData.ip.trim())) {
        Message.error('IP地址格式不正确，请检查输入');
        return;
      }

      this.$router.push({
        path: '/tempClassifyProtect',
        query: { ip: this.formData.ip }
      });
    },
  }
}
</script>

<style scoped>
.container {
  padding: 20px;
}

.box-card {
  margin-bottom: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #409EFF;
  margin-bottom: 10px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.login-form {
  max-width: 500px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.check-items {
  margin-top: 30px;
}

.checkbox-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  max-width: 200px;
}

.el-checkbox {
  margin-bottom: 15px;
  width: 100%;
}

.el-row {
  margin-bottom: 20px;
}

.control-bar {
  display: flex;
  align-items: center;
}

.selected-info {
  margin-top: 10px;
  color: #606266;
  font-size: 14px;
}

.temp-check-link {
  margin-top: -8px;
  margin-bottom: -13px;
  font-size: 12px;
  text-align: right;

  .el-link {
    display: inline-flex;
    align-items: center;

    i {
      margin-right: 3px;
      font-size: 14px;
    }
  }
}

.login-form >>> .el-form-item {
  margin-bottom: 18px;
}
</style>

