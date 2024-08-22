

<template>
  <div>
    <h1 id="linuxBaseline">等级保护测评</h1>

    <el-select v-model="selectedStatus" placeholder="请选择状态" style="width: 120px;margin-right: 20px;">
      <el-option label="全部" value="all"></el-option>
      <el-option label="通过" value="passed"></el-option>
      <el-option label="未通过" value="failed"></el-option>
    </el-select>

    <el-input placeholder="输入检测项关键字..." v-model="searchTerm" @input="filterSearchResults" style="width: 300px;margin-right: 20px;"></el-input>
    <el-button @click="computeResult" type="success" style="margin-right: 30px;">计算评分</el-button>
    <div class="result-container">
      <div class="score-display">得分：{{ resultScore }}</div>
      <div class="conclusion">
        结论：
        <template v-if="resultScore !== ''">
          <span v-if="resultScore >= 90">优</span>
          <span v-else-if="resultScore >= 80 && resultScore < 90">良</span>
          <span v-else-if="resultScore >= 70 && resultScore < 80">中</span>
          <span v-else>差</span>
        </template>
      </div>
    </div>
<!--    <span class="score-display">得分：{{ resultScore }}</span>-->
<!--    <div class="conclusion">-->
<!--      结论：-->
<!--      <template v-if="resultScore !== ''">-->
<!--        <span v-if="resultScore >= 90">优</span>-->
<!--        <span v-else-if="resultScore >= 80 && resultScore < 90">良</span>-->
<!--        <span v-else-if="resultScore >= 70 && resultScore < 80">中</span>-->
<!--        <span v-else>差</span>-->
<!--      </template>-->
<!--    </div>-->

    <el-table :data="filteredCheckresults" style="width: 100%">
<!--      <el-table-column type="selection" width="55"></el-table-column>-->
      <el-table-column prop="description" label="检测项"></el-table-column>
      <el-table-column prop="basis" label="检测依据"></el-table-column>
      <el-table-column prop="importantLevel" label="重要程度"></el-table-column>
      <el-table-column prop="result" label="检测结果"></el-table-column>
      <el-table-column prop="IsComply" label="是否符合基线" width="150%">
        <template slot-scope="scope">
          <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">{{ scope.row.IsComply }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="recommend" label="修改建议" width="400%"></el-table-column>
      <el-table-column label="结果评分" width="180">
        <template slot-scope="scope">
          <el-select v-model="scope.row.score" placeholder="请选择评分">
            <el-option label="符合" value="1"></el-option>
            <el-option label="部分符合" value="0.5"></el-option>
            <el-option label="不符合" value="0"></el-option>
          </el-select>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: "baseCheck",
  data() {
    return {
      checkresults: [],
      selectedStatus: 'all',
      searchTerm: '',
      resultScore: localStorage.getItem('resultScore') || '',
    }
  },
  computed: {
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
    fetchAndDisplayCheckResults() {
      fetch('/api/userinfo')
          .then(response => response.json())
          .then(data => {
            this.checkresults = data.Event_result.map(item => ({
              ...item,
              score: item.IsComply === 'true' ? '1' : '0.5'
              //score: item.score || '1' // 从后端获取评分数据，如果没有则默认空
            }));
          })
          .catch(error => console.error('Error:', error));
    },
    computeResult() {
      const scoreMeasures = this.checkresults.map(item => ({
        importantLevelJson: item.importantLevel,
        IsComplyLevel: item.score.toString(),
      }));

      fetch('/api/classifyProtect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ scoreMeasures })
      })
          .then(response => response.json())
          .then(data => {
            console.log("Received score from backend:", data.score); // Log the received score
            this.resultScore = data.score; // 更新 resultScore
            localStorage.setItem('resultScore', this.resultScore); // 将 resultScore 存储到 localStorage 中
          })
          .catch(error => console.error('Error:', error));
    }

  },
  mounted() {
    this.fetchAndDisplayCheckResults();
  }
}
</script>

<style scoped>
.failed-result {
  color: red;
}
.result-container {
  display: inline-flex;
  align-items: center;
  gap: 20px; /* Adds space between score and conclusion */
  margin-top: 10px;
}
.score-display,
.conclusion {
  font-size: 18px;
  font-weight: bold;
  color: #4CAF50;
}
</style>

