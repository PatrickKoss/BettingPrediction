<template>
  <v-card :dark="state.dark">
    <form>
      <v-row class="loginPadding">
        <v-col cols="12">
          <v-text-field
                  :error-messages="emailErrors"
                  @blur="$v.email.$touch()"
                  @input="$v.email.$touch()"
                  hide-details="auto"
                  label="Your email adress"
                  required
                  v-model="email"
          />
        </v-col>
      </v-row>
      <v-row class="loginPadding">
        <v-col cols="12">
          <v-text-field
                  :error-messages="usernameErrors"
                  @blur="$v.username.$touch()"
                  @input="$v.username.$touch()"
                  hide-details="auto"
                  label="Choose a username"
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
                  label="Choose your password"
                  required
                  v-model="password"
          />
        </v-col>
      </v-row>
      <v-row class="loginPadding">
        <v-col cols="12">
          <v-text-field
                  :append-icon="showPasswordConfirm ? 'mdi-eye' : 'mdi-eye-off'"
                  :error-messages="passwordConfirmErrors"
                  :type="showPasswordConfirm ? 'text' : 'password'"
                  @blur="$v.passwordConfirm.$touch()"
                  @click:append="showPasswordConfirm = !showPasswordConfirm"
                  @input="$v.passwordConfirm.$touch()"
                  hide-details="auto"
                  label="Confirm your password"
                  required
                  v-model="passwordConfirm"
          />
        </v-col>
      </v-row>
      <v-row class="loginPadding">
        <v-col align="start" justify="start" v-if="mode === 'accountUpdate'">
          <v-btn @click="$emit('accountUpdated')" color="primary">
            Abort
          </v-btn>
        </v-col>
        <v-col align="end" justify="end">
          <v-btn @click="submit()" color="primary">
            <span v-if="mode === 'registration'">Register</span>
            <span v-if="mode === 'accountUpdate'">Update Account</span>
          </v-btn>
        </v-col>
      </v-row>
    </form>
    <v-row v-if="mode === 'registration'">
      <v-spacer/>
      <p>
        Already have an account? <a @click="$router.push('/login')" style="margin-left: 3px">Login</a>!
      </p>
      <v-spacer/>
    </v-row>
  </v-card>
</template>

<script>
  import {Component, Prop, Vue, Watch} from 'vue-property-decorator';
  import {Validate} from 'vuelidate-property-decorators';
  import {email, maxLength, minLength, required, sameAs} from 'vuelidate/lib/validators'
  import {UserRestClient} from "../model/UserRestClient";
  import {login} from "../model/Helper";

  @Component
  class AccountDataInput extends Vue {
    @Prop() mode;
    showPassword = false;
    showPasswordConfirm = false;
    emailErrors = [];
    usernameErrors = [];
    passwordErrors = [];
    passwordConfirmErrors = [];
    state = this.$store.state;

    @Validate({required, maxLength: maxLength(30)})
    username = '';

    @Validate({required, email})
    email = '';

    @Validate({required, minLength: minLength(6)})
    password = '';

    @Validate({required, minLength: minLength(6), sameAs: sameAs('password')})
    passwordConfirm = '';

    mounted() {
      window.addEventListener('keydown', this.keyDown, false);
    }

    /**
     * check if enter was clicked to submit
     * @param e
     */
    keyDown(e) {
      if (e.key === "Enter") this.submit();
    }

    /**
     * check if the input values are correct and send data to the backend
     * @returns {Promise<void>}
     */
    async submit() {
      this.emailErrors = [];
      this.usernameErrors = [];
      this.passwordErrors = [];
      this.passwordConfirmErrors = [];
      !this.$v.email.email && this.emailErrors.push('Must be valid e-mail');
      !this.$v.email.required && this.emailErrors.push('E-mail is required');
      !this.$v.username.required && this.usernameErrors.push('Username is required');
      !this.$v.username.maxLength && this.usernameErrors.push('Username shouldn´t be longer than 30 signs');
      !this.$v.password.required && this.passwordErrors.push('Password is required');
      !this.$v.password.minLength && this.passwordErrors.push('Password should be at least 6 signs long');
      !this.$v.passwordConfirm.required && this.passwordConfirmErrors.push('Password Confirm is required');
      !this.$v.passwordConfirm.minLength && this.passwordConfirmErrors.push('Password Confirm should be at least 6 signs long');
      !this.$v.passwordConfirm.sameAs && this.passwordConfirmErrors.push('Password and Password Confirm do not match');
      this.$v.$touch();

      if (this.emailErrors.length === 0 && this.usernameErrors.length === 0 && this.passwordErrors.length === 0 && this.passwordConfirmErrors.length === 0) {
        // since the registration and the account update user the same form distinguish between those to modes
        if (this.mode === "registration") {
          let user = {username: this.username, password: this.password, email: this.email};
          let response = await new UserRestClient().register(user);
          this.state.message = response.message;
          if (this.state.message.messageType === "success") {
            await login(response.user, response.token);
          }
        }
        if (this.mode === "accountUpdate") {
          let user = {username: this.username, password: this.password, email: this.email};
          let response = await new UserRestClient().updateUser(user);
          this.state.message = response.message;
          if (this.state.message.messageType === "success") {
            await login(response.user, response.token);
          }
        }
      }
    }

    @Watch("username")
    __resetUsernameErrors() {
      this.usernameErrors = [];
    }

    @Watch("email")
    __resetEmailErrors() {
      this.emailErrors = [];
    }

    @Watch("password")
    __resetPasswordErrors() {
      this.passwordErrors = [];
    }

    @Watch("passwordConfirm")
    __resetPasswordConfirmErrors() {
      this.passwordConfirmErrors = [];
    }

    /**
     * set up the user if he is logged in
     * @private
     */
    @Watch('state.user', {immediate: true, deep: true})
    __checkUser() {
      if (this.state.user.username !== "") {
        this.username = this.state.user.username;
        this.email = this.state.user.email;
      }
    }

    /**
     * clean up logic
     */
    beforeDestroy() {
      window.removeEventListener("keydown", this.keyDown, false);
    }
  }

  export default AccountDataInput
</script>
<style scoped>
  .loginPadding {
    padding-left: 15px;
    padding-right: 15px;
  }
</style>
