<template>
  <v-card :dark="state.dark">
    <v-row no-gutters>
      <v-select
              :items="['BO1', 'BO3']"
              label="Mode"
              v-model="mode"
              style="margin: 10px; margin-bottom: -20px"
      />
    </v-row>
    <v-row no-gutters>
      <v-col :sm="5.9" style="margin: 10px">
        <v-row no-gutters>
          <v-autocomplete
                  :items="teams"
                  :return-object="true"
                  item-text="name"
                  label="Team 1"
                  v-model="team1Selection"
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
                  <v-text-field v-model.number="team1.Player_1.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_1.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_1.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_1.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_1.kast" dense type="number" min="0"/></td>
              </tr>
              <tr>
                <td>
                  <v-text-field v-model="team1.Player_2.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_2.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_2.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_2.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_2.kast" dense type="number" min="0"/></td>
              </tr>
              <tr>
                <td>
                  <v-text-field v-model="team1.Player_3.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_3.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_3.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_3.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_3.kast" dense type="number" min="0"/></td>
              </tr>
              <tr>
                <td>
                  <v-text-field v-model="team1.Player_4.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_4.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_4.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_4.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_4.kast" dense type="number" min="0"/></td>
              </tr>
              <tr>
                <td>
                  <v-text-field v-model="team1.Player_5.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_5.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_5.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_5.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team1.Player_5.kast" dense type="number" min="0"/></td>
              </tr>
              </tbody>
            </template>
          </v-data-table>
        </v-row>
      </v-col>
      <v-col :sm="5.9" style="margin: 10px">
        <v-row no-gutters>
          <v-autocomplete
                  :items="teams"
                  :return-object="true"
                  item-text="name"
                  label="Team 2"
                  v-model="team2Selection"
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
                  <v-text-field v-model="team2.Player_1.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_1.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_1.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_1.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_1.kast" dense type="number" min="0"/></td>
              </tr>
              <tr>
                <td>
                  <v-text-field v-model="team2.Player_2.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_2.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_2.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_2.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_2.kast" dense type="number" min="0"/></td>
              </tr>
              <tr>
                <td>
                  <v-text-field v-model="team2.Player_3.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_3.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_3.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_3.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_3.kast" dense type="number" min="0"/></td>
              </tr>
              <tr>
                <td>
                  <v-text-field v-model="team2.Player_4.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_4.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_4.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_4.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_4.kast" dense type="number" min="0"/></td>
              </tr>
              <tr>
                <td>
                  <v-text-field v-model="team2.Player_5.adr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_5.kpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_5.dpr" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_5.impact" dense type="number" min="0"/></td>
                <td>
                  <v-text-field v-model="team2.Player_5.kast" dense type="number" min="0"/></td>
              </tr>
              </tbody>
            </template>
          </v-data-table>
        </v-row>
      </v-col>
    </v-row>
    <v-row no-gutters v-if="prediction !== null" style="margin-left: 10px; margin-right: 10px">
      <label><pre>Team 1 Confidence: {{prediction.team_1_confidence}}</pre></label>
      <v-spacer/>
      <label><pre>Team 2 Confidence: {{prediction.team_2_confidence}}</pre></label>
    </v-row>
    <v-row no-gutters style="margin-right: 10px; padding-bottom: 10px">
      <v-spacer />
      <v-btn rounded color="primary" dark style="margin-top: 15px" @click="createPrediction()"><v-icon left>mdi-plus</v-icon>Predict the match</v-btn>
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

    async mounted() {
      let response = await new CSGORestClient().getTeams();
      this.teams = response.teams;
    }

    async createPrediction() {
      let response = await new CSGORestClient().createPrediction(this.team1, this.team2, this.mode);
      console.log(response);
      this.prediction = response.prediction;
    }

    @Watch("team1Selection", {immediate: true, deep: true})
    async __watchTeam1Selection() {
      if (this.team1Selection !== null) {
        let response = await new CSGORestClient().getTeam(this.team1Selection.id);
        this.team1 = response.team;
      }
    }

    @Watch("team2Selection", {immediate: true, deep: true})
    async __watchTeam2Selection() {
      if (this.team2Selection !== null) {
        let response = await new CSGORestClient().getTeam(this.team2Selection.id);
        this.team2 = response.team;
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
