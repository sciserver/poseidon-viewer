import Vue from 'vue';
import Vuex from 'vuex';
import { getField, updateField } from 'vuex-map-fields';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    timestamp: 0,
    timestamp2: 10311,
    maxTimestamp: 10311,
    depth: 0,
    maxDepth: 12,
    variable: 'salinity',
    variables: [
      {
        name: 'salinity',
        label: 'Salinity',
        vmin: 30,
        vmax: 37,
        step: 0.1,
        units: 'psu'
      },
      {
        name: 'temperature',
        label: 'Temperature',
        vmin: -2,
        vmax: 30,
        step: 0.1,
        units: '°C'
      },
      {
        name: 'Eta',
        label: 'Surface height anomaly',
        vmin: -2,
        vmax: 2,
        step: 0.05,
        units: 'm'
      },
      {
        name: 'vorticity',
        label: 'Vorticity',
        vmin: -0.001,
        defaultMin: -0.00015,
        vmax: 0.001,
        defaultMax: 0.00015,
        step: 0.00001,
        units: '1/s'
      }
    ],
    colormap: 'cmo.haline',
    colormaps: ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'seismic', 'RdBu_r', 'cmo.haline'],
    min: 0,
    max: 65535,
    showVelocity: false,
    showGrid: false,
    z_levels: [-5.000000e-01, -1.468000e+01, -5.269000e+01, -1.393650e+02,
       -2.995050e+02, -5.409350e+02, -8.558350e+02, -1.246005e+03,
       -1.753875e+03, -2.503415e+03, -3.792495e+03, -6.301185e+03]
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
