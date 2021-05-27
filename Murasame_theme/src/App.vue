<template>
  <the-header/>
  <on-error v-show="!servers"/>
  <on-ws-error v-show="!isWsAlive"/>
  <servers-table :servers="servers"/>
  <update-time :updated="updated"/>
  <servers-card :servers="servers"/>
  <the-footer/>
</template>

<script lang="ts">
import {defineComponent, ref, onMounted} from 'vue';
import axios from 'axios';
import TheHeader from '@/components/TheHeader.vue';
import OnError from '@/components/OnError.vue';
import OnWsError from '@/components/OnWsError.vue';
import ServersTable from '@/components/ServersTable.vue';
import UpdateTime from '@/components/UpdateTime.vue';
import ServersCard from '@/components/ServersCard.vue';
import TheFooter from '@/components/TheFooter.vue';

export default defineComponent({
  name: 'App',
  components: {
    TheHeader,
    OnError,
    OnWsError,
    ServersTable,
    ServersCard,
    TheFooter,
    UpdateTime
  },
  setup() {
    const servers = ref<Array<StatusItem | BoxItem>>();
    const updated = ref<number>();
    const ws = ref<WebSocket>();
    const isWsAlive = ref<boolean>();
    /*
    onMounted(() => setInterval(() => {
      axios.get('json/stats.json')
          .then(res => {
            const currentTime = Math.round(new Date().getTime()/1000);
            let i = 0;
            for(i=0;i<res.data.servers.length;i++){
              if(isNaN(res.data.servers[i].uptime)) continue
              const uptime = res.data.servers[i].uptime;
              if(uptime<60){
                res.data.servers[i].uptime = Math.round(uptime)+" 秒"
              }
              else if(uptime<60*60){
                res.data.servers[i].uptime = Math.round(uptime/60) + " 分 " + Math.round(uptime%60)+" 秒"
              }
              else if(uptime<60*60*24){
                res.data.servers[i].uptime = Math.round(uptime/(60*60)) + " 时 "+ Math.round((uptime/60)%60) + " 分 "
              }
              else{
                res.data.servers[i].uptime = Math.round(uptime/(60*60*24)) + " 天 " + Math.round(((uptime/(60*60)))%24) + " 时 "
              }
            }
            servers.value = res.data.servers;
            updated.value = Number(res.data.updated);
          })
          .catch(err => console.log(err));
    }, 2000));*/
    //websocket type
    onMounted(() => setInterval(() => {
      const host = window.location.host
        if(!ws.value) {
          try{
            if(window.location.protocol == "http:") ws.value = new WebSocket("ws://"+host+"/ws/stats");
            else ws.value = new WebSocket("wss://"+host+"/ws/stats");
            ws.value.onopen = ()=>{
              console.log('websocket连接成功');
              isWsAlive.value = true;
            }
            ws.value.onclose = (e)=>{
              ws.value = undefined
              isWsAlive.value = false
            }
            ws.value.onerror = (e)=>{
              ws.value = undefined
              isWsAlive.value = false
            }
            ws.value.onmessage = (res)=>{
              const reStatus = JSON.parse(res.data);
              let i = 0;
              for(i=0;i<reStatus.servers.length;i++){
                if(isNaN(reStatus.servers[i].uptime)) continue
                const uptime = reStatus.servers[i].uptime;
                if(uptime<60){
                  reStatus.servers[i].uptime = Math.round(uptime)+" 秒"
                }
                else if(uptime<60*60){
                  reStatus.servers[i].uptime = Math.round(uptime/60) + " 分 " + Math.round(uptime%60)+" 秒"
                }
                else if(uptime<60*60*24){
                  reStatus.servers[i].uptime = Math.round(uptime/(60*60)) + " 小时 "+ Math.round((uptime/60)%60) + " 分 " 
                }
                else{
                  reStatus.servers[i].uptime = Math.round(uptime/(60*60*24)) + " 天 " + Math.round(((uptime/(60*60)))%24) + " 小时 "
                }
              }
              servers.value = reStatus.servers;
              updated.value = Number(reStatus.updated);
            }
          }
          catch{
            isWsAlive.value = false
            ws.value = undefined
          }
        }
        else if(isWsAlive.value) ws.value?.send("get satats")
    }, 2000));
    return {
      servers,
      updated,
      isWsAlive
    };
  }
});
</script>

<style>
body {
  /*Replace your background image at this place!*/
  background: url("./assets/img/bg_parts.png") repeat-y left top, url('./assets/img/bg.png') repeat left top;
}

/*Global*/
div.bar {
  min-width: 0 !important;
}

/*Responsive*/
@media (max-width: 1200px) {
  html, body {
    font-size: 12px;
  }
}

@media only screen and (max-width: 992px) {
  #type, tr td:nth-child(3) {
    display: none;
  }

  #location, tr td:nth-child(4) {
    display: none;
  }
}

@media (max-width: 768px) {
  html, body {
    font-size: 11px;
  }

  #servers div.progress {
    width: 40px !important;
  }

  #cards .card div.card-header span {
    font-size: 1.55rem !important;
  }

  #cards .card div.card-content p {
    font-size: 1.25rem !important;
    margin-bottom: 0.6rem !important;
  }

  #header {
    height: 20rem !important;
    /*Replace your header image (for mobile use) at this place!*/
    background: url("assets/img/status_bg_mobile.png") no-repeat center center !important;
    background-size: cover !important;
  }
}

@media only screen and (max-width: 720px) {
  #uptime, tr td:nth-child(5) {
    display: none;
  }
}

@media only screen and (max-width: 660px) {
  #load, tr td:nth-child(6) {
    display: none;
  }
}

@media only screen and (max-width: 600px) {
  #traffic, tr td:nth-child(8) {
    display: none;
  }
}

@media only screen and (max-width: 533px) {
  #name, tr td:nth-child(2) {
    min-width: 20px;
    max-width: 60px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

  #hdd, tr td:nth-child(11) {
    display: none;
  }

  #cpu, #ram {
    min-width: 20px;
    max-width: 40px;
  }
}
</style>
