<!--
 * @FileDescription: 首页的仪表盘组件
 * @Author: kaedeshimizu
 * @Date: 2025/8/30
-->
<script setup lang="ts">
import { onMounted, ref } from "vue";
// @ts-ignore
import { Warning } from "@element-plus/icons-vue";
import { getUserListService } from "@/api/user";

// 总用户数量
const allUserCounter = ref(0);

// 总发帖量
const totalTopicsCounter = ref(0);

// 进入页面就获取用户数据
onMounted(async () => {
  const res1 = await getUserListService({ size: 1 });
  allUserCounter.value = res1.data.total;
});
</script>

<template>
  <el-card>
    <el-row :gutter="16">
      <el-col :span="12">
        <div class="statistic-card">
          <el-statistic
            :value="allUserCounter"
            v-loading="allUserCounter === 0"
          >
            <template #title>
              <div style="display: inline-flex; align-items: center">
                总用户数
                <el-tooltip
                  effect="dark"
                  content="仅限当前运行环境的累计用户数"
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
          <el-statistic
            :value="totalTopicsCounter"
            v-loading="totalTopicsCounter === 0"
          >
            <template #title>
              <div style="display: inline-flex; align-items: center">
                帖子总数
                <el-tooltip
                  effect="dark"
                  content="仅限当前运行环境的累计帖子数"
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
