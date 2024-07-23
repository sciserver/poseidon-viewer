<template>
  <v-app>
    <notifications position="bottom center" group="notify"/>

    <v-navigation-drawer v-model="drawerRight" app right width="400">
      <RightDrawer/>
    </v-navigation-drawer>

    <v-main>
      <div id="popup" class="ol-popup">
      <a href="#" id="popup-closer" class="ol-popup-closer"></a>
      <div id="popup-content"></div>
      </div>
      <OpenLayers/>


      <v-btn
        fab
        dark
        x-small
        color="primary"
        class="button-right"
        @click="drawerRight = !drawerRight"
      >
        <v-icon dark>
          mdi-menu
        </v-icon>
      </v-btn>

    </v-main>

  </v-app>
</template>

<script>
import OpenLayers from './components/OpenLayers';
import RightDrawer from './components/RightDrawer';

export default {
  name: 'App',

  components: {
    RightDrawer,
    OpenLayers
  },

  data: () => ({
    drawerRight: false
  }),

  mounted() {
    setTimeout(() => { this.drawerRight = true; }, 0);
  }
};
</script>

<style scoped>
.button-left {
  position: absolute;
  bottom: 16px;
  left: 16px;
}
.button-right {
  position: absolute;
  bottom: 16px;
  right: 16px;
}

      .ol-popup {
        position: absolute;
        background-color: white;
        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #cccccc;
        bottom: 12px;
        left: -50px;
        min-width: 280px;
      }
      .ol-popup:after, .ol-popup:before {
        top: 100%;
        border: solid transparent;
        content: " ";
        height: 0;
        width: 0;
        position: absolute;
        pointer-events: none;
      }
      .ol-popup:after {
        border-top-color: white;
        border-width: 10px;
        left: 48px;
        margin-left: -10px;
      }
      .ol-popup:before {
        border-top-color: #cccccc;
        border-width: 11px;
        left: 48px;
        margin-left: -11px;
      }
      .ol-popup-closer {
        text-decoration: none;
        position: absolute;
        top: 2px;
        right: 8px;
      }
      .ol-popup-closer:after {
        content: "✖";
      }
</style>
