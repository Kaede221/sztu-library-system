<script setup lang="ts">
import { onBeforeMount, ref } from "vue";
import { getUserListService } from "@/api/user.ts";
import UserInfoDialog from "@/components/UserInfoDialog.vue";
// @ts-ignore
import { Edit, Refresh, Search } from "@element-plus/icons-vue";

// 当前页面显示的用户列表
const userTabelData = ref<IUser[]>();

// 总页数
const totalPages = ref(0);

// 记录 是否表格正在加载
const isFormLoading = ref(false);

// 要搜索的用户名
const searchUserNickname = ref("");

// 定义方法 用来拉取用户数据
const fetchUserData = async (reqObj?: {
  page?: number;
  size?: number;
  nickName?: string;
}) => {
  isFormLoading.value = true;
  const res = await getUserListService({
    ...reqObj,
    size: 15,
    page: currentPageIndex.value,
    nickName: !!searchUserNickname.value.trim()
      ? searchUserNickname.value.trim()
      : "",
  });
  userTabelData.value = res.data.records;
  totalPages.value = res.data.pages;
  isFormLoading.value = false;
};

// 记录当前是第几页
const currentPageIndex = ref(1);

// 进入用户列表, 加载用户数据即可
onBeforeMount(async () => {
  await fetchUserData();
});

// 切换分页的回调函数
const handleChangePage = async (currentPage: number) => {
  currentPageIndex.value = currentPage;
  // 切换页面, 根据页面重新拉取数据
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
</script>

<template>
  <div class="user-list-container">
    <!--顶部操作区域-->
    <el-card>
      <div
        style="
          height: 100%;
          display: inline-flex;
          align-items: center;
          gap: 20px;
        "
      >
        <el-input
          v-model="searchUserNickname"
          placeholder="输入要搜索的用户昵称"
          @blur="handleSearch"
        />
        <el-button type="primary" plain :icon="Refresh" @click="fetchUserData"
          >刷新
        </el-button>
      </div>
    </el-card>
    <!--主要的用户信息表格-->
    <el-card>
      <el-table
        :data="userTabelData"
        style="width: 100%"
        height="61vh"
        v-loading="isFormLoading"
      >
        <el-table-column fixed prop="id" label="UID" width="80" />
        <el-table-column prop="avatar" label="用户头像" width="80">
          <template #default="scope">
            <el-avatar :src="scope.row.avatar" />
          </template>
        </el-table-column>
        <el-table-column prop="nickname" label="用户名" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="stuName" label="姓名" />
        <el-table-column prop="stuCla" label="班级" />
        <el-table-column prop="stuNum" label="学号" width="120" />
        <el-table-column prop="stuIsCheck" label="认证状态" width="100">
          <template #default="scope">
            <el-tag type="success" v-if="scope.row.stuIsCheck">已认证</el-tag>
            <el-tag type="warning" v-else>未认证</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="power"
          label="用户权限"
          width="120"
        ></el-table-column>
        <!-- 提供操作列表 -->
        <el-table-column fixed="right" label="操作" min-width="100">
          <template #default="scope">
            <el-button
              type="primary"
              plain
              :icon="Search"
              round
              circle
              @click="handleCheckUserInfo(scope.row, 'check')"
            ></el-button>
            <el-button
              type="danger"
              plain
              :icon="Edit"
              round
              circle
              @click="handleCheckUserInfo(scope.row, 'edit')"
            ></el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-card>
      <el-pagination
        background
        layout="prev, pager, next, jumper"
        :page-count="totalPages"
        @current-change="handleChangePage"
        :default-current-page="1"
      ></el-pagination>
    </el-card>

    <!-- 提供用户操作相关的弹窗 -->
    <UserInfoDialog
      :mode="userInfoDialogMode"
      v-model:visible="showUserInfoDialog"
      :current-user="currentShowUserInfo"
      @refresh-table="fetchUserData"
    ></UserInfoDialog>
  </div>
</template>

<style scoped lang="scss">
.user-list-container {
  display: flex;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
}
</style>
