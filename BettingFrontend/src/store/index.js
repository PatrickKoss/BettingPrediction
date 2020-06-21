import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    drawer: false,
    message: {messageType: "", message: ""},
    token: "",
    dark: false,
    user: {username: "", email: ""},
  },
  mutations: {
  },
  actions: {
  },
  modules: {
  }
})
