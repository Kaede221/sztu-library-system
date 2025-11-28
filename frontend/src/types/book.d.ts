// 图书信息接口 - 匹配后端 Book schema
interface IBook {
  id: number;
  name: string;
  preview_image: string | null;
  book_number: string;
  shelf_location: string;
  quantity: number;
}

// 创建图书请求参数
interface IBookCreateRequest {
  name: string;
  preview_image?: string;
  book_number: string;
  shelf_location: string;
  quantity: number;
}

// 更新图书请求参数
interface IBookUpdateRequest {
  name?: string;
  preview_image?: string;
  book_number?: string;
  shelf_location?: string;
  quantity?: number;
}

// 图书列表响应
interface IBookListResponse {
  total: number;
  books: IBook[];
}