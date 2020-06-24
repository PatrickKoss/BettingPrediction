import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Login from "../views/Account/Login";
import Register from "../views/Account/Register";
import Account from "../views/Account/Account";
import CSGOUpcommingMatches from "../views/CSGO/CSGOUpcommingMatches";
import CSGOTeamView from "../views/CSGO/CSGOTeamView";
import CSGOPredictionView from "../views/CSGO/CSGOPredictionView"

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
    path: "/csgo/upcomingMatches",
    name: 'CSGO',
    component: CSGOUpcommingMatches,
    icon: "mdi-plus-box",
    loggedIn: 1
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
    path: "/csgo/teams/:id",
    name: 'CSGOTeamView',
    component: CSGOTeamView,
    icon: "mdi-plus-box",
    loggedIn: -2
  },
  {
    path: "/csgo/teams/:id/:id2",
    name: 'CSGOTeamViewBoth',
    component: CSGOTeamView,
    icon: "mdi-plus-box",
    loggedIn: -2
  },
  {
    path: "/csgo/matchResult",
    name: 'CSGOMatchesResult',
    component: CSGOUpcommingMatches,
    icon: "mdi-plus-box",
    loggedIn: -2
  },
  {
    path: "/csgo/statistics",
    name: 'CSGOStatistics',
    component: CSGOUpcommingMatches,
    icon: "mdi-plus-box",
    loggedIn: -2
  },
  {
    path: "/csgo/prediction/",
    name: 'CSGOPrediction',
    component: CSGOPredictionView,
    icon: "mdi-plus-box",
    loggedIn: -2
  },
  {
    path: "/csgo/prediction/:team1-:mode-:team2",
    name: 'CSGOPredictionPreSet',
    component: CSGOPredictionView,
    icon: "mdi-plus-box",
    loggedIn: -2
  },
];

const router = new VueRouter({
  routes
});

export default router
