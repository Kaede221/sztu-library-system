import { getRequest } from "@/utils/request";

const request = getRequest();

/**
 * 获取分类列表
 * @param params 查询参数
 * @returns 分类列表
 */
export const getCategoryListService = (params?: {
  skip?: number;
  limit?: number;
  search?: string;
  parent_id?: number;
}) => {
  return request.get<ICategoryListResponse>("/category/list", { params });
};

/**
 * 获取分类树形结构
 * @returns 分类树
 */
export const getCategoryTreeService = () => {
  return request.get<ICategoryTreeResponse>("/category/tree");
};

/**
 * 根据ID获取分类
 * @param categoryId 分类ID
 * @returns 分类信息
 */
export const getCategoryByIdService = (categoryId: number) => {
  return request.get<ICategory>(`/category/${categoryId}`);
};

/**
 * 获取子分类
 * @param categoryId 父分类ID
 * @returns 子分类列表
 */
export const getCategoryChildrenService = (categoryId: number) => {
  return request.get<ICategoryListResponse>(`/category/${categoryId}/children`);
};

/**
 * 创建分类 (管理员)
 * @param data 分类数据
 * @returns 创建的分类信息
 */
export const createCategoryService = (data: ICategoryCreateRequest) => {
  return request.post<ICategory>("/category/create", data);
};

/**
 * 更新分类 (管理员)
 * @param categoryId 分类ID
 * @param data 更新参数
 * @returns 更新后的分类信息
 */
export const updateCategoryService = (categoryId: number, data: ICategoryUpdateRequest) => {
  return request.put<ICategory>(`/category/${categoryId}`, data);
};

/**
 * 删除分类 (管理员)
 * @param categoryId 分类ID
 * @param force 是否强制删除
 * @returns 消息响应
 */
export const deleteCategoryService = (categoryId: number, force: boolean = false) => {
  return request.delete<IMessageResponse>(`/category/${categoryId}`, { params: { force } });
};

/**
 * 批量创建分类 (管理员)
 * @param categories 分类列表
 * @returns 创建的分类列表
 */
export const batchCreateCategoriesService = (categories: ICategoryCreateRequest[]) => {
  return request.post<ICategory[]>("/category/batch-create", categories);
};