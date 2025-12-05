import { getRequest } from "@/utils/request";

const request = getRequest();

/**
 * 简单统计信息响应类型（向后兼容）
 */
export interface ISimpleStatsResponse {
  total_users: number;
  total_books: number;
  total_categories: number;
  active_users: number;
}

/**
 * 获取简单统计信息（向后兼容）
 * @returns 统计信息
 */
export const getSimpleStatsService = () => {
  return request.get<ISimpleStatsResponse>("/simple-stats");
};

// ==================== 仪表盘统计 ====================

/**
 * 获取仪表盘统计数据
 * @returns 仪表盘统计
 */
export const getDashboardStatsService = () => {
  return request.get<IDashboardStats>("/stats/dashboard");
};

// ==================== 图书排行榜 ====================

/**
 * 获取借阅排行榜
 * @param params 查询参数
 * @returns 排行榜数据
 */
export const getBorrowRankingService = (params?: {
  limit?: number;
  days?: number;
}) => {
  return request.get<IBookRankingResponse>("/stats/book-ranking/borrow", { params });
};

/**
 * 获取评分排行榜
 * @param params 查询参数
 * @returns 排行榜数据
 */
export const getRatingRankingService = (params?: {
  limit?: number;
  min_reviews?: number;
}) => {
  return request.get<IBookRankingResponse>("/stats/book-ranking/rating", { params });
};

// ==================== 用户借阅统计 ====================

/**
 * 获取用户借阅统计
 * @param userId 用户ID（可选，不填则返回当前用户）
 * @returns 用户借阅统计
 */
export const getUserBorrowStatsService = (userId?: number) => {
  return request.get<{
    user_id: number;
    username: string;
    total_borrows: number;
    current_borrows: number;
    overdue_count: number;
    total_fines: number;
    unpaid_fines: number;
    max_borrow_count: number;
  }>("/stats/user-borrow-stats", { params: { user_id: userId } });
};

// ==================== 月度统计 ====================

/**
 * 获取月度统计数据 (管理员)
 * @param months 统计月数
 * @returns 月度统计
 */
export const getMonthlyStatsService = (months: number = 12) => {
  return request.get<IMonthlyStatsResponse>("/stats/monthly", { params: { months } });
};

// ==================== 分类统计 ====================

/**
 * 获取分类统计数据
 * @returns 分类统计
 */
export const getCategoryStatsService = () => {
  return request.get<ICategoryStatsResponse>("/stats/category");
};

// ==================== 其他统计 ====================

/**
 * 获取系统概览 (管理员)
 * @returns 系统概览
 */
export const getOverviewService = () => {
  return request.get<{
    today: {
      borrows: number;
      returns: number;
      new_users: number;
    };
    this_week: {
      borrows: number;
      returns: number;
    };
    inventory: {
      total_quantity: number;
      available_quantity: number;
      borrowed_quantity: number;
    };
    reviews: {
      total: number;
      avg_rating: number;
    };
    favorites: {
      total: number;
    };
  }>("/stats/overview");
};

/**
 * 获取借阅最多的用户 (管理员)
 * @param params 查询参数
 * @returns 用户列表
 */
export const getTopBorrowersService = (params?: {
  limit?: number;
  days?: number;
}) => {
  return request.get<{
    top_borrowers: Array<{
      user_id: number;
      username: string;
      full_name: string | null;
      borrow_count: number;
    }>;
  }>("/stats/top-borrowers", { params });
};

// 向后兼容的别名
export const getStatsService = getSimpleStatsService;
export type IStatsResponse = ISimpleStatsResponse;