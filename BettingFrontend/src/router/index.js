import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Login from "../views/Login";
import Register from "../views/Register";
import Account from "../views/Account";
import CSGOUpcommingMatches from "../views/CSGOUpcommingMatches";

Vue.use(VueRouter);

export const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    icon: "mdi-home",
    loggedIn: 0
  },
  {
    path: "/account",
    name: 'Account',
    component: Account,
    icon: "mdi-account",
    loggedIn: 1
  },
  {
    path: "/login",
    name: 'Login',
    component: Login,
    icon: "mdi-login",
    loggedIn: -1
  },
  {
    path: "/logout",
    name: 'Logout',
    component: Home,
    icon: "mdi-logout",
    loggedIn: 1
  },
  {
    path: "/register",
    name: 'Register',
    component: Register,
    icon: "mdi-plus-box",
    loggedIn: -2
  },
  {
    path: "/csgo-upcomingMatches",
    name: 'CSGOUpcomingMatches',
    component: CSGOUpcommingMatches,
    icon: "mdi-plus-box",
    loggedIn: -2
  },
];

const router = new VueRouter({
  routes
});

export default router
