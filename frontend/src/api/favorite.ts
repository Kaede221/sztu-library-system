import { getRequest } from "@/utils/request";

const request = getRequest();

// ==================== 收藏操作 ====================

/**
 * 添加收藏
 * @param data 收藏数据
 * @returns 收藏记录
 */
export const addFavoriteService = (data: IFavoriteCreateRequest) => {
  return request.post<IFavorite>("/favorite/add", data);
};

/**
 * 取消收藏（通过图书ID）
 * @param bookId 图书ID
 * @returns 消息响应
 */
export const removeFavoriteService = (bookId: number) => {
  return request.delete<IMessageResponse>(`/favorite/remove/${bookId}`);
};

/**
 * 删除收藏（通过收藏ID）
 * @param favoriteId 收藏ID
 * @returns 消息响应
 */
export const deleteFavoriteService = (favoriteId: number) => {
  return request.delete<IMessageResponse>(`/favorite/${favoriteId}`);
};

// ==================== 收藏查询 ====================

/**
 * 获取当前用户的收藏列表
 * @param params 查询参数
 * @returns 收藏列表
 */
export const getMyFavoritesService = (params?: {
  skip?: number;
  limit?: number;
}) => {
  return request.get<IFavoriteDetailListResponse>("/favorite/my-favorites", { params });
};

/**
 * 检查是否已收藏某本书
 * @param bookId 图书ID
 * @returns 收藏状态
 */
export const checkFavoriteService = (bookId: number) => {
  return request.get<IFavoriteCheckResponse>(`/favorite/check/${bookId}`);
};

/**
 * 获取图书的收藏数量
 * @param bookId 图书ID
 * @returns 收藏数量
 */
export const getBookFavoriteCountService = (bookId: number) => {
  return request.get<{ book_id: number; favorite_count: number }>(`/favorite/book/${bookId}/count`);
};

// ==================== 管理员接口 ====================

/**
 * 获取所有收藏记录 (管理员)
 * @param params 查询参数
 * @returns 收藏列表
 */
export const getAllFavoritesService = (params?: {
  skip?: number;
  limit?: number;
  user_id?: number;
  book_id?: number;
}) => {
  return request.get<IFavoriteDetailListResponse>("/favorite/list", { params });
};

/**
 * 获取收藏最多的图书
 * @param limit 返回数量
 * @returns 热门图书列表
 */
export const getPopularBooksByFavoritesService = (limit: number = 10) => {
  return request.get<{
    popular_books: Array<{
      book_id: number;
      book_name: string;
      author: string | null;
      preview_image: string | null;
      favorite_count: number;
    }>;
  }>("/favorite/stats/popular-books", { params: { limit } });
};