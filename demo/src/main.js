import Vue from 'vue'
import router from './router/index.js'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import 'element-ui/lib/theme-chalk/icon.css';

// 导入自定义字体CSS (添加这一行)
// import '@/assets/custom-fonts.css';

import VueCodemirror from 'vue-codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/mode/python/python.js';
import 'codemirror/theme/material.css';

import { store } from './store/index.js'; // 引入 Vuex store
import axios from './api/axios/index.js'; // 引入自定义 Axios 实例

Vue.use(ElementUI);
Vue.use(VueCodemirror);

Vue.config.productionTip = false
Vue.prototype.$axios = axios

router.beforeEach((to, from, next) => {
  // 如果路由有 meta.title，则设置为页面标题
  if (to.meta.title) {
    document.title = to.meta.title;
  } else {
    // 默认标题
    document.title = '网络安全测试平台';
  }
  next();
});


new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app')




// import Vue from 'vue'
// import Router from 'vue-router';
// import router from '@/router/index.js'
// import App from './App.vue'
// import ElementUI from 'element-ui';
// import 'element-ui/lib/theme-chalk/index.css';
// import 'element-ui/lib/theme-chalk/icon.css';
//
// import VueCodemirror from 'vue-codemirror'; // 引入 vue-codemirror
// // import XLSX from 'xlsx';
// // 引入 Codemirror 相关依赖
// // import Codemirror from 'vue-codemirror';  // 引入 vue-codemirror
// import 'codemirror/lib/codemirror.css';   // Codemirror 核心样式
// import 'codemirror/mode/python/python.js';   // Python 语言模式
// import 'codemirror/theme/material.css';   // Codemirror 主题
//
//
// // 注册 Codemirror 作为 Vue 插件
// // Vue.use(Codemirror);
//
// Vue.use(ElementUI);
// Vue.use(Router);
// Vue.use(VueCodemirror); // 注册插件
//
//
// Vue.config.productionTip = false
//
// new Vue({
//   router,
//   render: h => h(App),
// }).$mount('#app')
