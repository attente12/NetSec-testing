<template>
    <div>
        <button @click="showPopup = true">打开弹窗</button>

        <!-- 遮罩层 -->
        <div v-if="showPopup" class="overlay" @click="showPopup = false"></div>

        <!-- 弹出框 -->
        <div v-if="showPopup" class="popup">
            <h2>弹出页面</h2>
            <p>这里是弹出层内容。</p>
            <button @click="showPopup = false">关闭</button>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            showPopup: false
        };
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
