---
name: ci-failure-analysis
description: "下载 GitHub Actions 任务日志并统计分析失败测试用例。当用户提供 CI 任务链接（actions/runs/.../job/...）并要求统计失败用例、分析失败原因时调用。"
---

# CI 失败用例分析

从 GitHub Actions 任务链接下载日志，统计失败测试用例并分析失败原因。适用于 Ascend/sglang 等仓库的 CI 任务（unittest/pytest 风格日志）。

## 触发条件

- 用户提供 `https://github.com/<org>/<repo>/actions/runs/<run_id>/job/<job_id>` 链接
- 用户要求"统计失败用例"、"下载日志"、"分析失败原因"

## 分析流程

### 1. 解析链接，获取任务元数据

从 URL 提取 `run_id` 和 `job_id`，调用 API 确认任务名称与结论：

```powershell
Invoke-WebRequest -Uri "https://api.github.com/repos/<org>/<repo>/actions/jobs/<job_id>" -UseBasicParsing
```

确认 `name`（如 `full-1-npu-a3 / run (0)`）、`conclusion`、失败的 step。

### 2. 下载日志

**日志接口需要认证**，匿名访问返回 403。使用 `$env:GITHUB_TOKEN`：

```powershell
$h = @{ Authorization = "token $env:GITHUB_TOKEN"; "User-Agent" = "log-downloader" }
Invoke-WebRequest -Uri "https://api.github.com/repos/<org>/<repo>/actions/jobs/<job_id>/logs" -Headers $h -OutFile job_log.bin -UseBasicParsing
```

下载后检查文件头判断格式（`50 4B` 为 ZIP，否则为纯文本），重命名为 `job_log.txt` 或解压。

**Windows/PowerShell 注意事项**：
- `curl` 是 `Invoke-WebRequest` 的别名，不支持 `-w`/`-o` 等参数，如需真 curl 用 `curl.exe`
- 不要使用 shell 的 `grep`/`find`，使用 Grep / Glob 专用工具

### 3. 定位失败用例

按日志格式搜索失败标记（使用 Grep 工具，output_mode=content，-n=true）：

| 格式 | 模式 |
|------|------|
| unittest 单用例失败 | `ERROR: test_` 或 `FAIL: test_` |
| unittest 文件级结果 | `FAILED \(errors=` 或 `FAILED \(failures=` |
| pytest | `^.*FAILED ` |
| CI 框架文件级汇总 | `✗ FAILED:.*exit code` |
| 进程被杀 | `Process completed with exit code`、`Terminated`、`Killed` |

注意排除干扰项：如 `vmtouch: ... FAILED`（缓存预热工具缺失的告警，非测试失败）。

### 4. 映射失败用例到测试文件

CI 逐个执行测试文件（日志中有 `python3 /path/to/test_xxx.py` 行）。对每个失败用例，取其行号之前最近的一条 `python3 ... .py` 行即为所属文件。

### 5. 提取失败原因

读取每个失败用例上方 30~50 行的 Traceback，提取最终异常行：
- `AssertionError: ...`（精度/断言失败）
- `ConnectionError / Connection refused`（服务器崩溃或未拉起，环境稳定性问题）
- `AssertionError: 404 != 200`（接口路由问题）

### 6. 交叉验证

日志末尾通常有框架汇总（如 `TIMINGS` 块中 `"passed": false` 的条目、`✗ FAILED` 列表），与第 3 步结果比对确认数量一致。

### 7. 输出格式

输出 Markdown 表格：

| # | 失败文件 | 失败用例 | 错误原因 |
|---|---------|---------|---------|
| 1 | 相对路径 | 类名.方法名 | 异常类型 + 一句话原因 |

末尾补充：
- 失败文件数 / 失败用例数 / 通过文件数
- 失败分类（环境问题 / 精度断言 / 接口问题等）

## 经验要点

- unittest 风格日志中，`FAILED (errors=1)` 是文件级结果，`ERROR: test_xxx` 才是具体用例
- 每个失败文件通常对应 1 个失败用例，但以 `ERROR: test_`/`FAIL: test_` 计数为准
- `Connection refused` 类失败优先怀疑服务器进程崩溃，可在用例前日志搜索服务器侧报错（如 `core dump`、`TE_AUTO_RESTART`、TBE 报错）佐证