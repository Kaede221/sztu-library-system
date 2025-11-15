<script setup lang="ts">
import TransDuration from "@/components/settings/TransDuration.vue";
</script>

<template>
  <div class="setting-page">
    <h1 class="title">核心设置</h1>
    <div class="settings-container">
      <TransDuration />
    </div>
  </div>
</template>

<style scoped lang="scss">
.setting-page {
  display: flex;
  justify-content: center;
  flex-direction: column;
  gap: 20px;
  padding: 20px;

  .title {
    font-size: 20px;
  }

  .settings-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;

    > * {
      flex: 0 0 calc(50% - 20px);
      min-width: 300px;
    }

    @media (max-width: 768px) {
      > * {
        flex-basis: 100%;
      }
    }
  }
}
</style>
