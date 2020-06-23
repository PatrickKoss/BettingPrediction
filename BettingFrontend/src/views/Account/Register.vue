<template>
  <span>
    <AccountDataInput :mode="'registration'"/>
  </span>
</template>

<script>
  import {Component, Vue} from 'vue-property-decorator';
  //import {UserRestClient} from "../model/UserRestClient";
  import AccountDataInput from "../../components/AccountDataInput";

  @Component({
    components: {
      AccountDataInput
    }
  })
  class Register extends Vue {
    state = this.$store.state;

    /**
     * if the user is logged in the route him to home.
     */
    mounted() {
      if (this.state.token !== "") this.$router.push("/");
    }
  }

  export default Register
</script>
<style scoped>
  .loginPadding {
    padding-left: 15px;
    padding-right: 15px;
  }
</style>
