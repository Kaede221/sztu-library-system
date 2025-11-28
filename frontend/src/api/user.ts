import { getRequest } from "@/utils/request";

const request = getRequest();

/**
 * 用户登录
 * @param data 登录参数 (username, password)
 * @returns Token信息
 */
export const userLoginService = (data: ILoginRequest) => {
  return request.post<ILoginResponse>("/user/login", data);
};

/**
 * 用户注册
 * @param data 注册参数
 * @returns 用户信息
 */
export const userRegisterService = (data: IRegisterRequest) => {
  return request.post<IUser>("/user/register", data);
};

/**
 * 获取当前用户信息
 * @returns 当前登录用户信息
 */
export const getCurrentUserService = () => {
  return request.get<IUser>("/user/me");
};

/**
 * 更新当前用户信息
 * @param data 更新参数
 * @returns 更新后的用户信息
 */
export const updateCurrentUserService = (data: IUserUpdateRequest) => {
  return request.put<IUser>("/user/me", data);
};

/**
 * 修改密码
 * @param data 修改密码参数
 * @returns 消息响应
 */
export const changePasswordService = (data: IChangePasswordRequest) => {
  return request.post<IMessageResponse>("/user/me/change-password", data);
};

/**
 * 获取用户列表 (管理员)
 * @param params 查询参数
 * @returns 用户列表
 */
export const getUserListService = (params?: {
  skip?: number | undefined;
  limit?: number | undefined;
  search?: string | undefined;
  role?: string | undefined;
  is_active?: boolean | undefined;
}) => {
  return request.get<IUserListResponse>("/user/list", { params });
};

/**
 * 根据ID获取用户 (管理员)
 * @param userId 用户ID
 * @returns 用户信息
 */
export const getUserByIdService = (userId: number) => {
  return request.get<IUser>(`/user/${userId}`);
};

/**
 * 更新用户信息 (管理员)
 * @param userId 用户ID
 * @param data 更新参数
 * @returns 更新后的用户信息
 */
export const updateUserService = (
  userId: number,
  data: IUserUpdateRequest & { role?: string; is_active?: boolean },
) => {
  return request.put<IUser>(`/user/${userId}`, data);
};

/**
 * 删除用户 (管理员)
 * @param userId 用户ID
 * @returns 消息响应
 */
export const deleteUserService = (userId: number) => {
  return request.delete<IMessageResponse>(`/user/${userId}`);
};

/**
 * 管理员创建用户
 * @param data 用户数据
 * @param role 用户角色
 * @returns 创建的用户信息
 */
export const createUserByAdminService = (
  data: IRegisterRequest,
  role: string = "user",
) => {
  return request.post<IUser>(`/user/create?role=${role}`, data);
};

/**
 * 初始化管理员账户
 * @returns 管理员用户信息
 */
export const initAdminService = () => {
  return request.post<IUser>("/user/init-admin");
};