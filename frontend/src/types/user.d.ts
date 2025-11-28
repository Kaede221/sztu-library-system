// 用户角色枚举
type UserRole = "user" | "admin";

// 用户信息接口 - 匹配后端 UserResponse
interface IUser {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 登录请求参数
interface ILoginRequest {
  username: string;
  password: string;
}

// 登录响应 - Token信息
interface ILoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// 用户注册请求参数
interface IRegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

// 用户更新请求参数
interface IUserUpdateRequest {
  username?: string | undefined;
  email?: string | undefined;
  full_name?: string | undefined;
  password?: string | undefined;
}

// 修改密码请求参数
interface IChangePasswordRequest {
  old_password: string;
  new_password: string;
}

// 通用消息响应
interface IMessageResponse {
  message: string;
  success: boolean;
}

// 用户列表响应
interface IUserListResponse {
  total: number;
  users: IUser[];
}
