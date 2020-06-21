import axios from "axios";
import {config} from "../config";
import store from "../store/index"

export class UserRestClient {

  api = config.apiEndpoint;

  /**
   * login the user
   * @param user
   * @returns {Promise<T>}
   */
  async login(user) {
    return (await axios.post(`${this.api}/user/login/`, user)).data;
  }

  /**
   * logout the user
   * @returns {Promise<T>}
   */
  async logout() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.post(`${this.api}/user/logout/`)).data;
  }

  /**
   * check if the user is logged in
   * @returns {Promise<T>}
   */
  async getAuthenticated() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.get(`${this.api}/user/authenticated/`)).data;
  }

  /**
   * register a new user
   * @param user
   * @returns {Promise<T>}
   */
  async register(user) {
    return (await axios.post(`${this.api}/user/register/`, user)).data;
  }

  /**
   * delete a user
   * @returns {Promise<T>}
   */
  async deleteUser() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.post(`${this.api}/user/delete/`)).data;
  }

  /**
   * update a user
   * @param user
   * @returns {Promise<T>}
   */
  async updateUser(user) {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.post(`${this.api}/user/update/`, user)).data;
  }
}
