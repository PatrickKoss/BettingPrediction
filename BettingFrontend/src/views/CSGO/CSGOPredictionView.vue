<template>
  <v-card :dark="state.dark">
    <v-row no-gutters v-if="loadingTeamParams">
      <v-progress-linear
              indeterminate
      />
    </v-row>
    <v-row no-gutters>
      <v-select
              :items="['BO1', 'BO3']"
              label="Mode"
              style="margin: 10px; margin-bottom: -20px"
              v-model="mode"
      />
    </v-row>
    <v-row no-gutters>
      <v-col :sm="6" :cols="12" style="padding: 10px">
        <v-row no-gutters>
          <v-autocomplete
                  :items="teams"
                  :return-object="true"
                  item-text="name"
                  label="Team 1"
                  v-model="team1Selection"
                  :loading="loadingTeams"
          />
        </v-row>
        <v-row no-gutters>
          <v-text-field label="Winning Percentage:" v-model="team1.winning_percentage"/>
        </v-row>
        <v-row no-gutters>
          <v-data-table
                  :headers="tableHeader"
                  :items-per-page="5"
                  hide-default-footer
          >
            <template v-slot:body="{  }">
              <tbody>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model.number="team1.Player_1.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_1.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_1.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_1.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_1.kast" max="1"/>
                </td>
              </tr>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_2.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_2.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_2.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_2.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_2.kast" max="1"/>
                </td>
              </tr>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_3.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_3.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_3.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_3.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_3.kast" max="1"/>
                </td>
              </tr>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_4.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_4.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_4.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_4.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_4.kast" max="1"/>
                </td>
              </tr>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_5.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_5.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_5.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_5.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team1.Player_5.kast" max="1"/>
                </td>
              </tr>
              </tbody>
            </template>
          </v-data-table>
        </v-row>
      </v-col>
      <v-col :sm="6" :cols="12" style="padding: 10px">
        <v-row no-gutters>
          <v-autocomplete
                  :items="teams"
                  :return-object="true"
                  item-text="name"
                  label="Team 2"
                  v-model="team2Selection"
                  :loading="loadingTeams"
          />
        </v-row>
        <v-row no-gutters>
          <v-text-field label="Winning Percentage:" v-model="team2.winning_percentage"/>
        </v-row>
        <v-row no-gutters>
          <v-data-table
                  :headers="tableHeader"
                  :items-per-page="5"
                  hide-default-footer
          >
            <template v-slot:body="{  }">
              <tbody>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_1.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_1.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_1.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_1.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_1.kast" max="1"/>
                </td>
              </tr>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_2.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_2.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_2.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_2.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_2.kast" max="1"/>
                </td>
              </tr>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_3.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_3.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_3.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_3.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_3.kast" max="1"/>
                </td>
              </tr>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_4.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_4.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_4.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_4.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_4.kast" max="1"/>
                </td>
              </tr>
              <tr>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_5.adr" max="1000"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_5.kpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_5.dpr" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_5.impact" max="1"/>
                </td>
                <td>
                  <v-text-field dense min="0" type="number" v-model="team2.Player_5.kast" max="1"/>
                </td>
              </tr>
              </tbody>
            </template>
          </v-data-table>
        </v-row>
      </v-col>
    </v-row>
    <v-row no-gutters style="margin-left: 10px; margin-right: 10px" v-if="prediction !== null">
      <label>
        <pre>Team 1 Confidence: {{prediction.team_1_confidence}}</pre>
      </label>
      <v-spacer/>
      <label>
        <pre>Team 2 Confidence: {{prediction.team_2_confidence}}</pre>
      </label>
    </v-row>
    <v-row no-gutters style="padding-bottom: 10px">
      <v-btn @click="goBack()" color="primary" dark rounded
             style="margin-top: 15px; margin-left: 10px">
        <v-icon left>mdi-arrow-left</v-icon>
        Go back
      </v-btn>
      <v-spacer/>
      <v-btn :disabled="loading" :loading="loading" @click="createPrediction()" color="primary" dark rounded
             style="margin-top: 15px; margin-right: 10px">
        <v-icon left>mdi-plus</v-icon>
        Predict the match
      </v-btn>
    </v-row>
  </v-card>
</template>

<script>
  import {Component, Vue, Watch} from 'vue-property-decorator'
  import {CSGORestClient} from "../../model/CSGORestClient";

  @Component
  class Home extends Vue {
    state = this.$store.state;
    teams = [];
    team1Selection = null;
    team2Selection = null;
    prediction = null;
    mode = "BO1";
    loading = false;
    loadingTeams = false;
    loadingTeamParams = false;

    team1 = {
      winning_percentage: 0,
      Player_1: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""},
      Player_2: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""},
      Player_3: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""},
      Player_4: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""},
      Player_5: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""}
    };
    team2 = {
      winning_percentage: 0,
      Player_1: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""},
      Player_2: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""},
      Player_3: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""},
      Player_4: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""},
      Player_5: {adr: 0, dpr: 0, impact: 0, kast: 0, kpr: 0, name: ""}
    };

    tableHeader = [{
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
     * do the init logic which get the data and check some stuff
     */
    async mounted() {
      if ("team1" in this.$route.params && "team2" in this.$route.params && "mode" in this.$route.params) {
        this.loadingTeamParams = true;
      }
      this.loadingTeams = true;
      let response = await new CSGORestClient().getTeams();
      this.teams = response.teams;
      this.loadingTeams = false;

      if ("team1" in this.$route.params && "team2" in this.$route.params && "mode" in this.$route.params) {
        this.team1Selection = this.teams.find(team => {
          return team.name === this.$route.params.team1
        });
        this.team2Selection = this.teams.find(team => {
          return team.name === this.$route.params.team2
        });
        if (this.$route.params.mode === "BO1") {
          this.mode = "BO1";
        } else {
          this.mode = "BO3";
        }
        this.loadingTeamParams = false;
      }
    }

    /**
     * sent data to the backend and get the prediction
     * @returns {Promise<void>}
     */
    async createPrediction() {
      this.loading = true;
      let response = await new CSGORestClient().createPrediction(this.team1, this.team2, this.mode);
      this.prediction = response.prediction;
      this.loading = false;
    }

    /**
     * reroute the user where he came from
     */
    goBack() {
      this.$router.back();
    }

    /**
     * watch which team was selected and update its stats
     * @returns {Promise<void>}
     * @private
     */
    @Watch("team1Selection", {immediate: true, deep: true})
    async __watchTeam1Selection() {
      if (this.team1Selection !== null) {
        this.loadingTeamParams = true;
        let response = await new CSGORestClient().getTeam(this.team1Selection.id);
        this.team1 = response.team;
        this.loadingTeamParams = false;
      }
    }

    /**
     * watch which team was selected and update its stats
     * @returns {Promise<void>}
     * @private
     */
    @Watch("team2Selection", {immediate: true, deep: true})
    async __watchTeam2Selection() {
      if (this.team2Selection !== null) {
        this.loadingTeamParams = true;
        let response = await new CSGORestClient().getTeam(this.team2Selection.id);
        this.team2 = response.team;
        this.loadingTeamParams = false;
      }
    }
  }

  export default Home
</script>
<style scoped>
  td {
    text-align: left;
  }

  ::v-deep input::-webkit-outer-spin-button,
  ::v-deep input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
</style>
