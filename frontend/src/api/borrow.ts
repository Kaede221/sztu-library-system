import { getRequest } from "@/utils/request";

const request = getRequest();

// ==================== 借阅操作 ====================

/**
 * 借阅图书
 * @param data 借阅数据
 * @returns 借阅记录
 */
export const borrowBookService = (data: IBorrowCreateRequest) => {
  return request.post<IBorrowRecord>("/borrow/borrow", data);
};

/**
 * 归还图书
 * @param recordId 借阅记录ID
 * @param data 归还数据
 * @returns 借阅记录
 */
export const returnBookService = (recordId: number, data?: IBorrowReturnRequest) => {
  return request.post<IBorrowRecord>(`/borrow/return/${recordId}`, data || {});
};

/**
 * 续借图书
 * @param recordId 借阅记录ID
 * @param data 续借数据
 * @returns 借阅记录
 */
export const renewBookService = (recordId: number, data?: IBorrowRenewRequest) => {
  return request.post<IBorrowRecord>(`/borrow/renew/${recordId}`, data || {});
};

// ==================== 借阅记录查询 ====================

/**
 * 获取当前用户的借阅记录
 * @param params 查询参数
 * @returns 借阅记录列表
 */
export const getMyBorrowRecordsService = (params?: {
  skip?: number;
  limit?: number;
  status_filter?: BorrowStatus;
}) => {
  return request.get<IBorrowRecordDetailListResponse>("/borrow/my-records", { params });
};

/**
 * 获取当前用户正在借阅的图书
 * @returns 借阅记录列表
 */
export const getCurrentBorrowsService = () => {
  return request.get<IBorrowRecordDetailListResponse>("/borrow/current");
};

/**
 * 获取借阅记录详情
 * @param recordId 借阅记录ID
 * @returns 借阅记录详情
 */
export const getBorrowRecordService = (recordId: number) => {
  return request.get<IBorrowRecordWithDetails>(`/borrow/${recordId}`);
};

// ==================== 管理员接口 ====================

/**
 * 获取所有借阅记录 (管理员)
 * @param params 查询参数
 * @returns 借阅记录列表
 */
export const getAllBorrowRecordsService = (params?: {
  skip?: number;
  limit?: number;
  user_id?: number;
  book_id?: number;
  status_filter?: BorrowStatus;
  overdue_only?: boolean;
}) => {
  return request.get<IBorrowRecordDetailListResponse>("/borrow/list", { params });
};

/**
 * 支付罚款 (管理员)
 * @param recordId 借阅记录ID
 * @returns 借阅记录
 */
export const payFineService = (recordId: number) => {
  return request.post<IBorrowRecord>(`/borrow/pay-fine/${recordId}`);
};

/**
 * 批量检查逾期 (管理员)
 * @returns 消息响应
 */
export const batchCheckOverdueService = () => {
  return request.post<IMessageResponse>("/borrow/batch-check-overdue");
};