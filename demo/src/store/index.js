//vuex用于管理整个项目的全局变量
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export const store = new Vuex.Store({
    state: {
        message: {}
    },
    mutations: {
        updateMessage(state, payload) {
            state.message = payload;
        },
    },
    actions: {
        asyncUpdateMessage({ commit }, payload) {
            setTimeout(() => {
                commit('updateMessage', payload);
            }, 1000);
        },
    },
    getters: {
        message: state => state.message,
    },
});
