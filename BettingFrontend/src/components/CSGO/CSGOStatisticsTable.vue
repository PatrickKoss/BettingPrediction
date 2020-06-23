<template>
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
</template>

<script>
  import {Component, Vue} from 'vue-property-decorator'
  import {CSGORestClient} from "../../model/CSGORestClient";

  @Component
  class CSGOStatisticsTable extends Vue {
    state = this.$store.state;
    itemsStats = [];

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

    async mounted() {
      let responseStats = await new CSGORestClient().getMatchesResultStats();
      this.itemsStats = responseStats.stats;
    }
  }

  export default CSGOStatisticsTable
</script>
<style scoped>
</style>
