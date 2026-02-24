# AI-Assistant-NEW GitHub 打包指南

本指南用于指导 OpenClaw 或其他自动化工具将此项目上传至 GitHub 并触发自动打包流程生成 Windows `.exe`。

## 1. 目录结构确认
确保 `AI-Assistant-NEW` 目录下包含以下核心文件：
- `app_eel.py` (主程序入口)
- `src/` (业务逻辑与核心驱动)
- `web/` (前端界面资源)
- `config/` (坐标与提示词配置)
- `.github/workflows/build_exe.yml` (自动打包脚本)
- `requirements.txt` (依赖清单)
- `catalog_template.xlsx` (目录模板)
- 以及其他数据文件夹 (`工具库`, `通用操作守则`)

## 2. GitHub 打包执行步骤

### 第一步：初始化并上传
在 `AI-Assistant-NEW` 目录中执行：
```bash
git init
git add .
git commit -m "Initialize modular AI Assistant with Eel UI"
# 请替换为您的实际仓库地址
git remote add origin https://github.com/您的用户名/您的仓库名.git
git branch -M main
git push -u origin main
```

### 第二步：触发自动构建
1. 打开浏览器进入您的 GitHub 仓库页面。
2. 点击顶部的 **Actions** 选项卡。
3. 侧边栏选择 **"Build Windows Exe"**。
4. 如果没有自动开始，点击 **"Run workflow"** 手动触发。

### 第三步：下载成品
1. 等待构建完成（出现绿色勾选框）。
2. 点击该次构建任务，拉到最下方的 **Artifacts**。
3. 下载 **AI-Work-Assistant-Windows** 压缩包。

## 3. 分发与运行
解压下载的压缩包，确保 `.exe` 文件与 `config`, `工具库` 等文件夹保持在**同级目录**下，双击运行即可。

---
*注：本文件由 AI Assistant 自动生成，用于指引自动化打包任务。*
