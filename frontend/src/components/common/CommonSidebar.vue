<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/store/user";
import {
  // @ts-ignore
  Calendar, // @ts-ignore
  Document, // @ts-ignore
  HomeFilled, // @ts-ignore
  Setting, // @ts-ignore
  User, // @ts-ignore
  Reading, // @ts-ignore
  Collection, // @ts-ignore
  Notebook, // @ts-ignore
  Bell, // @ts-ignore
  Star, // @ts-ignore
  DataAnalysis, // @ts-ignore
  Folder, // @ts-ignore
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
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

      <!-- 只有管理员才能看到用户管理 -->
      <el-menu-item v-if="userStore.isAdmin" index="/user" route="/user">
        <el-icon>
          <User />
        </el-icon>
        用户管理
      </el-menu-item>

      <el-menu-item index="/book" route="/book">
        <el-icon>
          <Reading />
        </el-icon>
        图书管理
      </el-menu-item>

      <!-- 分类管理（管理员） -->
      <el-menu-item v-if="userStore.isAdmin" index="/category" route="/category">
        <el-icon>
          <Folder />
        </el-icon>
        分类管理
      </el-menu-item>

      <!-- 我的借阅 -->
      <el-menu-item index="/borrow" route="/borrow">
        <el-icon>
          <Notebook />
        </el-icon>
        我的借阅
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
