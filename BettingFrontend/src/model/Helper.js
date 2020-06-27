import store from "../store/index";
import {UserRestClient} from "./UserRestClient";
import router from "../router";

/**
 * logout helper function for routing and clean up store variables
 * @returns {Promise<void>}
 */
export async function logout() {
  store.state.message = (await new UserRestClient().logout()).message;
  if (store.state.message.messageType === "success") {
    store.state.user = {username: "", email: ""};
    localStorage.token = undefined;
    store.state.token = "";
    if (router.currentRoute.path !== "/login") {
      await router.push("/login");
    }
  }
}

/**
 * login helper function for routing and setting up store variables
 * @returns {Promise<void>}
 */
export async function login(user, token) {
  store.state.token = token;
  store.state.user = user;
  localStorage.token = store.state.token;
  setTimeout(async () => {
    await router.push("/");
  }, 50)
}
