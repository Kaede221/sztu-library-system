# 图书馆管理后台

## 安装依赖

```bash
# 请先创建虚拟环境 不建议在全局环境执行!
pip install -r requirements.txt

# 或者 手动安装
pip install fastapi uvicorn
pip install "uvicorn[standard]"
```

## 启动后台系统

```bash
uvicorn src.main:app --reload
```

## 生成依赖文档

```bash
pipreqs ./src/ --encoding=utf8  --force
```