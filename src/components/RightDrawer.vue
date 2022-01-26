<template>
  <v-container>
    <v-form>
      <v-select
        v-model="variable"
        :items="variables"
        :item-text="'label'"
        :item-value="'name'"
        label="variable"
        dense
        outlined
      >
      </v-select>
      <v-select
        v-model="colormap"
        :items="colormaps"
        label="colormap"
        dense
        outlined
      ></v-select>
      <v-slider v-model="min" :min="0" :max="65535" label="value min" class="align-center">
        <template v-slot:append>
          <v-text-field
            v-model="min"
            type="number"
            style="width: 80px"
          ></v-text-field>
        </template>
      </v-slider>
      <v-slider v-model="max" :min="0" :max="65535" label="value max" class="align-center">
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
            <v-btn icon @click="toggleTimer()">
              <v-icon id="play">{{ icon }}</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>

      <v-checkbox
        v-model="showVelocity"
        label="Velocity (animation demo)"
      ></v-checkbox>
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
  }),
  computed: {
    ...mapState(["maxTimestamp", "variables", "colormaps", "maxDepth"]),
    ...mapFields(["timestamp", "depth", "variable", "colormap", "min", "max", "showVelocity"]),
  },
  watch: {
    variable: function() {
      if (this.variable == 'velocity') {
        this.colormap = 'seismic'
      } 
      else if (this.variable == 'SST' || this.variable == 'Eta') {
        this.colormap = 'RdBu_r'
      }
      else if (this.variable == 'SSS') {
        this.colormap = 'cmo.haline'
      }
      else {
        this.colormap = 'viridis'
      }
    }
  },
  methods: {
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