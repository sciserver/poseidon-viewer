<template>
  <v-container>
    <v-form>
      <v-select
        v-model="variable"
        :items="variables"
        :item-text="'label'"
        label="variable"
        dense
        outlined
        return-object
      >
      </v-select>
      <v-select
        v-model="colormap"
        :items="colormaps"
        label="colormap"
        dense
        outlined
      ></v-select>
          {{variable.units}}<v-img contain :src="colormapUrl" />
      <v-slider v-model="min" :min="variable.vmin" :max="variable.vmax" :step="(variable.vmax-variable.vmin)/255.0" :label="'min'" class="align-center">
        <template v-slot:append>
          <v-text-field
            v-model="min"
            type="number"
            style="width: 80px"
          ></v-text-field>
        </template>
      </v-slider>
      <v-slider v-model="max" :min="variable.vmin" :max="variable.vmax" :step="(variable.vmax-variable.vmin)/255.0" :label="'max'" class="align-center">
        <template v-slot:append>
          <v-text-field
            v-model="max"
            type="number"
            style="width: 80px"
          ></v-text-field>
        </template>
      </v-slider>
      <v-slider
        v-model="timestamp"
        :max="maxTimestamp"
        label="timestamp"
        class="align-center"
      >
        <template v-slot:append>
          <v-text-field
            v-model="timestamp"
            type="number"
            style="width: 60px"
          ></v-text-field>
        </template>
      </v-slider>

      <v-slider
        v-model="depth"
        :max="maxDepth"
        label="depth"
        class="align-center"
      >
        <template v-slot:append>
          <v-text-field
            v-model="depth"
            type="number"
            style="width: 60px"
          ></v-text-field>
        </template>
      </v-slider>

      <v-row>
        <v-col class="col-6">
          <v-row align="center">
            <v-text-field
              label="step"
              v-model="step"
              type="number"
              style="max-width: 60px; margin-left: 12px; margin-right: 12px"
            ></v-text-field>
            <v-btn icon @click="decreaseTimestamp()">
              <v-icon>mdi-rewind</v-icon>
            </v-btn>
            <v-btn icon @click="increaseTimestamp()">
              <v-icon>mdi-fast-forward</v-icon>
            </v-btn>
            <!--
            <v-btn icon @click="toggleTimer()">
              <v-icon id="play">{{ icon }}</v-icon>
            </v-btn>
            -->
          </v-row>
        </v-col>
      </v-row>

      <!--
      <v-checkbox
        v-model="showVelocity"
        label="Velocity (animation demo)"
      ></v-checkbox>
      -->
    </v-form>
  </v-container>
</template>

<script>
import { mapState } from "vuex";
import { mapFields } from "vuex-map-fields";

export default {
  data: () => ({
    step: 10,
    timer: null,
    icon: "mdi-play",
    colormapUrl: ''
  }),
  computed: {
    ...mapState(["maxTimestamp", "variables", "colormaps", "maxDepth"]),
    ...mapFields(["timestamp", "depth", "variable", "colormap", "min", "max", "showVelocity"]),
  },
  mounted() {
    this.variable = this.variables[0];
  },
  watch: {
    variable: function() { 
      this.min = this.variable.vmin;
      this.max = this.variable.vmax;
      if (this.variable.name == 'velocity') {
        this.colormap = 'seismic'
      } 
      else if (this.variable.name == 'SST' || this.variable.name == 'Eta') {
        this.colormap = 'RdBu_r'
      }
      else if (this.variable.name == 'SSS') {
        this.colormap = 'cmo.haline'
      }
      else {
        this.colormap = 'viridis'
      }
      this.updateColormapUrl();
    },
    min() {
      this.updateColormapUrl();
    },
    max() {
      this.updateColormapUrl();
    },
    colormap() {
      this.updateColormapUrl();
    }
  },
  methods: {
    updateColormapUrl() {
      this.colormapUrl = process.env.VUE_APP_SERVICE_URL + `/api/colormap?vmin=${this.min}&vmax=${this.max}&colormap=${this.colormap}`;
    },
    increaseTimestamp() {
      if (Number(this.timestamp) + Number(this.step) <= this.maxTimestamp) {
        this.timestamp = Number(this.timestamp) + Number(this.step);
      } else {
        this.timestamp = this.maxTimestamp;
      }
    },
    decreaseTimestamp() {
      if (Number(this.timestamp) - Number(parseInt(this.step)) >= 0) {
        this.timestamp = Number(this.timestamp) - Number(this.step);
      } else {
        this.timestamp = 0;
      }
    },
    handleTimer() {
      if (this.timestamp == this.maxTimestamp) {
        this.cancelTimer();
      } else {
        this.increaseTimestamp();
      }
    },
    cancelTimer() {
      clearInterval(this.timer);
      this.timer = null;
      this.icon = "mdi-play";
    },
    toggleTimer() {
      if (this.timer === null) {
        this.timer = setInterval(this.handleTimer, 500);
        this.icon = "mdi-stop";
      } else {
        this.cancelTimer();
      }
    },
  },
};
</script>