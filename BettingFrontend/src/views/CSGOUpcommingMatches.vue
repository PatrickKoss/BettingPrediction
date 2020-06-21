<template>
  <v-card :dark="state.dark">
    <v-tabs
            :dark="state.dark"
            background-color="transparent"
            grow
            v-model="tab"
    >
      <v-tab>
        Upcoming Matches
      </v-tab>
      <v-tab>
        Matches Result
      </v-tab>
      <v-tab>
        Statistics
      </v-tab>
    </v-tabs>

    <v-tabs-items v-model="tab">
      <v-tab-item>
        <v-card :dark="state.dark">
          <v-card-title>
            Add button
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
                  :items-per-page="100"
                  :search="upcomingMatchSearch"
          />
        </v-card>
      </v-tab-item>
      <v-tab-item>
        <v-card :dark="state.dark">
          <v-card-title>
            Add button
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
          />
        </v-card>
      </v-tab-item>
      <v-tab-item>
        <v-card :dark="state.dark">
          <v-card-title>
            Add button
            <v-spacer></v-spacer>
          </v-card-title>
          <v-data-table
                  :headers="statsHeader"
                  :items="itemsStats"
                  :items-per-page="10"
          />
        </v-card>
      </v-tab-item>
    </v-tabs-items>
  </v-card>
</template>

<script>
  import {Component, Vue} from 'vue-property-decorator';
  import {CSGORestClient} from '../model/CSGORestClient';

  @Component({
    components: {}
  })
  class CSGOUpcommingMatches extends Vue {
    state = this.$store.state;
    tab = null;
    upcomingMatchSearch = "";
    matchResultSearch = "";
    upcomingMatchHeader = [{text: "Date", align: 'start', sortable: false, value: 'date'}, {
      text: "Team 1",
      align: 'start',
      sortable: false,
      value: 'Team_1.name'
    }, {text: "Team 2", align: 'start', sortable: false, value: 'Team_2.name'}, {
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
    }, {text: "Confidence Team 2", align: 'start', sortable: false, value: 'team_2_confidence'}];

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

    statsHeader = [{text: "mode", align: 'start', sortable: false, value: 'mode'}, {
      text: "Roi",
      align: 'start',
      sortable: true,
      value: 'roi'
    }, {text: "Accuracy", align: 'start', sortable: true, value: 'accuracy'}, {
      text: "Sample Size",
      align: 'start',
      sortable: true,
      value: 'sampleSize'
    }];
    itemsUpcomingMatches = [];
    itemsMatchResult = [];
    itemsStats = [];

    async mounted() {
      if (this.state.token === "") this.$router.push("/");
      let responseUpcomingMatches = await new CSGORestClient().getUpcomingMatches();

      this.itemsUpcomingMatches = responseUpcomingMatches.upcoming_matches;
      for (let i = 0; i < this.itemsUpcomingMatches.length; i++) {
        let date = new Date(Date.parse(this.itemsUpcomingMatches[i].date));
        this.itemsUpcomingMatches[i].date = date.toLocaleString();
      }

      let responseMatchesResult = await new CSGORestClient().getMatchesResult();
      this.itemsMatchResult = responseMatchesResult.matchResult;
      for (let i = 0; i < this.itemsMatchResult.length; i++) {
        let date = new Date(Date.parse(this.itemsMatchResult[i].date));
        this.itemsMatchResult[i].date = date.toLocaleString();
      }

      let responseStats = await new CSGORestClient().getMatchesResultStats();
      this.itemsStats = responseStats.stats;
    }
  }

  export default CSGOUpcommingMatches
</script>
<style scoped>
</style>
