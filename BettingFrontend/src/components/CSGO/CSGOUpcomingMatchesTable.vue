<template>
  <v-card :dark="state.dark">
    <v-card-title>
      <v-btn rounded color="primary" dark style="margin-top: 22px" @click="goToPredictionCreator()"><v-icon left>mdi-plus</v-icon>Check own Match</v-btn>
      <v-spacer></v-spacer>
      <v-text-field
              append-icon="mdi-magnify"
              hide-details
              label="Search"
              single-line
              v-model="upcomingMatchSearch"
      />
    </v-card-title>
    <v-data-table
            :headers="upcomingMatchHeader"
            :items="itemsUpcomingMatches"
            :items-per-page="15"
            :search="upcomingMatchSearch"
            :loading="loading"
            multi-sort
            :sort-desc="[false, true]"
    >
      <template v-slot:body="{ items }">
        <tbody>
        <span v-if="loading"><pre>   </pre></span>
        <tr v-for="(item, index) in items" :key="index">
          <td @click="navigateToPrediction(item.Team_1.name, item.Team_2.name, item.mode)"><a>{{ item.date }}</a></td>
          <td @click="navigateToTeam(item.Team_1.id)"><a>{{ item.Team_1.name }}</a></td>
          <td @click="navigateToTeam(item.Team_2.id)"><a>{{ item.Team_2.name }}</a></td>
          <td>{{ item.mode }}</td>
          <td>{{ item.odds_team_1 }}</td>
          <td>{{ item.odds_team_2 }}</td>
          <td>{{ item.nnPickedTeam }}</td>
          <td>{{ item.svmPickedTeam }}</td>
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
  class CSGOUpcomingMatchesTable extends Vue {
    state = this.$store.state;
    upcomingMatchSearch = "";
    itemsUpcomingMatches = [];
    loading = false;

    upcomingMatchHeader = [{text: "Date", align: 'start', sortable: true, value: 'date'}, {
      text: "Team 1",
      align: 'start',
      sortable: true,
      value: 'Team_1.name'
    }, {text: "Team 2", align: 'start', sortable: true, value: 'Team_2.name'}, {
      text: "Mode",
      align: 'start',
      sortable: true,
      value: 'mode'
    }, {
      text: "Odds Team 1",
      align: 'start',
      sortable: true,
      value: 'odds_team_1'
    }, {text: "Odds Team 2", align: 'start', sortable: true, value: 'odds_team_2'}, {
      text: "NN Picked Team",
      align: 'start',
      sortable: true,
      value: 'nnPickedTeam'
    }, {text: "SVM Picked Team", align: 'start', sortable: true, value: 'svmPickedTeam'}];

    async mounted() {
      this.loading = true;
      let responseUpcomingMatches = await new CSGORestClient().getUpcomingMatches();
      this.itemsUpcomingMatches = responseUpcomingMatches.upcoming_matches;
      if (responseUpcomingMatches.message.messageType !== "error") {
        for (let i = 0; i < this.itemsUpcomingMatches.length; i++) {
          let date = new Date(Date.parse(this.itemsUpcomingMatches[i].date));
          date.setHours(date.getHours() - 2);
          this.itemsUpcomingMatches[i].date = date.toLocaleString();
        }
      }
      this.loading = false;
    }

    navigateToTeam(id) {
      this.$router.push(`/csgo/teams/${id}/`);
    }

    goToPredictionCreator() {
      this.$router.push(`/csgo/prediction/`);
    }

    navigateToPrediction(team1, team2, mode) {
      this.$router.push(`/csgo/prediction/${team1}-${mode}-${team2}`);
    }
  }

  export default CSGOUpcomingMatchesTable
</script>
<style scoped>
  td {
    text-align: left;
  }
</style>
