<script setup lang="ts">
import { onBeforeMount, ref } from "vue";
import { getUserListService } from "@/api/user";
import UserInfoDialog from "@/components/UserInfoDialog.vue";
// @ts-ignore
import { Edit, Refresh, Search } from "@element-plus/icons-vue";

// 当前页面显示的用户列表
const userTableData = ref<IUser[]>([]);

// 总数
const total = ref(0);

// 每页大小
const pageSize = 15;

// 记录 是否表格正在加载
const isFormLoading = ref(false);

// 要搜索的用户名
const searchKeyword = ref("");

// 角色筛选
const roleFilter = ref<string>("");

// 状态筛选
const activeFilter = ref<boolean | undefined>(undefined);

// 记录当前是第几页
const currentPageIndex = ref(1);

// 定义方法 用来拉取用户数据
const fetchUserData = async () => {
  isFormLoading.value = true;
  try {
    const res = await getUserListService({
      skip: (currentPageIndex.value - 1) * pageSize,
      limit: pageSize,
      search: searchKeyword.value.trim() || undefined,
      role: roleFilter.value || undefined,
      is_active: activeFilter.value,
    });
    // @ts-ignore - 响应拦截器已处理
    userTableData.value = res.users || [];
    // @ts-ignore
    total.value = res.total || 0;
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isFormLoading.value = false;
  }
};

// 进入用户列表, 加载用户数据即可
onBeforeMount(async () => {
  await fetchUserData();
});

// 切换分页的回调函数
const handleChangePage = async (currentPage: number) => {
  currentPageIndex.value = currentPage;
  await fetchUserData();
};

// * 用户展示相关
// 定义是否显示展示弹窗
const showUserInfoDialog = ref(false);

// 当前展示的用户信息
const currentShowUserInfo = ref<IUser>();

// 弹窗的模式
const userInfoDialogMode = ref<"check" | "edit">("check");

// 查看用户信息
const handleCheckUserInfo = (userInfo: IUser, mode: "check" | "edit") => {
  showUserInfoDialog.value = true;
  currentShowUserInfo.value = userInfo;
  userInfoDialogMode.value = mode;
};

// 搜索用户
const handleSearch = async () => {
  currentPageIndex.value = 1;
  await fetchUserData();
};

// 重置筛选
const handleReset = async () => {
  searchKeyword.value = "";
  roleFilter.value = "";
  activeFilter.value = undefined;
  currentPageIndex.value = 1;
  await fetchUserData();
};

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleString("zh-CN");
};
</script>

<template>
  <div class="user-list-container">
    <!--顶部操作区域-->
    <el-card>
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名或邮箱"
          clearable
          @keyup.enter="handleSearch"
          style="width: 200px"
        />
        <el-select
          v-model="roleFilter"
          placeholder="角色筛选"
          clearable
          style="width: 120px"
        >
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-select
          v-model="activeFilter"
          placeholder="状态筛选"
          clearable
          style="width: 120px"
        >
          <el-option label="已激活" :value="true" />
          <el-option label="已禁用" :value="false" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">
          搜索
        </el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      </div>
    </el-card>

    <!--主要的用户信息表格-->
    <el-card>
      <el-table
        :data="userTableData"
        style="width: 100%"
        height="55vh"
        v-loading="isFormLoading"
      >
        <el-table-column fixed prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="full_name" label="全名" min-width="120">
          <template #default="scope">
            {{ scope.row.full_name || "-" }}
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'info'">
              {{ scope.row.role === "admin" ? "管理员" : "普通用户" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? "已激活" : "已禁用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
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
              @click="handleCheckUserInfo(scope.row, 'check')"
              title="查看"
            />
            <el-button
              type="warning"
              plain
              :icon="Edit"
              circle
              size="small"
              @click="handleCheckUserInfo(scope.row, 'edit')"
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

    <!-- 提供用户操作相关的弹窗 -->
    <UserInfoDialog
      :mode="userInfoDialogMode"
      v-model:visible="showUserInfoDialog"
      :current-user="currentShowUserInfo"
      @refresh-table="fetchUserData"
    />
  </div>
</template>

<style scoped lang="scss">
.user-list-container {
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
