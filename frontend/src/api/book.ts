import { getRequest } from "@/utils/request";

const request = getRequest();

/**
 * 获取图书列表
 * @param params 查询参数
 * @returns 图书列表
 */
export const getBookListService = (params?: {
  skip?: number;
  limit?: number;
  search?: string;
  shelf_location?: string;
}) => {
  return request.get<IBookListResponse>("/book/list", { params });
};

/**
 * 根据ID获取图书
 * @param bookId 图书ID
 * @returns 图书信息
 */
export const getBookByIdService = (bookId: number) => {
  return request.get<IBook>(`/book/${bookId}`);
};

/**
 * 根据图书编号获取图书
 * @param bookNumber 图书编号
 * @returns 图书信息
 */
export const getBookByNumberService = (bookNumber: string) => {
  return request.get<IBook>(`/book/number/${bookNumber}`);
};

/**
 * 创建图书 (管理员)
 * @param data 图书数据
 * @returns 创建的图书信息
 */
export const createBookService = (data: IBookCreateRequest) => {
  return request.post<IBook>("/book/create", data);
};

/**
 * 更新图书信息 (管理员)
 * @param bookId 图书ID
 * @param data 更新参数
 * @returns 更新后的图书信息
 */
export const updateBookService = (bookId: number, data: IBookUpdateRequest) => {
  return request.put<IBook>(`/book/${bookId}`, data);
};

/**
 * 删除图书 (管理员)
 * @param bookId 图书ID
 * @returns 消息响应
 */
export const deleteBookService = (bookId: number) => {
  return request.delete<IMessageResponse>(`/book/${bookId}`);
};