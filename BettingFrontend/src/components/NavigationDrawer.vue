<template>
  <span>
    <v-navigation-drawer
            :dark="state.dark"
            absolute
            left
            temporary
            v-model="state.drawer"
    >
      <v-list
              dense
              nav
      >
        <v-list-item-group :key="route.name" v-for="route in routes">
          <v-list-item @click="navigateToRoute(route.path)">
            <v-list-item-icon>
              <v-icon>{{route.icon}}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{route.name}}</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
  </span>
</template>

<script>
  import {Component, Vue, Watch} from 'vue-property-decorator'
  import {routes} from "../router";
  import {logout} from "../model/Helper";

  @Component
  class NavigationDrawer extends Vue {
    drawer = this.$store.state.drawer;
    state = this.$store.state;
    routes = routes;

    /**
     * each navigation item has a route. Navigate to the route if the item is clicked.
     * @param route
     * @returns {Promise<void>}
     */
    async navigateToRoute(route) {
      if (route !== "/logout") {
        if (this.$router.currentRoute.path !== route) await this.$router.push(route)
      } else {
        await logout();
      }
    }

    /**
     * set up the routes based if the user is logged in or not. Some route shouldn´t also be viewed on the drawer.
     * @private
     */
    @Watch("state.token", {immediate: true, deep: true})
    __initRoutes() {
      this.routes = routes;
      let loggedInRoutes = [];
      let notLoggedInRoutes = [];
      this.routes.forEach(route => {
        if (route.loggedIn === 0 || route.loggedIn === 1) loggedInRoutes.push(route);
        if (route.loggedIn === 0 || route.loggedIn === -1) notLoggedInRoutes.push(route);
      });
      if (this.state.token.toString() !== "") {
        this.routes = loggedInRoutes.slice(0)
      } else {
        this.routes = notLoggedInRoutes.slice(0)
      }
    }
  }

  export default NavigationDrawer
</script>
<style scoped>
</style>
