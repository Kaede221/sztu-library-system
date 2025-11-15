import { getRequest } from "@/utils/request.js";

interface IUserLoginService {
  username: string;
  password: string;
}

declare interface IUserLoginServicePost {
  refresh_token: string;
  token: string;
  user: IUser;
}

/**
 * 用户登录
 * @param loginRequestObj
 */
export const userLoginService = async (loginRequestObj: IUserLoginService) => {
  return getRequest().post<IUserLoginServicePost>(
    "/admin/user/login",
    loginRequestObj,
  );
};

declare interface IGetUserListService {
  page?: number;
  size?: number;
  nickName?: string;
}

// 获取用户列表
export const getUserListService = async (reqObj: IGetUserListService) => {
  return getRequest().get("/admin/user/list", { params: reqObj });
};

/**
 * 删除用户信息
 * @param userId 需要删除的用户的ID
 */
export const userDeleteAuthInfoService = async (userId: number) => {
  return getRequest().post("/admin/user/clear", { userId });
};

interface IUserPreloadService {
  nick_name: string;
  pwd: string;
}

/**
 * 用户预认证接口
 * @param reqObj
 */
export const userPreloadService = async (reqObj: IUserPreloadService) => {
  const params = new URLSearchParams({
    nick_name: reqObj.nick_name,
    pwd: reqObj.pwd.trim(),
  });
  return getRequest().put(`/api/user/pre_authentication?${params.toString()}`);
};

interface IUserEditInfoService {
  avatar: string;
  nickname: string;
  power: number;
  stuCla: string;
  stuIsCheck: boolean;
  stuName: string;
  stuNum: string;
}

/**
 * 修改用户信息
 * @param id 需要修改的用户的ID
 * @param editObj 修改请求内容
 */
export const userEditInfoService = async (
  id: number,
  editObj: IUserEditInfoService,
) => {
  return getRequest().put(`/admin/user/${id}`, editObj);
};

/**
 * 获取目标用户的相关信息
 * @param target_user_id 需要获取的用户ID
 */
export const userGetTargetUserProfile = async (target_user_id: string) => {
  return getRequest().get("/api/user/user_profile", {
    params: { target_user_id },
  });
};
