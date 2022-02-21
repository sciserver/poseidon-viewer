import Vue from 'vue';
import Vuex from 'vuex';
import { getField, updateField } from 'vuex-map-fields';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    timestamp: 0,
    maxTimestamp: 239,
    depth: 0,
    maxDepth: 89,
    variable: 'SSS',
    variables: [
      {
        name: 'SSS',
        label: 'Salinity',
        vmin: 30,
        vmax: 37,
        units: 'PSU'
      },
      {
        name: 'SST',
        label: 'Temperature',
        vmin: -1,
        vmax: 30,
        units: '°C'
      },
      {
        name: 'Eta',
        label: 'Surface height anomaly',
        vmin: -2,
        vmax: 2,
        units: 'm'
      },
      {
        name: 'velocity',
        label: 'Vorticity',
        vmin: 0,
        vmax: 65535,
        units: ''
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
