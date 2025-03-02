<template>
  <div>
    <p class="refresh-tip">若刷新失败请尝试ctrl+shift+R</p>
    <div class="iframe-wrapper">
      <iframe
          :src="iframeUrl"
          width="100%"
          height="760px"
          frameborder="0"
          @load="onIframeLoad"
          v-if="iframeKey">
      </iframe>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      iframeKey: 1,
      baseUrl: 'http://10.9.130.140:5000/'
    }
  },
  computed: {
    iframeUrl() {
      return `${this.baseUrl}?cacheBuster=${Date.now()}`
    }
  },
  methods: {
    refreshIframe() {
      this.iframeKey += 1
    },
    onIframeLoad() {
      // 注入禁用缓存的JavaScript到iframe
      try {
        const iframeDoc = this.$refs.iframe.contentDocument || this.$refs.iframe.contentWindow.document
        const script = iframeDoc.createElement('script')
        script.text = `
          if(performance) {
            performance.mark('force_no_cache');
            window.addEventListener('beforeunload', () => {
              localStorage.removeItem('cachedData');
            });
          }
        `
        iframeDoc.head.appendChild(script)
      } catch (e) {
        console.log('跨域限制无法操作iframe内容')
      }
    }
  }
}
</script>




<!--<template>-->
<!--  <div>-->
<!--    <p class="refresh-tip">若刷新失败请尝试ctrl+shift+R</p>-->
<!--    <iframe-->
<!--        src="http://10.9.130.77:5000/"-->
<!--        width="100%"-->
<!--        height="760px"-->
<!--        frameborder="0">-->
<!--    </iframe>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  name: 'HomePage'-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.refresh-tip {-->
<!--  font-size: 12px;-->
<!--  color: #666;-->
<!--  margin-bottom: 5px;-->
<!--  text-align: left;-->
<!--}-->
<!--/* 如果你需要调整 iframe 的样式，可以在这里修改 */-->
<!--</style>-->

<!--<template>-->
<!--  <div>-->
<!--    &lt;!&ndash;    <h1>这是首页</h1>&ndash;&gt;-->
<!--    <iframe-->
<!--        src="http://10.9.130.77:5000/"-->
<!--        width="100%"-->
<!--        height="760px"-->
<!--        frameborder="0">-->
<!--    </iframe>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  name: 'HomePage'-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--/* 如果你需要调整 iframe 的样式，可以在这里修改 */-->
<!--</style>-->
