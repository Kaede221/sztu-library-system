<!--
 * @FileDescription: 切换页面之间的时间设置
 * @Author: kaedeshimizu
 * @Date: 2025/8/30
-->
<script setup lang="ts">
import { useSettingStore } from "@/store/setting";

const settingStore = useSettingStore();
</script>

<template>
  <el-card>
    <template #header>
      <div class="checkers-title-cotainer">
        <div class="checkers-title-cotainer-title">切换动画配置</div>
        <div class="checkers-title-cotainer-content">
          允许你修改页面切换时的动画时间长度
        </div>
      </div>
    </template>
    <el-slider :min="0" :max="500" v-model="settingStore.transitionDuration" />
  </el-card>
</template>

<style scoped lang="scss">
.checkers-title-cotainer {
  &-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 5px;
  }

  &-content {
    font-size: 16px;
  }
}
</style>
