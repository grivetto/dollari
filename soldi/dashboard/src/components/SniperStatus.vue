
<template>
  <div :class="{ active: status === 'ACTIVE', error: status !== 'ACTIVE' }">
    <h3>Sniper Status</h3>
    <p>{{ status }}</p>
  </div>
</template>

<script>
export default {
  name: 'SniperStatus',
  props: ['status']
};
</script>

<style scoped>
.active { color: green; }
.error { color: red; }
</style>
