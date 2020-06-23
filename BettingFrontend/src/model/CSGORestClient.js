import axios from "axios";
import {config} from "../config";
import store from "../store/index"

export class CSGORestClient {

  api = config.apiEndpoint;

  async getUpcomingMatches() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.get(`${this.api}/csgo/upcomingMatches/`)).data;
  }

  async getMatchesResult() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.get(`${this.api}/csgo/matchResult/`)).data;
  }

  async getMatchesResultStats() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.get(`${this.api}/csgo/matchResultStats/`)).data;
  }

  async getTeam(id) {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.get(`${this.api}/csgo/teams/${id}`)).data;
  }

  async getTeams() {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.get(`${this.api}/csgo/teams/`)).data;
  }

  async createPrediction(team1, team2, mode) {
    axios.defaults.headers.common['Authorization'] = store.state.token;
    return (await axios.post(`${this.api}/csgo/prediction/`, {team_1: team1, team_2: team2, mode: mode})).data;
  }
}
