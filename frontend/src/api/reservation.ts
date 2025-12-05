import { getRequest } from "@/utils/request";

const request = getRequest();

// ==================== 预约操作 ====================

/**
 * 预约图书
 * @param data 预约数据
 * @returns 预约记录
 */
export const createReservationService = (data: IReservationCreateRequest) => {
  return request.post<IReservation>("/reservation/create", data);
};

/**
 * 取消预约
 * @param reservationId 预约记录ID
 * @param reason 取消原因
 * @returns 预约记录
 */
export const cancelReservationService = (reservationId: number, reason?: string) => {
  return request.post<IReservation>(`/reservation/cancel/${reservationId}`, { reason });
};

/**
 * 完成预约（借阅预约的图书）
 * @param reservationId 预约记录ID
 * @returns 预约记录
 */
export const completeReservationService = (reservationId: number) => {
  return request.post<IReservation>(`/reservation/complete/${reservationId}`);
};

// ==================== 预约记录查询 ====================

/**
 * 获取当前用户的预约记录
 * @param params 查询参数
 * @returns 预约记录列表
 */
export const getMyReservationsService = (params?: {
  skip?: number;
  limit?: number;
  status_filter?: ReservationStatus;
}) => {
  return request.get<IReservationDetailListResponse>("/reservation/my-reservations", { params });
};

/**
 * 获取当前用户的有效预约
 * @returns 预约记录列表
 */
export const getActiveReservationsService = () => {
  return request.get<IReservationDetailListResponse>("/reservation/active");
};

/**
 * 获取预约记录详情
 * @param reservationId 预约记录ID
 * @returns 预约记录详情
 */
export const getReservationService = (reservationId: number) => {
  return request.get<IReservationWithDetails>(`/reservation/${reservationId}`);
};

/**
 * 获取图书的预约队列
 * @param bookId 图书ID
 * @returns 预约记录列表
 */
export const getBookReservationQueueService = (bookId: number) => {
  return request.get<IReservationListResponse>(`/reservation/book/${bookId}/queue`);
};

// ==================== 管理员接口 ====================

/**
 * 获取所有预约记录 (管理员)
 * @param params 查询参数
 * @returns 预约记录列表
 */
export const getAllReservationsService = (params?: {
  skip?: number;
  limit?: number;
  user_id?: number;
  book_id?: number;
  status_filter?: ReservationStatus;
}) => {
  return request.get<IReservationDetailListResponse>("/reservation/list", { params });
};

/**
 * 批量检查过期预约 (管理员)
 * @returns 消息响应
 */
export const batchCheckExpiredService = () => {
  return request.post<IMessageResponse>("/reservation/batch-check-expired");
};