# 校园E站 管理后台

## 项目介绍

校园E站管理后台是基于Vue 3 + TypeScript + Vite构建的现代化管理系统，为校园E站平台提供全面的管理功能。该项目是对原React版本的重构升级，拥有更丰富的功能特性和更优秀的用户体验。

## 技术栈

- **前端框架**: Vue 3
- **编程语言**: TypeScript
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **状态管理**: Pinia + pinia-plugin-persistedstate
- **路由管理**: Vue Router 4
- **HTTP客户端**: Axios
- **样式预处理器**: Sass
- **代码格式化**: Prettier

## 功能特性

- **用户管理**: 用户列表展示、用户信息编辑、用户状态管理
- **文章管理**: 文章列表展示、文章信息查看、文章审核管理
- **学期管理**: 学期信息管理、学期状态控制
- **系统设置**: 系统参数配置、个人资料管理
- **用户认证**: 登录授权、权限控制、Token管理
- **响应式设计**: 适配不同设备尺寸的响应式布局
- **国际化支持**: 支持中文语言环境

## 目录结构

```
src/
├── api/             # API接口定义
├── components/      # 通用组件
├── router/          # 路由配置
├── store/           # 状态管理
├── types/           # TypeScript类型定义
├── utils/           # 工具函数
├── views/           # 页面组件
├── App.vue          # 应用入口组件
├── main.ts          # 程序入口文件
└── style.css        # 全局样式
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 核心功能模块

### 1. 用户认证系统

- 基于Token的用户认证
- 路由守卫实现权限控制
- 自动处理Token过期和刷新
- 用户状态持久化存储

### 2. 数据管理功能

- 用户数据的增删改查
- 文章内容的管理与审核
- 学期信息的创建与维护

### 3. 系统设置

- 个人资料管理
- 系统参数配置

## API交互设计

- 统一的HTTP请求封装
- 请求和响应拦截器
- 错误处理机制
- Token认证集成

## 作者信息

- **作者**: kaedeshimizu
- **GitHub**: [Kaede221](https://github.com/Kaede221)
- **邮箱**: kaedeshimizu@qq.com

## 许可证

本项目采用 [MIT](https://opensource.org/licenses/MIT) 许可证
