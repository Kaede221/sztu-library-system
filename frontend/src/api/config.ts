import { getRequest } from "@/utils/request";

const request = getRequest();

// ==================== 配置查询接口 ====================

/**
 * 获取所有系统配置
 * @returns 配置列表
 */
export const getAllConfigsService = () => {
  return request.get<ISystemConfigListResponse>("/config/list");
};

/**
 * 获取指定配置
 * @param configKey 配置键
 * @returns 配置信息
 */
export const getConfigService = (configKey: string) => {
  return request.get<ISystemConfig>(`/config/${configKey}`);
};

/**
 * 获取配置值（简化接口）
 * @param configKey 配置键
 * @returns 配置值
 */
export const getConfigValueService = (configKey: string) => {
  return request.get<{ key: string; value: string }>(`/config/value/${configKey}`);
};

// ==================== 配置管理接口（管理员权限） ====================

/**
 * 创建新配置 (管理员)
 * @param data 配置数据
 * @returns 配置信息
 */
export const createConfigService = (data: ISystemConfigCreateRequest) => {
  return request.post<ISystemConfig>("/config/create", data);
};

/**
 * 更新配置 (管理员)
 * @param configKey 配置键
 * @param data 更新数据
 * @returns 配置信息
 */
export const updateConfigService = (configKey: string, data: ISystemConfigUpdateRequest) => {
  return request.put<ISystemConfig>(`/config/${configKey}`, data);
};

/**
 * 删除配置 (管理员)
 * @param configKey 配置键
 * @returns 消息响应
 */
export const deleteConfigService = (configKey: string) => {
  return request.delete<IMessageResponse>(`/config/${configKey}`);
};

// ==================== 批量操作接口 ====================

/**
 * 初始化默认配置 (管理员)
 * @returns 消息响应
 */
export const initDefaultConfigsService = () => {
  return request.post<IMessageResponse>("/config/init-defaults");
};

/**
 * 批量更新配置 (管理员)
 * @param configs 配置列表
 * @returns 消息响应
 */
export const batchUpdateConfigsService = (configs: ISystemConfigCreateRequest[]) => {
  return request.put<IMessageResponse>("/config/batch-update", configs);
};