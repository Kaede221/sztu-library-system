<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import { createUserByAdminService } from "@/api/user";

// 定义弹窗可见性
const visible = defineModel<boolean>("visible", { required: true });

// 定义事件
const emit = defineEmits<{
  refreshTable: [];
}>();

// 表单数据
const formData = reactive({
  username: "",
  email: "",
  password: "",
  full_name: "",
  role: "user" as "user" | "admin",
});

// 表单引用
const formRef = ref();

// 表单规则
const rules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    {
      min: 3,
      max: 50,
      message: "用户名长度在 3 到 50 个字符",
      trigger: "blur",
    },
  ],
  email: [
    { required: true, message: "请输入邮箱地址", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱地址", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    {
      min: 6,
      max: 100,
      message: "密码长度在 6 到 100 个字符",
      trigger: "blur",
    },
  ],
  full_name: [
    { max: 100, message: "全名长度不能超过 100 个字符", trigger: "blur" },
  ],
};

// 是否正在提交
const isSubmitting = ref(false);

// 关闭弹窗
const handleClose = () => {
  visible.value = false;
  resetForm();
};

// 重置表单
const resetForm = () => {
  formData.username = "";
  formData.email = "";
  formData.password = "";
  formData.full_name = "";
  formData.role = "user";
  if (formRef.value) {
    formRef.value.clearValidate();
  }
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  try {
    const valid = await formRef.value.validate();
    if (!valid) return;

    isSubmitting.value = true;

    // 调用创建用户接口
    await createUserByAdminService(
      {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || undefined,
      },
      formData.role,
    );

    // @ts-ignore
    ElMessage.success("用户创建成功");
    emit("refreshTable");
    handleClose();
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <el-dialog
    v-model="visible"
    title="添加用户"
    :show-close="true"
    @close="handleClose"
    close-on-click-modal
    width="500px"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="80px"
      label-position="right"
    >
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="formData.username"
          placeholder="请输入用户名（3-50个字符）"
          clearable
        />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input
          v-model="formData.email"
          placeholder="请输入邮箱地址"
          clearable
        />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="formData.password"
          type="password"
          placeholder="请输入密码（至少6个字符）"
          show-password
          clearable
        />
      </el-form-item>

      <el-form-item label="全名" prop="full_name">
        <el-input
          v-model="formData.full_name"
          placeholder="请输入全名（可选）"
          clearable
        />
      </el-form-item>

      <el-form-item label="角色" prop="role">
        <el-select v-model="formData.role" style="width: 100%">
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="isSubmitting" @click="handleSubmit">
          创建用户
        </el-button>
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
