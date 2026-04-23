
<template>
  <div id="app">
    <Dashboard />
  </div>
</template>

<script>
import { createApp } from 'vue';
import Dashboard from './components/Dashboard.vue';

createApp(Dashboard).mount('#app');
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
