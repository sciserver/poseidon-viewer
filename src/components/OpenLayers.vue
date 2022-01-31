<template>
  <div id="map" class="map"></div>
</template>

<script>
import Map from "ol/Map";
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer';
import { XYZ, Vector as VectorSource } from 'ol/source';
import View from "ol/View";
import 'ol/ol.css';
import { mapFields } from "vuex-map-fields";
import { WindLayer } from 'ol-wind';
import data from '../assets/wind';
import { Modify, Select, Draw } from 'ol/interaction';
import { Style, Stroke, Fill } from 'ol/style';
import { defaults as defaultControls, MousePosition } from 'ol/control';
import 'ol-ext/dist/ol-ext.css';
import Bar from 'ol-ext/control/Bar';
import Toggle from 'ol-ext/control/Toggle';
import Button from 'ol-ext/control/Button';
// import WKT from 'ol/format/WKT';
import GeoJSON from 'ol/format/GeoJSON';
import { copyTextToClipboard } from '../clipboard.js';
import { format as coordinateFormat } from 'ol/coordinate';
import axios from 'axios';

export default {
  data: () => ({
      map: null,
      layer: null,
      windData: data,
      windLayer: null,
      vectorLayer: null,
      toolButtons: {
        drawPolygon: null,
        select: null,
        delete: null,
        store: null
      },
      interactions: {
        select: null,
        modify: null,
        drawPolygon: null
      },
      geoFormat: new GeoJSON()
  }),
  computed: {
      ...mapFields(['timestamp', 'depth', 'variable', 'colormap', 'min', 'max', 'showVelocity'])
  },
  mounted() {
    this.init();
  },
  watch: {
    timestamp() {
        this.updateUrlTemplate();
    },
    depth() {
        this.updateUrlTemplate();  
    },
    variable() {
        this.updateUrlTemplate();
    },
    colormap() {
        this.updateUrlTemplate();
    },
    min() {
      this.updateUrlTemplate();
    },
    max() {
      this.updateUrlTemplate();
    },
    showVelocity() {
      this.windLayer.setVisible(this.showVelocity)
    }
  },
  methods: {
    getUrlTemplate() {
        return process.env.VUE_APP_SERVICE_URL + `/api/values/${this.variable}/${this.timestamp.toString().padStart(4,'0')}/{z}/{x}/{y}/${this.depth}?colormap=${this.colormap}&min=${this.min}&max=${this.max}`;
    },
    updateUrlTemplate() {
        this.layer.getSource().setUrl(this.getUrlTemplate())
    },
    init() {
      const mousePositionControl = new MousePosition({
        coordinateFormat: function(coordinate) {
          return coordinateFormat(coordinate, '{y}, {x}', 4);
        },
        projection: 'EPSG:4326',
        className: 'custom-mouse-position',
        undefinedHTML: '&nbsp;'
      });
      this.map = new Map({
        controls: defaultControls().extend([ mousePositionControl ]),
        target: "map",
        layers: [
          this.layer = new TileLayer({
            source: new XYZ({
              url: this.getUrlTemplate(),
            }),
          }),
          this.vectorLayer = new VectorLayer({
            source: new VectorSource(),
            style: new Style({
              fill: new Fill({
                color: 'rgba(255, 255, 255, 0.2)',
              }),
              stroke: new Stroke({
                color: '#FF8C00',
                width: 2,
              }),
            }),
            visible: true,
          }),
        ],
        view: new View({
          center: [0, 0],
          zoom: 0,
          minZoom: 0,
          maxZoom: 6,
        }),
      });
      
      this.addToolBar();



      this.windLayer = new WindLayer(this.windData, {
        wrapX: true,
        forceRender: false,
        visible: this.showVelocity,
        windOptions: {
          velocityScale: 0.01,
          paths: 10000,
          lineWidth: 1,
        },
      });

      this.map.addLayer(this.windLayer);

    },

    addToolBar() {
      const controlBar = new Bar({ position: "top" });
      this.map.addControl(controlBar);

      this.toolButtons.drawPolygon = new Toggle({	
        html: '<i class="fas fa-draw-polygon"></i>',
				onToggle: (active) => {	
          this.toggleDrawPolygon(active);
        }
      });
      controlBar.addControl(this.toolButtons.drawPolygon);

      this.toolButtons.select = new Toggle({	
        html: '<i class="fas fa-hand-pointer"></i>',
        onToggle: (active) => {	
          this.toggleSelect(active);
        }
      });
      controlBar.addControl(this.toolButtons.select);

      this.toolButtons.delete = new Button({
        html: '<i class="fas fa-trash-alt"></i>',
        handleClick: () => {	
          this.removeSelected();
        },
      });
      controlBar.addControl(this.toolButtons.delete);

      this.toolButtons.export = new Button({
        html: '<i class="fas fa-file-import"></i>',
        handleClick: () => {	
          this.exportSelected();
        },
      });
      controlBar.addControl(this.toolButtons.export);

      this.toolButtons.store = new Button({
        html: '<i class="mdi mdi-tray-arrow-down"></i>',
        handleClick: () => {	
          this.storeSelected();
        },
      });
      controlBar.addControl(this.toolButtons.store);

    },

    resetInteractions() {
      this.toolButtons.drawPolygon.setActive(false);
      this.toolButtons.select.setActive(false);
      this.map.removeInteraction(this.interactions.drawPolygon);
      this.map.removeInteraction(this.interactions.modify);
      this.map.removeInteraction(this.interactions.select);
    },

    toggleDrawPolygon(active) {
      if (active !== null) {
        this.resetInteractions();
        this.toolButtons.drawPolygon.setActive(active); // setting "active" property does not trigger "onToggle"
      }

      this.map.removeInteraction(this.interactions.drawPolygon);
      this.map.removeInteraction(this.interactions.modify);

      if (this.toolButtons.drawPolygon.getActive(active)) {
        this.interactions.drawPolygon = new Draw({   
          source: this.vectorLayer.getSource(),
          type:'Polygon',
        });

        this.interactions.modify = new Modify({
          source: this.vectorLayer.getSource() 
        });

        this.map.addInteraction(this.interactions.drawPolygon);
        this.map.addInteraction(this.interactions.modify);
      }
    },

    toggleSelect(active) {
      if (active !== null) {
        this.resetInteractions()
        this.toolButtons.select.setActive(active) // setting "active" property does not trigger "onToggle"
      }

      if (this.toolButtons.select.getActive(active)) {
        this.interactions.select = new Select({
          layers: [this.vectorLayer]
        });

        this.map.addInteraction(this.interactions.select);
      }
    },

    removeSelected() {
      this.interactions.select.getFeatures().forEach((f) => this.vectorLayer.getSource().removeFeature(f));
    },

    exportSelected() {
      let obj = [];
      this.interactions.select.getFeatures().forEach((f) => obj.push(JSON.parse(this.geoFormat.writeGeometry(f.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326')))));
      copyTextToClipboard(JSON.stringify(obj));
    },

    storeSelected() {
      let obj = [];
      this.interactions.select.getFeatures().forEach((f) => obj.push(JSON.parse(this.geoFormat.writeGeometry(f.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326')))));
      axios.post(process.env.VUE_APP_SERVICE_URL + '/api/shapes', obj)
          .then(() => {
            this.$notify({
              group: 'notify',
              type: 'success',
              duration: 1000,
              position: 'bottom center',
              text: 'Shapes stored'
            });
          })
          .catch((error) => {
            this.$notify({
              group: 'notify',
              type: 'error',
              duration: 1000,
              position: 'bottom center',
              text: error
            });
          });
    }
  },
};
</script>

<style scoped>
.map {
  height: 100%
}

.map::v-deep .ol-control.ol-bar .ol-toggle.ol-active > button {
  background: rgba(245, 45, 45, 0.7)
}

.map::v-deep .ol-control.ol-bar .ol-toggle.ol-active:hover > button {
  background: rgba(245, 45, 45, 0.7)
}

.map::v-deep .custom-mouse-position {
  text-align: right;
  padding-right: 4px;
  color: #FF8C00;
}
</style>
