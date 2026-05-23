---
name: npu-test-gap-v8
description: Analyze GPU vs NPU test coverage gap for ANY specified directory, identify missing NPU integration tests (exclude unit tests), and generate them. Use when asked about test coverage analysis, NPU test generation, or comparing GPU/NPU test suites for any feature module (lora, ep, moe, attention, etc.).
---

# NPU Test Gap Analysis Skill (Universal Version with Bilingual Documentation)

## Purpose

This skill analyzes GPU vs NPU test coverage for **any specified feature directory**, identifies missing NPU integration tests, and generates proper NPU test files with bilingual (English + Chinese) documentation.

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
- `*_unit.py` or `*_kernel.py`
- Tests using `MagicMock`, `unittest.mock`
- Tests with `pytest` only (no server)
- `logprob_diff` tests (performance benchmarks)
- API parsing tests without server
- **`test/manual/` directory** - Manual tests NOT running in CI pipeline

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
└── README_GENERATED.md  # Optional metadata file

test/registered/ascend/basic_function/parallel_strategy/context_parallelism/GENERATED_20260523/
├── test_npu_deepseek_v3_2_cp.py
└── README_GENERATED.md
```

**Generated test file docstring (English only - REQUIRED):**

Test class docstrings should be in English only, with minimal content. Detailed information goes in README_GENERATED.md.

**Docstring format (SIMPLIFIED):**
```python
class TestNPUFeature(CustomTestCase):
    """Test [FEATURE] on NPU.

    [Test Category] Feature
    [Test Target] [target components]
    """
```

**DO NOT include in test file docstring:**
- ❌ "Adapted from GPU test: xxx" (put in README_GENERATED.md)
- ❌ "Key adaptations for NPU" (put in README_GENERATED.md)
- ❌ Chinese comments (put in README_GENERATED.md)
- ❌ Detailed adaptation notes (put in README_GENERATED.md)

**Code comments in test body (ALLOWED):**
- ✅ English comments explaining logic (e.g., "# First request - no cache")
- ✅ Comments for test steps (e.g., "# Warmup phase", "# Main test")
- ❌ Chinese comments in code body (put in README_GENERATED.md)

**README_GENERATED.md template (Bilingual - REQUIRED):**

**All detailed information goes here (NOT in test files):**
- GPU test references
- GPU-NPU test mapping
- Key adaptations for NPU
- Chinese translations

```markdown
# Generated NPU Tests - <FEATURE>
# 生成的NPU测试 - <FEATURE中文>

**Generated Date**: YYYY-MM-DD
**生成日期**: YYYY-MM-DD

**Generator**: npu-test-gap-v8 skill
**生成器**: npu-test-gap-v8 skill

**Analyzed Scope**: test/registered/<feature>/ (only this directory)
**分析范围**: test/registered/<feature>/ (仅此目录)

## Corresponding GPU Tests
## 对应的GPU测试
- test/registered/<feature>/test_xxx.py

## Generated NPU Tests
## 生成的NPU测试
- test_npu_<feature>_xxx.py

## GPU-NPU Test Mapping
## GPU-NPU测试映射表

| GPU Test File | GPU Test Class | GPU Config | NPU Test File | NPU Test Class | NPU Config | Mapping Status | Adaptation Notes |
|---------------|----------------|------------|---------------|----------------|------------|----------------|------------------|
| test_xxx.py | TestClassA | TP=4 | test_npu_xxx.py | TestClassA | TP=4 | ⚠️ ADAPTED | Description |

**映射状态说明**:
- ⚠️ ADAPTED: 已适配 - NPU测试存在但需要适配GPU特性
- ❌ MISSING: 缺失 - 无对应NPU测试

## Key Adaptations for NPU
## NPU关键适配说明

1. **Feature Name**: Description / 功能名称: 描述
   - GPU: `--param value`
   - NPU: `--param value`

## Coverage Statistics
## 覆盖率统计

- **Before**: X% (Y/Z covered) / **生成前**: X% (Y/Z被覆盖)
- **After**: X% (Y/Z covered) / **生成后**: X% (Y/Z被覆盖)

## Test Scenarios
## 测试场景

### TestClassA
- English description
- 中文描述
```

**Directory creation:**
- Create new directory with `GENERATED_` prefix if missing tests are identified
- Use date suffix (YYYYMMDD format) for organization
- Group related tests together in the same `GENERATED_` directory
- Add `README_GENERATED.md` with bilingual documentation (REQUIRED)

### Phase 4: Compare and Identify Gaps

Generate **GPU-NPU Test Mapping Table** showing detailed correspondence:

**Mapping Table Format:**

| GPU Test File | GPU Test Class | GPU Config | NPU Test File | NPU Test Class | NPU Config | Mapping Status | Adaptation Notes |
|---------------|----------------|------------|---------------|----------------|------------|----------------|------------------|
| test_xxx.py | TestClassA | TP=4, EP=2 | test_npu_xxx.py | TestClassA | TP=4, EP=2 | ✅ EXACT MATCH | None |
| test_yyy.py | TestClassB | TP=8, EAGLE | test_npu_yyy.py | TestClassB | TP=8 | ⚠️ PARTIAL | EAGLE not supported on NPU |
| test_zzz.py | TestClassC | DP=2 | - | - | - | ❌ MISSING | Need to generate |

**Mapping Status Types:**
- ✅ **EXACT MATCH**: NPU test exists with same configuration
- ⚠️ **PARTIAL MATCH**: NPU test exists but with different config/missing features
- ❌ **MISSING**: No corresponding NPU test
- 🔄 **ADAPTED**: NPU test adapted from GPU (model/backend differences)

**Gap Summary Matrix (for specified directory only):**

| GPU Test | Test Type | Test Scenario | NPU Status | Action |
|----------|-----------|---------------|------------|--------|
| test_xxx.py | Integration | TP/Radix/... | EXISTS/MISSING | Keep/Generate |

### Phase 5: Generate NPU Integration Tests

**IMPORTANT: Use unittest framework (NOT pytest)**

Generated NPU tests MUST follow unittest conventions:

| Aspect | unittest (REQUIRED) | pytest (DO NOT USE) |
|--------|---------------------|---------------------|
| Base class | `CustomTestCase` or `unittest.TestCase` | No base class |
| Setup/teardown | `setUpClass/tearDownClass` | `@pytest.fixture` |
| Assertions | `self.assertEqual(x, y)` | `assert x == y` |
| Parametrize | Multiple test classes | `@pytest.mark.parametrize` |
| Entry point | `unittest.main()` | `pytest.main()` |

**IMPORTANT: Test Docstring Classification**

Test docstrings MUST use the following classification format:

```python
class TestNPUFeature(CustomTestCase):
    """Test [FEATURE] on NPU.

    [Test Category] {Category}
    [Test Target] {TestTarget}
    """
```

**[Test Category] MUST be one of:**

1. **Parameter** - Tests server parameters/configuration options
   - Examples: `--context-length`, `--kv-cache-dtype`, `--tp-size`, `--enable-lora`
   
2. **Model** - Tests model inference functionality
   - Examples: model paths like `vllm-ascend/DeepSeek-V3.2-Exp-W8A8`, `Qwen/Qwen3-Next-80B-A3B-Instruct`
   
3. **Interface** - Tests API endpoints or server interfaces
   - Examples: `/server_info`, `/v1/models`, `/generate`, `/health`

**[Test Target] Format:**

| Category | Test Target Format | Examples |
|----------|-------------------|----------|
| Parameter | `--param-name value` or `--param-name` | `--kv-cache-dtype fp8_e5m2`, `--context-length`, `--tp-size 4, --enable-lora` |
| Model | Model path/identifier | `vllm-ascend/DeepSeek-V3.2-Exp-W8A8`, `Qwen/Qwen3-Next-80B-A3B-Instruct` |
| Interface | Endpoint path | `/server_info`, `/v1/models`, `/generate` |

**IMPORTANT: No print statements in generated tests**

Generated tests MUST use assertions instead of print statements:

| Bad (DO NOT USE) | Good (REQUIRED) |
|------------------|-----------------|
| `print(f"Output: {response.json()}")` | `self.assertEqual(response.status_code, 200)` |
| `print(f"Found: {text}")` | `self.assertIn("expected_text", response.json()["text"])` |
| `print(f"Events: {events}")` | `self.assertGreater(len(events), 0, "Events should be found")` |

Debug information should be embedded in assertion error messages:
```python
self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}: {response.text}")
```

**Correct unittest pattern (English only, minimal docstring):**

**[Test Category] Testing Categories:**
Choose from the following three categories based on test content:
1. **Parameter**: Tests server parameters/configuration options
2. **Model**: Tests model inference functionality
3. **Interface**: Tests API endpoints or server interfaces

**[Test Target] Target Description:**
- **Parameter**: Fill in the tested parameter(s), e.g., `--context-length`, `--kv-cache-dtype`
- **Model**: Fill in the tested model path, e.g., `vllm-ascend/DeepSeek-V3.2-Exp-W8A8`
- **Interface**: Fill in the tested endpoint(s), e.g., `/server_info`, `/v1/models`

**Example - Parameter Test:**
```python
class TestNPUKVCacheDtype(CustomTestCase):
    """Test KV cache dtype parameter on NPU.

    [Test Category] Parameter
    [Test Target] --kv-cache-dtype fp8_e5m2
    """
    
    @classmethod
    def setUpClass(cls):
        other_args = ["--kv-cache-dtype", "fp8_e5m2"]
        cls.process = popen_launch_server(...)
```

**Example - Model Test:**
```python
class TestNPUDeepSeekV32(CustomTestCase):
    """Test DeepSeek-V3.2 model inference on NPU.

    [Test Category] Model
    [Test Target] vllm-ascend/DeepSeek-V3.2-Exp-W8A8
    """
    
    @classmethod
    def setUpClass(cls):
        cls.model = DEEPSEEK_V3_2_W8A8_WEIGHTS_PATH
        cls.process = popen_launch_server(cls.model, ...)
```

**Example - Interface Test:**
```python
class TestNPUServerInfoEndpoint(CustomTestCase):
    """Test server info endpoint on NPU.

    [Test Category] Interface
    [Test Target] /server_info
    """
    
    def test_server_info(self):
        response = requests.get(self.base_url + "/server_info")
        self.assertEqual(response.status_code, 200)
```

**Complete Example with Main Block:**
```python
if __name__ == "__main__":
    unittest.main()
```

**Wrong patterns (DO NOT use):**
```python
class TestNPUFeature(CustomTestCase):
    """Test [FEATURE] on NPU.
    测试NPU上的[FEATURE]功能。  # ❌ DO NOT add Chinese in test files
    
    [Test Category] Feature / [测试类别] 特性测试  # ❌ DO NOT use bilingual format
    
    Adapted from GPU test: test_gpu_xxx.py  # ❌ DO NOT include GPU reference
    
    Key adaptations for NPU:  # ❌ DO NOT include adaptation details
    - EAGLE removed
    """
```

**Output directory structure:**

Create new subdirectory for generated tests:
```
test/registered/ascend/basic_function/<feature>/GENERATED_<YYYYMMDD>/test_npu_<feature>_*.py
```

Example for LoRA (date: 20260521):
```
test/registered/ascend/basic_function/lora/GENERATED_20260521/
├── test_npu_lora_update.py
├── test_npu_lora_eviction.py
├── test_npu_lora_multi_backend.py
└── README_GENERATED.md  # Bilingual documentation
```

**NPU-specific adaptations:**

1. **Mandatory parameters:**
   ```python
   "--attention-backend", "ascend",
   "--disable-cuda-graph",
   "--mem-fraction-static", "0.3",  # Adjust based on model size
   ```

2. **Registration:**
   ```python
   register_npu_ci(est_time=500, suite="nightly-2-npu-a3", nightly=True)
   ```

3. **Model paths (from test_ascend_utils.py):**
   - `LLAMA_3_2_1B_INSTRUCT_WEIGHTS_PATH` - Default base model
   - `QWEN3_30B_A3B_INSTRUCT_2507_WEIGHTS_PATH` - Larger model
   - Feature-specific paths (check test_ascend_utils.py)
   
   **IMPORTANT: Match GPU test model selection**
   
   When generating NPU tests, the model selection should match the corresponding GPU test:
   
   | GPU Test Model | NPU Test Model Selection |
   |----------------|--------------------------|
   | `Qwen/Qwen3-0.6B` | Use `LLAMA_3_2_1B_INSTRUCT_WEIGHTS_PATH` (NPU default small model) |
   | `meta-llama/Llama-3.1-8B-Instruct` | Use `LLAMA_3_2_1B_INSTRUCT_WEIGHTS_PATH` or `LLAMA_3_1_8B_INSTRUCT_WEIGHTS_PATH` |
   | `Qwen/Qwen3-30B-A3B` | Use `QWEN3_30B_A3B_INSTRUCT_2507_WEIGHTS_PATH` |
   | Large MoE models | Use corresponding NPU-available MoE weights |
   
   **Model matching rules:**
   - Check GPU test file for model path constant or model name
   - Search test_ascend_utils.py for equivalent or closest NPU-available model
   - If GPU uses HuggingFace model name, find equivalent in MODEL_WEIGHTS_DIR
   - Prefer smaller models for faster NPU test execution when functionality is same

 4. **LoRA-specific:**
    ```python
    "--enable-lora",
    "--lora-path", f"lora_a={LORA_WEIGHTS_PATH}",
    "--max-loaded-loras", "2",
    "--max-loras-per-batch", "2",
    ```

 5. **EP-specific:**
    ```python
    "--moe-a2a-backend", "deepep",
    "--deepep-mode", "auto",  # or "low_latency"
    "--tp-size", "16",
    "--ep-size", "16",
    ```

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
  {"content": "收集GPU <FEATURE>集成测试文件", "status": "pending", "priority": "high"},
  {"content": "收集NPU <FEATURE>现有测试", "status": "pending", "priority": "high"},
  {"content": "对比分析GPU与NPU测试覆盖差异", "status": "pending", "priority": "high"},
  {"content": "生成缺失的NPU测试文件（仅英文注释）", "status": "pending", "priority": "medium"},
  {"content": "生成README_GENERATED.md（中英文双语）", "status": "pending", "priority": "medium"},
  {"content": "验证生成文件语法正确性", "status": "pending", "priority": "medium"}
]
```

## Output Format

Final report MUST include **detailed GPU-NPU correspondence with bilingual documentation**:

### 1. Graphify Analysis Summary / Graphify架构分析摘要
Key nodes and relationships discovered. / 发现的关键节点和关系。

### 2. GPU Tests Table (Integration tests only) / GPU测试表（仅集成测试）
| GPU Test File | Test Class | Model | Config | Test Scenario |
|---------------|------------|-------|--------|---------------|
| test_xxx.py | TestClassA | Model-A | TP=4, EP=2 | GSM8K accuracy |

### 3. NPU Tests Table (Existing tests) / NPU测试表（现有测试）
| NPU Test File | Test Class | Model | Config | Test Scenario |
|---------------|------------|-------|--------|---------------|
| test_npu_xxx.py | TestClassA | Model-A-NPU | TP=4, EP=2 | GSM8K accuracy |

### 4. GPU-NPU Test Mapping Table (REQUIRED - detailed correspondence) / GPU-NPU测试映射表（必需 - 详细对应关系）
**This is the KEY output showing exact test-to-test relationships:**

| GPU Test File | GPU Test Class | GPU Config | NPU Test File | NPU Test Class | NPU Config | Mapping Status | Adaptation Notes |
|---------------|----------------|------------|---------------|----------------|------------|----------------|------------------|
| `test_deepseek_v32_cp_single_node.py` | TestDeepseekV32CPInSeqSplit | TP=8, ATTN_CP=4, EAGLE | `GENERATED_20260523/test_npu_deepseek_v3_2_cp.py` | TestDeepseekV32CPAttnCP4 | TP=8, ATTN_CP=4 | ⚠️ ADAPTED | EAGLE removed, NSA prefill simplified |
| `test_deepseek_v32_cp_single_node.py` | TestDeepseekV32CPRoundRobinSplit | TP=8, ATTN_CP=8, EAGLE | `GENERATED_20260523/test_npu_deepseek_v3_2_cp.py` | TestDeepseekV32CPAttnCP8 | TP=8, ATTN_CP=8 | ⚠️ ADAPTED | EAGLE removed, NSA prefill simplified |
| `test_lora_update.py` | TestLoRAUpdate | TP=2, LoRA enabled | - | - | - | ❌ MISSING | Need to generate |

**Adaptation Notes Examples:**
- "EAGLE speculative decoding not supported on NPU - removed" / "EAGLE推测解码不支持NPU - 已移除"
- "Model changed from HuggingFace ID to local NPU weights path" / "模型从HuggingFace ID改为NPU本地权重路径"
- "CUDA graph disabled on NPU (--disable-cuda-graph added)" / "CUDA graph在NPU上禁用（添加--disable-cuda-graph）"
- "Attention backend changed to 'ascend'" / "注意力后端改为'ascend'"

### 5. Gap Analysis Matrix / 差距分析矩阵
Missing tests identification summary. / 缺失测试识别摘要。

### 6. Generated Files List / 生成的文件列表
New NPU test files created with directory path and corresponding GPU test. / 新创建的NPU测试文件，包含目录路径和对应的GPU测试。

### 7. Coverage Statistics / 覆盖率统计
- **Before**: GPU tests count vs NPU tests count (coverage %) / **生成前**: GPU测试数量 vs NPU测试数量（覆盖率%）
- **After**: Updated coverage after generation / **生成后**: 生成后的更新覆盖率
- **Example**: "Coverage for test/registered/cp/: 0% (0/2) → 100% (2/2)" / "覆盖率: 0% (0/2) → 100% (2/2)"

### 8. Directory Structure / 目录结构
Show `GENERATED_<YYYYMMDD>/` layout with README_GENERATED.md (bilingual). / 显示`GENERATED_<YYYYMMDD>/`目录结构，包含双语README_GENERATED.md。

## Key Principles

1. **Only generate integration tests** - Never generate unit tests / **仅生成集成测试** - 不要生成单元测试
2. **Follow NPU conventions** - ascend backend, disable cuda graph / **遵循NPU规范** - ascend后端，禁用cuda graph
3. **Use unittest framework** - MUST use unittest (NOT pytest) / **使用unittest框架** - 必须使用unittest（不是pytest）
4. **Use existing model paths** - From test_ascend_utils.py / **使用现有模型路径** - 来自test_ascend_utils.py
5. **Maintain test parity** - Aim for >90% GPU coverage / **保持测试一致性** - 目标GPU覆盖率>90%
6. **Verify syntax** - Always run py_compile on generated files / **验证语法** - 对生成文件运行py_compile
7. **Test files English only** - Test files docstrings in English only / **测试文件仅英文** - 测试文件docstring仅英文
8. **README bilingual** - README_GENERATED.md must be bilingual / **README双语** - README_GENERATED.md必须双语
9. **Minimal test docstring** - Only test description, [Test Category], [Test Target] / **简洁docstring** - 仅测试描述、类别、目标
10. **No GPU reference in test** - GPU mapping info goes in README_GENERATED.md / **测试无GPU引用** - GPU映射信息放README
11. **No adaptation details in test** - All adaptation notes in README_GENERATED.md / **测试无适配细节** - 适配说明放README
12. **English code comments allowed** - Keep useful comments like "# First request - no cache" / **英文代码注释可保留** - 保留有用注释如"# First request - no cache"
13. **No Chinese comments in test** - Chinese translations go in README_GENERATED.md / **测试无中文注释** - 中文翻译放README
14. **No copyright headers** - Generated test files should NOT include copyright/license headers / **无版权头** - 生成的测试文件不包含版权/许可头
15. **Create new subdirectory** - Generated tests go into `GENERATED_<YYYYMMDD>/` subdirectory / **创建新子目录** - 生成的测试放在`GENERATED_<YYYYMMDD>/`子目录
16. **Organize by feature** - Group related missing tests in same generated directory / **按功能组织** - 将相关缺失测试放在同一生成目录
17. **No print statements** - Use assertions instead of `print()` / **无print语句** - 使用断言代替`print()`
18. **Match GPU model selection** - NPU tests should use equivalent models / **匹配GPU模型选择** - NPU测试使用等效模型
19. **Show detailed mapping** - MUST output GPU-NPU Test Mapping Table / **显示详细映射** - 必须输出GPU-NPU测试映射表
20. **Strict scope limitation** - ONLY analyze user-specified directory / **严格范围限制** - 仅分析用户指定目录