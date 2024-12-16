<template>
  <v-container>
    <v-form>

    <v-container>
    <v-row align="center">
    <v-col>
    <a href="https://www.poseidon-ocean.net/" target="_blank" tooltip="Poseidon project website">
      <v-img
        :width="180"
        src="../assets/poseidon_logo_web.png"
      ></v-img>
    </a>
    </v-col>
    <v-spacer></v-spacer>

    <v-col>
    <a href="https://github.com/sciserver/poseidon-viewer" target="_blank">
      <v-img
        :width="50"
        src="../assets/github-mark.png"
      ></v-img>
    </a>
    </v-col>
    <v-spacer></v-spacer>

    <v-col>
    <a href="https://sciserver.github.io/poseidon-viewer/intro.html" target="_blank">
      <v-img
        :width="50"
        src="../assets/jb_logo-square.svg"
      ></v-img>
    </a>
    </v-col>
    </v-row>
    </v-container>

    <v-divider style="margin: 8px 0 8px 0"/>

      <v-tooltip left>
      <template v-slot:activator="{ on, attrs }">
      <v-container
        v-bind="attrs"
        v-on="on"
      >
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
      </v-container>
      </template>
      <span>Select variable</span>
      </v-tooltip>

      <v-tooltip left>
      <template v-slot:activator="{ on, attrs }">
      <v-container
        v-bind="attrs"
        v-on="on"
      >
      <v-select
        v-model="colormap"
        :items="colormaps"
        label="colormap"
        dense
        outlined
      ></v-select>
      </v-container>
      </template>
      <span>Select colormap</span>
      </v-tooltip>

      <v-divider style="margin: 8px 0 8px 0"/>

          {{variable.units}}<v-img contain :src="colormapUrl" />

      <v-tooltip left>
      <template v-slot:activator="{ on, attrs }">
      <v-container
        v-bind="attrs"
        v-on="on"
      >
      <v-slider v-model="tempMin" :min="variable.vmin" :max="variable.vmax" :step="variable.step" :label="'min ['+variable.units+']'" class="align-center" @end="updateValues()">
        <template v-slot:append>
          <v-text-field
            v-model="tempMin"
            type="number"
            :step="variable.step"
            style="width: 80px"
            @change="updateValues()"
          ></v-text-field>
        </template>
      </v-slider>
      </v-container>
      </template>
      <span>Select minimum value</span>
      </v-tooltip>

      <v-tooltip left>
      <template v-slot:activator="{ on, attrs }">
      <v-container
        v-bind="attrs"
        v-on="on"
      >
      <v-slider v-model="tempMax" :min="variable.vmin" :max="variable.vmax" :step="variable.step" :label="'max ['+variable.units+']'" class="align-center" @end="updateValues()">
        <template v-slot:append>
          <v-text-field
            v-model="tempMax"
            type="number"
            :step="variable.step"
            style="width: 80px"
            @change="updateValues()"
          ></v-text-field>
        </template>
      </v-slider>
      </v-container>
      </template>
      <span>Select maximum value</span>
      </v-tooltip>
      <v-divider style="margin: 8px 0 8px 0"/>

      <v-tooltip left>
      <template v-slot:activator="{ on, attrs }">
      <v-container
        v-bind="attrs"
        v-on="on"
      >
      <v-range-slider
        v-model="tempTimestamp"
        :max="maxTimestamp"
        label="timestamp"
        class="align-center"
        @end="updateValues()"
        style="max-height:50px"
        hide-details="true"
      >
        <template v-slot:append>
          <v-text-field
            v-model="tempTimestamp[0]"
            type="number"
            style="width: 60px"
            @change="updateValues()"
          ></v-text-field>
          <v-text-field
            v-model="tempTimestamp[1]"
            type="number"
            style="width: 60px"
            @change="updateValues()"
          ></v-text-field>
        </template>
      </v-range-slider>
      </v-container>
      </template>
      <span>Select time span</span>
      </v-tooltip>
      <p> From: {{getPrettyDate(tempTimestamp[0])}} (shown)</p>
      <p> To:&nbsp; &nbsp; &nbsp; {{getPrettyDate(tempTimestamp[1])}} </p>
      <v-tooltip left>
      <template v-slot:activator="{ on, attrs }">
      <v-container
        v-bind="attrs"
        v-on="on"
      >
      <v-row style="margin-top:16px">
        <v-col class="col-12">
          <v-row align="center">
            <v-text-field
              label="step"
              v-model="step"
              type="number"
              style="max-width: 60px; margin-left: 12px; margin-right: 12px"
            ></v-text-field> hours
            <v-btn icon @click="decreaseTimestamp()" style="margin-left: 16px">
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
      </v-container>
      </template>
      <span>Select time step</span>
      </v-tooltip>

      <v-divider style="margin: 16px 0 8px 0"/>
      <v-tooltip left>
      <template v-slot:activator="{ on, attrs }">
      <v-container
        v-bind="attrs"
        v-on="on"
      >
      <v-slider
        v-model="tempDepth"
        :max="maxDepth"
        label="depth"
        class="align-center"
        hide-details="true"
        @end="updateValues()"
        style="max-height:50px"
      >
        <template v-slot:append>
          <v-text-field
            v-model="tempDepth"
            type="number"
            style="width: 60px"
            @change="updateValues()"
          ></v-text-field>
        </template>

      </v-slider>
      </v-container>
      </template>
      <span>Select depth level</span>
      </v-tooltip>
      Depth: {{z_levels[tempDepth]}} m
      <!--
      <v-checkbox
        v-model="showVelocity"
        label="Velocity (animation demo)"
      ></v-checkbox>
      -->
     <v-tooltip left>
      <template v-slot:activator="{ on, attrs }">
      <v-container
        v-bind="attrs"
        v-on="on"
      >
      <v-checkbox
        v-model="showGrid"
        label="Show grid"
      ></v-checkbox>
      </v-container>
      </template>
      <span>Toggle grid display</span>
      </v-tooltip>
      <v-divider style="margin: 16px 0 8px 0"/>

      <p class="text-right">
      Click anywhere to see the spot value of the field.
    </p>

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
    colormapUrl: '',

    tempMin: Number(),
    tempMax: Number(),
    tempTimestamp: [0,0],
    tempDepth: Number(),
  }),
  computed: {
    ...mapState(["maxTimestamp", "variables", "colormaps", "maxDepth","z_levels"]),
    ...mapFields(["timestamp","timestamp2", "depth", "variable", "colormap", "min", "max", "showVelocity", "showGrid"]),
  },
  mounted() {
    this.variable = this.variables[0];
    this.tempTimestamp = [0, this.maxTimestamp];
  },
  watch: {
    variable: function() {
      this.tempMin = this.variable.defaultMin ?? this.variable.vmin;
      this.tempMax = this.variable.defaultMax ?? this.variable.vmax;
      if (this.variable.name == 'vorticity') {
        this.colormap = 'seismic'
      }
      else if (this.variable.name == 'temperature' || this.variable.name == 'Eta') {
        this.colormap = 'RdBu_r'
      }
      else if (this.variable.name == 'salinity') {
        this.colormap = 'cmo.haline'
      }
      else {
        this.colormap = 'viridis'
      }
      this.updateColormapUrl();
      this.updateValues();
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
    getPrettyDate(h) {
      var d = new Date(Date.parse('2012-04-25T00:00:00.000000Z'))
      d.setHours(d.getHours()+h)
      const formattedDate = `${d.getFullYear()}-${d.getMonth().toString().padStart(2, '0')}-${d.getDay().toString().padStart(2, '0')} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2, '0')}Z`;
      return formattedDate
    },
    updateValues() {
      this.min = this.tempMin;
      this.max = this.tempMax;
      this.depth = this.tempDepth;
      this.timestamp = this.tempTimestamp[0];
      this.timestamp2 = this.tempTimestamp[1];
    },
    updateColormapUrl() {
      this.colormapUrl = process.env.VUE_APP_SERVICE_URL + `/api/colormap?vmin=${this.min}&vmax=${this.max}&colormap=${this.colormap}`;
    },
    increaseTimestamp() {
      if (Number(this.tempTimestamp[0]) + Number(this.step) <= this.maxTimestamp) {
        //this.tempTimestamp[0] = Number(this.tempTimestamp[0]) + Number(this.step);
        this.$set(this.tempTimestamp,0,Number(this.tempTimestamp[0]) + Number(this.step));
      } else {
        this.$set(this.tempTimestamp,0,this.maxTimestamp);
      }
      this.updateValues();
    },
    decreaseTimestamp() {
      if (Number(this.tempTimestamp[0]) - Number(parseInt(this.step)) >= 0) {
        this.$set(this.tempTimestamp,0,Number(this.tempTimestamp[0]) - Number(this.step));
      } else {
        this.$set(this.tempTimestamp,0,0);
      }
      this.updateValues();
    },
    /*
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
    */
  },
};
</script>
