import Vue from 'vue'
import Router from 'vue-router';
import router from '@/router/index.js'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import 'element-ui/lib/theme-chalk/icon.css';

import VueCodemirror from 'vue-codemirror'; // 引入 vue-codemirror
// import XLSX from 'xlsx';
// 引入 Codemirror 相关依赖
// import Codemirror from 'vue-codemirror';  // 引入 vue-codemirror
import 'codemirror/lib/codemirror.css';   // Codemirror 核心样式
import 'codemirror/mode/python/python.js';   // Python 语言模式
import 'codemirror/theme/material.css';   // Codemirror 主题


// 注册 Codemirror 作为 Vue 插件
// Vue.use(Codemirror);

Vue.use(ElementUI);
Vue.use(Router);
Vue.use(VueCodemirror); // 注册插件


Vue.config.productionTip = false

export const EventBus = new Vue()

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
