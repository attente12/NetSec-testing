<template>
  <div class="container">
    <div class="title">
      <h1>POC验证</h1>
    </div>

    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header">POC任务</div>
          <el-button type="primary" @click="addTask" style="margin-top: 5px;">批量执行POC</el-button>
          <el-table
              :data="paginatedTasks"
              stripe
              style="width: 100%; margin-top: 10px"
              :row-key="row => row.CVEName"
              :default-sort="{prop: 'date', order: 'descending'}">
            <el-table-column type="selection" width="55"></el-table-column>
            <el-table-column prop="CVE" label="漏洞编号" width="180"></el-table-column>
            <el-table-column prop="CVEName" label="漏洞名称" width="180"></el-table-column>
            <el-table-column prop="CVSS" label="CVSS" width="100"></el-table-column>
            <el-table-column prop="searchTarget" label="扫描目标（端口）" width="210"></el-table-column>
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
            <el-table-column label="操作" width="350">
              <template slot-scope="scope">
                <el-button size="mini" :disabled="scope.row.POCState === '是'" @click="handleEdit(scope.$index, scope.row)">添加POC代码</el-button>
                <el-button size="mini" @click="handleExecutePOC(scope.row)">执行POC</el-button>
                <el-button size="mini" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
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
              :total="tasks.length">
          </el-pagination>
        </el-card>
      </el-col>
    </el-row>
  </div>

</template>

<script>
export default {
  data() {
    return {
      // scanTarget: '',
      // scanResults: [
      //   {
      //     "cpes": {
      //       "cpe:/o:linux:linux_kernel:2.6.32": [
      //         {
      //           "CVE_id": "CVE-2019-14896",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         },
      //         {
      //           "CVE_id": "CVE-2019-15505",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         },
      //         {
      //           "CVE_id": "CVE-2019-15292",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         },
      //         {
      //           "CVE_id": "CVE-2017-7895",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         },
      //         {
      //           "CVE_id": "CVE-2016-3955",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         },
      //         {
      //           "CVE_id": "CVE-2015-8812",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         },
      //         {
      //           "CVE_id": "CVE-2015-1421",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         },
      //         {
      //           "CVE_id": "CVE-2014-2523",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         },
      //         {
      //           "CVE_id": "CVE-2010-2495",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         },
      //         {
      //           "CVE_id": "CVE-2010-2521",
      //           "CVSS": "10.000000",
      //           "pocExist": false,
      //           "vulExist": "未验证"
      //         }
      //       ]
      //     },
      //     "ip": "192.168.177.129",
      //     "ports": [
      //       {
      //         "cpes": {
      //           "cpe:/a:openbsd:openssh:8.2p1": [ ],
      //           "cpe:/o:linux:linux_kernel": [
      //             {
      //               "CVE_id": "CVE-2022-31767",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             },
      //             {
      //               "CVE_id": "CVE-2021-39065",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             },
      //             {
      //               "CVE_id": "CVE-2020-9633",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             },
      //             {
      //               "CVE_id": "CVE-2020-12651",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             },
      //             {
      //               "CVE_id": "CVE-2020-4212",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             },
      //             {
      //               "CVE_id": "CVE-2020-4211",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             },
      //             {
      //               "CVE_id": "CVE-2020-4210",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             },
      //             {
      //               "CVE_id": "CVE-2019-8255",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             },
      //             {
      //               "CVE_id": "CVE-2019-14901",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             },
      //             {
      //               "CVE_id": "CVE-2019-14896",
      //               "CVSS": "10.000000",
      //               "pocExist": false,
      //               "vulExist": "未验证"
      //             }
      //           ]
      //         },
      //         "portId": "22",
      //         "protocol": "tcp",
      //         "service_name": "ssh",
      //         "status": "open",
      //         "version": "8.2p1 Ubuntu 4ubuntu0.11"
      //       },
      //       {
      //         "cpes": { },
      //         "portId": "5000",
      //         "protocol": "tcp",
      //         "service_name": "upnp",
      //         "status": "open",
      //         "version": ""
      //       }
      //     ]
      //   }
      // ],
      tasks: [
        { CVE:'CVE-2017-0143',searchTarget:'192.168.1.0/24:445',POCState:'是',searchResult:'存在漏洞'},
        { CVE: 'CVE-2018-1234', searchTarget: '192.168.0.0/24:3389', POCState: '是', searchResult: '未发现漏洞'},
        { CVE: 'CVE-2019-5678', searchTarget: '10.0.0.0/16:22', POCState: '否', searchResult: '未验证'},
        { CVE: 'CVE-2020-9999', searchTarget: '172.16.0.0/16:80', POCState: '是', searchResult: '未发现漏洞'},
        { CVE: 'CVE-2021-4321', searchTarget: '10.1.1.0/24:443', POCState: '否', searchResult: '未验证'},
        { CVE: 'CVE-2022-6789', searchTarget: '192.168.1.100:8080', POCState: '是', searchResult: '未发现漏洞'},
        { CVE: 'CVE-2018-1234', searchTarget: '192.168.0.0/24:3389', POCState: '是', searchResult: '未发现漏洞'},
        { CVE: 'CVE-2019-5678', searchTarget: '10.0.0.0/16:22', POCState: '否', searchResult: '未验证'},
        { CVE: 'CVE-2020-9999', searchTarget: '172.16.0.0/16:80', POCState: '是', searchResult: '未发现漏洞'},
        { CVE: 'CVE-2021-4321', searchTarget: '10.1.1.0/24:443', POCState: '否', searchResult: '未验证'},
        { CVE: 'CVE-2022-6789', searchTarget: '192.168.1.100:8080', POCState: '是', searchResult: '未发现漏洞'},
        { CVE: 'CVE-2018-1234', searchTarget: '192.168.0.0/24:3389', POCState: '是', searchResult: '未发现漏洞'},
        { CVE: 'CVE-2019-5678', searchTarget: '10.0.0.0/16:22', POCState: '否', searchResult: '未验证'},
        { CVE: 'CVE-2020-9999', searchTarget: '172.16.0.0/16:80', POCState: '是', searchResult: '未发现漏洞'},
        { CVE: 'CVE-2021-4321', searchTarget: '10.1.1.0/24:443', POCState: '否', searchResult: '未验证'},
        { CVE: 'CVE-2022-6789', searchTarget: '192.168.1.100:8080', POCState: '是', searchResult: '未发现漏洞'}
      ],
      pagination: {
        currentPage: 1,
        pageSize: 10
      }
    };
  },
  computed: {
    paginatedTasks() {
      const start = (this.pagination.currentPage - 1) * this.pagination.pageSize;
      const end = start + this.pagination.pageSize;
      return this.tasks.slice(start, end);
    }
  },
  created() {
    // 在组件创建时调用函数以从服务器获取CPE数据
    this.fetchCpeData();
  },
  methods: {
    // fetchCpeData() {
    //   fetch('http://192.168.177.129:8080/cveScan') // 使用fetch API从指定URL获取数据
    //       .then(response => {
    //         if (!response.ok) {
    //           throw new Error('Network response was not ok');
    //         }
    //         return response.json();
    //       })
    //       .then(data => {
    //         this.cpes = [];
    //         data.forEach(item => {
    //           item.ports.forEach(port => {
    //             this.addCpes(port.cpes); // 递归处理每个端口的cpes对象
    //           });
    //           this.addCpes(item.cpes); // 也处理最外层的cpes对象
    //         });
    //       })
    //       .catch(error => {
    //         console.error('Error fetching CPE data:', error);
    //       });
    // },
    // addCpes(cpes) {
    //   // 递归处理cpes对象，以确保从嵌套结构中提取所有CPE
    //   Object.keys(cpes).forEach(key => {
    //     if (!this.cpes.includes(key)) {
    //       this.cpes.push(key);
    //     }
    //     cpes[key].forEach(cpeObject => {
    //       if (cpeObject.cpes) {
    //         this.addCpes(cpeObject.cpes); // 递归检查是否有进一步嵌套的cpes
    //       }
    //     });
    //   });
    // },
    addTask() {
      console.log('添加任务');
    },
    handleEdit(index, row) {
      console.log('编辑任务', index, row);
    },
    handleExecutePOC(row) {
      if (row.POCState === '否') {
        this.$confirm(`${row.CVE} 不存在POC代码，请先添加POC代码。`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '去添加',
          type: 'warning',
          distinguishCancelAndClose: true
        }).then(() => {
          console.log('点击了确定');
        }).catch(action => {
          if (action === 'cancel') {
            this.handleAddPOC(row);  // 调用添加POC代码的方法
          }
        });
      } else {
        console.log('执行POC', row);
      }
    },

    handleAddPOC(row) {
      console.log(`准备为 ${row.CVEName} 添加POC代码`);
      // 这里可以添加实际的逻辑，比如打开一个模态窗口或者更改页面以填写POC代码
      // 例如：this.$router.push('/add-poc/${row.CVEName}');
    },
    handleDelete(index, row) {
      console.log('删除任务', index, row);
    },
    handleSizeChange(val) {
      this.pagination.pageSize = val;
    },
    handleCurrentChange(val) {
      this.pagination.currentPage = val;
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
