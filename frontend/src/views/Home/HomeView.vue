<script setup lang="ts">
import StatisticInfo from "@/components/home/StatisticInfo.vue";
import SystemInfo from "@/components/home/SystemInfo.vue";
</script>

<template>
  <div class="container">
    <h1>仪表盘</h1>
    <StatisticInfo></StatisticInfo>

    <h1>系统信息</h1>
    <SystemInfo></SystemInfo>
  </div>
</template>

<style scoped lang="scss">
.container {
  display: flex;
  align-self: center;
  justify-content: center;
  flex-direction: column;
  gap: 30px;
}
</style>
