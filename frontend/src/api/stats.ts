import { getRequest } from "@/utils/request";

const request = getRequest();

/**
 * 统计信息响应类型
 */
export interface IStatsResponse {
  total_users: number;
  total_books: number;
  active_users: number;
}

/**
 * 获取系统统计信息
 * @returns 统计信息
 */
export const getStatsService = () => {
  return request.get<IStatsResponse>("/stats");
};