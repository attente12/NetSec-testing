import axios from 'axios';

// 创建 Axios 实例
const instance = axios.create({
    timeout: 10000, // 请求超时时间（毫秒）
});

// 请求拦截器
instance.interceptors.request.use(
    config => {
        // 可在此添加请求前的处理，例如添加 token
        // config.headers.Authorization = `Bearer ${token}`;
        return config;
    },
    error => Promise.reject(error)
);

// 响应拦截器
instance.interceptors.response.use(
    response => response.data, // 直接返回数据
    error => {
        // 处理错误，例如提示用户
        console.error('请求错误:', error.message);
        return Promise.reject(error);
    }
);

export default instance;