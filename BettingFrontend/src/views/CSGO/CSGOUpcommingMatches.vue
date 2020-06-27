<template>
  <v-card :dark="state.dark">
    <v-tabs
            :dark="state.dark"
            background-color="transparent"
            grow
            v-model="tab"
    >
      <v-tab :key="t" v-for="t in tabs">
        {{t}}
      </v-tab>
    </v-tabs>

    <v-tabs-items v-model="tab">
      <v-tab-item>
        <CSGOUpcomingMatchesTable/>
      </v-tab-item>
      <v-tab-item>
        <CSGOMatchesResultTable/>
      </v-tab-item>
      <v-tab-item>
        <CSGOStatisticsTable/>
      </v-tab-item>
    </v-tabs-items>
  </v-card>
</template>

<script>
  import {Component, Vue, Watch} from 'vue-property-decorator';
  import CSGOStatisticsTable from '../../components/CSGO/CSGOStatisticsTable';
  import CSGOMatchesResultTable from '../../components/CSGO/CSGOMatchesResultTable';
  import CSGOUpcomingMatchesTable from '../../components/CSGO/CSGOUpcomingMatchesTable';

  @Component({
    components: {
      CSGOStatisticsTable,
      CSGOMatchesResultTable,
      CSGOUpcomingMatchesTable,
    }
  })
  class CSGOUpcommingMatches extends Vue {
    state = this.$store.state;
    tab = 0;
    tabs = ['Upcoming Matches', 'Matches Result', 'Statistics'];

    mounted() {
      if (this.$route.path === "/csgo/matchResult") {
        this.tab = 1;
      }
      if (this.$route.path === "/csgo/statistics") {
        this.tab = 2;
      }
    }

    @Watch("tab", {immediate: true, deep: true})
    __watch_tab() {
      if (this.tab === 0 && this.$route.path !== "/csgo/upcomingMatches") {
        this.$router.push(`/csgo/upcomingMatches`);
      } else if (this.tab === 1 && this.$route.path !== "/csgo/matchResult") {
        this.$router.push(`/csgo/matchResult`);
      } else if (this.tab === 2 && this.$route.path !== "/csgo/statistics") this.$router.push(`/csgo/statistics`);
    }
  }

  export default CSGOUpcommingMatches
</script>
<style scoped>
</style>
