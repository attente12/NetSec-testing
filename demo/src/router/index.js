//引入依赖及组件
import Vue from 'vue'
import Router from 'vue-router' //引入vue-router
Vue.use(Router)					//注册vue-router

import pagesOne from '../components/pagesOne'
import pagesTwo from '../components/pagesTwo'
import baseCheck from '../views/baseCheck.vue';
import homeCheckHome from '../views/baseCheckHome.vue';
import pocManage from '../views/pocManage'
import home from '../views/home'
import pocScanner from '../views/pocScanner.vue'
import pocVerify from "@/views/pocVerify.vue";
import weakPasswordDetect from "../views/weakPasswordDetect.vue"
import classifyProtect from "../views/classifyProtect.vue"
import CVELibrary from "@/views/CVELibrary.vue";
import toVerify from "@/views/toVerify.vue";
import pluginScan from "@/views/pluginScan.vue";
import assetManage from "@/views/assetManage.vue";
import hostDiscovery from "@/views/hostDiscovery.vue";
import test from "@/views/test.vue";
import tempBaseCheck from "@/views/tempBaseCheck.vue";
import classifyProtectHome from "@/views/classifyProtectHome.vue";
import tempClassifyProtect from "@/views/tempClassifyProtect.vue";
import vulTypeManage from "@/views/vulTypeManage.vue";
import baseCheckW from '../views/baseCheckW.vue'


export default new Router({
    routes: [
        {
            path: '/',
            name: 'home',
            component: home,
        },
        {
            path: '/hostDiscovery',
            name: 'hostDiscovery',
            component: hostDiscovery,
            meta: { title: '主机发现' }
        },
        {
            path: '/baseCheckHome',
            name: 'baseCheckHome',
            component: homeCheckHome,
            meta: { title: '基线检测' }
        },
        {
            path: '/pagesOne',
            name: 'pagesOne',
            component: pagesOne
        },
        {
            path: '/pagesTwo',
            name: 'pagesTwo',
            component: pagesTwo
        },
        {
            path: '/baseCheck',
            name: 'baseCheck',
            component: baseCheck,
            meta: { title: '基线检测结果' }
        },
        {
            path: '/pocManage',
            name: 'pocManage',
            component: pocManage,
            meta: { title: 'POC管理' }
        },
        {
            path: '/pocScanner',
            name: 'pocScanner',
            component: pocScanner,
            meta: { title: '漏洞扫描' }
        },
        {
            path: '/pocScanner/pocVerify',
            name: 'pocVerify',
            component: pocVerify,
            meta: { title: 'POC验证' }
        },
        {
            path: '/weakPasswordDetect',
            name: 'weakPasswordDetect',
            component: weakPasswordDetect,
            meta: { title: '弱口令检测' }
        },
        {
            path: '/classifyProtect',
            name: 'classifyProtect',
            component: classifyProtect,
            meta: { title: '测评历史' }
        },
        {
            path: '/CVELibrary',
            name: 'CVELibrary',
            component: CVELibrary,
            meta: { title: 'CVE库' }
        },
        {
            path: '/toVerify',
            name: 'toVerify',
            component: toVerify,
            meta: { title: '单个漏洞验证' }
        },
        {
            path: '/pluginScan',
            name: 'pluginScan',
            component: pluginScan,
            meta: { title: '插件化扫描' }
        },
        {
            path: '/assetManage',
            name: 'assetManage',
            component: assetManage,
            meta: { title: '资产管理' }
        },
        {
            path: '/test',
            name: 'test',
            component: test,
            meta: { title: '测试' }
        },
        {
            path: '/tempBaseCheck',
            name: 'tempBaseCheck',
            component: tempBaseCheck,
            meta: { title: '检测结果' }
        },
        {
            path: '/classifyProtectHome',
            name: 'classifyProtectHome',
            component: classifyProtectHome,
            meta: { title: '等级保护测评' }
        },
        {
            path: '/tempClassifyProtect',
            name: 'tempClassifyProtect',
            component: tempClassifyProtect,
            meta: { title: '等保测评结果' }
        },
        {
            path: '/vulTypeManage',
            name: 'vulTypeManage',
            component: vulTypeManage,
            meta: { title: '漏洞类型管理' }
        },
        {
            path: '/baseCheckW',
            name: 'baseCheckW',
            component: baseCheckW,
            meta: { title: 'Windows基线检测结果' }
        }

    ]
})
