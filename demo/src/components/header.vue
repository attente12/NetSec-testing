<!--<template>-->
<!--    <div class="head-breadcrumb">-->
<!--        <el-breadcrumb separator-class="el-icon-arrow-right">-->
<!--            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>-->
<!--&lt;!&ndash;            <el-breadcrumb-item :to="{ path: '/baseCheck' }">安全基线检测</el-breadcrumb-item>&ndash;&gt;-->
<!--&lt;!&ndash;            <el-breadcrumb-item>报告详情</el-breadcrumb-item>&ndash;&gt;-->
<!--            <el-breadcrumb-item>-->
<!--                {{$route.meta.title}}-->
<!--            </el-breadcrumb-item>-->
<!--        </el-breadcrumb>-->
<!--    </div>-->
<!--</template>-->

<!--<script>-->
<!--    export default {-->
<!--        name: "HeadBreadcrumb"-->
<!--    }-->
<!--</script>-->

<!--<style scoped>-->
<!--    .head-breadcrumb {-->
<!--        padding: 20px;-->
<!--    }-->
<!--</style>-->

<template>
    <div style="line-height: 60px; display: flex">
        <div style="flex: 1;">
            <span :class="collapseBtnClass" style="cursor: pointer;font-size:18px" @click="collapse"></span>
            <el-breadcrumb separator="/" style="display:inline-block;margin-left:10px ">
                <el-breadcrumb-item :to="'/'">首页</el-breadcrumb-item>
                <el-breadcrumb-item>{{$route.meta.title}}</el-breadcrumb-item>
            </el-breadcrumb>
        </div>
    </div>
</template>

<script>
    export default {
        name: "Header",
        props: {
            collapseBtnClass: String,
            collapse: Boolean,
        }
    }
</script>

<style scoped>

</style>