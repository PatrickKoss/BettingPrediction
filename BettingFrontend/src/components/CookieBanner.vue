<template>
  <v-snackbar
          :timeout="-1"
          multi-line
          v-model="showCookieBanner"
  >
    <span>We would like to use cookies so that we can optimize and personalize our websites for you. In addition, cookies are
    used to be able to offer functions of social media platforms, to analyze access to our websites and to pass on
    information on the use of our websites to our partners in the areas of social media, advertisements and analyzes. Do
      you revocably consent to the use of cookies on our websites?(<a href="http://patrick-koss.de/#/privacy-policy">more about it</a>) <br/></span>
    <v-btn
            @click="setAgreementCookie"
            color="primary"
            text
    >
      Agree
    </v-btn>
  </v-snackbar>
</template>

<script>
  import {Component, Vue} from 'vue-property-decorator'

  @Component
  class CookieBanner extends Vue {
    showCookieBanner = true;

    setAgreementCookie() {
      this.showCookieBanner = false;
      localStorage.cookieBanner = "0";
    }

    created() {
      if (localStorage.cookieBanner !== undefined) {
        if (localStorage.cookieBanner === "0") this.showCookieBanner = false;
      }
    }
  }

  export default CookieBanner
</script>

<style scoped>

</style>
