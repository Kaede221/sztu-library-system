<script setup lang="ts">
import { useUserStore } from "@/store/user";
import {
  // @ts-ignore
  User, // @ts-ignore
  Message, // @ts-ignore
  UserFilled, // @ts-ignore
  Calendar, // @ts-ignore
  Lock,
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { ref } from "vue";
import {
  getCurrentUserService,
  updateCurrentUserService,
  changePasswordService,
} from "@/api/user";

// 获取用户存储
const userStore = useUserStore();

// 本地用户数据副本（用于编辑）
const editForm = ref({
  username: userStore.user.username,
  email: userStore.user.email,
  full_name: userStore.user.full_name || "",
});

// 是否正在编辑
const isEditing = ref(false);

// 是否正在保存
const isSaving = ref(false);

// 修改密码对话框
const showPasswordDialog = ref(false);
const passwordForm = ref({
  old_password: "",
  new_password: "",
  confirm_password: "",
});
const isChangingPassword = ref(false);

// 格式化用户角色显示
const getUserRole = (role: string): string => {
  return role === "admin" ? "管理员" : "普通用户";
};

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleString("zh-CN");
};

// 开始编辑
const handleStartEdit = () => {
  editForm.value = {
    username: userStore.user.username,
    email: userStore.user.email,
    full_name: userStore.user.full_name || "",
  };
  isEditing.value = true;
};

// 取消编辑
const handleCancelEdit = () => {
  isEditing.value = false;
};

// 保存编辑
const handleSaveEdit = async () => {
  isSaving.value = true;
  try {
    const res = await updateCurrentUserService({
      username: editForm.value.username,
      email: editForm.value.email,
      full_name: editForm.value.full_name || undefined,
    });
    // @ts-ignore - 响应拦截器已处理
    userStore.setUser(res);
    // @ts-ignore
    ElMessage.success("保存成功");
    isEditing.value = false;
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isSaving.value = false;
  }
};

// 刷新用户信息
const handleRefreshUser = async () => {
  try {
    const res = await getCurrentUserService();
    // @ts-ignore - 响应拦截器已处理
    userStore.setUser(res);
    // @ts-ignore
    ElMessage.success("刷新成功");
  } catch {
    // 错误已在拦截器中处理
  }
};

// 打开修改密码对话框
const handleOpenPasswordDialog = () => {
  passwordForm.value = {
    old_password: "",
    new_password: "",
    confirm_password: "",
  };
  showPasswordDialog.value = true;
};

// 修改密码
const handleChangePassword = async () => {
  // 验证
  if (!passwordForm.value.old_password) {
    // @ts-ignore
    ElMessage.warning("请输入旧密码");
    return;
  }
  if (!passwordForm.value.new_password) {
    // @ts-ignore
    ElMessage.warning("请输入新密码");
    return;
  }
  if (passwordForm.value.new_password.length < 6) {
    // @ts-ignore
    ElMessage.warning("新密码至少6个字符");
    return;
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    // @ts-ignore
    ElMessage.warning("两次输入的密码不一致");
    return;
  }

  isChangingPassword.value = true;
  try {
    await changePasswordService({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    });
    // @ts-ignore
    ElMessage.success("密码修改成功");
    showPasswordDialog.value = false;
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isChangingPassword.value = false;
  }
};
</script>

<template>
  <div class="profile-container">
    <!-- 页面标题 -->
    <div class="profile-header">
      <h2>个人资料</h2>
      <el-button type="primary" text @click="handleRefreshUser">
        刷新信息
      </el-button>
    </div>

    <!-- 个人资料卡片 -->
    <el-card>
      <!-- 头像区域 -->
      <div class="profile-avatar-section">
        <el-avatar class="profile-avatar">
          <UserFilled />
        </el-avatar>
        <div class="profile-name">
          {{ userStore.user.full_name || userStore.user.username || "未设置" }}
        </div>
        <div class="profile-role">{{ getUserRole(userStore.user.role) }}</div>
        <el-tag
          :type="userStore.user.is_active ? 'success' : 'danger'"
          size="small"
        >
          {{ userStore.user.is_active ? "已激活" : "已禁用" }}
        </el-tag>
      </div>

      <!-- 信息区域 -->
      <div class="profile-info-section">
        <div class="info-grid" v-if="!isEditing">
          <div class="info-item">
            <div class="info-label">
              <User class="info-icon" />
              <span>用户名</span>
            </div>
            <div class="info-value">{{ userStore.user.username }}</div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <Message class="info-icon" />
              <span>邮箱</span>
            </div>
            <div class="info-value">{{ userStore.user.email }}</div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <User class="info-icon" />
              <span>全名</span>
            </div>
            <div class="info-value">
              {{ userStore.user.full_name || "未设置" }}
            </div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <Lock class="info-icon" />
              <span>用户ID</span>
            </div>
            <div class="info-value">{{ userStore.user.id }}</div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <Calendar class="info-icon" />
              <span>创建时间</span>
            </div>
            <div class="info-value">
              {{ formatDate(userStore.user.created_at) }}
            </div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <Calendar class="info-icon" />
              <span>更新时间</span>
            </div>
            <div class="info-value">
              {{ formatDate(userStore.user.updated_at) }}
            </div>
          </div>
        </div>

        <!-- 编辑表单 -->
        <el-form v-else label-width="80px" class="edit-form">
          <el-form-item label="用户名">
            <el-input v-model="editForm.username" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="editForm.email" type="email" />
          </el-form-item>
          <el-form-item label="全名">
            <el-input v-model="editForm.full_name" placeholder="可选" />
          </el-form-item>
        </el-form>

        <!-- 操作按钮区域 -->
        <div class="profile-actions">
          <template v-if="!isEditing">
            <el-button type="primary" @click="handleStartEdit">
              编辑资料
            </el-button>
            <el-button @click="handleOpenPasswordDialog">修改密码</el-button>
          </template>
          <template v-else>
            <el-button
              type="primary"
              @click="handleSaveEdit"
              :loading="isSaving"
            >
              保存
            </el-button>
            <el-button @click="handleCancelEdit" :disabled="isSaving">
              取消
            </el-button>
          </template>
        </div>
      </div>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form label-width="80px">
        <el-form-item label="旧密码">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            show-password
            placeholder="请输入旧密码"
          />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            show-password
            placeholder="请输入新密码（至少6位）"
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleChangePassword"
          :loading="isChangingPassword"
        >
          确认修改
        </el-button>
      </template>
    </el-dialog>
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
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      font-size: 24px;
      color: #333;
      font-weight: 600;
      margin: 0;
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
        font-size: 60px;
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

      .edit-form {
        margin-bottom: 30px;
      }

      .profile-actions {
        display: flex;
        gap: 10px;
      }
    }
  }
}
</style>
