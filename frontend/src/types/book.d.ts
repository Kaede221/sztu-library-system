// 图书信息接口 - 匹配后端 Book schema
interface IBook {
  id: number;
  name: string;
  preview_image: string | null;
  book_number: string;
  shelf_location: string | null;
  quantity: number;
  available_quantity: number;
  
  // 新增字段
  author: string | null;
  isbn: string | null;
  publisher: string | null;
  publish_date: string | null;
  price: number | null;
  description: string | null;
  category_id: number | null;
  tags: string | null;
  
  // 统计字段
  borrow_count: number;
  avg_rating: number;
  review_count: number;
  
  created_at: string;
  updated_at: string;
}

// 图书详情（包含分类信息）
interface IBookWithCategory extends IBook {
  category: ICategory | null;
}

// 创建图书请求参数
interface IBookCreateRequest {
  name: string;
  book_number: string;
  shelf_location?: string;
  quantity: number;
  available_quantity?: number;
  preview_image?: string;
  author?: string;
  isbn?: string;
  publisher?: string;
  publish_date?: string;
  price?: number;
  description?: string;
  category_id?: number;
  tags?: string;
}

// 更新图书请求参数
interface IBookUpdateRequest {
  name?: string;
  preview_image?: string;
  book_number?: string;
  shelf_location?: string;
  quantity?: number;
  available_quantity?: number;
  author?: string;
  isbn?: string;
  publisher?: string;
  publish_date?: string;
  price?: number;
  description?: string;
  category_id?: number;
  tags?: string;
}

// 图书列表响应
interface IBookListResponse {
  total: number;
  books: IBook[];
}

// 图书列表查询参数
interface IBookListParams {
  skip?: number;
  limit?: number;
  search?: string;
  shelf_location?: string;
  category_id?: number;
  author?: string;
  available_only?: boolean;
  sort_by?: string;
  sort_order?: string;
}

// ==================== 分类相关 ====================

interface ICategory {
  id: number;
  name: string;
  description: string | null;
  parent_id: number | null;
  sort_order: number;
  created_at: string;
}

interface ICategoryWithChildren extends ICategory {
  children: ICategoryWithChildren[];
}

interface ICategoryCreateRequest {
  name: string;
  description?: string;
  parent_id?: number;
  sort_order?: number;
}

interface ICategoryUpdateRequest {
  name?: string;
  description?: string;
  parent_id?: number;
  sort_order?: number;
}

interface ICategoryListResponse {
  total: number;
  categories: ICategory[];
}

interface ICategoryTreeResponse {
  categories: ICategoryWithChildren[];
}

// ==================== 借阅相关 ====================

type BorrowStatus = 'borrowed' | 'returned' | 'overdue';

interface IBorrowRecord {
  id: number;
  user_id: number;
  book_id: number;
  borrow_date: string;
  due_date: string;
  return_date: string | null;
  status: BorrowStatus;
  renew_count: number;
  fine_amount: number;
  fine_paid: boolean;
  created_at: string;
}

interface IBorrowRecordWithDetails extends IBorrowRecord {
  user?: IUser;
  book?: IBook;
}

interface IBorrowCreateRequest {
  book_id: number;
  user_id?: number;
  borrow_days?: number;
}

interface IBorrowReturnRequest {
  fine_paid?: boolean;
}

interface IBorrowRenewRequest {
  renew_days?: number;
}

interface IBorrowRecordListResponse {
  total: number;
  records: IBorrowRecord[];
}

interface IBorrowRecordDetailListResponse {
  total: number;
  records: IBorrowRecordWithDetails[];
}

// ==================== 预约相关 ====================

type ReservationStatus = 'pending' | 'available' | 'completed' | 'cancelled' | 'expired';

interface IReservation {
  id: number;
  user_id: number;
  book_id: number;
  reservation_date: string;
  expire_date: string | null;
  status: ReservationStatus;
  queue_position: number;
  notified: boolean;
  created_at: string;
}

interface IReservationWithDetails extends IReservation {
  user?: IUser;
  book?: IBook;
}

interface IReservationCreateRequest {
  book_id: number;
}

interface IReservationListResponse {
  total: number;
  reservations: IReservation[];
}

interface IReservationDetailListResponse {
  total: number;
  reservations: IReservationWithDetails[];
}

// ==================== 评论相关 ====================

interface IReview {
  id: number;
  user_id: number;
  book_id: number;
  rating: number;
  content: string | null;
  is_visible: boolean;
  created_at: string;
  updated_at: string;
}

interface IReviewWithUser extends IReview {
  user?: IUser;
}

interface IReviewCreateRequest {
  book_id: number;
  rating: number;
  content?: string;
}

interface IReviewUpdateRequest {
  rating?: number;
  content?: string;
}

interface IReviewListResponse {
  total: number;
  reviews: IReview[];
}

interface IReviewDetailListResponse {
  total: number;
  reviews: IReviewWithUser[];
}

// ==================== 收藏相关 ====================

interface IFavorite {
  id: number;
  user_id: number;
  book_id: number;
  created_at: string;
}

interface IFavoriteWithBook extends IFavorite {
  book?: IBook;
}

interface IFavoriteCreateRequest {
  book_id: number;
}

interface IFavoriteListResponse {
  total: number;
  favorites: IFavorite[];
}

interface IFavoriteDetailListResponse {
  total: number;
  favorites: IFavoriteWithBook[];
}

interface IFavoriteCheckResponse {
  is_favorited: boolean;
  favorite_id: number | null;
}

// ==================== 通知相关 ====================

type NotificationType = 'borrow_due' | 'reservation_ready' | 'overdue' | 'system';

interface INotification {
  id: number;
  user_id: number;
  title: string;
  content: string;
  notification_type: NotificationType;
  is_read: boolean;
  related_id: number | null;
  created_at: string;
}

interface INotificationListResponse {
  total: number;
  unread_count: number;
  notifications: INotification[];
}

interface INotificationCreateRequest {
  user_id: number;
  title: string;
  content: string;
  notification_type?: NotificationType;
  related_id?: number;
}

interface INotificationBroadcastRequest {
  title: string;
  content: string;
}

// ==================== 统计相关 ====================

interface IDashboardStats {
  total_users: number;
  total_books: number;
  total_categories: number;
  active_users: number;
  total_borrow_records: number;
  active_borrows: number;
  overdue_borrows: number;
  total_reservations: number;
  pending_reservations: number;
}

interface IBookRankingItem {
  book_id: number;
  book_name: string;
  author: string | null;
  borrow_count: number;
  avg_rating: number;
}

interface IBookRankingResponse {
  rankings: IBookRankingItem[];
}

interface IMonthlyStats {
  month: string;
  borrow_count: number;
  return_count: number;
  new_users: number;
  new_books: number;
}

interface IMonthlyStatsResponse {
  stats: IMonthlyStats[];
}

interface ICategoryStats {
  category_id: number;
  category_name: string;
  book_count: number;
  borrow_count: number;
}

interface ICategoryStatsResponse {
  stats: ICategoryStats[];
}

// ==================== 系统配置相关 ====================

interface ISystemConfig {
  id: number;
  config_key: string;
  config_value: string;
  description: string | null;
  updated_at: string;
}

interface ISystemConfigCreateRequest {
  config_key: string;
  config_value: string;
  description?: string;
}

interface ISystemConfigUpdateRequest {
  config_value: string;
  description?: string;
}

interface ISystemConfigListResponse {
  configs: ISystemConfig[];
}