<script setup lang="ts">
import { onBeforeMount, ref } from "vue";
import {
  getCategoryListService,
  getCategoryTreeService,
  createCategoryService,
  updateCategoryService,
  deleteCategoryService,
} from "@/api/category";
// @ts-ignore
import { Plus, Edit, Delete, Refresh } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";

// 分类列表
const categoryList = ref<ICategory[]>([]);
// 分类树
const categoryTree = ref<ICategoryWithChildren[]>([]);
// 加载状态
const isLoading = ref(false);
// 显示模式
const viewMode = ref<"list" | "tree">("tree");

// 弹窗相关
const showDialog = ref(false);
const dialogMode = ref<"create" | "edit">("create");
const currentCategory = ref<ICategory | null>(null);
const formData = ref<ICategoryCreateRequest>({
  name: "",
  description: "",
  parent_id: undefined,
  sort_order: 0,
});
const isSubmitting = ref(false);

// 获取分类列表
const fetchCategoryList = async () => {
  isLoading.value = true;
  try {
    const res = await getCategoryListService({ limit: 500 });
    // @ts-ignore
    categoryList.value = res.categories || [];
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isLoading.value = false;
  }
};

// 获取分类树
const fetchCategoryTree = async () => {
  isLoading.value = true;
  try {
    const res = await getCategoryTreeService();
    // @ts-ignore
    categoryTree.value = res.categories || [];
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isLoading.value = false;
  }
};

// 初始化
onBeforeMount(async () => {
  await fetchCategoryTree();
  await fetchCategoryList();
});

// 刷新数据
const handleRefresh = async () => {
  await fetchCategoryTree();
  await fetchCategoryList();
};

// 打开新增弹窗
const handleAdd = (parentId?: number) => {
  dialogMode.value = "create";
  currentCategory.value = null;
  formData.value = {
    name: "",
    description: "",
    parent_id: parentId,
    sort_order: 0,
  };
  showDialog.value = true;
};

// 打开编辑弹窗
const handleEdit = (category: ICategory) => {
  dialogMode.value = "edit";
  currentCategory.value = category;
  formData.value = {
    name: category.name,
    description: category.description || "",
    parent_id: category.parent_id || undefined,
    sort_order: category.sort_order,
  };
  showDialog.value = true;
};

// 提交表单
const handleSubmit = async () => {
  if (!formData.value.name) {
    ElMessage.warning("请输入分类名称");
    return;
  }

  isSubmitting.value = true;
  try {
    if (dialogMode.value === "create") {
      await createCategoryService(formData.value);
      ElMessage.success("创建成功");
    } else if (currentCategory.value) {
      await updateCategoryService(currentCategory.value.id, formData.value);
      ElMessage.success("更新成功");
    }
    showDialog.value = false;
    await handleRefresh();
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isSubmitting.value = false;
  }
};

// 删除分类
const handleDelete = async (category: ICategory) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类"${category.name}"吗？`,
      "确认删除",
      { type: "warning" }
    );
    
    await deleteCategoryService(category.id);
    ElMessage.success("删除成功");
    await handleRefresh();
  } catch (error: any) {
    if (error !== "cancel") {
      // 错误已在拦截器中处理
    }
  }
};

// 获取父分类选项（排除自己和子分类）
const getParentOptions = (excludeId?: number) => {
  if (!excludeId) return categoryList.value;
  
  const excludeIds = new Set<number>();
  excludeIds.add(excludeId);
  
  // 递归获取所有子分类ID
  const getChildIds = (parentId: number) => {
    categoryList.value.forEach(cat => {
      if (cat.parent_id === parentId) {
        excludeIds.add(cat.id);
        getChildIds(cat.id);
      }
    });
  };
  getChildIds(excludeId);
  
  return categoryList.value.filter(cat => !excludeIds.has(cat.id));
};

// 树形表格的属性
const treeProps = {
  children: "children",
  hasChildren: "hasChildren",
};
</script>

<template>
  <div class="category-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <div class="header-actions">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="tree">树形</el-radio-button>
              <el-radio-button label="list">列表</el-radio-button>
            </el-radio-group>
            <el-button type="primary" :icon="Plus" @click="handleAdd()">
              新增分类
            </el-button>
            <el-button :icon="Refresh" @click="handleRefresh">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 树形视图 -->
      <el-table
        v-if="viewMode === 'tree'"
        :data="categoryTree"
        v-loading="isLoading"
        row-key="id"
        :tree-props="treeProps"
        style="width: 100%"
      >
        <el-table-column prop="name" label="分类名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="200">
          <template #default="scope">
            {{ scope.row.description || "-" }}
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="100" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              :icon="Plus"
              @click="handleAdd(scope.row.id)"
            >
              添加子分类
            </el-button>
            <el-button
              type="warning"
              size="small"
              :icon="Edit"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 列表视图 -->
      <el-table
        v-else
        :data="categoryList"
        v-loading="isLoading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200">
          <template #default="scope">
            {{ scope.row.description || "-" }}
          </template>
        </el-table-column>
        <el-table-column prop="parent_id" label="父分类" width="150">
          <template #default="scope">
            <span v-if="scope.row.parent_id">
              {{ categoryList.find(c => c.id === scope.row.parent_id)?.name || "-" }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button
              type="warning"
              size="small"
              :icon="Edit"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="categoryList.length === 0 && !isLoading" description="暂无分类数据" />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="showDialog"
      :title="dialogMode === 'create' ? '新增分类' : '编辑分类'"
      width="500px"
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="分类名称" required>
          <el-input v-model="formData.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select
            v-model="formData.parent_id"
            placeholder="选择父分类（可选）"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="cat in getParentOptions(currentCategory?.id)"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="formData.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="isSubmitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.category-list-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>