import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Login from "../views/Account/Login";
import Account from "../views/Account/Account";
import CSGOUpcommingMatches from "../views/CSGO/CSGOUpcommingMatches";
import CSGOTeamView from "../views/CSGO/CSGOTeamView";
import CSGOPredictionView from "../views/CSGO/CSGOPredictionView";
import {CSGORestClient} from "../model/CSGORestClient";
import AppStore from "../store/index";
import {UserRestClient} from "../model/UserRestClient";

Vue.use(VueRouter);

async function checkPermissions(next, response, from) {
  if (response.status === 401) {
    AppStore.state.message = response.message;
    localStorage.token = undefined;
    AppStore.state.token = "";
    if (from.name !== "Login") next({name: 'Login'});
  }
  else if (response.status === 403) {
    AppStore.state.message = response.message;
    if (from.name !== "Home") next({name: 'Home'});
  } else {
    next();
  }
}

export const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    icon: "mdi-home",
    loggedIn: 1,
    beforeEnter: async (to, from, next) => {
      if (localStorage.token !== undefined) AppStore.state.token = localStorage.token;
      await checkPermissions(next, await new UserRestClient().getAuthenticated(), from);
    }
  },
  {
    path: "/csgo/upcomingMatches",
    name: 'CSGO',
    component: CSGOUpcommingMatches,
    icon: "mdi-plus-box",
    loggedIn: 1,
    beforeEnter: async (to, from, next) => {
      if (localStorage.token !== undefined) AppStore.state.token = localStorage.token;
      await checkPermissions(next, await new CSGORestClient().checkPermissions(), from);
    }
  },
  {
    path: "/account",
    name: 'Account',
    component: Account,
    icon: "mdi-account",
    loggedIn: 1,
    beforeEnter: async (to, from, next) => {
      if (localStorage.token !== undefined) AppStore.state.token = localStorage.token;
      await checkPermissions(next, await new UserRestClient().getAuthenticated(), from);
    }
  },
  {
    path: "/login",
    name: 'Login',
    component: Login,
    icon: "mdi-login",
    loggedIn: -1,
  },
  {
    path: "/logout",
    name: 'Logout',
    component: Home,
    icon: "mdi-logout",
    loggedIn: 1
  },
/*  {
    path: "/register",
    name: 'Register',
    component: Register,
    icon: "mdi-plus-box",
    loggedIn: -2
  },*/
  {
    path: "/csgo/teams/:id",
    name: 'CSGOTeamView',
    component: CSGOTeamView,
    icon: "mdi-plus-box",
    loggedIn: -2,
    beforeEnter: async (to, from, next) => {
      if (localStorage.token !== undefined) AppStore.state.token = localStorage.token;
      await checkPermissions(next, await new CSGORestClient().checkPermissions(), from);
    }
  },
  {
    path: "/csgo/teams/:id/:id2",
    name: 'CSGOTeamViewBoth',
    component: CSGOTeamView,
    icon: "mdi-plus-box",
    loggedIn: -2,
    beforeEnter: async (to, from, next) => {
      if (localStorage.token !== undefined) AppStore.state.token = localStorage.token;
      await checkPermissions(next, await new CSGORestClient().checkPermissions(), from);
    }
  },
  {
    path: "/csgo/matchResult",
    name: 'CSGOMatchesResult',
    component: CSGOUpcommingMatches,
    icon: "mdi-plus-box",
    loggedIn: -2,
    beforeEnter: async (to, from, next) => {
      if (localStorage.token !== undefined) AppStore.state.token = localStorage.token;
      await checkPermissions(next, await new CSGORestClient().checkPermissions(), from);
    }
  },
  {
    path: "/csgo/statistics",
    name: 'CSGOStatistics',
    component: CSGOUpcommingMatches,
    icon: "mdi-plus-box",
    loggedIn: -2,
    beforeEnter: async (to, from, next) => {
      if (localStorage.token !== undefined) AppStore.state.token = localStorage.token;
      await checkPermissions(next, await new CSGORestClient().checkPermissions(), from);
    }
  },
  {
    path: "/csgo/prediction/",
    name: 'CSGOPrediction',
    component: CSGOPredictionView,
    icon: "mdi-plus-box",
    loggedIn: -2,
    beforeEnter: async (to, from, next) => {
      if (localStorage.token !== undefined) AppStore.state.token = localStorage.token;
      await checkPermissions(next, await new CSGORestClient().checkPermissions(), from);
    }
  },
  {
    path: "/csgo/prediction/:team1-:mode-:team2",
    name: 'CSGOPredictionPreSet',
    component: CSGOPredictionView,
    icon: "mdi-plus-box",
    loggedIn: -2,
    beforeEnter: async (to, from, next) => {
      if (localStorage.token !== undefined) AppStore.state.token = localStorage.token;
      await checkPermissions(next, await new CSGORestClient().checkPermissions(), from);
    }
  },
];

const router = new VueRouter({
  routes
});

export default router
