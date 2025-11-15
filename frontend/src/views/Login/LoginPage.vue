<!--登录页面-->
<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import type { FormRules } from "element-plus";
import { ElMessage } from "element-plus";
import { userLoginService } from "@/api/user";
import { useUserStore } from "@/store/user";
import { useSettingStore } from "@/store/setting";
import { router } from "@/router";

const userStore = useUserStore();
const settingStore = useSettingStore();

// 定义表单的内容列表对象
const form = ref({
  username: "",
  password: "",
});

// 定义表单的校验规则
const formRules: FormRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { pattern: /^[0-9]{12}$/, message: "用户名是长度为12的学号" },
  ],
  password: [
    {
      required: true,
      message: "请输入密码 ",
      trigger: "blur",
    },
  ],
};

// 获取表单
const formRef = ref();

// 登录的回调函数
const handleLogin = async () => {
  // 校验是否通过
  await formRef.value.validate();

  // 通过了, 弹出提示
  // @ts-ignore
  ElMessage.primary("登录中");

  // 进行登录相关操作
  userLoginService(form.value)
    .then((res) => {
      // 储存到本地
      userStore.setRefreshToken(res.data.refresh_token);
      userStore.setToken(res.data.token);
      userStore.setUser(res.data.user);

      // @ts-ignore
      ElMessage.success("登录成功");
      router.push("/");
    })
    .catch(() => {
      // @ts-ignore
      ElMessage.error("登录失败, 请重试");
    });
};

// 鼠标跟随光晕相关
const mouseX = ref(0);
const mouseY = ref(0);

// 监听鼠标移动事件
const handleMouseMove = (e: MouseEvent) => {
  mouseX.value = e.clientX;
  mouseY.value = e.clientY;
};

// 组件挂载时添加事件监听
onMounted(() => {
  document.addEventListener("mousemove", handleMouseMove);
});

// 组件卸载时移除事件监听
onUnmounted(() => {
  document.removeEventListener("mousemove", handleMouseMove);
});

// 定义当前环境
const currentEnvString = ref(
  settingStore.currentEnvironment === 0 ? "开发环境" : "生产环境",
);

watch(
  () => currentEnvString.value,
  (newVal) => {
    settingStore.setCurrentEnvironment(newVal === "开发环境" ? 0 : 1);
  },
);
</script>

<template>
  <div class="container">
    <!-- 静态光圈背景 -->
    <div class="bg-glow bg-glow-1"></div>
    <div class="bg-glow bg-glow-2"></div>
    <div class="bg-glow bg-glow-3"></div>
    <!-- 跟随鼠标移动的光晕 -->
    <div
      class="mouse-glow"
      :style="{
        left: `${mouseX}px`,
        top: `${mouseY}px`,
        transform: `translate(-50%, -50%)`,
      }"
    ></div>

    <el-card>
      <template #header>欢迎来到 校园E站</template>
      <!-- 提供一个表单就行 -->
      <el-form
        class="container-form"
        ref="formRef"
        :model="form"
        :rules="formRules"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input show-password type="password" v-model="form.password" />
        </el-form-item>
        <el-form-item>
          <el-button @click="handleLogin" type="primary">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <div class="env-changer">
        <span>当前登录环境: </span>
        <el-segmented
          v-model="currentEnvString"
          block
          :options="['开发环境', '生产环境']"
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.container {
  width: 100vw;
  height: 100vh;
  background-color: #0f1423;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 20px;
  position: relative;
  overflow: hidden;

  &-form {
    background-color: rgba(255, 255, 255, 0.95);
    height: 100%;
  }
}

// 登录卡片
.el-card {
  background-color: rgba($color: #ffffff, $alpha: 0.9) !important;

  .env-changer {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
  }

  .el-card__header {
    background-color: transparent;
  }

  .el-card__body {
    background-color: transparent;

    .el-form {
      background-color: transparent;
    }
  }
}

/* 静态光圈背景 */
.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.6;
  z-index: 0;
}

.bg-glow-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(
    circle,
    rgba(76, 175, 80, 0.8) 0%,
    rgba(76, 175, 80, 0) 70%
  );
  top: -200px;
  left: -100px;
  animation: glowMove 15s ease-in-out infinite alternate;
}

.bg-glow-2 {
  width: 600px;
  height: 600px;
  background: radial-gradient(
    circle,
    rgba(33, 150, 243, 0.8) 0%,
    rgba(33, 150, 243, 0) 70%
  );
  bottom: -300px;
  right: -200px;
  animation: glowMove 18s ease-in-out infinite alternate-reverse;
}

.bg-glow-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(
    circle,
    rgba(156, 39, 176, 0.8) 0%,
    rgba(156, 39, 176, 0) 70%
  );
  top: 50%;
  right: 10%;
  animation: glowMove 12s ease-in-out infinite alternate;
}

/* 跟随鼠标移动的光晕 */
.mouse-glow {
  position: fixed;
  width: 500px;
  height: 500px;
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.3) 0%,
    rgba(255, 255, 255, 0) 70%
  );
  pointer-events: none;
  z-index: 0;
  transition:
    left 0.1s ease-out,
    top 0.1s ease-out;
  mix-blend-mode: screen;
}

/* 光圈动画 */
@keyframes glowMove {
  0% {
    transform: translate(0, 0) scale(1);
  }

  50% {
    transform: translate(30px, 30px) scale(1.1);
  }

  100% {
    transform: translate(10px, -10px) scale(0.9);
  }
}

/* 卡片样式调整 */
:deep(.el-card) {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

:deep(.el-form-item__label) {
  color: #333;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-button--primary) {
  width: 100%;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
}
</style>
