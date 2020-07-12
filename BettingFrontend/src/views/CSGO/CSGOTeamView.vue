<template>
  <v-card :dark="state.dark">
    <v-row no-gutters v-if="loadingTeams">
      <v-progress-linear
              indeterminate
      />
    </v-row>
    <v-row no-gutters v-if="team !== null">
      <v-col :sm="6">
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
      </v-col>
      <v-col :sm="6" v-if="team2 !== null">
        <h2>Team: {{team2.name}}</h2>
        <v-row no-gutters style="margin-left: 10px; margin-top: 15px">
          <label>
            <pre>Winning Percentage: </pre>
          </label> <span>{{Math.round(team2.winning_percentage * 100)}}%</span>
        </v-row>
        <v-row no-gutters>
          <v-data-table
                  :headers="teamHeader"
                  :items="playerItems2"
                  :items-per-page="5"
                  hide-default-footer
          />
        </v-row>
      </v-col>
    </v-row>
    <v-row no-gutters style="margin-top: 15px; margin-left: 10px; padding-bottom: 10px">
      <v-btn @click="goBack()" color="primary" dark rounded>
        <v-icon left>mdi-arrow-left</v-icon>
        Go back
      </v-btn>
    </v-row>
  </v-card>
</template>

<script>
  import {Component, Vue} from 'vue-property-decorator';
  import {CSGORestClient} from "../../model/CSGORestClient";

  @Component
  class CSGOTeamView extends Vue {
    state = this.$store.state;
    loadingTeams = false;
    team = null;
    team2 = null;
    playerItems = [];
    playerItems2 = [];
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
    }];

    /**
     * do the init logic
     */
    async mounted() {
      this.loadingTeams = true;
      let id = this.$route.params.id;
      let id2 = null;
      // check if id is in the route params
      if ("id2" in this.$route.params) {
        id2 = this.$route.params.id2;
      }
      // get the team for the id
      let response = await new CSGORestClient().getTeam(id);
      this.team = response.team;
      // set the players and transform their kast value
      this.playerItems = [this.team.Player_1, this.team.Player_2, this.team.Player_3, this.team.Player_4, this.team.Player_5];
      this.playerItems.forEach(player => {
        player.kast = (player.kast * 100) + "%";
      });
      if (id2 !== null) {
        // do the same as previous with id 1
        let response = await new CSGORestClient().getTeam(id2);
        this.team2 = response.team;
        this.playerItems2 = [this.team2.Player_1, this.team2.Player_2, this.team2.Player_3, this.team2.Player_4, this.team2.Player_5];
        this.playerItems2.forEach(player => {
          player.kast = (player.kast * 100) + "%";
        });
      }
      this.loadingTeams = false;
    }

    /**
     * reroute to where the user came from
     */
    goBack() {
      this.$router.back();
    }
  }

  export default CSGOTeamView
</script>
<style scoped>
</style>
