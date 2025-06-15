<template>
  <div class="poc-manage">
    <h1>PocManage</h1>
    <p>This is the PocManage component.</p>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'PocManage',
  data() {
    return {
      // Define your component data here
    };
  },
  methods: {
    async loadDataNew() {
      try {
        const response = await axios.get('/api/getPocTable')
        console.log(response.data)
      } catch (error) {
        console.error('发生错误:', error);
      }
    },
  },
  mounted() {
    this.loadDataNew();
    // Code to run when the component is mounted
  }
};

</script>