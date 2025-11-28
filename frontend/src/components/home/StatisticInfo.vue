<!--
 * @FileDescription: 首页的仪表盘组件
 * @Author: kaedeshimizu
 * @Date: 2025/8/30
-->
<script setup lang="ts">
import { onMounted, ref } from "vue";
// @ts-ignore
import { Warning } from "@element-plus/icons-vue";
import { getStatsService } from "@/api/stats";

// 总用户数量
const allUserCounter = ref(0);

// 总图书数量
const totalBooksCounter = ref(0);

// 数据加载状态
const loading = ref(true);

// 进入页面就获取统计数据
onMounted(async () => {
  try {
    const res = await getStatsService();
    // @ts-ignore - axios拦截器已返回response.data
    allUserCounter.value = res.total_users;
    // @ts-ignore
    totalBooksCounter.value = res.total_books;
  } catch (error) {
    console.error("获取统计数据失败:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <el-card v-loading="loading">
    <el-row :gutter="16">
      <el-col :span="12">
        <div class="statistic-card">
          <el-statistic :value="allUserCounter">
            <template #title>
              <div style="display: inline-flex; align-items: center">
                总用户数
                <el-tooltip
                  effect="dark"
                  content="系统中注册的用户总数"
                  placement="top"
                >
                  <el-icon style="margin-left: 4px" :size="12">
                    <Warning />
                  </el-icon>
                </el-tooltip>
              </div>
            </template>
          </el-statistic>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="statistic-card">
          <el-statistic :value="totalBooksCounter">
            <template #title>
              <div style="display: inline-flex; align-items: center">
                图书总数
                <el-tooltip
                  effect="dark"
                  content="图书馆中的图书总数"
                  placement="top"
                >
                  <el-icon style="margin-left: 4px" :size="12">
                    <Warning />
                  </el-icon>
                </el-tooltip>
              </div>
            </template>
          </el-statistic>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<style scoped lang="scss">
.el-statistic {
  --el-statistic-content-font-size: 28px;
}

.statistic-card {
  height: 100%;
  padding: 10px;
}
</style>
