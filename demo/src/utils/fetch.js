// src/utils/fetch.js
import { getCookie } from './cookie';

export function neoFetch(url, options = {}) {
    const username = getCookie('username');
    const headers = {
        ...options.headers,
        'Content-Type': 'application/json',
    };

    if (username) {
        headers['Authorization'] = `Bearer ${username}`; // 添加到请求头
    }

    return fetch(url, {
        ...options,
        headers,
    });
}