<template>
    <div>
        <h1 id="linuxBaseline">Linux基线检测</h1>
        <button id="recheckButton" @click="onRecheckButton">重新检测</button>

        <select id="statusFilter" v-model="selectedStatus" @change="filterRows">
            <option value="all">全部</option>
            <option value="passed">通过</option>
            <option value="failed">未通过</option>
        </select>

        <label id="searchProject" for="searchBox">搜索检测项:</label>
        <input type="text" id="searchBox" v-model="searchTerm" @keyup="filterSearchResults" placeholder="输入检测项关键字...">

        <table>
            <thead>
            <tr>
                <th><input type="checkbox" name="row-select" id="selectAll" @change="toggleCheckboxes"></th>
                <th>检测项</th>
                <th>检测依据</th>
                <th>检测结果</th>
                <th>是否符合基线</th>
                <th>修改建议</th>
            </tr>
            </thead>
            <tbody id="baselinebody">
            <tr v-for="checkresult in filteredCheckresults" :key="checkresult.id">
                <td><input type="checkbox" name="row-select" class="row-checkbox"></td>
                <td>{{ checkresult.description }}</td>
                <td>{{ checkresult.basis }}</td>
                <td>{{ checkresult.result }}</td>
                <td>{{ checkresult.IsComply }}</td>
                <td>{{ checkresult.recommand }}</td>
            </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                checkresults: [], // 初始空数组，用于存储检测结果
                selectedStatus: 'all', // 用于绑定下拉选择框的值
                searchTerm: '' // 用于绑定搜索框的值
            }
        },
        computed: {
            // 通过计算属性对检测结果进行过滤
            filteredCheckresults() {
                return this.checkresults.filter(result => {
                    const matchesStatus = this.selectedStatus === 'all' || result.IsComply.toString() === this.selectedStatus;
                    const matchesSearch = !this.searchTerm || result.description.toLowerCase().includes(this.searchTerm.toLowerCase());
                    return matchesStatus && matchesSearch;
                });
            }
        },
        methods: {
            fetchAndDisplayChenckResults() {
                fetch('http://localhost:8080/userinfo')
                    .then(response => response.json())
                    .then(checkresults => {
                        this.checkresults = checkresults;
                    })
                    .catch(error => console.error('Error:', error));
            },
            onRecheckButton() {
                alert('重新检测按钮被点击!');
            },
            toggleCheckboxes(event) {
                const isChecked = event.target.checked;
                this.$el.querySelectorAll('.row-checkbox').forEach(checkbox => {
                    checkbox.checked = isChecked;
                });
            },
            filterRows() {
                // 由于我们使用了计算属性来过滤检测结果，所以这个方法可以留空或用于其他逻辑
            },
            filterSearchResults() {
                // 搜索逻辑已经通过计算属性处理，这个方法可以留空
            }
        },
        mounted() {
            this.fetchAndDisplayChenckResults();
        }
    }
</script>

<style scoped>
    /* 在这里添加您的CSS代码，保持与提供的CSS相同 */
    #linuxBaseline {
        font-size: 24px;
        color: #141010e1;
        text-align: center;
        margin-top: 20px;
    }

    th.checkbox-column, td.checkbox-column {
        width: 20px; /* Minimize the width of the checkbox column */
        white-space: nowrap;
        padding: 8px 4px; /* Smaller padding for the checkbox column */
        text-align: center; /* Center align the checkboxes */
    }

    /* Style for the checkboxes */
    input[type="checkbox"] {
        margin-right: 5px;
        cursor: pointer;
    }

    #recheckButton, #statusFilter,#searchProject{
        padding: 10px 15px;
        margin: 2px;
        border: none;
        color: white;
        background-color: #4967ddbf; /* Bootstrap primary color */
        cursor: pointer;
    }

    #searchBox{
        padding: 10px 15px;
        margin: 2px;
        border: none;
        color: black;
        background-color: #dee0e8bf; /* Bootstrap primary color */
        cursor: pointer;
    }

    #recheckButton:hover,#statusFilter:hover{
        background-color: #0056b3; /* Darker shade for hover effect */
    }

    table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
    }

    thead {
        background-color: #f2f2f2;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8px;
    }

    tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    th {
        padding-top: 12px;
        padding-bottom: 12px;
        text-align: left;
        background-color: #4967dd93;
        color: white;
    }

</style>
