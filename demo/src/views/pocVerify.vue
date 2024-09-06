<template>
  <div class="container">
    <div class="title">
      <h1>POC验证</h1>
      <el-button size="medium" @click="goPocScanner" type="info">返回上一步（漏洞扫描）</el-button>
    </div>

    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header">POC任务</div>
          <el-button type="primary" @click="batchExecutePOC" style="margin-top: 5px;">批量执行POC</el-button>
          <el-table
              ref="table"
              :data="paginatedTasks"
              stripe
              style="width: 100%; margin-top: 10px"
              :row-key="row => row.CVE"
              :default-sort="{prop: 'CVE', order: 'descending'}">

            <el-table-column type="selection" width="55"></el-table-column>
            <el-table-column prop="CVE" label="漏洞编号" width="180"></el-table-column>
            <el-table-column prop="CVEName" label="漏洞名称" width="180"></el-table-column>
            <el-table-column prop="CVSS" label="CVSS" width="100"></el-table-column>

            <el-table-column prop="POCState" label="POC是否存在" width="150">
              <template slot-scope="scope">
                <span :class="{ 'failed-result': scope.row.POCState === '否' }">{{ scope.row.POCState }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="searchResult" label="扫描结果" width="140">
              <template slot-scope="scope">
                <span :class="{ 'failed-result': scope.row.searchResult === '未发现漏洞' }">{{ scope.row.searchResult }}</span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="400">
              <template slot-scope="scope">
                <el-button size="mini" :disabled="scope.row.POCState === '是'" @click="handleEdit(scope.$index, scope.row)">添加POC代码</el-button>
                <el-button size="mini" @click="executePOC(scope.row)">执行POC</el-button>
                <el-button size="mini" @click="lookDetails(scope.$index, scope.row)">查看执行细节</el-button>
<!--                <el-button size="mini" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>-->
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="pagination.currentPage"
              :page-sizes="[5, 10, 20, 50]"
              :page-size="pagination.pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalTasks">
          </el-pagination>
        </el-card>
      </el-col>
    </el-row>

    <!-- 弹窗显示CVE详情 -->
    <el-dialog :title="currentCveId" :visible.sync="detailsDialogVisible" width="50%">
      <div>
        <p><strong>CVE ID:</strong> {{ currentCveId }}</p>
        <p><strong>漏洞名称:</strong> {{ currentCveName }}</p>
        <p><strong>CVSS:</strong> {{ currentCvss }}</p>
        <p><strong>详情:</strong> {{ details }}</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="detailsDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      scanResults: [],
      pagination: {
        currentPage: 1,
        pageSize: 10
      },
      totalTasks: 0, // 总任务数量
      detailsDialogVisible: false, // 弹窗是否显示
      currentCveId: '', // 当前选择的CVE ID
      currentCveName: '', // 当前选择的漏洞名称
      currentCvss: '', // 当前选择的CVSS分数
      details: '', // 详情信息
    };
  },
  computed: {
    paginatedTasks() {
      // 处理 scanResults 数据，提取需要的 CVE 信息
      let results = [];

      this.scanResults.forEach(scanHostResult => {
        scanHostResult.ports.forEach(port => {
          Object.keys(port.cpes).forEach(cpeKey => {
            const cveList = port.cpes[cpeKey];

            cveList.forEach(cve => {
              results.push({
                CVE: cve.CVE_id,
                CVEName: cve.vul_name || 'N/A',
                CVSS: cve.CVSS || 'N/A',
                POCState: cve.pocExist ? '是' : '否',
                searchResult: cve.vulExist
              });
            });
          });
        });
      });

      const start = (this.pagination.currentPage - 1) * this.pagination.pageSize;
      const end = start + this.pagination.pageSize;

      return results.slice(start, end);
    }
  },
  created() {
    this.fetchCpeData();
  },
  methods: {
    fetchCpeData() {
      axios.post('api/pocSearch', null)
          .then(response => {
            this.scanResults = response.data;
            this.updateTotalTasks();  // 更新总任务数量
          })
          .catch(error => {
            console.error("There was an error fetching the scan results:", error.response || error);
            this.$message.error('请求失败，请稍后再试');
          });
    },
    batchExecutePOC() {
      const selectedRows = this.$refs.table.selection;
      const cveIds = selectedRows.map(row => row.CVE);

      if (cveIds.length === 0) {
        this.$message.warning('请至少选择一个任务进行批量执行');
        return;
      }

      axios.post('/api/pocVerify', { cve_ids: cveIds })
          .then(() => {
            this.$message.success('批量执行POC成功');
            this.fetchCpeData(); // 刷新数据
          })
          .catch(error => {
            console.error("There was an error during batch POC execution:", error);
            this.$message.error('批量执行POC失败，请稍后再试');
          });
    },
    executePOC(row) {
      axios.post('/api/pocVerify', { cve_ids: [row.CVE] })
          .then(() => {
            this.$message.success(`POC 执行成功: ${row.CVE}`);
            this.fetchCpeData(); // 刷新数据
          })
          .catch(error => {
            console.error(`There was an error executing POC for ${row.CVE}:`, error);
            this.$message.error('执行POC失败，请稍后再试');
          });
    },
    handleEdit(index, row) {
      console.log('编辑任务', index, row);
      this.$router.push('/pocManage');
    },
    lookDetails(index, row) {
      console.log('查看细节', index, row);
      this.currentCveId = row.CVE;
      this.currentCveName = row.CVEName;
      this.currentCvss = row.CVSS;

      axios
          .post('/api/details', { cve_id: row.CVE })
          .then((response) => {
            this.details = response.data.details || '未提供详情';
            this.detailsDialogVisible = true; // 打开弹窗
          })
          .catch((error) => {
            console.error('There was an error fetching the CVE details:', error);
            this.$message.error('获取漏洞详情失败，请稍后再试');
          });
    },
    handleDelete(index, row) {
      console.log('删除任务', index, row);
    },
    updateTotalTasks() {
      let results = [];

      this.scanResults.forEach(scanHostResult => {
        scanHostResult.ports.forEach(port => {
          Object.keys(port.cpes).forEach(cpeKey => {
            const cveList = port.cpes[cpeKey];

            cveList.forEach(cve => {
              results.push({
                CVE: cve.CVE_id,
                CVEName: cve.vul_name || 'N/A',
                CVSS: cve.CVSS || 'N/A',
                POCState: cve.pocExist ? '是' : '否',
                searchResult: cve.vulExist
              });
            });
          });
        });
      });

      this.totalTasks = results.length; // 更新总任务数量
    },
    handleSizeChange(newSize) {
      this.pagination.pageSize = newSize;
      this.pagination.currentPage = 1; // 重置到第一页
      this.updateTotalTasks(); // 更新总任务数
    },
    handleCurrentChange(newPage) {
      this.pagination.currentPage = newPage;
      this.updateTotalTasks(); // 更新总任务数
    },
    goPocScanner(){
      this.$nextTick(() => {
        this.$router.push('/pocScanner');
      });
    }
  }
}
</script>

<style scoped>
.container {
  margin: 20px;
}

.box-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.scan-button {
  text-align: right;
  margin-top: 10px;
}

.failed-result {
  color: red;
}
</style>

