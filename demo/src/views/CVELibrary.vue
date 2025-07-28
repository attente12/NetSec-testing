<template>
  <div>
    <p class="refresh-tip">若刷新失败请尝试 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>R</kbd> 强制刷新</p>
    <div class="iframe-wrapper">
      <iframe :src="iframeUrl" width="100%" height="760px" frameborder="0" @load="onIframeLoad" v-if="iframeKey">
      </iframe>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      iframeKey: 1,
      baseUrl: 'http://192.168.0.129:5000/'
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