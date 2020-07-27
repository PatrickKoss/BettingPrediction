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
            :loading="loading"
            multi-sort
            :sort-desc="[false, true]"
    >
      <template v-slot:body="{ items }">
        <tbody>
        <span v-if="loading"><pre>   </pre></span>
        <tr :key="index" v-for="(item, index) in items">
          <td @click="navigateToTeamBoth(item.Team_1_id, item.Team_2_id)"><a>{{ item.date }}</a></td>
          <td @click="navigateToTeam(item.Team_1_id)"><a>{{ item.Team1 }}</a></td>
          <td @click="navigateToTeam(item.Team_2_id)"><a>{{ item.Team2 }}</a></td>
          <td>{{ item.mode }}</td>
          <td>{{ item.odds_team_1 }}</td>
          <td>{{ item.odds_team_2 }}</td>
          <td>{{ item.nnPickedTeam }}</td>
          <td>{{ item.svmPickedTeam }}</td>
          <td>{{item.winningTeam}}</td>
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
    loading = false;

    matchResultHeader = [{text: "Date", align: 'start', sortable: true, value: 'date'}, {
      text: "Team 1",
      align: 'start',
      sortable: true,
      value: 'Team1'
    }, {text: "Team 2", align: 'start', sortable: true, value: 'Team2'}, {
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
    }, {
      text: "SVM Picked Team",
      align: 'start',
      sortable: true,
      value: 'svmPickedTeam'
    }, {
      text: "Winning Team",
      align: 'start',
      sortable: true,
      value: 'winningTeam'
    }];

    async mounted() {
      this.loading = true;
      let responseMatchesResult = await new CSGORestClient().getMatchesResult();
      this.itemsMatchResult = responseMatchesResult.matchResult;
      if (responseMatchesResult.message.messageType !== "error") {
        for (let i = 0; i < this.itemsMatchResult.length; i++) {
          let date = new Date(Date.parse(this.itemsMatchResult[i].date));
          date.setHours(date.getHours() - 2);
          this.itemsMatchResult[i].date = date.toLocaleString();
        }
      }
      this.loading = false;
    }

    navigateToTeam(id) {
      this.$router.push(`/csgo/teams/${id}/`);
    }

    navigateToTeamBoth(id, id2) {
      this.$router.push(`/csgo/teams/${id}/${id2}`);
    }
  }

  export default CSGOMatchesResultTable
</script>
<style scoped>
  td {
    text-align: left;
  }
</style>
