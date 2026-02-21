# Railway 部署说明

本项目已配置好通过 [Railway](https://railway.com) 进行云部署。

## 一、部署步骤

### 方式 A：从 GitHub 部署（推荐）

1. **推送代码到 GitHub**
   - 将本仓库 push 到你的 GitHub 仓库。

2. **在 Railway 创建项目**
   - 打开 [railway.app](https://railway.app) 并登录。
   - 点击 **New Project** → **Deploy from GitHub repo**。
   - 选择该仓库并授权（如未绑定 GitHub，按提示绑定）。

3. **配置环境变量**
   - 进入该 Service → **Variables**。
   - 添加变量（见下方「环境变量」）。

4. **生成公网域名**
   - **Settings** → **Networking** → **Generate Domain**。
   - 保存生成的 URL，即可通过浏览器访问。

### 方式 B：使用 Railway CLI

```bash
# 安装 CLI: https://docs.railway.com/develop/cli
npm i -g @railway/cli
# 或: brew install railway

railway login
railway init   # 选 Create new project
railway up     # 上传并部署
```

部署完成后在 Dashboard 里为该 Service 添加环境变量并 **Generate Domain**。

---

## 二、环境变量

在 Railway 的 **Variables** 中至少配置：

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `OPENAI_API_KEY` | 是 | OpenAI API Key，用于对话与 RAG 分析。 |

可选（若使用 Gemini）：

| 变量名 | 说明 |
|--------|------|
| `GEMINI_API_KEY` | 使用 `provider=gemini` 时需要。 |

本地开发时可在项目根目录使用 `.env` 文件（不要提交到 Git）。

---

## 三、注意事项

1. **SQLite 与文件存储**
   - 当前使用 SQLite（`agent.db`）和本地 `docs/` 做 RAG。Railway 实例重启或重新部署后，**磁盘数据会重置**，会话和索引会丢失。
   - 若需持久化，可后续在 Railway 添加 **Volume** 并把 `agent.db` 与 `data/`、`docs/` 等放到 Volume 路径。

2. **RAG 索引**
   - 首次部署或重启后，RAG 会按 `docs/` 下的文档重新建索引（若代码中有自动建索引逻辑）。确保所需文档已包含在仓库或通过 Volume 挂载。

3. **冷启动**
   - 使用 `sentence-transformers` 等模型时，首次请求可能较慢（模型加载），属正常现象。

---

## 四、已包含的部署相关文件

- **requirements.txt**：Python 依赖。
- **Procfile**：`web` 进程启动命令（uvicorn）。
- **railway.json**：Railway 构建与启动配置（Nixpacks + startCommand）。
- **runtime.txt**：建议的 Python 版本（如 3.11）。

如需改用 Docker 构建，可新增 `Dockerfile`，Railway 会优先使用 Dockerfile 构建。
