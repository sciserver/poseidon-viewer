import Vue from 'vue';
import Vuex from 'vuex';
import { getField, updateField } from 'vuex-map-fields';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    timestamp: 0,
    maxTimestamp: 1504,
    depth: 0,
    maxDepth: 89,
    variable: 'SSS',
    variables: [
      {
        name: 'SSS',
        label: 'Salinity',
      },
      {
        name: 'SST',
        label: 'Temperature',
      },
      {
        name: 'velocity',
        label: 'Vorticity'
      }
    ],
    colormap: 'cmo.haline',
    colormaps: ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'seismic', 'RdBu_r', 'cmo.haline'],
    min: 0,
    max: 65535,
    showVelocity: false
  },
  getters: {
    getField
  },
  mutations: {
    updateField
  },
  actions: {
  },
  modules: {
  }
})
