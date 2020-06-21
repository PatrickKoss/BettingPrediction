<template>
  <v-card :dark="state.dark">
    <v-form>
      <v-row class="loginPadding">
        <v-col cols="12">
          <v-text-field
                  :error-messages="usernameErrors"
                  @blur="$v.username.$touch()"
                  @input="$v.username.$touch()"
                  hide-details="auto"
                  label="Username"
                  required
                  v-model="username"
          />
        </v-col>
      </v-row>
      <v-row class="loginPadding">
        <v-col cols="12">
          <v-text-field
                  :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  :error-messages="passwordErrors"
                  :type="showPassword ? 'text' : 'password'"
                  @blur="$v.password.$touch()"
                  @click:append="showPassword = !showPassword"
                  @input="$v.password.$touch()"
                  hide-details="auto"
                  label="Password"
                  required
                  v-model="password"
          />
        </v-col>
      </v-row>
      <v-row class="loginPadding">
        <v-col align="end" cols="12" justify="end">
          <v-btn @click="login()" color="primary">Login</v-btn>
        </v-col>
      </v-row>
    </v-form>
    <v-row>
      <v-spacer/>
      <p>
        Do not have an account yet? Register<a @click="$router.push('/register')" style="margin-left: 3px">here</a>!
      </p>
      <v-spacer/>
    </v-row>
  </v-card>
</template>

<script>
  import {Component, Vue, Watch} from 'vue-property-decorator'
  import {UserRestClient} from "../model/UserRestClient";
  import {Validate} from 'vuelidate-property-decorators';
  import {maxLength, minLength, required} from 'vuelidate/lib/validators'
  import {login} from "../model/Helper";

  @Component
  class Login extends Vue {
    state = this.$store.state;
    showPassword = false;
    usernameErrors = [];
    passwordErrors = [];

    @Validate({required, maxLength: maxLength(30)})
    username = '';

    @Validate({required, minLength: minLength(6)})
    password = '';

    /**
     * if the user is already logged in route him to home
     */
    mounted() {
      if (this.state.token !== "") this.$router.push("/");
      window.addEventListener('keydown', this.keyDown, false);
    }

    /**
     * login logic. Check input values if they are correct and throw errors if not
     * @returns {Promise<void>}
     */
    async login() {
      this.usernameErrors = [];
      this.passwordErrors = [];
      !this.$v.username.required && this.usernameErrors.push('Username is required');
      !this.$v.username.maxLength && this.usernameErrors.push('Username shouldn´t be longer than 30 signs');
      !this.$v.password.required && this.passwordErrors.push('Password is required');
      !this.$v.password.minLength && this.passwordErrors.push('Password should be at least 6 signs long');
      if (this.usernameErrors.length === 0 && this.passwordErrors.length === 0) {
        let user = {username: this.username, password: this.password};
        let res = await new UserRestClient().login(user);
        this.state.message = res.message;
        if (this.state.message.messageType === "success") {
          await login(res.user, res.token);
        }
      }
    }

    /**
     * check if enter was clicked to submit
     * @param e
     */
    keyDown(e) {
      if (e.key === "Enter") this.login();
    }

    /**
     * reset the password errors if the user input change
     * @private
     */
    @Watch("password")
    __resetPasswordErrors() {
      this.passwordErrors = [];
    }

    /**
     * reset the username errors if the user input change
     * @private
     */
    @Watch("username")
    __resetUsernameErrors() {
      this.usernameErrors = [];
    }

    /**
     * clean up logic
     */
    beforeDestroy() {
      window.removeEventListener("keydown", this.keyDown, false);
    }
  }

  export default Login
</script>
<style scoped>
  .loginPadding {
    padding-left: 15px;
    padding-right: 15px;
  }
</style>
