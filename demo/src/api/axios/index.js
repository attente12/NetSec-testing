import axios from 'axios';
import { getCookie } from '../../utils/cookie';

const instance = axios.create({
    baseURL: 'http://192.168.0.129:8081', // 基础URL
    timeout: 10000, // 请求超时时间（毫秒）
});

// 请求拦截器
instance.interceptors.request.use(
    config => {
        const username = getCookie('username');
        if (username) {
            config.headers['Authorization'] = `Bearer ${username}`;
        }
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