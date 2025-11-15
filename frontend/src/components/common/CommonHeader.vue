<script setup lang="ts">
// @ts-ignore
import { CircleClose, Collection, HomeFilled } from "@element-plus/icons-vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { onMounted, ref } from "vue";

const userStore = useUserStore();
const router = useRouter();

// 模拟用户信息
const userInfo = {
  name: userStore.user.nickname,
  avatar: userStore.user.avatar,
};

const handleUserDropdownCommand = (command: string) => {
  // 判断当前跳转方式
  if (command === "logout") {
    // 询问用户是否退出登录
    ElMessageBox.confirm("确定退出登录吗？", "退出登录", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(() => {
        // 退出登录
        userStore.logoutUser();

        // 显示退出成功消息
        // @ts-ignore
        ElMessage.success("退出登录成功");

        // 跳转到登录页面
        router.push("/login");
      })
      .catch(() => {});
  } else if (command === "profile") {
    // 跳转到个人资料页面
    router.push("/other/user-profile");
  }
};

// 获取当前时间段
const currentTimePart = ref("");
onMounted(() => {
  const curTime = new Date();
  if (curTime.getHours() <= 11) {
    currentTimePart.value = "早上";
  } else if (curTime.getHours() <= 13) {
    currentTimePart.value = "中午";
  } else if (curTime.getHours() <= 18) {
    currentTimePart.value = "下午";
  } else {
    currentTimePart.value = "晚上";
  }
});
</script>

<template>
  <el-header>
    <div class="header-left">
      <span>{{ userStore.user.nickname }} {{ currentTimePart }}好!</span>
      <span>欢迎使用图书馆管理后台</span>
    </div>
    <div class="header-right">
      <el-dropdown @command="handleUserDropdownCommand">
        <!-- 正常显示的部分 -->
        <div class="user-avatar" style="cursor: pointer; outline: none">
          <el-avatar :src="userInfo.avatar">
            <HomeFilled v-if="!userInfo.avatar" />
          </el-avatar>
          <span style="margin-left: 8px">{{ userInfo.name }}</span>
          <el-icon style="margin-left: 4px">
            <svg viewBox="0 0 1024 1024" width="16" height="16">
              <path
                d="M868 546.678L512 816 156 546.678c-4.96-4.046-12.784-4.046-17.744 0-4.96 4.046-4.96 10.614 0 14.66l360 288c2.48 1.965 5.558 2.98 8.872 2.98s6.392-1.015 8.872-2.98l360-288c4.96-4.046 4.96-10.614 0-14.66z"
                fill="currentColor"
              />
              <path
                d="M868 477.322L512 208 156 477.322c-4.96 4.046-12.784 4.046-17.744 0-4.96-4.046-4.96-10.614 0-14.66l360-288c2.48-1.965 5.558-2.98 8.872-2.98s6.392 1.015 8.872 2.98l360 288c4.96 4.046 4.96 10.614 0 14.66z"
                fill="currentColor"
              />
            </svg>
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile" :icon="Collection"
              >个人资料
            </el-dropdown-item>
            <el-dropdown-item command="logout" :icon="CircleClose"
              >退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<style scoped lang="scss">
.el-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  color: #333;
  font-weight: bold;
  font-size: 20px;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 60px;

  .header-left {
    font-size: 15px;
    font-weight: normal;
    display: flex;
    gap: 10px;

    span:nth-child(1) {
      font-weight: bold;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 20px;

    .user-avatar {
      display: flex;
      align-items: center;
      color: #333;

      .el-avatar {
        width: 36px;
        height: 36px;
        border: 2px solid #e8e8e8;
      }
    }
  }
}
</style>
