<template>
  <v-app>
    <notifications position="bottom center" group="notify"/>

    <v-navigation-drawer v-model="drawerRight" app right width="400">
      <RightDrawer/>
    </v-navigation-drawer>
    
    <v-main>
      
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
</style>