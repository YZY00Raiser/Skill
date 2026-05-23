# NPU Test Gap Analysis Skill v8.0
# NPU测试差距分析 Skill v8.0

## Overview / 概述

This skill analyzes GPU vs NPU test coverage for **any feature module**, identifies missing NPU integration tests, and generates them automatically with **bilingual documentation (English + Chinese)**.
此skill分析任意功能模块的GPU vs NPU测试覆盖，识别缺失的NPU集成测试，并自动生成包含**双语文档（英文+中文）**的测试文件。

## Key Features / 主要特性

- **Bilingual Documentation**: All generated tests and README include both English and Chinese descriptions
- **双语文档**: 所有生成的测试和README包含英文和中文描述
- **Universal Coverage**: Works with any feature module (lora, ep, moe, cp, etc.)
- **通用覆盖**: 支持任意功能模块（lora, ep, moe, cp等）
- **Automatic Generation**: Generates NPU tests from GPU test patterns
- **自动生成**: 从GPU测试模式生成NPU测试
- **Syntax Verification**: Validates generated files with py_compile
- **语法验证**: 使用py_compile验证生成文件

## Supported Features / 支持的功能

| Feature | GPU Directory | NPU Directory | Feature CN |
|---------|--------------|---------------|------------|
| `lora` | test/registered/lora | test/registered/ascend/basic_function/lora | LoRA适配器 |
| `ep` / `expert_parallelism` | test/registered/ep, test/manual/ep | test/registered/ascend/.../expert_parallelism | 专家并行 |
| `moe` | test/registered/moe | test/registered/ascend/.../moe | 混合专家模型 |
| `cp` / `context_parallelism` | test/registered/cp | test/registered/ascend/.../context_parallelism | 上下文并行 |
| `attention` | test/srt/attention | test/registered/ascend/.../attention | 注意力机制 |
| `quantization` | test/registered/quant | test/registered/ascend/.../quant | 量化 |

## Usage Examples / 使用示例

### Example 1: Analyze LoRA Module / 示例1: 分析LoRA模块
```
User: 分析lora目录下gpu用例与npu用例差异

Agent will / Agent将:
1. Query graphify for "lora" architecture / 查询graphify获取lora架构
2. Collect GPU tests from test/registered/lora / 从test/registered/lora收集GPU测试
3. Collect NPU tests from test/registered/ascend/basic_function/lora / 从NPU目录收集测试
4. Identify missing tests (TP, Radix Cache) / 识别缺失测试
5. Generate test_npu_lora_tp.py (with bilingual docstring) / 生成测试（含双语docstring）
6. Generate README_GENERATED.md (bilingual) / 生成双语README
7. Verify syntax with py_compile / 使用py_compile验证语法
```

### Example 2: Analyze CP Module / 示例2: 分析CP模块
```
User: 分析cp目录下gpu和npu测试覆盖情况

Agent will / Agent将:
1. Query graphify for "context_parallelism" / 查询graphify获取上下文并行架构
2. Collect GPU tests from test/registered/cp / 从test/registered/cp收集GPU测试
3. Identify missing DeepSeek-V3.2 CP tests / 识别缺失的DeepSeek-V3.2 CP测试
4. Generate test_npu_deepseek_v3_2_cp.py / 生成测试文件
5. Generate bilingual README_GENERATED.md / 生成双语README
6. Verify syntax / 验证语法
```

## Workflow / 工作流程

```
Phase 1: Architecture Analysis / 阶段1: 架构分析
  └─> graphify query "<feature>" --budget 3000

Phase 2: GPU Test Collection / 阶段2: GPU测试收集
  └─> Filter integration tests (server startup required) / 过滤集成测试（需要服务器启动）
  └─> Exclude unit tests (mock, kernel, logprob_diff) / 排除单元测试

Phase 3: NPU Test Collection / 阶段3: NPU测试收集
  └─> Pattern: test_npu_<feature>*.py / 匹配模式: test_npu_<feature>*.py

Phase 4: Gap Analysis / 阶段4: 差距分析
  └─> Compare GPU scenarios vs NPU coverage / 对比GPU场景与NPU覆盖
  └─> Identify missing tests / 识别缺失测试

Phase 5: Test Generation (Bilingual) / 阶段5: 测试生成（双语）
  └─> Apply NPU-specific adaptations / 应用NPU特有适配
  └─> Add bilingual docstrings / 添加双语docstring

Phase 6: README Generation (Bilingual) / 阶段6: README生成（双语）
  └─> Generate README_GENERATED.md with bilingual content / 生成双语README

Phase 7: Syntax Verification / 阶段7: 语法验证
  └─> python -m py_compile <generated_file> / 验证生成文件语法
```

## Bilingual Documentation Format / 双语文档格式

### Test Class Docstring / 测试类Docstring
```python
class TestNPUFeature(CustomTestCase):
    """Test [FEATURE] on NPU.
    测试NPU上的[FEATURE]功能。
    
    [Test Category] Feature / [测试类别] 特性测试
    [Test Target] Components / [测试目标] 组件
    
    Adapted from GPU test: test_gpu_xxx.py
    源GPU测试: test_gpu_xxx.py
    
    Key adaptations for NPU / NPU适配说明:
    - EAGLE removed (not supported) / EAGLE已移除（不支持）
    - Model path changed to NPU weights / 模型路径改为NPU权重
    """
```

### README_GENERATED.md / README_GENERATED.md
```markdown
# Generated NPU Tests - Feature
# 生成的NPU测试 - 功能

**Generated Date**: YYYY-MM-DD
**生成日期**: YYYY-MM-DD

## Corresponding GPU Tests
## 对应的GPU测试
- test_gpu_xxx.py

## Generated NPU Tests
## 生成的NPU测试
- test_npu_xxx.py

## Key Adaptations for NPU
## NPU关键适配说明
1. **EAGLE**: Removed / **EAGLE**: 已移除
```

## NPU Test Template (Bilingual) / NPU测试模板（双语）

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
    """Test [FEATURE] on NPU.
    测试NPU上的[FEATURE]功能。
    
    [Test Category] Feature / [测试类别] 特性测试
    [Test Target] Components / [测试目标] 组件
    """
    
    @classmethod
    def setUpClass(cls):
        other_args = [
            "--attention-backend", "ascend",     # Mandatory / 必需
            "--disable-cuda-graph",              # Mandatory / 必需
            "--mem-fraction-static", "0.3",      # Adjust by model / 按模型调整
        ]
        cls.process = popen_launch_server(...)
    
    @classmethod
    def tearDownClass(cls):
        kill_process_tree(cls.process.pid)
    
    def test_scenario(self):
        """Test scenario / 测试场景"""
        response = requests.post(...)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
```

## File Structure / 文件结构

```
.opencode/skills/npu-test-gap-v8/
├── SKILL.md          # Skill documentation (loaded by opencode) / Skill文档
├── config.json       # Feature configuration / 功能配置
├── templates.py      # Test generation templates (bilingual) / 测试生成模板（双语）
├── analyze.py        # Execution script (bilingual) / 执行脚本（双语）
└── README.md         # This file / 本文件
```

## Generated Output Structure / 生成的输出结构

```
test/registered/ascend/basic_function/<feature>/GENERATED_<YYYYMMDD>/
├── test_npu_<feature>_xxx.py      # Generated test (bilingual docstring)
├── test_npu_<feature>_yyy.py      # Generated test (bilingual docstring)
└── README_GENERATED.md            # Bilingual README
```

## Key Principles / 关键原则

1. **Only generate integration tests** - Never unit tests / 仅生成集成测试 - 不生成单元测试
2. **Follow NPU conventions** - ascend backend, disable cuda graph / 遵循NPU规范
3. **Bilingual documentation** - English first, then Chinese / 双语文档 - 英文优先，然后中文
4. **Use existing model paths** - From test_ascend_utils.py / 使用现有模型路径
5. **Maintain parity** - Aim for >90% GPU coverage / 保持一致性 - 目标GPU覆盖率>90%
6. **Verify syntax** - Always run py_compile / 验证语法 - 运行py_compile
7. **Generate README** - Include bilingual mapping table / 生成README - 包含双语映射表

## Version History / 版本历史

| Version | Changes / 变更 |
|---------|---------------|
| v8.0 | Added bilingual documentation (English + Chinese) / 添加双语文档（英文+中文） |
| v7.0 | Added context parallelism support / 添加上下文并行支持 |
| v2.0 | Universal feature support / 通用功能支持 |