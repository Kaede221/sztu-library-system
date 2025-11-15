<script setup lang="ts">
import { zhCn } from "element-plus/es/locale/index";
</script>

<template>
  <el-config-provider :locale="zhCn">
    <RouterView></RouterView>
  </el-config-provider>
</template>

<style scoped></style>
