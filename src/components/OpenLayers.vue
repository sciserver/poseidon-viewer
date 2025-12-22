<template>
  <div id="map" class="map"></div>

</template>

<script>
import Map from "ol/Map";
import { Tile as TileLayer, Vector as VectorLayer, Graticule } from 'ol/layer';
import { XYZ, TileDebug, Vector as VectorSource } from 'ol/source';
import View from "ol/View";
import 'ol/ol.css';
import { mapState } from "vuex";
import { mapFields } from "vuex-map-fields";
import { WindLayer } from 'ol-wind';
import data from '../assets/wind';
import { Modify, Select, Draw } from 'ol/interaction';
import { Style, Stroke, Fill, Circle } from 'ol/style';
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
import Overlay from 'ol/Overlay';
import {toLonLat} from 'ol/proj';
import {toStringHDMS} from 'ol/coordinate';
import numeral from 'numeral';
export default {
  data: () => ({
      map: null,
      layer: null,
      windData: data,
      windLayer: null,
      vectorLayer: null,
      gridLayer: null,
      overlay: null,
      content: null,
      overlayEnabled: true,
      toolButtons: {
        drawPolygon: null,
        drawLine: null,
        select: null,
        delete: null,
        store: null
      },
      interactions: {
        select: null,
        modify: null,
        drawPolygon: null,
        drawPoint: null
      },
      geoFormat: new GeoJSON()
  }),
  computed: {
    ...mapState(["maxTimestamp", "variables", "colormaps", "maxDepth","z_levels"]),
    ...mapFields(["timestamp","timestamp2", "depth", "variable", "colormap", "min", "max", "showVelocity", "showGrid"]),
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
    },
    showGrid() {
      this.gridLayer.setVisible(this.showGrid)
    }
  },
  methods: {
    getPrettyDate(h) {
      var d = new Date(Date.parse('2012-04-25T00:00:00.000000Z'))
      d.setHours(d.getHours()+h)
      const formattedDate = `${d.getFullYear()}-${d.getMonth().toString().padStart(2, '0')}-${d.getDay().toString().padStart(2, '0')} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2, '0')}Z`;
      return formattedDate
    },
    getDate(h) {
      var d = new Date(Date.parse('2012-04-25T00:00:00.000000Z'))
      d.setHours(d.getHours()+h)
      return d.toISOString()
    },
    getUrlTemplate() {
        return process.env.VUE_APP_SERVICE_URL + `/api/values/${this.variable.name}/${this.timestamp.toString().padStart(4,'0')}/{z}/{x}/{y}/${this.depth}?colormap=${this.colormap}&min=${this.min}&max=${this.max}`;
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
      const container = document.getElementById('popup');
      this.content = document.getElementById('popup-content');
      console.log(this.content)
      const closer = document.getElementById('popup-closer');
      const that = this
      closer.onclick = function () {
        that.overlay.setPosition(undefined);
        closer.blur();
        return false;
      };
      this.overlay = new Overlay({
        element: container,
        autoPan: {
          animation: {
            duration: 250,
          },
        },
      });
      this.map = new Map({
        overlays: [this.overlay],
        controls: defaultControls().extend([ mousePositionControl ]),
        target: "map",
        layers: [
          this.layer = new TileLayer({
            source: new XYZ({
              url: this.getUrlTemplate(),
            }),
            // visible: false
          }),
          this.gridLayer = new Graticule({
            // the style to use for the lines, optional.
            strokeStyle: new Stroke({
              color: 'rgba(255,120,0,0.7)',
              width: 2,
              lineDash: [0.5, 4],
            }),
            showLabels: true,
            //wrapX: false,
            visible: this.showGrid
          }),
          this.vectorLayer = new VectorLayer({
            source: new VectorSource({wrapX: false}),
            style: new Style({
              fill: new Fill({
                color: 'rgba(255, 255, 255, 0.2)',
              }),
              stroke: new Stroke({
                color: '#FF8C00',
                width: 2,
              }),
              image: new Circle({
                radius: 6,
                fill: new Fill({color: '#FF8C00'})
              })
            }),
            visible: true,
          }),
          this.debugLayer = new TileLayer({
            source: new TileDebug(),
            visible: false
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

      this.map.on('singleclick', function (event) {
        if (that.overlayEnabled) {
          const coordinate = event.coordinate;
          const hdms = toStringHDMS(toLonLat(coordinate));

          //that.content.innerHTML = '<p>You clicked here:</p><code>' + hdms + '</code>';
          //that.overlay.setPosition(coordinate);

          const grid = that.layer.getSource().getTileGrid();
          const tileCord = grid.getTileCoordForCoordAndZ(event.coordinate, Math.floor(that.map.getView().getZoom()));
          const extent = that.layer.getSource().getTileGrid().getTileCoordExtent(tileCord);
          const a = event.coordinate[0] - extent[0]
          const b = - event.coordinate[1] + extent[3]
          const st = that.layer.getSource().getTileGrid().getTileSize()
          const se = extent[2] - extent[0]
          const theseUnits = that.variable.units
          const thisDateTime = that.getPrettyDate(that.timestamp)
          const thisDepth = that.z_levels[that.depth]

          let newX = tileCord[1] % Math.pow(2, tileCord[0])
          if (newX < 0) {
            newX = Math.pow(2, tileCord[0]) + newX;
          }
          let format_str = '0.000'
          if (that.variable.name=="vorticity") {
             format_str = '0.000e+0'
          }
          console.log(format_str)

          axios.get(process.env.VUE_APP_SERVICE_URL + `/api/val/${that.variable.name}/${that.timestamp.toString().padStart(4,'0')}/${tileCord[0]}/${newX}/${tileCord[2]}/${that.depth}?x=${Math.floor(a/se*st)}&y=${Math.floor(b/se*st)}`)
          .then(function(response) {
              that.content.innerHTML = that.variable.label + ' at:</br>' + thisDateTime + ', ' + numeral(thisDepth).format('0.0') + 'm,</br>' +  hdms + '</br>= ' + numeral(response.data.value).format(format_str) + '&nbsp' + theseUnits;
              that.overlay.setPosition(coordinate);
              //console.log(response.data)
          })
        }
      });

      /*
      this.map.on('click', function(event) {
        const grid = that.layer.getSource().getTileGrid();
        const tileCord = grid.getTileCoordForCoordAndZ(event.coordinate, Math.floor(that.map.getView().getZoom()));
        const extent = that.layer.getSource().getTileGrid().getTileCoordExtent(tileCord);
        //console.log('clicked ', event.coordinate[0], event.coordinate[1]);
        //console.log('tile z,x,y is:', tileCord[0], tileCord[1], tileCord[2]);
        const a = event.coordinate[0] - extent[0]
        const b = - event.coordinate[1] + extent[3]
        const st = that.layer.getSource().getTileGrid().getTileSize()
        const se = extent[2] - extent[0]
        //console.log([a/se*st,b/se*st])

        //console.log(extent)
      });
      */
    },

    addToolBar() {
      const controlBar = new Bar({ position: "top" });
      this.map.addControl(controlBar);

      this.toolButtons.drawPoint = new Toggle({
        html: '<i class="mdi mdi-vector-point" title="Select stations with points"></i>',
				onToggle: (active) => {
          this.toggleDrawPoint(active);
        }
      });
      controlBar.addControl(this.toolButtons.drawPoint);

      this.toolButtons.drawLine = new Toggle({
        html: '<i class="mdi mdi-vector-polyline" title="Draw section with line segments"></i>',
				onToggle: (active) => {
          this.toggleDrawLine(active);
        }
      });
      controlBar.addControl(this.toolButtons.drawLine);

      this.toolButtons.drawPolygon = new Toggle({
        html: '<i class="mdi mdi-vector-polygon" title="Draw region with a polygon"></i>',
				onToggle: (active) => {
          this.toggleDrawPolygon(active);
        }
      });
      controlBar.addControl(this.toolButtons.drawPolygon);

      this.toolButtons.select = new Toggle({
        html: '<i class="fas fa-hand-pointer" title="Select a drawing element"></i>',
        onToggle: (active) => {
          this.toggleSelect(active);
        }
      });
      controlBar.addControl(this.toolButtons.select);

      this.toolButtons.delete = new Button({
        html: '<i class="fas fa-trash-alt" title="Delete drawing element"></i>',
        handleClick: () => {
          this.removeSelected();
        },
      });
      controlBar.addControl(this.toolButtons.delete);

      this.toolButtons.export = new Button({
        html: '<i class="fas fa-file-import" title="Copy drawing element shape to clipboard"></i>',
        handleClick: () => {
          this.exportSelected();
        },
      });
      controlBar.addControl(this.toolButtons.export);

      this.toolButtons.store = new Button({
        html: '<i class="mdi mdi-tray-arrow-down" title="Store drawing element shape"></i>',
        handleClick: () => {
          this.storeSelected();
        },
      });
      controlBar.addControl(this.toolButtons.store);

    },

    resetInteractions() {
      this.toolButtons.drawPolygon.setActive(false);
      this.toolButtons.drawLine.setActive(false);
      this.toolButtons.drawPoint.setActive(false);
      this.toolButtons.select.setActive(false);
      this.map.removeInteraction(this.interactions.drawPolygon);
      this.map.removeInteraction(this.interactions.drawLine);
      this.map.removeInteraction(this.interactions.drawPoint);
      this.map.removeInteraction(this.interactions.modify);
      this.map.removeInteraction(this.interactions.select);
      this.overlayEnabled = true;
    },

    toggleDrawPolygon(active) {
      if (active !== null) {
        this.resetInteractions();
        this.toolButtons.drawPolygon.setActive(active); // setting "active" property does not trigger "onToggle"
      }

      this.map.removeInteraction(this.interactions.drawPolygon);
      this.map.removeInteraction(this.interactions.modify);

      if (this.toolButtons.drawPolygon.getActive(active)) {
        this.overlayEnabled = false;
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

    toggleDrawLine(active) {
      if (active !== null) {
        this.resetInteractions();
        this.toolButtons.drawLine.setActive(active); // setting "active" property does not trigger "onToggle"
      }

      this.map.removeInteraction(this.interactions.drawLine);
      this.map.removeInteraction(this.interactions.modify);

      if (this.toolButtons.drawLine.getActive(active)) {
        this.overlayEnabled = false;
        this.interactions.drawLine = new Draw({
          source: this.vectorLayer.getSource(),
          type:'LineString',
        });

        this.interactions.modify = new Modify({
          source: this.vectorLayer.getSource()
        });

        this.map.addInteraction(this.interactions.drawLine);
        this.map.addInteraction(this.interactions.modify);
      }
    },

    toggleDrawPoint(active) {
      if (active !== null) {
        this.resetInteractions();
        this.toolButtons.drawPoint.setActive(active); // setting "active" property does not trigger "onToggle"
      }

      this.map.removeInteraction(this.interactions.drawPoint);
      this.map.removeInteraction(this.interactions.modify);

      if (this.toolButtons.drawPoint.getActive(active)) {
        this.overlayEnabled = false;
        this.interactions.drawPoint = new Draw({
          source: this.vectorLayer.getSource(),
          type:'Point',
        });

        this.interactions.modify = new Modify({
          source: this.vectorLayer.getSource()
        });

        this.map.addInteraction(this.interactions.drawPoint);
        this.map.addInteraction(this.interactions.modify);
      }
    },

    toggleSelect(active) {
      if (active !== null) {
        this.resetInteractions()
        this.toolButtons.select.setActive(active) // setting "active" property does not trigger "onToggle"
      }

      if (this.toolButtons.select.getActive(active)) {
        this.overlayEnabled = false;
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
      let obj =
      {
        type: "FeatureCollection",
        features: []
      };
      this.interactions.select.getFeatures().forEach((f) => obj.features.push({
        type: "Feature",
        properties: {
          timeFrom: this.getDate(this.timestamp),
          timeTo: this.getDate(this.timestamp2)
        },
        geometry: JSON.parse(this.geoFormat.writeGeometry(f.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326')))
      }));
      copyTextToClipboard(JSON.stringify(obj));
    },

    storeSelected() {
      let obj =
      {
        type: "FeatureCollection",
        features: []
      };
      this.interactions.select.getFeatures().forEach((f) => obj.features.push({
        type: "Feature",
        properties: {
          timeFrom: this.getDate(this.timestamp),
          timeTo: this.getDate(this.timestamp2)
        },
        geometry: JSON.parse(this.geoFormat.writeGeometry(f.getGeometry().clone().transform('EPSG:3857', 'EPSG:4326')))
      }));
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
