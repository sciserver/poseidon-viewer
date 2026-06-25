<template>
  <v-app>
    <notifications position="bottom center" group="notify" />

    <v-navigation-drawer
      v-model="drawerRight"
      :app="!isMobile"
      :right="!isMobile"
      :bottom="isMobile"
      :temporary="isMobile"
      :fixed="isMobile"
      :width="isMobile ? '100%' : 400"
      :height="isMobile ? '70vh' : '100%'"
    >
      <RightDrawer />
    </v-navigation-drawer>

    <v-main>
      <div id="popup" class="ol-popup">
        <a href="#" id="popup-closer" class="ol-popup-closer"></a>
        <div id="popup-content"></div>
      </div>

      <OpenLayers />

      <v-tooltip right>
        <template v-slot:activator="{ on, attrs }">
          <v-container v-bind="attrs" v-on="on">
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
          </v-container>
        </template>
        <span>Toggle control panel display</span>
      </v-tooltip>
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

  computed: {
    isMobile() {
      return this.$vuetify.breakpoint.smAndDown;
    }
  },

  mounted() {
    // Open the drawer by default only on desktop
    if (!this.isMobile) {
      setTimeout(() => {
        this.drawerRight = true;
      }, 0);
    }
  }
};
</script>

<style scoped>
.button-right {
  position: fixed;
  right: 16px;
  bottom: 16px;
  z-index: 2000;
}

@media (max-width: 600px) {
  .button-right {
    width: 56px;
    height: 56px;
  }
}
</style>
