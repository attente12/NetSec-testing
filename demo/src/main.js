import Vue from 'vue'
import Router from 'vue-router';
import router from '@/router/index.js'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
// import XLSX from 'xlsx';

Vue.use(ElementUI);
Vue.use(Router);


Vue.config.productionTip = false

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
