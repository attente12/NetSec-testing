//引入依赖及组件
import Vue from 'vue'
import Router from 'vue-router' //引入vue-router
Vue.use(Router)					//注册vue-router

import pagesOne from '../components/pagesOne'
import pagesTwo from '../components/pagesTwo'
import baseCheck from '../views/baseCheck.vue';
import CheckHome from '../views/baseCheckHome.vue';
import pocManage from '../views/pocManage'
import home from '../views/home'
import pocScanner from '../views/pocScanner.vue'
import pocVerify from "@/views/pocVerify.vue";
import weakPasswordDetect from "../views/weakPasswordDetect.vue"
import classifyProtect from "../views/classifyProtect.vue"
import CVELibrary from "@/views/CVELibrary.vue";
import toVerify from "@/views/toVerify.vue";
// import BaseCheck_copy from '../views/baseCheck_copy.vue'


export default new Router({
    routes: [
        {
            path: '/',
            name: 'home',
            component: home,
        },
        {
            path: '/baseCheckHome',
            name: 'baseCheckHome',
            component: CheckHome,
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
            meta: { title: '等级保护测评' }
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

    ]
})
