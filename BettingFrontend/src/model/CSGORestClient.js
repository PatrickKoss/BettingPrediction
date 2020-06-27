import axios from "axios";
import {config} from "../config";
import store from "../store/index"

export class CSGORestClient {

  api = config.apiEndpoint;

  async getUpcomingMatches() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/upcomingMatches/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  async getMatchesResult() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/matchResult/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  async getMatchesResultStats() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/matchResultStats/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  async getTeam(id) {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/teams/${id}`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  async getTeams() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/teams/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  async createPrediction(team1, team2, mode) {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.post(`${this.api}/csgo/prediction/`, {team_1: team1, team_2: team2, mode: mode})).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }

  async checkPermissions() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    try {
      return (await axios.get(`${this.api}/csgo/checkPermissions/`)).data;
    } catch (error) {
      return {message: error.response.data.message, status: error.response.status};
    }
  }
}
