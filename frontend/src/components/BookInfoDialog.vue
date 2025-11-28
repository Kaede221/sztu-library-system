<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { updateBookService, deleteBookService } from "@/api/book";
import { ElMessage, ElMessageBox } from "element-plus";

// 定义props
const props = defineProps<{
  mode: "check" | "edit";
  visible: boolean;
  currentBook?: IBook;
}>();

// 定义emits
const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (e: "refreshTable"): void;
}>();

// 表单数据
const formData = ref<IBookUpdateRequest>({
  name: "",
  book_number: "",
  shelf_location: "",
  quantity: 0,
  preview_image: "",
});

// 是否正在提交
const isSubmitting = ref(false);

// 计算属性：是否为查看模式
const isCheckMode = computed(() => props.mode === "check");

// 计算属性：弹窗标题
const dialogTitle = computed(() => {
  return isCheckMode.value ? "查看图书信息" : "编辑图书信息";
});

// 监听currentBook变化，更新表单数据
watch(
  () => props.currentBook,
  (newBook) => {
    if (newBook) {
      formData.value = {
        name: newBook.name,
        book_number: newBook.book_number,
        shelf_location: newBook.shelf_location,
        quantity: newBook.quantity,
        preview_image: newBook.preview_image || "",
      };
    }
  },
  { immediate: true }
);

// 关闭弹窗
const handleClose = () => {
  emit("update:visible", false);
};

// 提交更新
const handleSubmit = async () => {
  if (!props.currentBook) return;

  isSubmitting.value = true;
  try {
    await updateBookService(props.currentBook.id, formData.value);
    ElMessage.success("更新成功");
    emit("update:visible", false);
    emit("refreshTable");
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isSubmitting.value = false;
  }
};

// 删除图书
const handleDelete = async () => {
  if (!props.currentBook) return;

  try {
    await ElMessageBox.confirm("确定要删除这本图书吗？", "删除确认", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await deleteBookService(props.currentBook.id);
    ElMessage.success("删除成功");
    emit("update:visible", false);
    emit("refreshTable");
  } catch {
    // 用户取消或错误已在拦截器中处理
  }
};
</script>

<template>
  <el-dialog
    :model-value="visible"
    :title="dialogTitle"
    width="500px"
    @close="handleClose"
  >
    <el-form :model="formData" label-width="100px" :disabled="isCheckMode">
      <el-form-item label="图书ID">
        <el-input :model-value="currentBook?.id?.toString()" disabled />
      </el-form-item>

      <el-form-item label="图书名称">
        <el-input v-model="formData.name" placeholder="请输入图书名称" />
      </el-form-item>

      <el-form-item label="图书编号">
        <el-input v-model="formData.book_number" placeholder="请输入图书编号" />
      </el-form-item>

      <el-form-item label="书架位置">
        <el-input
          v-model="formData.shelf_location"
          placeholder="请输入书架位置"
        />
      </el-form-item>

      <el-form-item label="数量">
        <el-input-number
          v-model="formData.quantity"
          :min="0"
          :disabled="isCheckMode"
        />
      </el-form-item>

      <el-form-item label="预览图片">
        <el-input
          v-model="formData.preview_image"
          placeholder="请输入图片URL"
        />
      </el-form-item>

      <el-form-item v-if="formData.preview_image" label="图片预览">
        <el-image
          :src="formData.preview_image"
          style="width: 100px; height: 100px"
          fit="cover"
        >
          <template #error>
            <div class="image-error">加载失败</div>
          </template>
        </el-image>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <template v-if="!isCheckMode">
          <el-button type="danger" @click="handleDelete">删除</el-button>
          <el-button type="primary" :loading="isSubmitting" @click="handleSubmit"
            >保存</el-button
          >
        </template>
      </span>
    </template>
  </el-dialog>
</template>

<style scoped lang="scss">
.image-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 12px;
}
</style>