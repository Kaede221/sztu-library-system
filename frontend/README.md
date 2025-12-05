# 图书馆管理系统 - 前端

基于 Vue 3 + TypeScript + Element Plus 构建的图书馆管理系统前端项目。

## 技术栈

- **框架**: Vue 3.5 (Composition API)
- **构建工具**: Vite 7
- **语言**: TypeScript 5.8
- **UI 组件库**: Element Plus 2.11
- **状态管理**: Pinia 3 + pinia-plugin-persistedstate
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **样式预处理**: Sass

## 项目结构

```
frontend/
├── public/                 # 静态资源
│   └── favicon.png
├── src/
│   ├── api/               # API 接口封装
│   │   ├── book.ts        # 图书相关接口
│   │   ├── stats.ts       # 统计相关接口
│   │   └── user.ts        # 用户相关接口
│   ├── components/        # 公共组件
│   │   ├── common/        # 通用组件
│   │   │   ├── CommonHeader.vue    # 顶部导航栏
│   │   │   └── CommonSidebar.vue   # 侧边栏菜单
│   │   ├── home/          # 首页组件
│   │   │   ├── StatisticInfo.vue   # 统计信息
│   │   │   └── SystemInfo.vue      # 系统信息
│   │   ├── settings/      # 设置组件
│   │   │   └── TransDuration.vue   # 过渡动画设置
│   │   ├── AddUserDialog.vue       # 添加用户弹窗
│   │   ├── BookInfoDialog.vue      # 图书信息弹窗
│   │   ├── SemesterInfoDialog.vue  # 学期信息弹窗
│   │   └── UserInfoDialog.vue      # 用户信息弹窗
│   ├── router/            # 路由配置
│   │   └── index.ts
│   ├── store/             # 状态管理
│   │   ├── index.ts       # Pinia 配置
│   │   ├── setting.ts     # 设置状态
│   │   └── user.ts        # 用户状态
│   ├── types/             # TypeScript 类型定义
│   │   ├── book.d.ts      # 图书类型
│   │   └── user.d.ts      # 用户类型
│   ├── utils/             # 工具函数
│   │   └── request.ts     # Axios 请求封装
│   ├── views/             # 页面视图
│   │   ├── Books/         # 图书管理
│   │   │   └── BookList.vue
│   │   ├── Home/          # 首页
│   │   │   └── HomeView.vue
│   │   ├── Login/         # 登录页
│   │   │   └── LoginPage.vue
│   │   ├── Other/         # 其他页面
│   │   │   ├── ProfilePage.vue     # 个人资料
│   │   │   └── SettingPage.vue     # 系统设置
│   │   ├── Users/         # 用户管理
│   │   │   └── UserList.vue
│   │   └── LayoutContainer.vue     # 布局容器
│   ├── App.vue            # 根组件
│   ├── main.ts            # 入口文件
│   └── style.css          # 全局样式
├── index.html             # HTML 模板
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript 配置
├── vite.config.ts         # Vite 配置
└── vercel.json            # Vercel 部署配置
```

## 功能模块

### 用户认证
- 用户登录/注册
- Token 认证 (Bearer Token)
- 路由守卫保护
- 登录状态持久化

### 用户管理 (管理员)
- 用户列表查看
- 用户信息编辑
- 用户角色管理
- 用户状态管理
- 创建/删除用户

### 图书管理
- 图书列表查看
- 图书搜索
- 图书信息编辑 (管理员)
- 图书添加/删除 (管理员)

### 系统设置
- 过渡动画时长设置
- 个人资料管理
- 密码修改

## 安装依赖

```bash
# 使用 yarn (推荐)
yarn install

# 或使用 npm
npm install
```

## 开发运行

```bash
# 启动开发服务器
yarn dev

# 或
npm run dev
```

开发服务器启动后，会自动打开浏览器访问 `http://localhost:5173`

## 构建部署

```bash
# 构建生产版本
yarn build

# 或
npm run build
```

构建产物将输出到 `dist/` 目录。

## 预览构建

```bash
# 预览构建后的项目
yarn preview

# 或
npm run preview
```

## 配置说明

### API 地址配置

API 基础地址在 [`src/utils/request.ts`](src/utils/request.ts:7) 中配置：

```typescript
const BASE_URL = "http://127.0.0.1:8000";
```

### 路径别名

项目配置了 `@` 路径别名指向 `src/` 目录，可在代码中使用：

```typescript
import { useUserStore } from "@/store/user";
```

## 开发规范

- 使用 Composition API 编写组件
- 使用 TypeScript 进行类型检查
- 使用 Prettier 进行代码格式化
- 组件命名采用 PascalCase
- API 接口函数命名采用 `xxxService` 格式

## 作者

- **梁宸 殷一婷**
- Email: kaedeshimizu@qq.com
- GitHub: [Kaede221](https://github.com/Kaede221)

## 许可证

MIT License