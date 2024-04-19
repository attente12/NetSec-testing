<template>
    <div class="aside" style="height: 100%; width: 100%;">
        <el-row class="tac" style="height: 100%; width: 100%;">
            <el-col :span="12" style="height: 100%; width: 100%;">
                <el-menu
                        default-active="this.$route.path" router
                        class="el-menu-vertical-demo"
                        @open="handleOpen"
                        @close="handleClose"
                        background-color="#545c64"
                        text-color="#fff"
                        active-text-color="#ffd04b"
                        style="height: 100%; width: 100%;">
                    <div style="height: 60px; line-height: 60px; text-align: center">
                        <img src="../assets/logo.png" alt="" style="width: 20px; position: relative; top: 5px; right: 5px">
                        <b style="color: white">网络安全测试平台</b>
                    </div>
<!--                    <el-submenu index="/pagesOne">-->
<!--                        <template slot="title">-->
<!--                            <i class="el-icon-location"></i>-->
<!--                            <span>导航一</span>-->
<!--                        </template>-->
<!--                        <el-menu-item-group>-->
<!--                            <el-menu-item index="/">选项1</el-menu-item>-->
<!--                            <el-menu-item index="/">选项2</el-menu-item>-->
<!--                            <el-menu-item index="/">选项3</el-menu-item>-->
<!--                        </el-menu-item-group>-->
<!--                        <el-submenu index="1-4">-->
<!--                            <template slot="title">选项4</template>-->
<!--                            <el-menu-item index="1-4-1">选项1</el-menu-item>-->
<!--                        </el-submenu>-->
<!--                    </el-submenu>-->
                    <el-menu-item index="/">
                        <i class="el-icon-menu"></i>
                        <span slot="title">安全基线检测</span>
                    </el-menu-item>
                    <el-menu-item index="">
                        <i class="el-icon-menu"></i>
                        <span slot="title">导航二</span>
                    </el-menu-item>
                    <el-menu-item index="/pagesOne">
                        <i class="el-icon-document"></i>
                        <span slot="title">导航三</span>
                    </el-menu-item>
                    <el-menu-item index="/pagesTwo">
                        <i class="el-icon-setting"></i>
                        <span slot="title">导航四</span>
                    </el-menu-item>
                    <el-menu-item index="/baseCheck">
                        <i class="el-icon-setting"></i>
                        <span slot="title">导航四</span>
                    </el-menu-item>
                </el-menu>
            </el-col>
        </el-row>
    </div>
</template>

<script>

    export default {
        name: "asideNav",
        props: {
            logoTextShow: Boolean
        },
        methods: {
            handleOpen(key, keyPath) {
                console.log(key, keyPath);
            },
            handleClose(key, keyPath) {
                console.log(key, keyPath);
            }
        }
    }
</script>
