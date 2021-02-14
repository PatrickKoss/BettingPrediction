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
    try {
      return (await axios.post(`${this.api}/users/login/`, user)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /**
   * logout the user
   * @returns {Promise<T>}
   */
  async logout() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.post(`${this.api}/users/logout/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /**
   * check if the user is logged in
   * @returns {Promise<T>}
   */
  async getAuthenticated() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/users/authenticated/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /**
   * register a new user
   * @param user
   * @returns {Promise<T>}
   */
  async register(user) {
    try {
      return (await axios.post(`${this.api}/users/`, user)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /**
   * delete a user
   * @returns {Promise<T>}
   */
  async deleteUser(id) {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.delete(`${this.api}/users/${id}/`)).data;
  }

  /**
   * update a user
   * @param user
   * @returns {Promise<T>}
   */
  async updateUser(user) {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.put(`${this.api}/users/`, user)).data;
  }
}
