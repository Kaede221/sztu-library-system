<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import {
  // @ts-ignore
  Calendar, // @ts-ignore
  Document, // @ts-ignore
  HomeFilled, // @ts-ignore
  Setting, // @ts-ignore
  User, // @ts-ignore
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
</script>

<template>
  <el-aside width="200px">
    <!-- 侧边栏的顶部部分 -->
    <div class="home-aside-header" @click="router.push('/')">
      图书馆管理后台
    </div>
    <el-menu router :default-active="route.path">
      <el-menu-item index="/" route="/">
        <el-icon>
          <home-filled />
        </el-icon>
        <span>首页</span>
      </el-menu-item>

      <el-menu-item index="/user" route="/user">
        <el-icon>
          <User />
        </el-icon>
        用户管理
      </el-menu-item>

      <el-sub-menu index="other-setting">
        <template #title>
          <el-icon>
            <Setting />
          </el-icon>
          <span>设置</span>
        </template>
        <el-menu-item index="/other/setting" route="/other/setting"
          >核心设置
        </el-menu-item>
        <el-menu-item index="/other/user-profile" route="/other/user-profile"
          >个人资料
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </el-aside>
</template>

<style scoped lang="scss">
// 侧边栏样式
.el-aside {
  .home-aside-header {
    height: 60px;
    line-height: 60px;
    text-align: center;
    font-size: 20px;
    color: #000000;
    background-color: #ffffff;

    // 用户不可选中文本
    -webkit-user-select: none; /* 适用于Webkit浏览器 */
    -moz-user-select: none; /* 适用于Firefox */
    -ms-user-select: none; /* 适用于IE10及以上 */
    user-select: none; /* 标准属性 */
  }
}
</style>
