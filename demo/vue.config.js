module.exports = {
    devServer: {
        proxy: {
            //定义需要代理的请求路径，所有以 /api 开头的请求都会被代理
            '/api': {
                // 代理的目标地址
                target: 'http://172.20.10.2:8081',
                changeOrigin: true,//代理服务器会把请求头中的Host字段改为目标地址
                pathRewrite: { '^/api': '' }
            }
        }
    },
    // 添加 chainWebpack 配置来处理字体文件
    // chainWebpack: config => {
    //     // 处理字体文件
    //     config.module
    //         .rule('fonts')
    //         .test(/\.(woff2?|eot|ttf|otf)(\?.*)?$/)
    //         .use('url-loader')
    //         .loader('url-loader')
    //         .options({
    //             limit: 10240,
    //             name: 'fonts/[name].[hash:8].[ext]'
    //         });
    // }
};


// module.exports = {
//     devServer: {
//         proxy: {
//             //定义需要代理的请求路径，所有以 /api 开头的请求都会被代理
//             '/api': {
//                 // 代理的目标地址
//                 target: 'http://10.9.130.67:8081',
//                 changeOrigin: true,//代理服务器会把请求头中的Host字段改为目标地址
//                 pathRewrite: { '^/api': '' }
//             }
//         }
//     }
// };
