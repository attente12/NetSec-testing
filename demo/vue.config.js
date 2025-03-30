module.exports = {
    devServer: {
        proxy: {
            //定义需要代理的请求路径，所有以 /api 开头的请求都会被代理
            '/api': {
                // 代理的目标地址
                target: 'http://192.168.0.129:8081',
                changeOrigin: true,//代理服务器会把请求头中的Host字段改为目标地址
                pathRewrite: { '^/api': '' }
            }
        }
    }
};
