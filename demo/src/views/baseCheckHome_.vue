<template>
    <div>
        <button @click="showPopup = true">打开弹窗</button>

        <!-- 遮罩层 -->
        <div v-if="showPopup" class="overlay" @click="showPopup = false"></div>

        <!-- 弹出框 -->
        <div v-if="showPopup" class="popup">
            <BaseCheck_copy></BaseCheck_copy>
            <button @click="showPopup = false">关闭</button>
        </div>
    </div>
</template>

<script>
import BaseCheck_copy from './baseCheck_copy.vue';

export default {
    components: {
        BaseCheck_copy
    },
    props: {},
    data() {
        return {
            showPopup: false
        };
    },
    methods: {
        closePopup(event) {
            if (event.key === 'Escape') {
                this.showPopup = false; // 隐藏PDF相关内容
            }
        }// 这里可以添加其他方法
    },
    mounted() {
        // 监听键盘事件
        window.addEventListener('keydown', this.closePopup);
    },
    beforeUnMount() {
        // 移除键盘事件监听
        window.removeEventListener('keydown', this.closePopup);
    }
};
</script>

<style>
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
}

.popup {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    z-index: 1001;
}
</style>
