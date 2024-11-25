<template>
    <div class="aside" style="height: 100%; width: 100%;">
        <el-row class="tac" style="height: 100%; width: 100%;">
            <el-col :span="12" style="height: 100%; width: 100%;">
                <el-menu
                    :default-active="activeMenu"
                    :default-openeds="openeds"
                    unique-opened
                    router
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

                    <el-menu-item index="/">
                        <i class="el-icon-menu"></i>
                        <span slot="title">首页</span>
                    </el-menu-item>

                    <el-submenu index="1">
                        <template slot="title">
                            <i class="el-icon-location"></i>
                            <span>安全基线检测</span>
                        </template>
                        <el-menu-item-group>
                            <el-menu-item index="/baseCheckHome">基线检测启动</el-menu-item>
                            <el-menu-item index="/baseCheck">基线检测报告</el-menu-item>
                        </el-menu-item-group>
                    </el-submenu>

                    <el-submenu index="2">
                        <template slot="title">
                            <i class="el-icon-bangzhu"></i>
                            <span>安全风险评估</span>
                        </template>
                        <el-menu-item-group>
                            <el-menu-item index="/CVELibrary">CVE库</el-menu-item>
                            <el-menu-item index="/pocManage">POC管理</el-menu-item>
                            <el-menu-item index="/pocScanner">漏洞扫描</el-menu-item>
                            <el-menu-item index="/pluginScan">插件化扫描</el-menu-item>
                        </el-menu-item-group>
                    </el-submenu>

                  <el-menu-item index="/weakPasswordDetect">
                    <i class="el-icon-attract"></i>
                    <span slot="title">弱口令检测</span>
                  </el-menu-item>

                  <el-menu-item index="/classifyProtect">
                    <i class="el-icon-share"></i>
                    <span slot="title">等级保护测评</span>
                  </el-menu-item>

                  <el-menu-item index="/assetManage">
                    <i class="el-icon-s-help"></i>
                    <span slot="title">资产管理</span>
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
        data() {
          return {
            activeMenu: '',
            openeds: [], // 当前展开的 sub-menu 的 index 数组
          }
        },
        watch: {
          $route: {
            handler(route) {
              // 处理特殊路由
              this.handleRoute(route);
            },
            immediate: true
          }
        },
        created() {
          // 初始化激活菜单项
          this.handleRoute(this.$route);
        },
        methods: {
          handleRoute(route) {
            const path = route.path;
            // 设置当前激活的菜单项
            this.activeMenu = path;

            // 根据当前路径决定要展开哪些子菜单
            if (path.startsWith('/baseCheckHome') || path.startsWith('/baseCheck')) {
              this.openeds = ['1'];
            } else if (['/CVELibrary', '/pocManage', '/pocScanner', '/pluginScan'].some(p => path.startsWith(p))) {
              this.openeds = ['2'];
            }
          },
            handleOpen(key, keyPath) {
                console.log(key, keyPath);
            },
            handleClose(key, keyPath) {
                console.log(key, keyPath);
            }
        }
    }
</script>



<!--<template>-->
<!--  <div class="aside" style="height: 100%; width: 100%;">-->
<!--    <el-row class="tac" style="height: 100%; width: 100%;">-->
<!--      <el-col :span="12" style="height: 100%; width: 100%;">-->
<!--        <el-menu-->
<!--            default-active="this.$route.path" router-->
<!--            class="el-menu-vertical-demo"-->
<!--            @open="handleOpen"-->
<!--            @close="handleClose"-->
<!--            background-color="#545c64"-->
<!--            text-color="#fff"-->
<!--            active-text-color="#ffd04b"-->
<!--            style="height: 100%; width: 100%;">-->
<!--          <div style="height: 60px; line-height: 60px; text-align: center">-->
<!--            <img src="../assets/logo.png" alt="" style="width: 20px; position: relative; top: 5px; right: 5px">-->
<!--            <b style="color: white">网络安全测试平台</b>-->
<!--          </div>-->

<!--          <el-menu-item index="/">-->
<!--            <i class="el-icon-menu"></i>-->
<!--            <span slot="title">首页</span>-->
<!--          </el-menu-item>-->

<!--          <el-submenu index="1">-->
<!--            <template slot="title">-->
<!--              <i class="el-icon-location"></i>-->
<!--              <span>安全基线检测</span>-->
<!--            </template>-->
<!--            <el-menu-item-group>-->
<!--              <el-menu-item index="/baseCheckHome">基线检测启动</el-menu-item>-->
<!--              <el-menu-item index="/baseCheck">基线检测报告</el-menu-item>-->
<!--            </el-menu-item-group>-->
<!--          </el-submenu>-->

<!--          <el-submenu index="2">-->
<!--            <template slot="title">-->
<!--              <i class="el-icon-bangzhu"></i>-->
<!--              <span>安全风险评估</span>-->
<!--            </template>-->
<!--            <el-menu-item-group>-->
<!--              <el-menu-item index="/CVELibrary">CVE库</el-menu-item>-->
<!--              <el-menu-item index="/pocManage">POC管理</el-menu-item>-->
<!--              <el-menu-item index="/pocScanner">漏洞扫描</el-menu-item>-->
<!--              <el-menu-item index="/pluginScan">插件化扫描</el-menu-item>-->
<!--              <el-menu-item index="/assetManage">资产管理</el-menu-item>-->
<!--            </el-menu-item-group>-->
<!--          </el-submenu>-->

<!--          <el-menu-item index="/weakPasswordDetect">-->
<!--            <i class="el-icon-attract"></i>-->
<!--            <span slot="title">弱口令检测</span>-->
<!--          </el-menu-item>-->

<!--          <el-menu-item index="/classifyProtect">-->
<!--            <i class="el-icon-share"></i>-->
<!--            <span slot="title">等级保护测评</span>-->
<!--          </el-menu-item>-->

<!--        </el-menu>-->
<!--      </el-col>-->
<!--    </el-row>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->

<!--export default {-->
<!--  name: "asideNav",-->
<!--  props: {-->
<!--    logoTextShow: Boolean-->
<!--  },-->
<!--  methods: {-->
<!--    handleOpen(key, keyPath) {-->
<!--      console.log(key, keyPath);-->
<!--    },-->
<!--    handleClose(key, keyPath) {-->
<!--      console.log(key, keyPath);-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->
