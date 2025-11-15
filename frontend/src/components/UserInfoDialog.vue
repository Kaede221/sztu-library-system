<script setup lang="ts">
import { ref, watch } from "vue";
import { ElMessageBox, ElMessage } from "element-plus";
import {
  userDeleteAuthInfoService,
  userEditInfoService,
  userPreloadService,
} from "@/api/user.ts";

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

// ! 操作部分
// 删除用户的认证信息
const deleteUserAuthInfo = async () => {
  ElMessageBox.confirm("确认要删除该用户的认证信息吗?", "警告", {
    confirmButtonText: "删除",
    cancelButtonText: "取消",
    type: "error",
  })
    .then(() => {
      userDeleteAuthInfoService(currentUser.value!.id).then(() => {
        // @ts-ignore
        ElMessage.success("删除成功");
        emit("refreshTable");
        handleClose();
      });
    })
    .catch(() => {});
};

// 保存用户的认证信息
const saveUserInfo = async () => {
  if (currentUser.value) {
    // 调用保存信息的接口
    userEditInfoService(currentUser.value.id, {
      ...currentUser.value,
    })
      .then((res) => {
        // @ts-ignore
        if (res.success) {
          // @ts-ignore
          ElMessage.success("保存成功");
          handleClose();
          emit("refreshTable");
        } else {
          // @ts-ignore
          ElMessage.error("操作失败, 请重试");
        }
      })
      .catch(() => {
        // @ts-ignore
        ElMessage.error("操作失败, 请重试");
      });
  } else {
    // @ts-ignore
    ElMessage.error("操作失败, 请重试");
  }
};

// 用户预认证部分
// 预认证表单
const preloadForm = ref({
  password: "",
});

const preloadFormRef = ref();

const preloadFormRules = {
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

// 是否展示预认证的弹窗
const showUserPreloadDialog = ref(false);

// 关闭对话框处理函数
const handleClose = () => {
  visible.value = false;
};

// 用户预认证
const userPreload = async () => {
  preloadFormRef.value
    .validate()
    .then(async () => {
      // 成功, 开始删除
      // @ts-ignore
      ElMessage.info("预认证中");

      userPreloadService({
        nick_name: currentUser.value!.nickname,
        pwd: preloadForm.value.password,
      })
        .then((res) => {
          // @ts-ignore
          if (res.success) {
            // @ts-ignore
            ElMessage.success("预认证成功");
            showUserPreloadDialog.value = false;
            handleClose();
            emit("refreshTable");
          }
        })
        .catch(() => {
          // @ts-ignore
          ElMessage.error("操作失败, 请重试");
        });
    })
    .catch(() => {});
};
</script>

<template>
  <el-dialog
    v-model="visible"
    :show-close="false"
    @close="handleClose"
    close-on-click-modal
  >
    <el-form label-width="80" label-position="right">
      <el-form-item label="用户头像">
        <el-avatar :src="currentUser!.avatar" />
      </el-form-item>
      <el-form-item label="用户ID">
        <el-input v-model="currentUser!.id" disabled />
      </el-form-item>
      <el-form-item label="用户名">
        <el-input
          v-model="currentUser!.nickname"
          :disabled="props.mode === 'check'"
        />
      </el-form-item>
      <el-form-item label="性别">
        <el-input v-model="currentUser!.gender" disabled />
      </el-form-item>
      <el-form-item label="姓名">
        <el-input
          v-model="currentUser!.stuName"
          :disabled="props.mode === 'check'"
        />
      </el-form-item>
      <el-form-item label="班级">
        <el-input
          v-model="currentUser!.stuCla"
          :disabled="props.mode === 'check'"
        />
      </el-form-item>
      <el-form-item label="学号">
        <el-input
          v-model="currentUser!.stuNum"
          :disabled="props.mode === 'check'"
        />
      </el-form-item>
      <el-form-item label="认证状态">
        <el-tag type="success" v-if="props.currentUser!.stuIsCheck"
          >已认证
        </el-tag>
        <el-tag type="warning" v-else>未认证</el-tag>
      </el-form-item>
      <el-form-item label="用户权限">
        <el-input
          type="number"
          v-model="currentUser!.power"
          :disabled="props.mode === 'check'"
        />
      </el-form-item>
    </el-form>

    <!-- 提供快捷操作 -->
    <div class="dialog-operators" v-if="props.mode === 'edit'">
      <el-divider></el-divider>
      <div>
        <el-button type="primary" plain @click="showUserPreloadDialog = true"
          >用户预认证
        </el-button>
        <el-button type="danger" plain @click="deleteUserAuthInfo"
          >删除认证信息
        </el-button>
        <el-button type="success" plain @click="saveUserInfo">保存</el-button>
        <el-button plain @click="handleClose">取消</el-button>
      </div>
    </div>
  </el-dialog>

  <!-- 预认证弹窗 -->
  <el-dialog v-model="showUserPreloadDialog" title="学生预认证" width="500">
    <el-form
      :model="preloadForm"
      :rules="preloadFormRules"
      ref="preloadFormRef"
    >
      <el-form-item label="请输入密码" prop="password">
        <el-input
          v-model="preloadForm.password"
          show-password
          type="password"
          autocomplete="off"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="showUserPreloadDialog = false">取消</el-button>
        <el-button type="primary" @click="userPreload">确认</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped lang="scss">
.dialog-operators {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
