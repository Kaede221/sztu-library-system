<script setup lang="ts">
import { ref, watch } from "vue";
import { ElMessageBox, ElMessage } from "element-plus";
import { updateUserService, deleteUserService } from "@/api/user";

// 定义用户信息
interface IUserInfoDialog {
  currentUser: IUser | undefined;
  mode: "check" | "edit";
}

const props = defineProps<IUserInfoDialog>();
const emit = defineEmits<{
  refreshTable: [];
}>();

const visible = defineModel<boolean>("visible", { required: true });

// 创建本地用户数据副本
const currentUser = ref<IUser | undefined>(
  props.currentUser ? JSON.parse(JSON.stringify(props.currentUser)) : undefined,
);

// 监听props.currentUser变化以更新本地副本
watch(
  () => props.currentUser,
  (newVal) => {
    currentUser.value = JSON.parse(JSON.stringify(newVal || {}));
  },
  { immediate: true },
);

// 关闭对话框处理函数
const handleClose = () => {
  visible.value = false;
};

// 删除用户
const deleteUser = async () => {
  if (!currentUser.value) return;

  ElMessageBox.confirm("确认要删除该用户吗? 此操作不可恢复!", "警告", {
    confirmButtonText: "删除",
    cancelButtonText: "取消",
    type: "error",
  })
    .then(async () => {
      try {
        await deleteUserService(currentUser.value!.id);
        // @ts-ignore
        ElMessage.success("删除成功");
        emit("refreshTable");
        handleClose();
      } catch {
        // 错误已在拦截器中处理
      }
    })
    .catch(() => {});
};

// 保存用户信息
const saveUserInfo = async () => {
  if (!currentUser.value) {
    // @ts-ignore
    ElMessage.error("操作失败, 请重试");
    return;
  }

  try {
    await updateUserService(currentUser.value.id, {
      username: currentUser.value.username,
      email: currentUser.value.email,
      full_name: currentUser.value.full_name || undefined,
      role: currentUser.value.role,
      is_active: currentUser.value.is_active,
    });
    // @ts-ignore
    ElMessage.success("保存成功");
    emit("refreshTable");
    handleClose();
  } catch {
    // 错误已在拦截器中处理
  }
};

// 切换用户激活状态
const toggleUserActive = async () => {
  if (!currentUser.value) return;

  const newStatus = !currentUser.value.is_active;
  const actionText = newStatus ? "启用" : "禁用";

  ElMessageBox.confirm(`确认要${actionText}该用户吗?`, "确认", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        await updateUserService(currentUser.value!.id, {
          is_active: newStatus,
        });
        currentUser.value!.is_active = newStatus;
        // @ts-ignore
        ElMessage.success(`${actionText}成功`);
        emit("refreshTable");
      } catch {
        // 错误已在拦截器中处理
      }
    })
    .catch(() => {});
};
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="props.mode === 'check' ? '查看用户信息' : '编辑用户信息'"
    :show-close="true"
    @close="handleClose"
    close-on-click-modal
    width="500px"
  >
    <el-form label-width="80" label-position="right" v-if="currentUser">
      <el-form-item label="用户ID">
        <el-input :model-value="currentUser.id" disabled />
      </el-form-item>
      <el-form-item label="用户名">
        <el-input
          v-model="currentUser.username"
          :disabled="props.mode === 'check'"
        />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input
          v-model="currentUser.email"
          :disabled="props.mode === 'check'"
        />
      </el-form-item>
      <el-form-item label="全名">
        <el-input
          v-model="currentUser.full_name"
          :disabled="props.mode === 'check'"
          placeholder="未设置"
        />
      </el-form-item>
      <el-form-item label="角色">
        <el-select
          v-model="currentUser.role"
          :disabled="props.mode === 'check'"
        >
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-tag :type="currentUser.is_active ? 'success' : 'danger'">
          {{ currentUser.is_active ? "已激活" : "已禁用" }}
        </el-tag>
      </el-form-item>
      <el-form-item label="创建时间">
        <el-input :model-value="currentUser.created_at" disabled />
      </el-form-item>
      <el-form-item label="更新时间">
        <el-input :model-value="currentUser.updated_at" disabled />
      </el-form-item>
    </el-form>

    <!-- 提供快捷操作 -->
    <template #footer v-if="props.mode === 'edit'">
      <div class="dialog-footer">
        <el-button
          :type="currentUser?.is_active ? 'warning' : 'success'"
          plain
          @click="toggleUserActive"
        >
          {{ currentUser?.is_active ? "禁用用户" : "启用用户" }}
        </el-button>
        <el-button type="danger" plain @click="deleteUser">删除用户</el-button>
        <el-button type="primary" @click="saveUserInfo">保存</el-button>
        <el-button @click="handleClose">取消</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped lang="scss">
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
