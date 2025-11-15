<script setup lang="ts">
import { ref, watch } from "vue";
import { semesterAddNewTerm } from "@/api/semester.js";
import { ElMessage } from "element-plus";

interface Props {
  semesterData: IItemSemester | null;
}

const visible = defineModel<boolean>("visible", { required: true });

const props = defineProps<Props>();
const emit = defineEmits(["update:visible", "updateForm"]);

const tempEmptyForm = ref<IItemSemester>({
  startDate: "",
  term: "",
  totalWeeks: 1,
});
const tempFormRef = ref();
const tempFormRules = {
  startDate: [{ required: true, message: "请输入开始日期", trigger: "blur" }],
  term: [
    { required: true, message: "请输入学期名称", trigger: "blur" },
    {
      pattern: /^\d{4}-\d{4}-\d$/,
      message: "学期需要按照固定格式: Year1-Year2-Term",
      trigger: "blur",
    },
  ],
  totalWeeks: [{ required: true, message: "请输入总周数", trigger: "blur" }],
};

// 添加学期
const addNewSemester = async () => {
  tempFormRef.value.validate().then(async () => {
    // 通过校验了 进行添加操作
    semesterAddNewTerm(tempEmptyForm.value)
      .then(() => {
        // @ts-ignore
        ElMessage.success("添加成功");
        emit("updateForm");
        handleClose();
      })
      .catch((err) => {
        // @ts-ignore
        ElMessage.error("添加失败");
        console.log(err);
      });
  });
};

// 通用的 关闭弹窗的操作
const handleClose = () => {
  visible.value = false;
  tempEmptyForm.value = {
    startDate: "",
    term: "",
    totalWeeks: 1,
  };
};
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="props.semesterData ? '查看学期' : '新增学期'"
    width="500px"
    @close="handleClose"
  >
    <el-form
      v-if="props.semesterData"
      :model="props.semesterData"
      label-width="100px"
    >
      <el-form-item label="学期名称">
        <el-input v-model="props.semesterData.term" disabled />
      </el-form-item>
      <el-form-item label="开始日期">
        <el-input v-model="props.semesterData.startDate" disabled />
      </el-form-item>
      <el-form-item label="周数">
        <el-input v-model="props.semesterData.totalWeeks" disabled />
      </el-form-item>
      <el-form-item label="学期ID">
        <el-input v-model="props.semesterData.id" disabled />
      </el-form-item>
    </el-form>
    <!--否则就是新增一个学期-->
    <el-form
      ref="tempFormRef"
      :model="tempEmptyForm"
      :rules="tempFormRules"
      v-else
      label-width="100px"
    >
      <el-form-item label="学期名称" prop="term">
        <el-input v-model="tempEmptyForm.term" placeholder="2024-2025-1" />
      </el-form-item>
      <el-form-item label="开始日期" prop="startDate">
        <el-date-picker
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          v-model="tempEmptyForm.startDate"
          type="date"
          placeholder="选择开始日期"
        />
      </el-form-item>
      <el-form-item label="周数" prop="totalWeeks">
        <el-input type="number" v-model="tempEmptyForm.totalWeeks" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="!props.semesterData"
          @click="addNewSemester"
          type="primary"
          >添加</el-button
        >
      </span>
    </template>
  </el-dialog>
</template>

<style scoped lang="scss"></style>
