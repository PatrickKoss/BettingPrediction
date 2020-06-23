<template>
  <v-card :dark="state.dark">
    <v-card-title>
      <v-spacer></v-spacer>
      <v-text-field
              append-icon="mdi-magnify"
              hide-details
              label="Search"
              single-line
              v-model="matchResultSearch"
      />
    </v-card-title>
    <v-data-table
            :headers="matchResultHeader"
            :items="itemsMatchResult"
            :items-per-page="10"
            :search="matchResultSearch"
    >
      <template v-slot:body="{ items }">
        <tbody>
        <tr :key="index" v-for="(item, index) in items">
          <td>{{ item.date }}</td>
          <td @click="navigateToTeam(item.Team_1_id)"><a>{{ item.Team1 }}</a></td>
          <td @click="navigateToTeam(item.Team_2_id)"><a>{{ item.Team2 }}</a></td>
          <td>{{ item.mode }}</td>
          <td>{{ item.odds_team_1 }}</td>
          <td>{{ item.odds_team_2 }}</td>
          <td>{{ item.team_1_confidence }}</td>
          <td>{{ item.team_2_confidence }}</td>
          <td>{{item.team_1_win}}</td>
          <td>{{item.team_2_win}}</td>
        </tr>
        </tbody>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
  import {Component, Vue} from 'vue-property-decorator'
  import {CSGORestClient} from "../../model/CSGORestClient";

  @Component
  class CSGOMatchesResultTable extends Vue {
    state = this.$store.state;
    matchResultSearch = "";
    itemsMatchResult = [];

    matchResultHeader = [{text: "Date", align: 'start', sortable: false, value: 'date'}, {
      text: "Team 1",
      align: 'start',
      sortable: false,
      value: 'Team1'
    }, {text: "Team 2", align: 'start', sortable: false, value: 'Team2'}, {
      text: "Mode",
      align: 'start',
      sortable: false,
      value: 'mode'
    }, {
      text: "Odds Team 1",
      align: 'start',
      sortable: false,
      value: 'odds_team_1'
    }, {text: "Odds Team 2", align: 'start', sortable: false, value: 'odds_team_2'}, {
      text: "Confidence Team 1",
      align: 'start',
      sortable: false,
      value: 'team_1_confidence'
    }, {
      text: "Confidence Team 2",
      align: 'start',
      sortable: false,
      value: 'team_2_confidence'
    }, {
      text: "Team 1 Win",
      align: 'start',
      sortable: false,
      value: 'team_1_win'
    }, {text: "Team 2 Win", align: 'start', sortable: false, value: 'team_2_win'}];

    async mounted() {
      let responseMatchesResult = await new CSGORestClient().getMatchesResult();
      this.itemsMatchResult = responseMatchesResult.matchResult;
      for (let i = 0; i < this.itemsMatchResult.length; i++) {
        let date = new Date(Date.parse(this.itemsMatchResult[i].date));
        this.itemsMatchResult[i].date = date.toLocaleString();
      }
    }

    navigateToTeam(id) {
      this.$router.push(`/csgo/teams/${id}/`);
    }
  }

  export default CSGOMatchesResultTable
</script>
<style scoped>
</style>
