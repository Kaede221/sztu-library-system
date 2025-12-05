import { getRequest } from "@/utils/request";

const request = getRequest();

// ==================== 评论操作 ====================

/**
 * 创建评论
 * @param data 评论数据
 * @returns 评论记录
 */
export const createReviewService = (data: IReviewCreateRequest) => {
  return request.post<IReview>("/review/create", data);
};

/**
 * 更新评论
 * @param reviewId 评论ID
 * @param data 更新数据
 * @returns 评论记录
 */
export const updateReviewService = (reviewId: number, data: IReviewUpdateRequest) => {
  return request.put<IReview>(`/review/${reviewId}`, data);
};

/**
 * 删除评论
 * @param reviewId 评论ID
 * @returns 消息响应
 */
export const deleteReviewService = (reviewId: number) => {
  return request.delete<IMessageResponse>(`/review/${reviewId}`);
};

// ==================== 评论查询 ====================

/**
 * 获取图书的评论列表
 * @param bookId 图书ID
 * @param params 查询参数
 * @returns 评论列表
 */
export const getBookReviewsService = (bookId: number, params?: {
  skip?: number;
  limit?: number;
}) => {
  return request.get<IReviewDetailListResponse>(`/review/book/${bookId}`, { params });
};

/**
 * 获取当前用户的评论列表
 * @param params 查询参数
 * @returns 评论列表
 */
export const getMyReviewsService = (params?: {
  skip?: number;
  limit?: number;
}) => {
  return request.get<IReviewDetailListResponse>("/review/my-reviews", { params });
};

/**
 * 获取评论详情
 * @param reviewId 评论ID
 * @returns 评论详情
 */
export const getReviewService = (reviewId: number) => {
  return request.get<IReviewWithUser>(`/review/${reviewId}`);
};

// ==================== 管理员接口 ====================

/**
 * 获取所有评论 (管理员)
 * @param params 查询参数
 * @returns 评论列表
 */
export const getAllReviewsService = (params?: {
  skip?: number;
  limit?: number;
  user_id?: number;
  book_id?: number;
  rating?: number;
  visible_only?: boolean;
}) => {
  return request.get<IReviewDetailListResponse>("/review/list", { params });
};

/**
 * 切换评论可见性 (管理员)
 * @param reviewId 评论ID
 * @returns 评论记录
 */
export const toggleReviewVisibilityService = (reviewId: number) => {
  return request.post<IReview>(`/review/toggle-visibility/${reviewId}`);
};