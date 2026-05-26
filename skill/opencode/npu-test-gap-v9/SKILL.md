---
name: npu-test-gap-v9
description: Analyze GPU vs NPU test coverage gap for ANY specified directory, identify missing NPU tests (exclude unit tests only), and generate them. Use when asked about test coverage analysis, NPU test generation, or comparing GPU/NPU test suites for any feature module (lora, ep, moe, attention, etc.).
---

# NPU Test Gap Analysis Skill v9.1 (Universal Version with Chinese Documentation)

## Version History

| Version | Key Changes |
|---------|-------------|
| v9.1 | 1. **GPU_NPU_MAPPING_TABLE.md改为纯中文**，移除双语格式<br/>2. 保持测试文件docstring为英文（符合代码规范） |
| v9 | 1. Only exclude `*_unit.py` tests (include kernel/logprob_diff)<br/>2. **Merge documentation files**: GPU_NPU_MAPPING_TABLE.md combines README_GENERATED.md + mapping table into single file<br/>3. Bilingual content in one comprehensive report |
| v8 | Separate README_GENERATED.md and GPU_NPU_MAPPING_TABLE.md files |
| v7 | Basic NPU test generation with GPU mapping |

---

## Purpose

This skill analyzes GPU vs NPU test coverage for **any specified feature directory**, identifies missing NPU tests (excluding only unit tests), and generates proper NPU test files with **纯中文文档**.

**Key Changes (v9.1)**:
1. **GPU_NPU_MAPPING_TABLE.md纯中文**: 分析报告完全使用中文，更易阅读和维护
2. **测试文件docstring英文**: 代码文件保持英文docstring（符合国际代码规范）
3. Only `*_unit.py` tests are excluded. Kernel tests, logprob_diff tests, and all other functional tests are included and should be adapted for NPU where models/features are available.
4. **Single documentation file**: GPU_NPU_MAPPING_TABLE.md is the merged complete report (combines previous README_GENERATED.md + mapping table). No need to generate two separate files.

## Usage

```
User: 分析lora目录下gpu用例与npu用例差异
User: 分析ep目录下gpu和npu测试覆盖
User: 分析moe模块的测试缺失情况
```

## Workflow

### Phase 1: Architecture Analysis (Graphify)

Use graphify knowledge graph to understand the feature architecture:

```bash
graphify query "<feature_name>" --budget 3000
```

**Example queries:**
- `graphify query "lora"` - LoRA architecture
- `graphify query "expert_parallelism"` - EP architecture
- `graphify query "moe"` - MoE architecture

**Key nodes to identify:**
- Core managers (e.g., `LoRAManager`, `Scheduler`)
- Backend implementations (e.g., `TritonBackend`, `AscendBackend`)
- Config classes and data structures

### Phase 2: Collect GPU Integration Tests

**Integration test identification criteria:**

| Criteria | Integration Test | Unit Test |
|----------|-----------------|-----------|
| Server startup | Required | Not required |
| Runner type | `SRTRunner`, `HFRunner`, `popen_launch_server` | Mock objects |
| Functionality | End-to-end inference | Pure logic/kernel |
| External deps | Model weights, server | None or mocked |

**Files to EXCLUDE:**
- `*_unit.py` ONLY (unit-level tests without server/inference)
- Tests using `MagicMock`, `unittest.mock`
- Tests with `pytest` only (no server)
- API parsing tests without server
- **`test/manual/` directory** - Manual tests NOT running in CI pipeline

**Files to INCLUDE (DO NOT exclude):**
- `*_kernel.py` - Kernel tests should be adapted for NPU backend
- `logprob_diff` tests - Performance benchmarks should be adapted for NPU
- All other functional tests regardless of naming convention

**GPU test directories (ONLY analyze registered tests):**
- `test/registered/<feature>/` - Primary integration tests (CI pipeline)
- `test/srt/<feature>/` - SRT-level tests (if applicable)

**CRITICAL: Scope Limitation**
- **ONLY analyze files in the user-specified directory**
- Do NOT search for related tests in other directories (e.g., `4-gpu-models/`, `moe/`, etc.)
- Example: If user asks to analyze `cp/` directory, only analyze `test/registered/cp/`, NOT `test/registered/4-gpu-models/test_qwen3_30b.py`

**IMPORTANT:** Do NOT analyze `test/manual/<feature>/` - these tests are developer-only and not part of CI pipeline.

### Phase 3: Collect NPU Existing Tests

**NPU test directories:**
- `test/registered/ascend/basic_function/<feature>/`
- `test/registered/ascend/generated_tests/`
- `test/registered/ascend/performance/`

**Pattern matching:**
```
GPU: test_<feature>_xxx.py
NPU: test_npu_<feature>_xxx.py
```

**Generated tests directory naming:**

New NPU test files MUST be placed in a **clearly marked subdirectory** with **GENERATED** identifier:

**Naming Pattern (REQUIRED):**
```
test/registered/ascend/basic_function/<feature>/GENERATED_<YYYYMMDD>/test_npu_<feature>_*.py
test/registered/ascend/generated_tests/<feature>_GENERATED_<YYYYMMDD>/test_npu_<feature>_*.py
```

**Key naming requirements:**
1. **Prefix**: MUST use `GENERATED_` prefix (uppercase) for easy identification
2. **Date suffix**: YYYYMMDD format for version tracking
3. **NPU test prefix**: All test files MUST start with `test_npu_`

**Example:**
```
test/registered/ascend/basic_function/lora/GENERATED_20260521/
├── test_npu_lora_update.py
├── test_npu_lora_eviction.py
└── GPU_NPU_MAPPING_TABLE.md  # Complete report (merged)

test/registered/ascend/basic_function/parallel_strategy/context_parallelism/GENERATED_20260523/
├── test_npu_deepseek_v3_2_cp.py
└── GPU_NPU_MAPPING_TABLE.md  # Complete report (merged)
```

**Generated test file docstring (English only - REQUIRED):**

Test class docstrings should be in English only, with minimal content. Detailed information goes in GPU_NPU_MAPPING_TABLE.md.

**Docstring format (SIMPLIFIED):**
```python
class TestNPUFeature(CustomTestCase):
    """Test [FEATURE] on NPU.

    [Test Category] Feature
    [Test Target] [target components]
    """
```

**DO NOT include in test file docstring:**
- ❌ "Adapted from GPU test: xxx" (put in GPU_NPU_MAPPING_TABLE.md)
- ❌ "Key adaptations for NPU" (put in GPU_NPU_MAPPING_TABLE.md)
- ❌ Chinese comments (put in GPU_NPU_MAPPING_TABLE.md)
- ❌ Detailed adaptation notes (put in GPU_NPU_MAPPING_TABLE.md)

**Code comments in test body (ALLOWED):**
- ✅ English comments explaining logic (e.g., "# First request - no cache")
- ✅ Comments for test steps (e.g., "# Warmup phase", "# Main test")
- ❌ Chinese comments in code body (put in GPU_NPU_MAPPING_TABLE.md)

**GPU_NPU_MAPPING_TABLE.md模板（纯中文 - 必需）：**

**完整分析报告文件，包含所有分析、映射和执行信息：**

```markdown
# GPU与NPU <FEATURE中文> 测试覆盖分析（完整报告）

**分析日期**: YYYY-MM-DD

**分析范围**: test/registered/<feature>/ (仅此目录)

**生成器**: npu-test-gap-v9.1 skill

---

## 1. 排除测试（仅单元测试）

(排除的单元测试列表，若无则说明"本目录无单元测试排除")

---

## 2. GPU集成测试摘要

| GPU测试文件 | 测试类 | 测试类型 | 模型 | 配置 | 测试场景 |
|------------|--------|---------|------|------|---------|
| test_xxx.py | TestClassA | 集成测试 | Model-A | TP=4 | 功能测试 |
| test_yyy.py | TestClassB | 性能测试 | Model-B | - | 性能对比 |

---

## 3. NPU现有测试摘要

| NPU测试文件 | 测试类 | 模型 | 配置 | 测试场景 | 状态 |
|------------|--------|------|------|---------|------|
| test_npu_xxx.py | TestClassA | Model-A-NPU | TP=4 | 功能测试 | 已存在 |
| test_npu_yyy.py | TestClassB | Model-B-NPU | TP=2 | 性能测试 | 已生成 |

---

## 4. GPU-NPU测试映射表（完整）

**关键输出：展示精确的测试对应关系**

| 序号 | GPU测试文件 | GPU测试类 | 测试类型 | 模型 | NPU测试文件 | NPU测试类 | 映射状态 | NPU状态 | 关键适配说明 |
|-----|------------|----------|---------|------|------------|----------|---------|---------|-------------|
| 1 | test_xxx.py | TestClassA | 集成测试 | Model-A | test_npu_xxx.py | TestClassA | ⚠️ 已适配 | 已生成 | 模型已更换 |
| 2 | test_yyy.py | TestClassB | 性能测试 | 大模型 | - | - | ❌ 不支持 | - | 模型权重不可用 |
| 3 | test_zzz.py | TestClassC | 性能测试 | Model-C | test_npu_zzz.py | TestClassC | ⚠️ 已适配 | 已生成 | HF对比已跳过 |

**适配说明示例**：
- "模型：大模型 → 小模型（NPU简化版本）"
- "HF对比已跳过 - 仅NPU上运行SGLang推理"
- "模型权重在NPU上不可用 - 标记为不支持"
- "EAGLE推测解码不支持NPU - 已移除"

---

## 5. 覆盖率统计

**生成前**：
- GPU测试数量：X
- NPU测试数量：0
- 覆盖率：**0%** (0/X)

**生成后**：
- GPU测试数量：X
- NPU测试数量：Y（已生成）
- 支持的测试：Z
- 不支持的测试：W（模型权重不可用）
- **有效覆盖率**：Z/X%

---

## 6. 差距分析矩阵

| GPU测试 | NPU支持原因 | 状态 | 所需操作 |
|--------|------------|------|---------|
| test_xxx.py | ✅ 模型可用，功能支持 | 已生成 | 运行测试验证阈值 |
| test_yyy.py | ❌ 模型权重不可用 | 不支持 | 申请模型权重或使用替代模型 |

---

## 7. NPU测试增强机会

### 7.1 模型可用性问题
（说明哪些模型在NPU上不可用）

### 7.2 算法支持
（说明GPU与NPU算法差异，如EAGLE → EAGLE3）

### 7.3 后端考虑
（说明后端差异，如Triton → Ascend）

### 7.4 量化方案
（说明量化差异，如FP8 → W8A8）

---

## 8. 推荐测试生成优先级

### 阶段1（已完成）
| 优先级 | GPU测试 | 功能 | NPU适配 | 模型路径 | 配置 | 状态 |
|-------|--------|------|--------|---------|------|------|
| 高 | test_xxx.py | 功能A | 模型适配 | PATH_A | TP=8 | ✅ 已生成 |

### 阶段2（受阻 - 模型权重）
| 优先级 | GPU测试 | 功能 | 阻碍因素 | 解决方案 |
|-------|--------|------|---------|---------|
| 中 | test_yyy.py | 功能B | 模型不可用 | 申请权重 |

---

## 9. NPU关键适配说明

### 9.1 算法适配
（算法层面的适配说明）

### 9.2 后端适配
（后端层面的适配说明）

### 9.3 模型适配
（模型层面的适配说明）

### 9.4 并行策略
（并行策略层面的适配说明）

### 9.5 评估阈值
（评估阈值的调整说明）

### 9.6 环境变量
（必要的NPU环境变量）

### 9.7 超时调整
（超时时间的调整说明）

---

## 10. 生成的NPU测试场景

### 10.1 test_npu_xxx.py
**TestClassA**

**测试类别**: 功能测试

**测试目标**:
- 目标组件1
- 目标组件2

**测试方法**:
1. `test_method_a()`: 验证功能A
2. `test_method_b()`: 验证功能B

**服务配置**:
```
--trust-remote-code
--attention-backend ascend
--其他参数...
```

---

## 11. 运行测试

### 11.1 运行所有生成测试
```bash
python -m unittest sglang518.test.registered.ascend.basic_function.<feature>.GENERATED_YYYYMMDD.test_npu_xxx.TestClassA
```

### 11.2 运行特定测试方法
```bash
python -m unittest ...TestClassA.test_method_a
```

### 11.3 语法验证
```bash
python -m py_compile sglang518/test/registered/ascend/basic_function/<feature>/GENERATED_YYYYMMDD/test_npu_xxx.py
```

---

## 12. 后续工作

### 12.1 受阻任务（模型权重）
（说明哪些任务因模型不可用而受阻）

### 12.2 阈值验证
（说明需要验证的阈值）

### 12.3 扩展测试
（说明可能扩展的测试）

### 12.4 集成工作
（说明CI集成工作）

---

## 13. 总结

当前NPU <FEATURE中文>测试覆盖率已从 **X%** 提升至 **Y%**，共生成Z个新测试。

**主要限制**：
1. ❌ 限制1：说明
2. ⚠️ 限制2：说明

**建议**：
1. 建议1
2. 建议2

---

## 14. 生成的文件

| 文件 | 目录 | 描述 |
|-----|------|------|
| test_npu_xxx.py | GENERATED_YYYYMMDD/ | 功能测试 |
| GPU_NPU_MAPPING_TABLE.md | GENERATED_YYYYMMDD/ | 完整分析报告（本文件） |

**完整路径**:
```
sglang518/test/registered/ascend/basic_function/<feature>/GENERATED_YYYYMMDD/
├── test_npu_xxx.py
├── test_npu_yyy.py
└── GPU_NPU_MAPPING_TABLE.md
```

**File placement requirement:**
- `GPU_NPU_MAPPING_TABLE.md` MUST be placed in `GENERATED_<YYYYMMDD>/` directory
- Example: `test/registered/ascend/basic_function/<feature>/GENERATED_<YYYYMMDD>/GPU_NPU_MAPPING_TABLE.md`
- This is the ONLY documentation file (merged from README_GENERATED.md + mapping table)

### Phase 6: Verify Generated Tests

```bash
# Create directory if not exists
mkdir -p test/registered/ascend/basic_function/<feature>/GENERATED_<YYYYMMDD>

# Verify syntax
python -m py_compile test/registered/ascend/basic_function/<feature>/GENERATED_<YYYYMMDD>/test_npu_<feature>_*.py
```

**After verification:**
- Update graphify: `graphify update test/registered/ascend`

## Template Library

### Template A: Basic Feature Test (English only in docstring)

```python
import unittest
import requests

from sglang.srt.utils import kill_process_tree
from sglang.test.ascend.test_ascend_utils import (
    LLAMA_3_2_1B_INSTRUCT_WEIGHTS_PATH,
)
from sglang.test.ci.ci_register import register_npu_ci
from sglang.test.test_utils import (
    DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
    DEFAULT_URL_FOR_TEST,
    CustomTestCase,
    popen_launch_server,
)

register_npu_ci(est_time=400, suite="nightly-2-npu-a3", nightly=True)

class TestNPUFeature(CustomTestCase):
    """Test [FEATURE] functionality on NPU.

    [Test Category] Feature
    [Test Target] [target components]
    """
    
    base_model = LLAMA_3_2_1B_INSTRUCT_WEIGHTS_PATH
    
    @classmethod
    def setUpClass(cls):
        other_args = [
            "--attention-backend", "ascend",
            "--disable-cuda-graph",
            "--mem-fraction-static", "0.3",
        ]
        cls.process = popen_launch_server(
            cls.base_model,
            DEFAULT_URL_FOR_TEST,
            timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
            other_args=other_args,
        )
    
    @classmethod
    def tearDownClass(cls):
        kill_process_tree(cls.process.pid)
    
    def test_basic_scenario(self):
        response = requests.post(
            DEFAULT_URL_FOR_TEST + "/generate",
            json={
                "text": "prompt",
                "sampling_params": {"temperature": 0, "max_new_tokens": 32},
            },
        )
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
```

### Template B: Multi-Config Test (English only in docstring)

```python
class TestNPUFeatureConfigA(CustomTestCase):
    """Test [FEATURE] with config A on NPU.

    [Test Category] Feature
    [Test Target] [target components]
    """
    
    @classmethod
    def setUpClass(cls):
        other_args = [
            "--enable-feature-x",
        ]
        cls.process = popen_launch_server(...)

class TestNPUFeatureConfigB(CustomTestCase):
    """Test [FEATURE] with config B on NPU.

    [Test Category] Feature
    [Test Target] [target components]
    """
    
    @classmethod
    def setUpClass(cls):
        other_args = [
            "--disable-feature-x",
        ]
        cls.process = popen_launch_server(...)
```

### Template C: KV Cache Test (English only in docstring, code comments allowed)

```python
def test_kv_cache_reuse(self):
    """Test KV cache reuse behavior."""
    input_ids_first = [1] * 200
    input_ids_second = input_ids_first + [2] * 70
    
    # First request - no cache
    response1 = requests.post(
        DEFAULT_URL_FOR_TEST + "/generate",
        json={"input_ids": input_ids_first, ...},
    )
    cached_tokens_1 = response1.json()["meta_info"]["cached_tokens"]
    self.assertEqual(cached_tokens_1, 0)
    
    # Second request - should have cache
    response2 = requests.post(
        DEFAULT_URL_FOR_TEST + "/generate",
        json={"input_ids": input_ids_second, ...},
    )
    cached_tokens_2 = response2.json()["meta_info"]["cached_tokens"]
    self.assertGreater(cached_tokens_2, 0)
```

## Feature-Specific Reference

### LoRA Feature

**GPU directory:** `test/registered/lora/`
**NPU directory:** `test/registered/ascend/basic_function/lora/`
**Generated tests directory:** `test/registered/ascend/basic_function/lora/GENERATED_<YYYYMMDD>/`
**Model paths:**
- `LLAMA_3_2_1B_INSTRUCT_TOOL_CALLING_LORA_WEIGHTS_PATH`
- `LLAMA_3_2_1B_INSTRUCT_TOOL_FAST_LORA_WEIGHTS_PATH`

### EP (Expert Parallelism) Feature

**GPU directory:** `test/registered/ep/`, `test/manual/ep/`
**NPU directory:** `test/registered/ascend/basic_function/parallel_strategy/expert_parallelism/`
**Generated tests directory:** `test/registered/ascend/basic_function/parallel_strategy/expert_parallelism/GENERATED_<YYYYMMDD>/`
**Model paths:**
- `DEEPSEEK_V3_2_W8A8_WEIGHTS_PATH`
- `QWEN3_30B_A3B_W8A8_WEIGHTS_PATH`

### MoE Feature

**GPU directory:** `test/registered/moe/`
**NPU directory:** `test/registered/ascend/basic_function/moe/` (if exists)
**Generated tests directory:** `test/registered/ascend/basic_function/moe/GENERATED_<YYYYMMDD>/`

### Context Parallelism Feature

**GPU directory:** `test/registered/cp/`
**NPU directory:** `test/registered/ascend/basic_function/parallel_strategy/context_parallelism/`
**Generated tests directory:** `test/registered/ascend/basic_function/parallel_strategy/context_parallelism/GENERATED_<YYYYMMDD>/`
**Model paths:**
- `DEEPSEEK_V3_2_W8A8_WEIGHTS_PATH`
- `QWEN3_30B_A3B_WEIGHTS_PATH`

## Task Decomposition Template

When executing this skill, create todo list:

```json
[
  {"content": "使用graphify分析<FEATURE>架构", "status": "pending", "priority": "high"},
  {"content": "收集GPU <FEATURE>测试文件（排除*_kernel.py）", "status": "pending", "priority": "high"},
  {"content": "收集NPU <FEATURE>现有测试", "status": "pending", "priority": "high"},
  {"content": "对比分析GPU与NPU测试覆盖差异（包含logprob_diff）", "status": "pending", "priority": "high"},
  {"content": "生成缺失的NPU测试文件（功能测试+logprob_diff）", "status": "pending", "priority": "medium"},
  {"content": "标记不支持的测试（大模型/无权重）", "status": "pending", "priority": "medium"},
  {"content": "生成GPU_NPU_MAPPING_TABLE.md（完整映射）", "status": "pending", "priority": "medium"},
  {"content": "验证生成文件语法正确性", "status": "pending", "priority": "medium"}
]
```

## Output Format

最终报告必须包含**完整的GPU-NPU对应关系（仅排除kernel测试）与纯中文文档**。

**重要：单文档文件策略（v9.1）**:
- 输出一个文件：`GPU_NPU_MAPPING_TABLE.md`（合并完整报告）
- 该文件完全使用**中文**撰写
- 合并之前的 `README_GENERATED.md` + `GPU_NPU_MAPPING_TABLE.md` 为单个综合文档
- 优势：减少冗余、易于维护、一站式参考
- 包含14个章节：排除测试、GPU摘要、NPU摘要、完整映射、覆盖率统计、差距分析、增强机会、优先级、适配说明、测试场景、运行命令、后续工作、总结、文件列表

### 1. 排除测试（仅Kernel）
| GPU测试文件 | 测试类型 | 排除原因 |
|------------|---------|---------|
| test_*_kernel.py | Kernel | CUDA/triton实现要求 |

### 2. GPU测试表（排除kernel的所有测试）
| GPU测试文件 | 测试类 | 测试类型 | 模型 | 配置 | 测试场景 |
|------------|--------|---------|------|------|---------|
| test_xxx.py | TestClassA | 集成测试 | Model-A | TP=4 | 功能测试 |
| test_yyy_logprob_diff.py | TestClassB | 性能测试 | Model-B | - | Logprob对比 |

### 3. NPU测试表（现有+生成）
| NPU测试文件 | 测试类 | 模型 | 配置 | 测试场景 | 状态 |
|------------|--------|------|------|---------|------|
| test_npu_xxx.py | TestClassA | Model-A-NPU | TP=4 | 功能测试 | 已存在 |
| test_npu_yyy_logprob_diff.py | TestClassB | Model-B-NPU | TP=2 | Logprob测试 | 已生成 |

### 4. GPU-NPU测试映射表（必需 - 包含logprob_diff）
**关键输出：展示精确的测试对应关系**

| 序号 | GPU测试文件 | GPU测试类 | 测试类型 | 模型 | NPU测试文件 | NPU测试类 | 映射状态 | NPU状态 | 关键适配说明 |
|-----|------------|----------|---------|------|------------|----------|---------|---------|-------------|
| 1 | test_xxx.py | TestClassA | 集成测试 | Model-A | test_npu_xxx.py | TestClassA | ⚠️ 已适配 | 已生成 | 模型已更换 |
| 2 | test_yyy_logprob_diff.py | TestClassB | 性能测试 | 大模型 | - | - | ❌ 不支持 | - | 模型权重不可用 |
| 3 | test_zzz_logprob_diff.py | TestClassC | 性能测试 | Model-C | test_npu_zzz_logprob_diff.py | TestClassC | ⚠️ 已适配 | 已生成 | HF对比已跳过 |

**适配说明示例**:
- "模型：大模型 → 小模型（NPU简化版本）"
- "HF对比已跳过 - 仅NPU上运行SGLang推理"
- "模型权重在NPU上不可用 - 标记为不支持"
- "EAGLE推测解码不支持NPU - 已移除"

### 5. 差距分析矩阵
缺失测试识别摘要。

### 6. 生成的文件列表
新创建的NPU测试文件，包含目录路径和对应的GPU测试。

### 7. 覆盖率统计
- **生成前**: GPU测试数量 vs NPU测试数量（覆盖率%）
- **生成后**: 生成后的更新覆盖率
- **示例**: "覆盖率: 0% (0/2) → 100% (2/2)"

### 8. 目录结构
显示`GENERATED_<YYYYMMDD>/`目录结构，包含GPU_NPU_MAPPING_TABLE.md（合并完整报告）。

**示例目录结构**:
```
test/registered/ascend/basic_function/<feature>/GENERATED_<YYYYMMDD>/
├── test_npu_<feature>_xxx.py
├── test_npu_<feature>_yyy.py
└── GPU_NPU_MAPPING_TABLE.md         # 完整报告（纯中文）
```

**文件命名**:
- GPU_NPU_MAPPING_TABLE.md 包含所有文档（映射表 + 运行命令 + 后续工作）
- 这是 GENERATED_<YYYYMMDD>/ 目录中唯一的文档文件

## Key Principles

1. **仅排除kernel测试** - 仅`*_kernel.py`，包含unit和logprob_diff
2. **遵循NPU规范** - ascend后端，禁用cuda graph
3. **使用unittest框架** - 必须使用unittest（不是pytest）
4. **使用现有模型路径** - 来自test_ascend_utils.py
5. **适配logprob_diff测试** - 替换大模型，跳过HF对比
6. **标记不支持** - 大模型/无权重清晰标记
7. **验证语法** - 对生成文件运行py_compile
8. **测试文件仅英文** - 测试文件docstring仅英文
9. **映射表纯中文** - GPU_NPU_MAPPING_TABLE.md必须纯中文
10. **简洁docstring** - 仅测试描述、[Test Category]、[Test Target]
11. **测试无GPU引用** - GPU映射信息放GPU_NPU_MAPPING_TABLE.md
12. **测试无适配细节** - 适配说明放GPU_NPU_MAPPING_TABLE.md
13. **英文代码注释可保留** - 保留有用注释如"# First request - no cache"
14. **测试无中文注释** - 中文说明放GPU_NPU_MAPPING_TABLE.md
15. **无版权头** - 生成的测试文件不包含版权/许可头
16. **创建新子目录** - 生成的测试放在`GENERATED_<YYYYMMDD>/`子目录
17. **按功能组织** - 将相关缺失测试放在同一生成目录
18. **无print语句** - 使用断言代替`print()`
19. **匹配GPU模型选择** - NPU测试使用等效模型
20. **显示详细映射** - 必须输出完整映射表，存放在GENERATED_<YYYYMMDD>/目录下
21. **严格范围限制** - 仅分析用户指定目录