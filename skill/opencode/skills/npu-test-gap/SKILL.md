---
name: npu-test-gap
description: analyze GPU vs NPU test coverage, identify missing NPU tests, and generate them automatically
trigger: /npu-test-gap
---

# /npu-test-gap

Analyze GPU vs NPU test coverage for a given feature, identify missing NPU test cases, and generate them automatically.

## Usage

```
/npu-test-gap <feature_name>                                    # analyze and generate missing NPU tests for a feature
/npu-test-gap <feature_name> --repo <path>                      # specify repo root (default: current directory)
/npu-test-gap <feature_name> --gpu-dir <path>                   # override GPU test directory
/npu-test-gap <feature_name> --npu-dir <path>                   # override NPU test directory
/npu-test-gap <feature_name> --output-dir <path>                # override output directory for new tests
/npu-test-gap <feature_name> --analyze-only                     # only analyze, do not generate tests
/npu-test-gap <feature_name> --graphify                         # use graphify knowledge graph for deeper analysis
```

## What This Skill Does

Automates the complete workflow of:
1. **Discovery** - Find all GPU and NPU test files for a given feature
2. **Comparison** - Build a coverage matrix comparing GPU vs NPU test dimensions
3. **Gap Analysis** - Identify what NPU is missing relative to GPU
4. **Generation** - Create properly adapted NPU test files for each gap

## When Invoked

Follow these steps in order. Do not skip steps.

### Step 1 - Validate inputs and set paths

If no feature name was given, ask the user for one. Example feature names: `hicache`, `speculative`, `quantization`, `moe`, `attention`.

Set default paths:

```
REPO_ROOT = <path from --repo or current directory>
GPU_TEST_DIR = <path from --gpu-dir or "{REPO_ROOT}/test/registered/{feature}">
NPU_TEST_DIR = <path from --npu-dir or search under "{REPO_ROOT}/test/registered/ascend" for matching directories>
OUTPUT_DIR = <path from --output-dir or "{NPU_PARENT_DIR}/{Feature}_npu_new">
```

Where `{Feature}` is the feature name with first letter capitalized (e.g., `hicache` → `HiCache`, `ep` → `expert_parallelism`).

For features with nested NPU directories (e.g., `parallel_strategy/expert_parallelism`), the output directory should be created as a sibling: `parallel_strategy/expert_parallelism_npu_new`.

### Step 2 - Discover GPU test files

Search for all test files related to the feature in GPU directories:

```bash
# Search in registered test directories
Get-ChildItem -Path "{REPO_ROOT}/test/registered" -Recurse -Filter "test*{feature}*.py"
# Also search manual test directories
Get-ChildItem -Path "{REPO_ROOT}/test/manual" -Recurse -Filter "test*{feature}*.py"
# Also search multi-gpu directories
Get-ChildItem -Path "{REPO_ROOT}/test/registered" -Recurse -Filter "test*{feature}*.py"
```

For each GPU test file found, read its contents and extract:
- Test class names
- Test method names
- Key server arguments (--enable-*, --*-backend, --*-size, etc.)
- CI registration (register_cuda_ci, register_amd_ci)
- **Model constants used** (CRITICAL: must map to NPU equivalent)
- Test categories (accuracy, performance, functionality, etc.)

### Step 3 - Discover NPU test files

Search for all test files related to the feature in NPU directories:

```bash
Get-ChildItem -Path "{REPO_ROOT}/test/registered/ascend" -Recurse -Filter "test_npu*{feature}*.py"
Get-ChildItem -Path "{REPO_ROOT}/test/registered/ascend" -Recurse -Filter "test_npu*{Feature}*.py"
```

For each NPU test file found, read its contents and extract the same information as Step 2.

### Step 4 - Build coverage matrix

Create a comparison table mapping GPU test dimensions to NPU coverage:

| Dimension | GPU Test File | NPU Test File | Status |
|-----------|--------------|---------------|--------|
| Basic functionality | test_xxx.py | test_npu_xxx.py | ✅ Covered |
| Storage backend A | test_xxx_a.py | ❌ None | ❌ Missing |
| Storage backend B | test_xxx_b.py | ❌ None | ❌ Missing |
| Accuracy validation | test_xxx.py (method) | test_npu_xxx.py | ✅ Covered |
| Performance/TTFT | ❌ None | test_npu_perf.py | NPU only |

Group test files by their **test dimension** (not just filename). Common dimensions:
- Basic functionality / parameter combinations
- Storage backends (file, mooncake, 3fs, nixl, etc.)
- Runtime management (attach/detach, clear, status)
- Speculative decoding integration
- Pipeline parallelism integration
- Disaggregation (prefill/decode split)
- Accuracy validation (GSM8K, MMLU)
- Performance benchmarks (TTFT, throughput)
- Large model / multi-GPU scale
- KV events / monitoring
- Model variants (MLA, MHA, EAGLE, etc.)

### Step 5 - Identify missing NPU tests

For each GPU test dimension that has no NPU equivalent, create a gap entry:

```
GAP_ENTRY = {
    "id": "NPU-{FEATURE}-{SEQ}",
    "dimension": "<test dimension>",
    "gpu_reference": "<gpu test file path>",
    "priority": "P0|P1|P2",
    "description": "<what this test covers>",
    "output_file": "<target NPU test file path>"
}
```

Priority rules:
- **P0 (Critical)**: Core functionality, storage backends, runtime management, speculative integration
- **P1 (High)**: Alternative backends, model variants, accuracy validation
- **P2 (Medium)**: Performance benchmarks, large scale, monitoring/events

### Step 6 - If --analyze-only, stop and report

Print the coverage matrix and gap analysis. Do not generate any files.

### Step 7 - Generate missing NPU test files

For each gap entry, generate a complete NPU test file.

#### NPU adaptation rules (apply to ALL generated files):

| GPU Default | NPU Adaptation |
|-------------|----------------|
| `register_cuda_ci()` | `register_npu_ci(est_time=400, suite="nightly-1-npu-a3", nightly=True)` |
| `register_amd_ci()` | `register_npu_ci(est_time=400, suite="nightly-1-npu-a3", nightly=True)` |
| `--attention-backend flashinfer` (implicit) | `--attention-backend ascend` |
| `--hicache-io-backend direct` | `--hicache-io-backend kernel_ascend` |
| `--hicache-mem-layout page_first` | `--hicache-mem-layout page_first_direct` |
| No cuda-graph flag | `--disable-cuda-graph` |
| Model constant (see mapping below) | Use corresponding NPU model path from `test_ascend_utils` |

#### GPU to NPU model mapping (MUST use GPU's original model type):

When generating NPU tests, identify the GPU model constant used and map to the NPU equivalent:

| GPU Model Constant | NPU Equivalent | Use Case |
|-------------------|----------------|----------|
| `DEFAULT_MODEL_NAME_FOR_TEST` | `QWEN3_8B_WEIGHTS_PATH` | General LLM tests |
| `DEFAULT_MODEL_NAME_FOR_TEST_MLA` | `DEEPSEEK_V3_2_W8A8_WEIGHTS_PATH` | MLA/DeepSeek EP tests |
| `DEFAULT_MLA_MODEL_NAME_FOR_TEST` | `DEEPSEEK_V3_2_W8A8_WEIGHTS_PATH` | MLA architecture tests |
| `DEFAULT_MODEL_NAME_FOR_TEST_MLA_NEXTN` | NPU draft model path | MTP/Speculative tests |
| Large model (70B+) | `QWEN3_32B_WEIGHTS_PATH` | Large model scale tests |
| `LLAMA_3_2_1B_INSTRUCT_WEIGHTS_PATH` | `LLAMA_3_2_1B_INSTRUCT_WEIGHTS_PATH` | Small model tests |

**IMPORTANT**: Always read the GPU test file first to identify which model constant it uses, then map to the corresponding NPU model. Do NOT default to a generic model.

#### File generation template:

For each gap, create a test file following this structure:

```python
"""
<Description of what this test covers on Ascend NPU>.

NPU-specific adaptations:
- --attention-backend ascend
- --disable-cuda-graph
- <feature-specific NPU flags>

Usage:
    python3 -m pytest <output_file> -v
"""

import unittest

from sglang.srt.utils import kill_process_tree
from sglang.test.ascend.test_ascend_utils import <MAPPED_NPU_MODEL>
from sglang.test.ci.ci_register import register_npu_ci
from sglang.test.test_utils import (
    DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
    DEFAULT_URL_FOR_TEST,
    CustomTestCase,
    popen_launch_server,
)

register_npu_ci(est_time=400, suite="nightly-1-npu-a3", nightly=True)
```

#### Adaptation specifics per test type:

**For storage backend tests** (file, mooncake, 3fs):
- Use Mixin pattern if the GPU test uses it
- Adapt `_get_base_server_args()` to include NPU flags
- Map GPU model to NPU equivalent (see model mapping table)
- Keep the same test methods but adapt assertions if needed

**For runtime attach/detach tests**:
- Copy the HTTP helper methods from GPU reference
- Adapt server args to include NPU flags
- Keep the same test phases (auth, attach, detach, re-attach)

**For speculative decoding tests**:
- Add `@unittest.skip("EAGLE3 speculative decoding not yet supported on Ascend NPU")` if EAGLE3 is not available
- Otherwise, adapt the GPU test with NPU flags

**For accuracy tests**:
- Use `run_eval_few_shot_gsm8k` from `sglang.test.few_shot_gsm8k`
- Keep the same accuracy thresholds
- Adapt port extraction for NPU environment

**For large model / multi-NPU tests**:
- Map GPU large model to NPU equivalent (e.g., 70B+ → `QWEN3_32B_WEIGHTS_PATH`)
- Set `--tp-size` to match NPU cluster size (typically 2 or 4)

### Step 8 - Create output directory and write files

```bash
New-Item -ItemType Directory -Path "{OUTPUT_DIR}" -Force
```

Write each generated test file to `{OUTPUT_DIR}/<filename>.py`.

### Step 9 - Report results

Print a summary:

```
NPU Test Gap Analysis Complete
==============================

Feature: <feature_name>
GPU test files found: <count>
NPU test files found: <count>
Missing NPU tests identified: <count>
Generated NPU test files: <count>

Output directory: {OUTPUT_DIR}

Generated files:
  - <file1.py> (P0)
  - <file2.py> (P0)
  - <file3.py> (P1)
  ...

Coverage improvement:
  Before: <NPU coverage percentage>%
  After:  <projected coverage percentage>%
```

## Known NPU Adaptation Patterns

### Common CLI flag adaptations:

```
GPU: (implicit defaults)
NPU: --attention-backend ascend --disable-cuda-graph

GPU: --hicache-io-backend direct
NPU: --hicache-io-backend kernel_ascend

GPU: --hicache-mem-layout page_first
NPU: --hicache-mem-layout page_first_direct

GPU: --page-size 64
NPU: --page-size 128 (NPU typically requires larger page sizes)
```

### CI registration patterns:

```python
# GPU
register_cuda_ci(est_time=148, suite="stage-b-test-2-gpu-large")
register_amd_ci(est_time=526, suite="stage-b-test-2-gpu-large-amd")

# NPU
register_npu_ci(est_time=400, suite="nightly-1-npu-a3", nightly=True)
register_npu_ci(est_time=400, suite="stage-b-test-4-npu-a3", nightly=False)
```

### NPU-specific test categories:

- `test_npu_hierarchical_cache*.py` - Hierarchical cache specific tests
- `test_npu_hicache*.py` - HiCache specific tests
- `test_npu_disaggregation*.py` - Disaggregation tests
- `test_npu_enable_offload*.py` - KV cache offload tests

## Examples

### Example 1: Analyze hicache feature

```
/npu-test-gap hicache
```

This will:
1. Find GPU hicache tests in `test/registered/hicache/`
2. Find NPU hicache tests in `test/registered/ascend/basic_function/HiCache/`
3. Compare and identify gaps
4. Generate missing NPU tests to `test/registered/ascend/basic_function/HiCache_npu_new/`

### Example 2: Analyze-only mode

```
/npu-test-gap speculative --analyze-only
```

This will only print the coverage matrix and gap analysis without generating files.

### Example 3: Use graphify for deeper analysis

```
/npu-test-gap hicache --graphify
```

This will use the graphify knowledge graph to find additional relationships between test files and source code, providing more accurate gap analysis.
