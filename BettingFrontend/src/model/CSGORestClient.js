import axios from "axios";
import {config} from "../config";
import store from "../store/index"

export class CSGORestClient {

  api = config.apiEndpoint;

  /**
   * get the upcoming matches
   * @returns {Promise<{message: *, status: number}|T>}
   */
  async getUpcomingMatches() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/upcoming-matches/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /**
   * get the result of matches
   * @returns {Promise<{message: *, status: number}|T>}
   */
  async getMatchesResult() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/results/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /**
   * get stats of matches how the model performed
   * @returns {Promise<{message: *, status: number}|T>}
   */
  async getMatchesResultStats() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/results-stats/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /**
   * get a team by its id
   * @param id
   * @returns {Promise<{message: *, status: number}|T>}
   */
  async getTeam(id) {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/teams/${id}`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /**
   * get all teams
   * @returns {Promise<{message: *, status: number}|T>}
   */
  async getTeams() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/teams/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /**
   * get a prediction
   * @param team1
   * @param team2
   * @param mode
   * @returns {Promise<{message: *, status: number}|T>}
   */
  async createPrediction(team1, team2, mode) {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.post(`${this.api}/csgo/predictions/`, {team_1: team1, team_2: team2, mode: mode})).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  /***
   * check if a user has the right permissions
   * @returns {Promise<{message: *, status: number}|T>}
   */
  async checkPermissions() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/check-permissions/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }
}
