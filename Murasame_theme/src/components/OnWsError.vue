<template>
  <p>
    Websocket连接断开，服务器信息将不会更新
  </p>
</template>
<script lang="ts">
import {defineComponent} from 'vue';

export default defineComponent({
  name: 'OnWs'
});
</script>
<style scoped>
p {
  text-align: center;
  color: #616366;
  margin-bottom: 0;
}
</style>
