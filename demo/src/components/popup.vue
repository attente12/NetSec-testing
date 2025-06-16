<template>
  <div>
    <h1 id="linuxBaseline">基线检测报告</h1>
    <!-- 检测时间 -->
    <div style="text-align:right; margin-top:20px;">
      <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>
    </div>
    <el-row :gutter="20">
      <el-col :span="12">
        <p>主机名：{{ serverInfo.hostname }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机架构：{{ serverInfo.arch }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机CPU信息：{{ serverInfo.cpu }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机物理CPU核心数：{{ serverInfo.cpuCore }}</p>
      </el-col>
      <el-col :span="12">
        <p>硬件型号：{{ serverInfo.ProductName }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机版本信息：{{ serverInfo.version }}</p>
      </el-col>
    </el-row>

    <el-select v-model="selectedStatus" placeholder="请选择状态" style="width: 120px;">
      <el-option label="全部" value="all"></el-option>
      <el-option label="通过" value="passed"></el-option>
      <el-option label="未通过" value="failed"></el-option>
    </el-select>

    <el-input placeholder="输入检测项关键字..." v-model="searchTerm" @input="filterSearchResults"
      style="width: 300px;"></el-input>

    <el-table :data="filteredCheckresults" style="width: 100%">
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="description" label="检测项"></el-table-column>
      <el-table-column prop="basis" label="检测依据"></el-table-column>
      <el-table-column prop="result" label="检测结果"></el-table-column>
      <el-table-column prop="IsComply" label="是否符合基线" width="200%">
        <template slot-scope="scope">
          <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">{{ scope.row.IsComply }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="recommend" label="修改建议" width="600%"></el-table-column>
    </el-table>

  </div>
</template>

<script>

export default {
  name: "baseCheck",
  data() {
    return {
      checkresults: [],
      serverInfo: {},
      selectedStatus: 'all',
      searchTerm: '',
      showContentForPDF: false // 控制内容显示的数据属性
    }
  },
  props: {
    dataFromParent: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    message() {
      return this.$store.state.message; // 读取共享状态
    },
    filteredCheckresults() {
      return this.checkresults.filter(result => {
        const matchesStatus = this.selectedStatus === 'all' ||
          (this.selectedStatus === 'passed' && result.IsComply === 'true') ||
          (this.selectedStatus === 'failed' && result.IsComply === 'false');
        const matchesSearch = !this.searchTerm ||
          result.description.toLowerCase().includes(this.searchTerm.toLowerCase());
        return matchesStatus && matchesSearch;
      });
    }

  },
  methods: {

  },
  mounted() {
    if (this.dataFromParent.Event_result.length !== 0) {
      this.serverInfo = this.dataFromParent.ServerInfo
      this.checkresults = this.dataFromParent.Event_result
    } else {
      return alert('检测数据不存在')
    }
  },
}
</script>

<style scoped>
/* 保留原有样式或按需调整 */
#linuxBaseline {
  font-size: 24px;
  color: #141010e1;
  text-align: center;
  margin-top: 20px;
}

#linuxBaseline2 {
  font-size: 32px;
  color: #141010e1;
  text-align: center;
  margin-top: 20px;
}

/*结果为false则显示为红色*/
.failed-result {
  color: red;
}

.server1 .el-col p {
  font-size: 22px;
  /* 增大字体大小为16像素 */
  white-space: pre-wrap;
  /* 允许自动换行 */
  line-height: 1.6;
  /* 增加行间距使阅读更加舒适 */
  margin-bottom: 5px;
  /* 增加段落之间的底部间距 */
}



/*文字分割的正确版本*/
.pdf-content {
  font-size: 10pt;
  /* 设置字体大小为10磅 */
  max-width: 297mm;
  /* A4 宽度约为 210mm */
  padding: 15mm;
  /* A4 页面常用边距 */
  box-sizing: border-box;
}

/* 单独调整某些元素的字体大小 */
.pdf-content h1 {
  font-size: 14pt;
  /* 较大的标题字体 */
}

.pdf-content p {
  font-size: 9pt;
  /* 正文的字体大小 */
}
</style>
