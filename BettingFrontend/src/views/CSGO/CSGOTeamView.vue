<template>
  <v-card :dark="state.dark">
    <h2>Team: {{team.name}}</h2>
    <v-row no-gutters style="margin-left: 10px; margin-top: 15px">
      <label>
        <pre>Winning Percentage: </pre>
      </label> <span>{{Math.round(team.winning_percentage * 100)}}%</span>
    </v-row>
    <v-row no-gutters>
      <v-data-table
              :headers="teamHeader"
              :items="playerItems"
              :items-per-page="5"
              hide-default-footer
      />
    </v-row>
  </v-card>
</template>

<script>
  import {Component, Vue} from 'vue-property-decorator';
  import {CSGORestClient} from "../../model/CSGORestClient";

  @Component
  class CSGOTeamView extends Vue {
    state = this.$store.state;
    team = {};
    playerItems = [];
    teamHeader = [{text: "Name", align: 'start', sortable: false, value: 'name'}, {
      text: "ADR",
      align: 'start',
      sortable: false,
      value: 'adr'
    }, {text: "KPR", align: 'start', sortable: false, value: 'kpr'}, {
      text: "DPR",
      align: 'start',
      sortable: false,
      value: 'dpr'
    }, {text: "Impact", align: 'start', sortable: false, value: 'impact'}, {
      text: "Kast",
      align: 'start',
      sortable: false,
      value: 'kast'
    }]

    async mounted() {
      let id = this.$route.params.id;
      let response = await new CSGORestClient().getTeam(id);
      this.team = response.team;
      this.playerItems = [this.team.Player_1, this.team.Player_2, this.team.Player_3, this.team.Player_4, this.team.Player_5]
      this.playerItems.forEach(player => {
        player.kast = (player.kast * 100) + "%";
      })
    }
  }

  export default CSGOTeamView
</script>
<style scoped>
</style>
