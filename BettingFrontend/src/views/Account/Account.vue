<template>
  <span v-if="editingMode">
    <AccountDataInput :mode="'accountUpdate'" @accountUpdated="editingMode = false"/>
  </span>
  <v-card :dark="state.dark" v-else-if="state.user">
    <v-row class="accountPadding">
      <v-text-field
              :disabled="!editingMode"
              :value="state.user.email"
              hide-details="auto"
              label="Your email adress"
      />
    </v-row>
    <v-row class="accountPadding">
      <v-text-field
              :disabled="!editingMode"
              :value="state.user.username"
              hide-details="auto"
              label="Your Username"
      />
    </v-row>
    <v-row style="padding: 15px">
      <v-spacer/>
      <v-dialog
              v-model="deleteDialog"
              width="500"
      >
        <template v-slot:activator="{ on }">
          <v-btn
                  color="red lighten-2"
                  dark
                  v-on="on"
          >
            Delete Account
          </v-btn>
        </template>

        <v-card :dark="state.dark">
          <v-card-title
                  primary-title
          >
            Delete Account
          </v-card-title>

          <v-card-text>
            Are you sure you want to delete your account?
          </v-card-text>

          <v-divider/>

          <v-card-actions>
            <v-btn
                    @click="deleteDialog = false"
                    color="primary"
                    text
            >
              Abort
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
                    @click="deleteAccount"
                    color="red lighten-2"
                    text
            >
              Yes, delete the account
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-btn @click="editingMode = true" color="primary" style="margin-left: 15px" type="submit">Update Account Data
      </v-btn>
      <v-spacer/>
    </v-row>
  </v-card>
</template>

<script>
  import {Component, Vue} from 'vue-property-decorator';
  import AccountDataInput from "../../components/AccountDataInput";
  import {UserRestClient} from "../../model/UserRestClient";
  import store from "../../store";
  import router from "../../router";

  @Component({
    components: {
      AccountDataInput
    }
  })
  class Account extends Vue {
    editingMode = false;
    state = this.$store.state;
    deleteDialog = false;

    /**
     * check if the user is logged in and if not then send it to home
     */
    mounted() {
      if (this.state.token === "") this.$router.push("/");
    }

    /**
     * delete the account
     * @returns {Promise<void>}
     */
    async deleteAccount() {
      this.state.message = await new UserRestClient().deleteUser();
      if (this.state.message.messageType === "success") {
        // reset the data in store and local store
        store.state.user = {username: "", email: ""};
        localStorage.token = undefined;
        store.state.token = "";
        // navigate to home
        if (router.currentRoute.path !== "/") {
          await router.push("/");
        }
      }
    }
  }

  export default Account
</script>
<style scoped>
  .accountPadding {
    padding-right: 25px;
    padding-top: 15px;
    padding-left: 25px;
  }
</style>
