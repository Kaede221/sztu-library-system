<script setup lang="ts">
import { onBeforeMount, ref, computed } from "vue";
import {
  getMyBorrowRecordsService,
  getCurrentBorrowsService,
  returnBookService,
  renewBookService,
} from "@/api/borrow";
// @ts-ignore
import { Refresh, Search, Back, Timer } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();
const isAdmin = computed(() => userStore.userInfo?.role === "admin");

// 当前借阅列表
const currentBorrows = ref<IBorrowRecordWithDetails[]>([]);
// 历史借阅列表
const historyBorrows = ref<IBorrowRecordWithDetails[]>([]);
// 总数
const total = ref(0);
// 每页大小
const pageSize = 10;
// 当前页
const currentPage = ref(1);
// 加载状态
const isLoading = ref(false);
// 当前标签页
const activeTab = ref("current");
// 状态筛选
const statusFilter = ref("");

// 获取当前借阅
const fetchCurrentBorrows = async () => {
  isLoading.value = true;
  try {
    const res = await getCurrentBorrowsService();
    // @ts-ignore
    currentBorrows.value = res.records || [];
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isLoading.value = false;
  }
};

// 获取历史借阅
const fetchHistoryBorrows = async () => {
  isLoading.value = true;
  try {
    const res = await getMyBorrowRecordsService({
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
      status_filter: statusFilter.value as BorrowStatus || undefined,
    });
    // @ts-ignore
    historyBorrows.value = res.records || [];
    // @ts-ignore
    total.value = res.total || 0;
  } catch {
    // 错误已在拦截器中处理
  } finally {
    isLoading.value = false;
  }
};

// 初始化
onBeforeMount(async () => {
  await fetchCurrentBorrows();
});

// 切换标签页
const handleTabChange = async (tab: string) => {
  if (tab === "current") {
    await fetchCurrentBorrows();
  } else {
    await fetchHistoryBorrows();
  }
};

// 切换分页
const handlePageChange = async (page: number) => {
  currentPage.value = page;
  await fetchHistoryBorrows();
};

// 归还图书
const handleReturn = async (record: IBorrowRecordWithDetails) => {
  try {
    await ElMessageBox.confirm(
      `确定要归还《${record.book?.name || "未知图书"}》吗？`,
      "确认归还",
      { type: "warning" }
    );
    
    await returnBookService(record.id);
    ElMessage.success("归还成功");
    await fetchCurrentBorrows();
  } catch (error: any) {
    if (error !== "cancel") {
      // 错误已在拦截器中处理
    }
  }
};

// 续借图书
const handleRenew = async (record: IBorrowRecordWithDetails) => {
  try {
    await ElMessageBox.confirm(
      `确定要续借《${record.book?.name || "未知图书"}》吗？续借后将延长14天。`,
      "确认续借",
      { type: "info" }
    );
    
    await renewBookService(record.id);
    ElMessage.success("续借成功");
    await fetchCurrentBorrows();
  } catch (error: any) {
    if (error !== "cancel") {
      // 错误已在拦截器中处理
    }
  }
};

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleDateString("zh-CN");
};

// 计算剩余天数
const getRemainingDays = (dueDate: string) => {
  const due = new Date(dueDate);
  const now = new Date();
  const diff = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  return diff;
};

// 获取状态标签类型
const getStatusType = (status: BorrowStatus) => {
  switch (status) {
    case "borrowed":
      return "primary";
    case "returned":
      return "success";
    case "overdue":
      return "danger";
    default:
      return "info";
  }
};

// 获取状态文本
const getStatusText = (status: BorrowStatus) => {
  switch (status) {
    case "borrowed":
      return "借阅中";
    case "returned":
      return "已归还";
    case "overdue":
      return "已逾期";
    default:
      return status;
  }
};

// 重置筛选
const handleReset = async () => {
  statusFilter.value = "";
  currentPage.value = 1;
  await fetchHistoryBorrows();
};
</script>

<template>
  <div class="borrow-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的借阅</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 当前借阅 -->
        <el-tab-pane label="当前借阅" name="current">
          <el-table :data="currentBorrows" v-loading="isLoading" style="width: 100%">
            <el-table-column prop="book.name" label="图书名称" min-width="180">
              <template #default="scope">
                {{ scope.row.book?.name || "未知图书" }}
              </template>
            </el-table-column>
            <el-table-column prop="book.author" label="作者" width="120">
              <template #default="scope">
                {{ scope.row.book?.author || "-" }}
              </template>
            </el-table-column>
            <el-table-column prop="borrow_date" label="借阅日期" width="120">
              <template #default="scope">
                {{ formatDate(scope.row.borrow_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="应还日期" width="120">
              <template #default="scope">
                <span :class="{ 'text-danger': getRemainingDays(scope.row.due_date) < 0 }">
                  {{ formatDate(scope.row.due_date) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="剩余天数" width="100">
              <template #default="scope">
                <el-tag :type="getRemainingDays(scope.row.due_date) < 0 ? 'danger' : 
                              getRemainingDays(scope.row.due_date) <= 3 ? 'warning' : 'success'">
                  {{ getRemainingDays(scope.row.due_date) }} 天
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="renew_count" label="续借次数" width="100">
              <template #default="scope">
                {{ scope.row.renew_count }} / 2
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="scope">
                <el-button
                  type="primary"
                  size="small"
                  :icon="Back"
                  @click="handleReturn(scope.row)"
                >
                  归还
                </el-button>
                <el-button
                  type="success"
                  size="small"
                  :icon="Timer"
                  :disabled="scope.row.renew_count >= 2 || scope.row.status === 'overdue'"
                  @click="handleRenew(scope.row)"
                >
                  续借
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="currentBorrows.length === 0 && !isLoading" description="暂无借阅记录" />
        </el-tab-pane>

        <!-- 历史借阅 -->
        <el-tab-pane label="借阅历史" name="history">
          <div class="filter-bar">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px">
              <el-option label="借阅中" value="borrowed" />
              <el-option label="已归还" value="returned" />
              <el-option label="已逾期" value="overdue" />
            </el-select>
            <el-button type="primary" :icon="Search" @click="fetchHistoryBorrows">搜索</el-button>
            <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          </div>

          <el-table :data="historyBorrows" v-loading="isLoading" style="width: 100%">
            <el-table-column prop="book.name" label="图书名称" min-width="180">
              <template #default="scope">
                {{ scope.row.book?.name || "未知图书" }}
              </template>
            </el-table-column>
            <el-table-column prop="borrow_date" label="借阅日期" width="120">
              <template #default="scope">
                {{ formatDate(scope.row.borrow_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="应还日期" width="120">
              <template #default="scope">
                {{ formatDate(scope.row.due_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="return_date" label="归还日期" width="120">
              <template #default="scope">
                {{ scope.row.return_date ? formatDate(scope.row.return_date) : "-" }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="fine_amount" label="罚款" width="100">
              <template #default="scope">
                <span v-if="scope.row.fine_amount > 0" class="text-danger">
                  ¥{{ scope.row.fine_amount.toFixed(2) }}
                  <el-tag v-if="scope.row.fine_paid" type="success" size="small">已付</el-tag>
                  <el-tag v-else type="danger" size="small">未付</el-tag>
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="total > pageSize"
            background
            layout="total, prev, pager, next"
            :total="total"
            :page-size="pageSize"
            :current-page="currentPage"
            @current-change="handlePageChange"
            style="margin-top: 20px; justify-content: center;"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.borrow-list-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.text-danger {
  color: #f56c6c;
}
</style>