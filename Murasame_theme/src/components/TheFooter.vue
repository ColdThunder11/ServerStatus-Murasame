<template>
  <p>Powered by <a
      href="https://github.com/ColdThunder11/ServerStatus-Murasame">ServerStatus-Murasame</a></p>
  <p><a href="https://github.com/ColdThunder11/ServerStatus-Murasame">manage</a></p>
</template>

<script lang="ts">
import {defineComponent} from 'vue';

export default defineComponent({
  name: 'TheFooter'
});
</script>

<style scoped>
p {
  text-align: center;
  padding-bottom: 15px;
}

p a {
  vertical-align: middle;
}

p a:hover {
  color: #ff779a;
}
</style>
