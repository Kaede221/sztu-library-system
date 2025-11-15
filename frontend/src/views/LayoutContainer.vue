<script setup lang="ts">
import CommonSidebar from "@/components/common/CommonSidebar.vue";
import CommonHeader from "@/components/common/CommonHeader.vue";
import { useSettingStore } from "@/store/setting";

const settingStore = useSettingStore();
</script>

<template>
  <div
    class="layout-wrapper"
    :style="{ '--trans-time': settingStore.transitionDuration + 'ms' }"
  >
    <!--外部container-->
    <el-container>
      <!--侧边栏部分-->
      <CommonSidebar></CommonSidebar>
      <el-container>
        <CommonHeader></CommonHeader>
        <el-main>
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped lang="scss">
.layout-wrapper {
  height: 100vh;
  overflow: hidden;

  .el-container {
    height: 100%;
    display: flex;
    flex-direction: row;

    .el-container {
      display: flex;
      flex-direction: column;
      // 主内容区样式
      .el-main {
        padding: 20px;
        background-color: #f5f5f5;
        flex: 1;
        overflow: auto;
      }
    }
  }
}

// NOTE 配置路由动画
.fade-enter-from {
  /* 进入时的透明度为0 和 刚开始进入时的原始位置通过active透明度渐渐变为1 */
  opacity: 0;
  transform: translateX(-100%);
}

.fade-enter-to {
  /*定义进入完成后的位置 和 透明度 */
  transform: translateX(0%);
  opacity: 1;
}

.fade-leave-active,
.fade-enter-active {
  transition: all var(--trans-time) ease-out;
}

.fade-leave-from {
  /* 页面离开时一开始的css样式,离开后为leave-to，经过active渐渐透明 */
  transform: translateX(0%);
  opacity: 1;
}

.fade-leave-to {
  /* 这个是离开后的透明度通过下面的active阶段渐渐变为0 */
  transform: translateX(100%);
  opacity: 0;
}
</style>
