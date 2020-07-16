<template>
  <v-card :dark="state.dark">
    <v-card-title>
      <v-spacer></v-spacer>
      <v-text-field
              append-icon="mdi-magnify"
              hide-details
              label="Search"
              single-line
              v-model="statisticSearch"
      />
    </v-card-title>
    <v-data-table
            :headers="statsHeader"
            :items="itemsStats"
            :items-per-page="15"
            :loading="loading"
            multi-sort
            :sort-desc="[false, true]"
            :search="statisticSearch"
    />
  </v-card>
</template>

<script>
  import {Component, Vue} from 'vue-property-decorator'
  import {CSGORestClient} from "../../model/CSGORestClient";

  @Component
  class CSGOStatisticsTable extends Vue {
    state = this.$store.state;
    itemsStats = [];
    loading = false;
    statisticSearch = "";

    statsHeader = [{text: "Mode", align: 'start', sortable: true, value: 'mode'}, {
      text: "Model",
      align: 'start',
      sortable: true,
      value: 'svm'
    }, {
      text: "Roi",
      align: 'start',
      sortable: true,
      value: 'roi'
    }, {text: "Accuracy", align: 'start', sortable: true, value: 'accuracy'}, {
      text: "Average Odds",
      align: 'start',
      sortable: true,
      value: 'averageOdds'
    }, {
      text: "Average Winning Odds",
      align: 'start',
      sortable: true,
      value: 'average_winning_odds'
    }, {text: " Model picked Odds higher than", align: 'start', sortable: true, value: 'odds'}, {
      text: "Sample Size",
      align: 'start',
      sortable: true,
      value: 'sampleSize'
    }];

    /**
     * do the init logic. Basically get the data
     * @returns {Promise<void>}
     */
    async mounted() {
      this.loading = true;
      let responseStats = await new CSGORestClient().getMatchesResultStats();
      this.itemsStats = responseStats.stats;
      this.loading = false;
    }
  }

  export default CSGOStatisticsTable
</script>
<style scoped>
</style>
