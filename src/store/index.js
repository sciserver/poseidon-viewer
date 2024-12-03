import Vue from 'vue';
import Vuex from 'vuex';
import { getField, updateField } from 'vuex-map-fields';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    timestamp: 0,
    timestamp2: 239,
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
        step: 0.1,
        units: 'psu'
      },
      {
        name: 'SST',
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
    z_levels: [-5.000000e-01, -1.570000e+00, -2.790000e+00, -4.185000e+00,
      -5.780000e+00, -7.595000e+00, -9.660000e+00, -1.201000e+01,
      -1.468000e+01, -1.770500e+01, -2.112500e+01, -2.499000e+01,
      -2.934500e+01, -3.424000e+01, -3.972500e+01, -4.585500e+01,
      -5.269000e+01, -6.028000e+01, -6.868500e+01, -7.796500e+01,
      -8.817500e+01, -9.937000e+01, -1.116000e+02, -1.249150e+02,
      -1.393650e+02, -1.549900e+02, -1.718250e+02, -1.899000e+02,
      -2.092350e+02, -2.298550e+02, -2.517700e+02, -2.749850e+02,
      -2.995050e+02, -3.253200e+02, -3.524200e+02, -3.807900e+02,
      -4.104100e+02, -4.412550e+02, -4.733050e+02, -5.065400e+02,
      -5.409350e+02, -5.764650e+02, -6.131100e+02, -6.508550e+02,
      -6.896850e+02, -7.295950e+02, -7.705850e+02, -8.126600e+02,
      -8.558350e+02, -9.001350e+02, -9.455950e+02, -9.922600e+02,
      -1.040180e+03, -1.089425e+03, -1.140080e+03, -1.192235e+03,
      -1.246005e+03, -1.301520e+03, -1.358920e+03, -1.418375e+03,
      -1.480075e+03, -1.544225e+03, -1.611060e+03, -1.680845e+03,
      -1.753875e+03, -1.830475e+03, -1.911015e+03, -1.995905e+03,
      -2.085595e+03, -2.180595e+03, -2.281470e+03, -2.388845e+03,
      -2.503415e+03, -2.625955e+03, -2.757325e+03, -2.898480e+03,
      -3.050485e+03, -3.214515e+03, -3.391875e+03, -3.584005e+03,
      -3.792495e+03, -4.019105e+03, -4.265775e+03, -4.534630e+03,
      -4.828000e+03, -5.148440e+03, -5.498725e+03, -5.881880e+03,
      -6.301185e+03, -6.760170e+03]
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
