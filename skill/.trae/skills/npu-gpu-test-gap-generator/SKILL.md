---
name: "npu-gpu-test-gap-generator"
description: "Generates test cases for NPU based on GPU vs NPU test gap analysis reports. Invoke when user needs to generate missing NPU test cases from a gap analysis document."
---

# NPU vs GPU Test Gap Test Case Generator

This skill generates comprehensive test case code for NPU (Ascend) based on gap analysis reports comparing NPU and GPU test coverage.

## When to Invoke

Invoke this skill when:
1. User has a `NPU_vs_GPU_*_Test_Gap_Analysis.md` document
2. User wants to generate missing NPU test cases
3. User needs to fill test coverage gaps identified in analysis
4. User asks to "generate test cases" or "create tests" based on gap analysis

## Input Requirements

The skill expects:
1. **Gap Analysis Document**: A markdown file following the NPU vs GPU gap analysis format
2. **Target Directory**: Where to save the generated test files
3. **Test Priority**: Which priority level tests to generate (high/medium/low/all)

## Output Structure

Generated tests are organized as:
```
<target_directory>/
├── generated_tests/
│   ├── test_npu_*_logprob_diff.py      # Precision/comparison tests
│   ├── test_npu_*_eviction.py          # Memory management tests
│   ├── test_npu_*_update.py            # Dynamic adapter tests
│   ├── test_npu_*_tp.py                # Tensor parallel tests
│   ├── test_npu_*_moe*.py              # MoE-specific tests
│   └── ...
├── __init__.py
└── README.md
```

## Test Case Template

Each generated test follows this structure:

```python
"""
Test NPU <Feature> - <中文描述>

Tests <feature> on Ascend NPU:
1. <Test point 1>
2. <Test point 2>
3. <Test point 3>
"""

import os
import sys
import pytest
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../.."))

from sglang.test.test_ascend_utils import (
    run_sglang_server,
    kill_sglang_server,
    wait_for_server_ready,
    call_sglang_generate,
    # ... other imports
)

# Test configuration
MODEL_NAME = "<model-name>"
ADAPTER_URL = "<adapter-url>"

PROMPTS = [
    "<prompt 1>",
    "<prompt 2>",
]

# Thresholds
LOGPROB_DIFF_THRESHOLD = 0.01
TOP_K_TOKENS = 50


class TestNpu<Feature>:
    """Test <feature> on Ascend NPU."""

    @pytest.fixture(scope="class")
    def server_process(self):
        """Start SGLang server for testing."""
        server_config = {
            "model_path": MODEL_NAME,
            "tp_size": 1,
            "lora_paths": f"{{'test-lora':'{ADAPTER_URL}'}}",
            "lora_backend": "ascend",
            "device": "npu",
            "attention_backend": "ascend",
            "enable_lora": True,
        }
        
        server_process = run_sglang_server(**server_config)
        wait_for_server_ready(timeout=300)
        
        yield server_process
        
        kill_sglang_server(server_process)

    def test_<feature>(self, server_process):
        """Test <feature> functionality."""
        # Test implementation
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
```

## Generation Process

1. **Parse Gap Analysis**: Extract missing test information from the markdown report
2. **Classify Tests**: Categorize by priority (high/medium/low) and type (precision/integration/parameter)
3. **Generate Templates**: Create test files with appropriate imports, fixtures, and test methods
4. **Validate**: Ensure generated code is syntactically correct
5. **Document**: Create README with usage instructions

## Usage Example

```python
# User request: "Generate test cases for NPU LoRA based on gap analysis"

# The skill will:
# 1. Read NPU_vs_GPU_LoRA_Test_Gap_Analysis.md
# 2. Parse the gap table and priority lists
# 3. Generate corresponding test files in generated_tests/
# 4. Create __init__.py and README.md
```

## Quality Assurance

Generated tests include:
- ✅ Proper test fixtures for server lifecycle management
- ✅ Comprehensive docstrings (English + Chinese)
- ✅ Proper error handling and assertions
- ✅ Consistent code style and structure
- ✅ Import statements for required utilities

## Limitations

- Generated tests use placeholder model names and URLs - update these before running
- Some advanced features (like TP=8) may need manual adjustment based on available hardware
- Test thresholds (logprob diff) may need tuning for specific models
