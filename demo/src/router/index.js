//引入依赖及组件
import Vue from 'vue'
import Router from 'vue-router' //引入vue-router
Vue.use(Router)					//注册vue-router

import pagesOne from '../components/pagesOne'
import pagesTwo from '../components/pagesTwo'
import baseCheck from '../components/baseCheck.vue';
import home from '../views/home.vue';


export default new Router({
    routes: [
        {
            path: '/',
            name: 'home',
            component: home
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
            component: baseCheck
        }
    ]
})
