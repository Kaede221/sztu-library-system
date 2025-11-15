<script setup lang="ts">
import { useUserStore } from "@/store/user";
import {
  // @ts-ignore
  User, // @ts-ignore
  School, // @ts-ignore
  UserFilled, // @ts-ignore
  Briefcase, // @ts-ignore
  Calendar, // @ts-ignore
  Compass,
} from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import UserInfoDialog from "@/components/UserInfoDialog.vue";
import { userGetTargetUserProfile } from "@/api/user.ts";
import { ref } from "vue";

// 获取用户存储
const userStore = useUserStore();
const user = userStore.user;

// 格式化用户角色显示
const getUserRole = (power: number): string => {
  if (power === 999) return "管理员";
  return "普通用户";
};

// 修改密码的回调函数
const handleChangePassword = () => {
  // @ts-ignore
  ElMessage.error("请前往校务系统更改密码");
};

// 是否展示编辑资料弹窗
const showEditUserDialog = ref(false);

// 重新拉取个人信息部分
const handleRefreshUser = async () => {
  userGetTargetUserProfile(userStore.user.id.toString())
    .then((res) => {
      console.log(res);
    })
    .catch(() => {
      // @ts-ignore
      ElMessage.error("操作失败, 请重试");
    });
};
</script>

<template>
  <div class="profile-container">
    <!-- 页面标题 -->
    <div class="profile-header">
      <h2>个人资料</h2>
    </div>

    <!-- 个人资料卡片 -->
    <el-card>
      <!-- 头像区域 -->
      <div class="profile-avatar-section">
        <el-avatar :src="user.avatar" class="profile-avatar">
          <UserFilled v-if="!user.avatar" />
        </el-avatar>
        <div class="profile-name">{{ user.nickname || "未设置昵称" }}</div>
        <div class="profile-role">{{ getUserRole(user.power) }}</div>
        <el-tag v-if="user.stuIsCheck" type="primary">已认证</el-tag>
        <el-tag v-else type="warning">未认证</el-tag>
      </div>

      <!-- 右侧信息区域 -->
      <div class="profile-info-section">
        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">
              <User class="info-icon" />
              <span>姓名</span>
            </div>
            <div class="info-value">{{ user.stuName || "未设置" }}</div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <User class="info-icon" />
              <span>性别</span>
            </div>
            <div class="info-value">{{ user.gender }}</div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <Compass class="info-icon" />
              <span>学号</span>
            </div>
            <div class="info-value">{{ user.stuNum || "未设置" }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">
              <School class="info-icon" />
              <span>学校</span>
            </div>
            <div class="info-value">{{ user.school || "未设置" }}</div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <Briefcase class="info-icon" />
              <span>班级</span>
            </div>
            <div class="info-value">{{ user.stuCla || "未设置" }}</div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <Calendar class="info-icon" />
              <span>ID</span>
            </div>
            <div class="info-value">{{ user.id || "未设置" }}</div>
          </div>
        </div>

        <!-- 操作按钮区域 -->
        <div class="profile-actions">
          <el-button
            type="primary"
            size="default"
            @click="showEditUserDialog = true"
            >编辑资料
          </el-button>
          <el-button size="default" @click="handleChangePassword"
            >修改密码
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 编辑资料的弹窗 -->
    <UserInfoDialog
      v-model:visible="showEditUserDialog"
      :current-user="userStore.user"
      @refresh-table="handleRefreshUser"
      mode="edit"
    ></UserInfoDialog>
  </div>
</template>

<style scoped lang="scss">
// 主容器样式
.profile-container {
  // 页面标题样式
  .profile-header {
    margin-bottom: 30px;
    border-bottom: 2px solid #e8e8e8;
    padding-bottom: 10px;

    h2 {
      font-size: 24px;
      color: #333;
      font-weight: 600;
    }
  }

  .el-card {
    // NOTE 头像区域样式
    .profile-avatar-section {
      flex: 0 0 200px;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
      background: #f7f7f7;
      border-radius: 8px;

      .profile-avatar {
        width: 120px;
        height: 120px;
        margin-bottom: 15px;
        border: 3px solid #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }

      .profile-name {
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin-bottom: 5px;
      }

      .profile-role {
        font-size: 14px;
        color: #666;
        margin-bottom: 10px;
      }
    }

    // 信息区域样式
    .profile-info-section {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      margin-top: 20px;

      .info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 30px;

        .info-item {
          display: flex;
          align-items: center;
          padding: 10px 0;
          border-bottom: 1px solid #f0f0f0;

          .info-label {
            flex: 0 0 120px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #666;

            .info-icon {
              color: #999;
              width: 18px;
            }
          }

          .info-value {
            flex: 1;
            font-size: 14px;
            color: #333;
            text-wrap: nowrap;
          }
        }
      }
    }
  }
}
</style>
