<!--
 * @FileDescription: 首页的系统信息管理
 * @Author: kaedeshimizu
 * @Date: 2025/8/30
-->
<script setup lang="ts">
// @ts-ignore
import pkg from "../../../package.json";
</script>

<template>
  <el-card>
    <div class="system-info-container">
      <div class="circle-card">
        <el-progress type="circle" :percentage="100" status="success" />
      </div>
      <div class="info-details">
        <div class="info-item">
          <span class="info-label">系统名称:</span>
          <span class="info-value">{{ pkg.name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">版本号:</span>
          <span class="info-value">{{ pkg.version }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">作者:</span>
          <span class="info-value">{{ pkg.author.name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">许可证:</span>
          <span class="info-value">{{ pkg.license }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">技术栈:</span>
          <span class="info-value">Vue 3, TypeScript, Element Plus, Python, MySQL</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<style scoped lang="scss">
.system-info-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 50px;

  .circle-card {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 10px;
  }

  .info-details {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .info-title {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }

  .info-item {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .info-label {
    font-weight: 500;
    color: #606266;
    min-width: 80px;
  }

  .info-value {
    color: #303133;
  }
}
</style>
