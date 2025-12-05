import { getRequest } from "@/utils/request";

const request = getRequest();

// ==================== 用户通知接口 ====================

/**
 * 获取当前用户的通知列表
 * @param params 查询参数
 * @returns 通知列表
 */
export const getMyNotificationsService = (params?: {
  skip?: number;
  limit?: number;
  unread_only?: boolean;
  notification_type?: NotificationType;
}) => {
  return request.get<INotificationListResponse>("/notification/my-notifications", { params });
};

/**
 * 获取未读通知数量
 * @returns 未读数量
 */
export const getUnreadCountService = () => {
  return request.get<{ unread_count: number }>("/notification/unread-count");
};

/**
 * 标记通知为已读
 * @param notificationId 通知ID
 * @returns 通知记录
 */
export const markAsReadService = (notificationId: number) => {
  return request.post<INotification>(`/notification/mark-read/${notificationId}`);
};

/**
 * 标记所有通知为已读
 * @returns 消息响应
 */
export const markAllAsReadService = () => {
  return request.post<IMessageResponse>("/notification/mark-all-read");
};

/**
 * 删除通知
 * @param notificationId 通知ID
 * @returns 消息响应
 */
export const deleteNotificationService = (notificationId: number) => {
  return request.delete<IMessageResponse>(`/notification/${notificationId}`);
};

/**
 * 清空所有通知
 * @returns 消息响应
 */
export const clearAllNotificationsService = () => {
  return request.delete<IMessageResponse>("/notification/clear-all");
};

// ==================== 管理员接口 ====================

/**
 * 发送通知给指定用户 (管理员)
 * @param data 通知数据
 * @returns 通知记录
 */
export const sendNotificationService = (data: INotificationCreateRequest) => {
  return request.post<INotification>("/notification/send", data);
};

/**
 * 广播通知给所有用户 (管理员)
 * @param data 广播数据
 * @returns 消息响应
 */
export const broadcastNotificationService = (data: INotificationBroadcastRequest) => {
  return request.post<IMessageResponse>("/notification/broadcast", data);
};

/**
 * 获取所有通知 (管理员)
 * @param params 查询参数
 * @returns 通知列表
 */
export const getAllNotificationsService = (params?: {
  skip?: number;
  limit?: number;
  user_id?: number;
  notification_type?: NotificationType;
  unread_only?: boolean;
}) => {
  return request.get<INotificationListResponse>("/notification/list", { params });
};

/**
 * 管理员删除通知
 * @param notificationId 通知ID
 * @returns 消息响应
 */
export const adminDeleteNotificationService = (notificationId: number) => {
  return request.delete<IMessageResponse>(`/notification/admin/${notificationId}`);
};