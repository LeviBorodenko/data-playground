<template>
  <div id="app">
    <componentMain></componentMain>
  </div>
</template>

<script>
import M from 'materialize-css';

import componentMain from './components/main.vue';


export default {
  name: 'App',
  components: {
    componentMain,
  },
  mounted() {
    M.AutoInit();
  },
};
</script>

<style lang="scss">
</style>
