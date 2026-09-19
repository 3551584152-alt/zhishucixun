# 智枢词训（基于多智能体协同的四级英语自适应词汇学习项目）

CT4 系列迭代至 3.0 的四级英语自适应词汇学习系统：
**Vue 3.5.25（Vite）前端 + Django 6.1 纯 JSON API 后端**，前端由 Django 同源托管，彻底前后端解耦（Django 不再渲染业务页面模板）。

## 技术栈
| 层 | 技术 |
|---|---|
| 前端 | Vue 3.5.25 · Vite 6 · Vue Router 4（原 uni-app/Vue2 迁移而来） |
| 后端 | Django 6.1.1 · SQLite · simpleui 中文管理后台 |
| 接口 | 自定义 Bearer Token 鉴权（无第三方依赖） |
| AI | 本地结构化降级（未配大模型 Key 可离线演示，接口与 1.0 一致） |

## 目录结构
```
CT4项目2.0/
├─ manage.py / db.sqlite3
├─ ct4project/            # Django 项目配置（URL 分发、SPA 托管）
├─ core/                  # 核心应用
│  ├─ models.py           # Word / StudyRecord / ReviewState / ApiToken
│  ├─ services.py         # 取词/排程/统计/计划/词本/本地AI
│  ├─ ebbinghaus.py       # 考频加权艾宾浩斯复习算法
│  ├─ auth.py             # Token 鉴权
│  ├─ views.py / urls.py  # JSON API
│  ├─ data/word_bank.json # 内置 28 个 CET-4 示例词
│  └─ management/commands/seed_words.py
└─ frontend/              # Vue 3.5.25 前端（npm run build -> dist 由 Django 托管）
   ├─ src/views/          # Login/Study/Plan/AI/Stats/Notebook/Dict
   ├─ src/api/            # 接口封装（与 1.0 客户端契约一致）
   ├─ src/utils/          # config/ui/uni 适配/speech/offline
   └─ src/components/     # Ct4Header + 底部 TabBar
```

## 启动
```powershell
# 后端（自动托管前端 dist）
cd "D:\py\CT4项目2.0"
.venv\Scripts\Activate.ps1
python manage.py migrate          # 首次
python manage.py seed_words       # 首次导入词库
python manage.py runserver        # http://127.0.0.1:8000

# 前端（仅开发热更新需要，独立于 8000）
cd "D:\py\CT4项目2.0\frontend"
npm install
npm run dev                       # http://127.0.0.1:5174
npm run build                     # 重新构建 -> dist（部署以 8000 为准）
```

## 地址与账号
| 项 | 地址 | 账号 |
|---|---|---|
| 前端应用 | http://127.0.0.1:8000/ | 注册新账号或 demo / demo123 |
| Django 后台 | http://127.0.0.1:8000/admin/ | admin / Admin@2026 |
| API 健康检查 | http://127.0.0.1:8000/api/health | - |

## 功能清单
- 背诵：单词卡（考频/难度/英英美音朗读）、认识/模糊/忘记（艾宾浩斯排程）、AI 例句、词汇辅导
- 练习测试：英译汉 / 汉译英 / 拼写 / 诵读 四种题型
- 计划：今日队列（新学/复习/顽固词）、未来 7 天到期、快速复习
- AI 智能体：学情规划 / 词汇辅导 / 训练评估（四题型 + 顽固词特训，本地可演示）
- 统计：已学/掌握/正确率/连续天数/题型正确率/近 7 天趋势
- 词本：错题本 / 顽固词本（自动派生）
- 词典：词库浏览/搜索/详情 + 牛津词典外链

## 已修复的关键问题（迁移中）
1. 前端 5173 端口被占用 → 改 5174；最终由 Django 同源托管在 8000。
2. `/api/plan/daily?date=` 日期字符串未解析导致 500 → 已修复。
3. 读取路径误用 `get_or_create` 创建学习状态，导致“只看未学”的词从今日队列消失（背诵模块空）→ 已改为读取不建状态、按“是否作答过”判定新词，并清理误建数据。
## 大模型配置（已启用）
- Key 存放于项目根目录 .env（LLM_API_KEY / LLM_BASE_URL / LLM_MODEL），密钥只存在于后端。
- AI 例句、词汇辅导、学情规划、错题分析已接入 DeepSeek（OpenAI 兼容）；训练评估使用本地出题引擎保证稳定。
- 未配置或调用失败时自动降级为本地结果，不影响使用。
