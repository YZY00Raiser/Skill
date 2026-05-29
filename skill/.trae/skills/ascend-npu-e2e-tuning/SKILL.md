---
name: "ascend-e2e-tuning"
description: "Ascend NPU 测试用例 CI 全流程自动化：提交用户指定的代码→PR→CI 触发→lint 修复→用例执行→根据报错修复。Invoke when user wants to submit existing test code to PR, run CI, and fix errors based on results (no shell-to-python conversion, no performance tuning)."
---

# Ascend NPU 测试用例 CI 全流程

将用户指定的 Python 测试代码提交到 PR，自动触发 CI，修复 lint 和运行时错误，确保测试用例通过。

---

## 一、使用方式

### 1.1 触发方式

在对话中描述任务意图即可自动触发，例如：

```
"提交这个测试用例到 PR 并跑 CI：test/registered/ascend/basic_function/HiCache_npu_new/test_npu_xxx.py"
"把这个测试用例提交到 PR 并修复 CI 报错"
"运行 test_npu_xxx.py 的 CI 测试并修复失败"
```

### 1.2 输入信息

输入信息分为**项目级（固定）**和**任务级（每次变化）**两类：

| 类型 | 信息 | 说明 | 示例 |
|------|------|------|------|
| 🔧 项目级 | 个人仓库 | Fork 的 sglang 仓库 | `YZY00Raiser/ascend-sglang` |
| 🔧 项目级 | 目标仓库 | 上游仓库 | `Ascend/sglang` |
| 🔧 项目级 | 目标分支 | PR 合入分支 | `testcases` |
| 🔧 项目级 | GitHub Token | 有 push 权限的 token | `ghp_xxx` |
| 🔧 项目级 | GitHub 账号 | PR 作者账号 | `YZY00Raiser` |
| 🔧 项目级 | 本地仓库路径 | 代码仓库绝对路径 | `d:\skill_test\sglang` |
| � 项目级 | Docker 镜像 | CI 运行使用的镜像 | `swr.cn-southwest-2.myhuaweicloud.com/base_image/dockerhub/lmsysorg/sglang:main-cann8.5.0-a3` |
| � 任务级 | 测试用例文件 | 要提交的 Python 测试文件路径 | `test/registered/ascend/basic_function/HiCache_npu_new/test_npu_xxx.py` |
| 📋 任务级 | 分支名称 | 新建的 PR 分支名 | `hicache-npu-new-testcases` |

### 1.3 配置文件（承载项目级信息）

项目级信息通过配置文件 `.trae/task_input.yml` 承载，**同一项目只需配置一次**，后续执行自动读取。

执行流程：
1. 启动时读取 `.trae/task_input.yml` 获取项目级信息
2. 若配置文件不存在，提示用户创建
3. 任务级信息从用户对话中获取

### 1.5 默认 Docker 镜像

CI 默认使用以下镜像：
```yaml
docker_image: swr.cn-southwest-2.myhuaweicloud.com/base_image/dockerhub/lmsysorg/sglang:main-cann8.5.0-a3
```

如需使用其他镜像，可在 `task_input.yml` 中配置 `docker_image` 字段覆盖默认值。

### 1.4 使用示例

**最简用法**（配置文件已存在时）：

```
"提交 test_npu_hicache_3fs_backend.py 到 PR 并跑 CI"
```

**完整用法**（指定所有信息）：

```
"按 task_input.yml 执行，测试用例：test/registered/ascend/basic_function/HiCache_npu_new/test_npu_xxx.py"
```

---

## 二、全流程步骤

### 阶段 1：创建分支并提交代码

**⚠️ 重要策略：用户未明确说明时，每个新用例必须新建独立 PR**

- **默认行为**：每个新用例创建新的分支和新的 PR，避免将之前已通过 CI 的用例再次加入流水线
- **yml 配置原则**：`single-test-npu.yml` 中只包含**当前要测试的用例**，不包含历史用例
- **修改范围**：用户未额外说明的情况下，只修改 `d:\transplant518test\sglang518\.github\workflows\single-test-npu.yml` 以配置当前用例，不添加其他用例
- **例外情况**：用户明确说"把用例 A 和 B 一起提交"或"添加到已有 PR"时才合并提交

#### 1.1 从模板生成 single-test-npu.yml

Skill 会自动使用模板文件生成 CI 配置：

```powershell
# 读取模板文件
$templatePath = ".trae/skills/ascend-npu-e2e-tuning/resources/single-test-npu.yml"
$templateContent = Get-Content $templatePath -Raw

# 替换占位符
$testCasePath = "test/registered/ascend/basic_function/xxx/test_npu_xxx.py"  # 用户指定的测试用例路径
$testRound = 1  # 测试轮次，每次触发 CI 时递增
$testDescription = "测试用例描述"  # 简要描述当前测试内容

$ymlContent = $templateContent `
    -replace "<TEST_CASE_PATH>", $testCasePath `
    -replace "test round 1: <测试用例描述>", "test round ${testRound}: ${testDescription}"

# 写入目标仓库
$targetYmlPath = "<本地仓库路径>/.github/workflows/single-test-npu.yml"
$ymlContent | Out-File -FilePath $targetYmlPath -Encoding utf8
```

**模板占位符说明**：

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `<TEST_CASE_PATH>` | 测试用例文件路径 | `test/registered/ascend/basic_function/lora/test_npu_lora_eviction.py` |
| `test round 1: <测试用例描述>` | 注释行，用于触发 CI | `test round 1: LoRA eviction test` |

**多测试用例配置**（用户明确要求时）：

```powershell
# 多个测试用例
$testCases = @(
    "test/registered/ascend/basic_function/lora/test_npu_lora_eviction.py",
    "test/registered/ascend/basic_function/lora/test_npu_lora_update.py"
)

# 构建 test_cases 数组内容
$testCasesArray = $testCases | ForEach-Object { "    \"$_\"" }
$testCasesContent = "test_cases=(`n" + ($testCasesArray -join "`n") + "`n)"

# 替换模板中的 test_cases 部分
$templateContent = $templateContent -replace "test_cases=\(\n    \"<TEST_CASE_PATH>\"\n\)", $testCasesContent
```

#### 1.2 创建分支并提交

```
git checkout -b <分支名> upstream/testcases   # 从上游新建干净分支
git add .github/workflows/single-test-npu.yml   # 添加生成的 yml 文件
git add <具体文件>                              # 添加测试用例文件（禁止 git add -A）
git commit -m "<描述>"
git push origin <分支名>
```

**分支命名建议**：
| 场景 | 分支名示例 |
|------|-----------|
| 新用例首次提交 | `test-lora-eviction` |
| 修复已有用例 | `fix-lora-tied-lm-head` |
| 用户明确要求合并多个用例 | `multi-lora-tests` |

通过 GitHub API 创建 PR（确保作者账号正确）：

```powershell
$headers = @{ "Authorization" = "token <TOKEN>"; "Accept" = "application/vnd.github+json" }
$body = @{
    title = "<PR 标题>"
    head = "YZY00Raiser:<分支名>"
    base = "testcases"
    body = "<PR 描述>"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/Ascend/sglang/pulls" -Headers $headers -Body $body -ContentType "application/json"
```

**创建 yml 时的检查清单**：
- [ ] yml 中 `test_case` 变量只指向**当前要测试的用例文件**
- [ ] 不包含之前已合并或已测试的其他用例路径
- [ ] 只修改 `d:\transplant518test\sglang518\.github\workflows\single-test-npu.yml` 配置当前用例
- [ ] 如需测试多个用例，确认用户已明确说明"一起提交"

### 阶段 2：CI 触发与 lint 修复

**触发方式**：修改 `single-test-npu.yml` 中的注释行递增测试轮次，触发 PR CI

```powershell
# 读取当前 yml 文件
$ymlPath = "<本地仓库路径>/.github/workflows/single-test-npu.yml"
$ymlContent = Get-Content $ymlPath -Raw

# 递增测试轮次（例如从 round 1 改为 round 2）
$currentRound = 1
$nextRound = $currentRound + 1
$ymlContent = $ymlContent -replace "test round ${currentRound}:", "test round ${nextRound}:"

# 写回文件
$ymlContent | Out-File -FilePath $ymlPath -Encoding utf8
```

修改后的注释行示例：
```yaml
name: Single Test (NPU)
# test round 2: <测试说明>  # 轮次递增触发 CI
```

**lint 常见问题及修复**：

| 问题 | 修复方式 |
|------|---------|
| black-jupyter 行超 88 字符 | 拆分类定义跨多行 |
| 文件编码 UTF-16 BOM | 用 Python 脚本重写为 UTF-8 |
| isort 导入顺序 | 按标准库→第三方→本地排序 |
| unused imports | 只导入用例实际使用的符号 |

**修复流程**：
1. 下载 lint 日志分析错误
2. 修改代码（**只修改当前用例相关文件，不要添加其他用例**）
3. `git add <具体文件>; git commit; git push`
4. 等待 CI 重新检查

**⚠️ 修复时的重要原则**：
- 修复 Lint 错误时，**只修改导致错误的文件**
- **禁止**在修复 Lint 的提交中顺便添加其他测试用例到 yml
- **修改范围限制**：只修改 `d:\transplant518test\sglang518\.github\workflows\single-test-npu.yml` 配置当前用例，不添加其他用例
- 如需添加新用例，应新建分支和 PR 单独提交

### 阶段 3：用例执行与错误修复

**常见运行时错误**：

| 错误 | 原因 | 修复 |
|------|------|------|
| `Invalid repo_id: model, must be of format namespace/name` | 模型路径大小写不匹配 ModelScope 仓库 | 修正路径大小写（如 `W8A8`→`w8a8`） |
| `ModuleNotFoundError: No module named 'sglang.test.ascend.e2e'` | sglang 包路径硬编码 | `sglang_pkg_path=$(pip show sglang \| grep Location \| awk '{print $2}')` |
| `The testcase does not exit` | yml 中引用的文件名与实际文件名不一致 | 检查文件名是否被 lint 重命名 |
| 服务器启动失败 | 环境变量/参数错误 | 对比 shell 脚本检查 |
| `AttributeError: 'xxx' object has no attribute 'set_embed'` | EAGLE3 draft 模型缺少 `set_embed` 方法（如 `DeepseekV3ForCausalLMNextN`） | **不能修改 sglang 源码**，在 CI yml 中给 draft 模型类设置 `load_lm_head_from_target = True`，让 `eagle_worker.py` 走现有的 `set_embed_and_head` 路径（见下方示例） |

**运行时启用 `load_lm_head_from_target` 示例**（不能修改 sglang 源码时使用）：

原理：`eagle_worker.py` 中 EAGLE3 初始化时检查模型是否有 `load_lm_head_from_target = True`：
- 有 → 调用 `set_embed_and_head()`（`DeepseekV2ForCausalLM` 父类已实现）
- 无 → 调用 `set_embed()`（DeepSeek 模型未实现）

所以只需给 draft 模型添加 `load_lm_head_from_target = True`，即可复用现有 `set_embed_and_head` 逻辑。

在 `single-test-npu.yml` 中，用 Python 修改容器内安装包（非 git 跟踪的源码仓库）：

由于 `check-yaml` 和 `check for duplicate workflow job names` 等 pre-commit 钩子无法处理 YAML `run:` 块内的多行 `python -c "..."` 字符串，因此必须使用**单行形式**：

```yaml
# Enable load_lm_head_from_target on DeepseekV3ForCausalLMNextN so that
# eagle_worker.py uses the existing set_embed_and_head (from DeepseekV2ForCausalLM)
# instead of calling the non-existent set_embed.
python -c "f=open('${sglang_pkg_path}/sglang/srt/models/deepseek_nextn.py');c=f.read();f.close();c=c.replace('self.logits_processor = LogitsProcessor(config)','self.logits_processor = LogitsProcessor(config)\n        self.load_lm_head_from_target = True\n        self.hot_token_id = None');f=open('${sglang_pkg_path}/sglang/srt/models/deepseek_nextn.py','w');f.write(c);f.close();print('Added load_lm_head_from_target=True and hot_token_id=None')"
```

> **注意**：必须使用单行 `python -c`，因为 YAML pre-commit 钩子（`check-yaml`、`check for duplicate workflow job names`）在解析 `run:` 块内的多行引号字符串时会误报语法错误。

**用例执行完成**：

用例执行完成后，查看 CI 结果并修复报错：

```powershell
$headers = @{ "Authorization" = "token <TOKEN>"; "Accept" = "application/vnd.github+json" }
$runs = Invoke-RestMethod -Uri "https://api.github.com/repos/Ascend/sglang/actions/runs?branch=<分支名>&per_page=5" -Headers $headers
$runs.workflow_runs | Select-Object name, status, conclusion, created_at

# 获取 job 日志
$jobs = Invoke-RestMethod -Uri "https://api.github.com/repos/Ascend/sglang/actions/runs/<run_id>/jobs" -Headers $headers
$jobId = ($jobs.jobs | Where-Object { $_.name -match "single-node-poc" }).id
$logs = Invoke-RestMethod -Uri "https://api.github.com/repos/Ascend/sglang/actions/jobs/$jobId/logs" -Headers $headers
$logs | Out-File -FilePath ".trae/ci_log_run<run_id>.txt" -Encoding utf8
```

根据日志分析错误并修复，直到所有测试通过。

**CI 轮询检查策略（节省 Token）**：

CI 执行需要较长时间，频繁轮询会消耗大量 API Token。等待时间应根据**用例数量**动态调整：

**基础时间估算（单用例）**：
| 阶段 | 建议等待时间 | 说明 |
|------|-------------|------|
| Lint 阶段 | 提交后等待 **3-5 分钟** 再首次检查 | Lint 通常 3-5 分钟完成 |
| NPU 测试阶段 | 首次检查等待 **10 分钟**，之后每 **5 分钟** 检查一次 | 模型加载和服务器启动耗时较长 |

**用例数量与等待时间调整**：

| 用例数量 | Lint 首次检查 | NPU 首次检查 | 后续轮询间隔 |
|---------|--------------|-------------|-------------|
| 1 个用例 | 3 分钟 | 10 分钟 | 5 分钟 |
| 2-3 个用例 | 5 分钟 | 15 分钟 | 5 分钟 |
| 4-5 个用例 | 7 分钟 | 20 分钟 | 5-10 分钟 |
| 5 个以上 | 10 分钟 | 25 分钟 | 10 分钟 |

**调整原则**：
- **Lint 阶段**：每增加 1 个用例文件，Lint 首次检查等待时间增加约 **1-2 分钟**（pre-commit 需要检查的文件增多）
- **NPU 测试阶段**：每增加 1 个用例，首次检查等待时间增加约 **3-5 分钟**（串行执行累积）
- 多个用例串行执行时，总时间 ≈ 基础时间 × 用例数量
- 如果 yml 中配置了 `timeout-minutes` 较长（如 120 分钟），说明预期执行时间很长，应相应延长等待时间

**轮询检查示例**：
```powershell
# 根据用例数量计算等待时间（示例：3 个用例）
$testCaseCount = 3
$lintWaitSeconds = 180 + ($testCaseCount - 1) * 120   # 3 + (3-1)*2 = 7 分钟
$npuFirstWaitSeconds = 600 + ($testCaseCount - 1) * 300   # 10 + (3-1)*5 = 20 分钟
$pollingIntervalSeconds = 300                             # 5 分钟

# 首次检查 Lint
Start-Sleep -Seconds $lintWaitSeconds
$runs = Invoke-RestMethod -Uri "https://api.github.com/repos/Ascend/sglang/actions/runs?branch=<分支名>&per_page=5" -Headers $headers

# 首次检查 NPU 测试
Start-Sleep -Seconds $npuFirstWaitSeconds
$runs = Invoke-RestMethod -Uri ...

# 后续轮询直到完成
while ($runs.workflow_runs | Where-Object { $_.status -eq "in_progress" }) {
    Start-Sleep -Seconds $pollingIntervalSeconds
    $runs = Invoke-RestMethod -Uri ...
}
```

**注意**：不要连续快速轮询（如每秒或每 30 秒），这会导致不必要的 Token 消耗。

**其他节省 Token 的建议**：

1. **日志过滤下载**：下载日志时使用关键词过滤，只获取错误相关行，避免下载完整日志（通常数万行）
   ```powershell
   $logs = Invoke-RestMethod -Uri "https://api.github.com/repos/Ascend/sglang/actions/jobs/$jobId/logs" -Headers $headers
   $lines = $logs -split "`n"
   $errorLines = $lines | Select-String -Pattern "(ERROR|FAILED|Traceback|Error|AssertionError)" | Select-Object -First 50
   $errorLines -join "`n"
   ```

2. **批量查询替代多次查询**：使用 `per_page=5` 一次获取多个 workflow runs，而不是逐个查询

3. **本地 pre-commit 预检查**：提交前在本地运行 `pre-commit run --all-files`，提前发现并修复 lint 问题，减少 CI 失败重试次数
   ```bash
   pip install pre-commit
   pre-commit install
   pre-commit run --all-files
   ```

4. **合并修复提交**：如果 Lint 和 NPU 测试可能同时失败，先本地修复所有已知问题，然后一次性提交，避免多次触发 CI

5. **复用已有分支**：如果同一测试用例需要多次调试，复用已有 PR 分支，避免重复创建 PR 消耗资源

6. **设置合理的超时**：yml 中 `timeout-minutes` 不要设置过长（如不需要 120 分钟可设为 60 分钟），失败后会更快释放资源

7. **单用例单 PR 原则**：默认每个新用例新建独立 PR，避免历史用例重复运行浪费资源。只有在用户明确要求时才合并多个用例到一个 PR

---

## 三、关键注意事项

### 3.1 Git 操作规范

| 规则 | 说明 |
|------|------|
| **禁止 `git add -A`** | 只 add 具体修改的文件 |
| **禁止 `git add .`** | 同上 |
| **禁止 `git stash`** | 会导致 .trae 目录文件丢失 |
| **禁止 `git clean`** | 会删除未跟踪的 .trae 文件 |
| **禁止 `git pull --rebase`** | 可能导致仓库损坏 |
| **使用 `git add <file1> <file2>...`** | 精确添加修改的文件 |
| **提交前检查** | `git diff --cached --stat` 确认变更范围 |

### 3.2 CI 触发条件

`single-test-npu.yml` 的 PR 触发条件：

```yaml
on:
  pull_request:
    paths:
      - ".github/workflows/single-test-npu.yml"  # 仅修改此文件触发
```

**因此**：每次需要修改 yml 文件（添加/修改注释行）才能触发 CI。

### 3.3 文件编码

- 所有 Python 文件必须为 **UTF-8** 编码
- 禁止 UTF-16 BOM
- 使用 Python 脚本写文件时指定 `encoding="utf-8"`, `newline="\n"`

### 3.4 .trae 目录

- 调优数据、日志等保存在 `.trae/` 目录
- **不推送到远程仓库**（通过 git add 精确排除）
- **禁止对 .trae 目录执行 git stash/clean 操作**

### 3.5 文件名一致性

- yml 中引用的文件名必须与实际文件名完全一致
- lint 可能自动重命名文件（如去掉 `_50ms` 后缀）
- 提交前检查 yml 引用与实际文件名是否匹配

---

## 四、完整执行流程图

```
1. 接收任务（指定测试用例文件）
   ↓
2. 创建分支并提交代码
   ↓
3. 提交 PR
   ↓
4. 触发 CI → Lint 检查
   ↓
5. 修复 Lint 错误（如有）
   ↓
6. 执行测试用例
   ↓
7. 分析报错并修复
   ↓
8. 重复步骤 4-7 直到所有测试通过
   ↓
9. 完成
```

---

## 五、API 参考

### GitHub Actions API

```powershell
# 获取 workflow runs
$runs = Invoke-RestMethod -Uri "https://api.github.com/repos/<owner>/<repo>/actions/runs?branch=<branch>&per_page=5" -Headers $headers

# 获取 job 日志
$jobs = Invoke-RestMethod -Uri "https://api.github.com/repos/<owner>/<repo>/actions/runs/<run_id>/jobs" -Headers $headers
$jobId = ($jobs.jobs | Where-Object { $_.name -match "<job_name>" }).id
$logs = Invoke-RestMethod -Uri "https://api.github.com/repos/<owner>/<repo>/actions/jobs/$jobId/logs" -Headers $headers
$logs | Out-File -FilePath ".trae/ci_log.txt" -Encoding utf8
```

### GitHub Pull Request API

```powershell
# 创建 PR
$body = @{
    title = "<PR 标题>"
    head = "<username>:<branch>"
    base = "testcases"
    body = "<PR 描述>"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/<owner>/<repo>/pulls" -Headers $headers -Body $body -ContentType "application/json"

# 关闭/重新打开 PR
$body = @{ state = "closed" } | ConvertTo-Json  # 或 "open"
Invoke-RestMethod -Method Patch -Uri "https://api.github.com/repos/<owner>/<repo>/pulls/<pr_number>" -Headers $headers -Body $body -ContentType "application/json"
```

---

## 六、自检清单

执行任务前检查：

- [ ] `.trae/task_input.yml` 配置正确
- [ ] GitHub Token 有效且有 push 权限
- [ ] 本地仓库路径正确
- [ ] 分支名唯一（不与现有分支重复）
- [ ] 测试用例文件存在且路径正确

提交前检查：

- [ ] 只 add 了具体修改的文件
- [ ] 提交信息清晰描述变更内容
- [ ] yml 中引用的文件名与实际文件名一致
- [ ] 代码格式通过本地 pre-commit 检查

CI 失败时检查：

- [ ] Lint 日志分析完整
- [ ] 修复了所有报告的格式问题
- [ ] 导入顺序正确（标准库→第三方→本地）
- [ ] 移除了未使用的导入
- [ ] 文件编码为 UTF-8
- [ ] 运行时日志分析完整
- [ ] 修复了所有报告的实际错误
