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
}
