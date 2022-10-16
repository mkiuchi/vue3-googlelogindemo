import { createApp } from 'vue'
import App from './App.vue'
import MainPage from './components/MainPage.vue'
import LoginDialog1 from './components/LoginDialog1.vue'
import LoginDialog2 from './components/LoginDialog2.vue'
import vuetify from './plugins/vuetify'
import { createRouter, createWebHistory } from 'vue-router'
import vue3GoogleLogin from 'vue3-google-login'
import { createPinia } from 'pinia'
import { globalCookiesConfig } from "vue3-cookies"
import { AppOptions } from '@/appoptions'

globalCookiesConfig({
  expireTimes: "7d"
})

const pinia = createPinia()

const routes = [
  { path: '/', name: 'MainPage', component: MainPage },
  { path: '/login1', name: 'LoginDialog1', component: LoginDialog1 },
  { path: '/login2', name: 'LoginDialog2', component: LoginDialog2 },
]

const router = createRouter({
  history: createWebHistory(),
  routes, // short for `routes: routes`
})

createApp(App)
  .use(pinia)
  .use(vuetify)
  .use(router)
  .use(vue3GoogleLogin, {
    clientId: AppOptions().googleClientId,
    scope: 'email profile openid'
  })
  .mount('#app')
