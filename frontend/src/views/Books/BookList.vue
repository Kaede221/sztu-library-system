<script setup lang="ts">
import { onBeforeMount, ref } from "vue";
import { getBookListService, createBookService } from "@/api/book";
import { getCategoryListService } from "@/api/category";
import BookInfoDialog from "@/components/BookInfoDialog.vue";
// @ts-ignore
import { Edit, Refresh, Search, Plus } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

// 当前页面显示的图书列表
const bookTableData = ref<IBook[]>([]);

// 总数
const total = ref(0);

// 每页大小
const pageSize = 15;

// 记录 是否表格正在加载
const isFormLoading = ref(false);

// 要搜索的关键词
const searchKeyword = ref("");

// 书架位置筛选
const shelfLocationFilter = ref("");

// 分类筛选
const categoryFilter = ref<number | undefined>(undefined);

// 记录当前是第几页
const currentPageIndex = ref(1);

// 定义方法 用来拉取图书数据
const fetchBookData = async () => {
  isFormLoading.value = true;
  try {
    const res = await getBookListService({
      skip: (currentPageIndex.value - 1) * pageSize,
      limit: pageSize,
      search: searchKeyword.value.trim() || undefined,
      shelf_location: shelfLocationFilter.value || undefined,
      category_id: categoryFilter.value,
    });
    // @ts-ignore - 响应拦截器已处理
    bookTableData.value = res.books || [];
    // @ts-ignore
    total.value = res.total || 0;
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isFormLoading.value = false;
  }
};

// 进入图书列表, 加载图书数据即可
onBeforeMount(async () => {
  await fetchBookData();
  await fetchCategoryList();
});

// 切换分页的回调函数
const handleChangePage = async (currentPage: number) => {
  currentPageIndex.value = currentPage;
  await fetchBookData();
};

// * 图书展示相关
// 定义是否显示展示弹窗
const showBookInfoDialog = ref(false);

// 当前展示的图书信息
const currentShowBookInfo = ref<IBook>();

// 弹窗的模式
const bookInfoDialogMode = ref<"check" | "edit">("check");

// 查看图书信息
const handleCheckBookInfo = (bookInfo: IBook, mode: "check" | "edit") => {
  showBookInfoDialog.value = true;
  currentShowBookInfo.value = bookInfo;
  bookInfoDialogMode.value = mode;
};

// 搜索图书
const handleSearch = async () => {
  currentPageIndex.value = 1;
  await fetchBookData();
};

// 重置筛选
const handleReset = async () => {
  searchKeyword.value = "";
  shelfLocationFilter.value = "";
  categoryFilter.value = undefined;
  currentPageIndex.value = 1;
  await fetchBookData();
};

// * 新增图书相关
const showAddDialog = ref(false);
const addFormData = ref<IBookCreateRequest>({
  name: "",
  book_number: "",
  shelf_location: "",
  quantity: 0,
  preview_image: "",
  category_id: undefined,
});
const isAddSubmitting = ref(false);

// 分类列表
const categoryList = ref<ICategory[]>([]);
const isLoadingCategories = ref(false);

// 获取分类列表
const fetchCategoryList = async () => {
  isLoadingCategories.value = true;
  try {
    const res = await getCategoryListService({ limit: 500 });
    // @ts-ignore
    categoryList.value = res.categories || [];
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isLoadingCategories.value = false;
  }
};

// 根据分类ID获取分类名称
const getCategoryName = (categoryId: number | null | undefined): string => {
  if (!categoryId) return "-";
  const category = categoryList.value.find(cat => cat.id === categoryId);
  return category?.name || "-";
};

// 打开新增弹窗
const handleOpenAddDialog = () => {
  addFormData.value = {
    name: "",
    book_number: "",
    shelf_location: "",
    quantity: 0,
    preview_image: "",
    category_id: undefined as number | undefined,
  };
  showAddDialog.value = true;
  // 如果分类列表为空，则获取
  if (categoryList.value.length === 0) {
    fetchCategoryList();
  }
};

// 提交新增
const handleAddSubmit = async () => {
  if (!addFormData.value.name || !addFormData.value.book_number) {
    ElMessage.warning("请填写必要信息");
    return;
  }

  isAddSubmitting.value = true;
  try {
    await createBookService(addFormData.value);
    ElMessage.success("添加成功");
    showAddDialog.value = false;
    await fetchBookData();
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isAddSubmitting.value = false;
  }
};
</script>

<template>
  <div class="book-list-container">
    <!--顶部操作区域-->
    <el-card>
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索书名或图书编号"
          clearable
          @keyup.enter="handleSearch"
          style="width: 200px"
        />
        <el-input
          v-model="shelfLocationFilter"
          placeholder="书架位置筛选"
          clearable
          style="width: 150px"
        />
        <el-select
          v-model="categoryFilter"
          placeholder="分类筛选"
          clearable
          style="width: 150px"
          :loading="isLoadingCategories"
        >
          <el-option
            v-for="cat in categoryList"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">
          搜索
        </el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        <el-button type="success" :icon="Plus" @click="handleOpenAddDialog">
          新增图书
        </el-button>
      </div>
    </el-card>

    <!--主要的图书信息表格-->
    <el-card>
      <el-table
        :data="bookTableData"
        style="width: 100%"
        height="55vh"
        v-loading="isFormLoading"
      >
        <el-table-column fixed prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="图书名称" min-width="180" />
        <el-table-column prop="book_number" label="图书编号" min-width="120" />
        <el-table-column
          prop="shelf_location"
          label="书架位置"
          min-width="100"
        />
        <el-table-column prop="quantity" label="数量" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.quantity > 0 ? 'success' : 'danger'">
              {{ scope.row.quantity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_id" label="分类" width="120">
          <template #default="scope">
            <span>{{ getCategoryName(scope.row.category_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="preview_image" label="预览图" width="100">
          <template #default="scope">
            <el-image
              v-if="scope.row.preview_image"
              :src="scope.row.preview_image"
              style="width: 50px; height: 50px"
              fit="cover"
              :preview-src-list="[scope.row.preview_image]"
            >
              <template #error>
                <span style="font-size: 12px; color: #909399">无图</span>
              </template>
            </el-image>
            <span v-else style="font-size: 12px; color: #909399">无图</span>
          </template>
        </el-table-column>
        <!-- 提供操作列表 -->
        <el-table-column fixed="right" label="操作" width="120">
          <template #default="scope">
            <el-button
              type="primary"
              plain
              :icon="Search"
              circle
              size="small"
              @click="handleCheckBookInfo(scope.row, 'check')"
              title="查看"
            />
            <el-button
              type="warning"
              plain
              :icon="Edit"
              circle
              size="small"
              @click="handleCheckBookInfo(scope.row, 'edit')"
              title="编辑"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card>
      <el-pagination
        background
        layout="total, prev, pager, next, jumper"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPageIndex"
        @current-change="handleChangePage"
      />
    </el-card>

    <!-- 提供图书操作相关的弹窗 -->
    <BookInfoDialog
      :mode="bookInfoDialogMode"
      v-model:visible="showBookInfoDialog"
      :current-book="currentShowBookInfo"
      @refresh-table="fetchBookData"
    />

    <!-- 新增图书弹窗 -->
    <el-dialog v-model="showAddDialog" title="新增图书" width="500px">
      <el-form :model="addFormData" label-width="100px">
        <el-form-item label="图书名称" required>
          <el-input
            v-model="addFormData.name"
            placeholder="请输入图书名称"
          />
        </el-form-item>

        <el-form-item label="图书编号" required>
          <el-input
            v-model="addFormData.book_number"
            placeholder="请输入图书编号"
          />
        </el-form-item>

        <el-form-item label="书架位置" required>
          <el-input
            v-model="addFormData.shelf_location"
            placeholder="请输入书架位置"
          />
        </el-form-item>

        <el-form-item label="数量">
          <el-input-number v-model="addFormData.quantity" :min="0" />
        </el-form-item>

        <el-form-item label="预览图片">
          <el-input
            v-model="addFormData.preview_image"
            placeholder="请输入图片URL"
          />
        </el-form-item>

        <el-form-item label="分类">
          <el-select
            v-model="addFormData.category_id"
            placeholder="选择分类（可选）"
            clearable
            style="width: 100%"
            :loading="isLoadingCategories"
          >
            <el-option
              v-for="cat in categoryList"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button
            type="primary"
            :loading="isAddSubmitting"
            @click="handleAddSubmit"
            >确定</el-button
          >
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.book-list-container {
  display: flex;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}
</style>