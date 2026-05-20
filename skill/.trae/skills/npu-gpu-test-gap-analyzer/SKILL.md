---
name: "npu-gpu-test-gap-analyzer"
description: "Analyzes test coverage gaps between NPU and GPU test suites by comparing knowledge base documents. Invoke when user needs to compare NPU vs GPU test coverage, identify missing NPU tests, or generate gap analysis reports."
---

# NPU vs GPU Test Gap Analyzer

This skill analyzes test coverage gaps between NPU (Ascend) and GPU test suites by comparing their respective knowledge base documents. It produces a structured gap analysis report identifying missing NPU tests, parameter coverage differences, and prioritized recommendations.

## When to Invoke

- User wants to compare NPU and GPU test coverage for a specific module
- User needs to identify which GPU tests are not covered by NPU tests
- User asks for a gap analysis report between two test suites
- User wants to know what NPU tests are missing compared to GPU

## Input Requirements

The skill expects two knowledge base markdown files as input:

1. **GPU Knowledge Base**: A markdown file documenting GPU test suite (e.g., `LoRA_Testing_Knowledge_Base.md` in the GPU test directory)
2. **NPU Knowledge Base**: A markdown file documenting NPU test suite (e.g., `LoRA_Testing_Knowledge_Base.md` in the NPU/Ascend test directory)

Both files should follow the standard knowledge base format with sections for:
- Overview / 概述
- Core Parameters / 核心参数
- Test Function Points / 测试功能点
- Observable Points / 可观察点
- Test File Summary / 测试文件汇总

## Analysis Workflow

### Step 1: Read and Parse Knowledge Bases

Read both knowledge base files completely. Extract the following information from each:

- **Test file list** with test types (Unit/Integration/Precision/Parameter/Interface)
- **Parameters covered** with test file mappings
- **Function points** per test file
- **Observable points** per test file
- **Models covered** (if applicable)
- **CI registration** details (if available)

### Step 2: Test Scale Comparison

Generate a comparison table covering:

| Dimension | GPU | NPU (Ascend) |
|-----------|-----|-------------|
| Total test files | N | M |
| Unit tests | N | M |
| Integration tests | N | M |
| Precision tests | N | M |
| Parameter tests | N | M |
| Interface tests | N | M |
| Tests requiring coverage (excluding unit tests) | N | M |
| Models covered | N+ | M |

**Important**: Unit tests are marked as "NPU does not need to cover" because:
- GPU kernel tests (SGMV, MoE fusion, virtual experts) are GPU-architecture-specific
- Pure logic tests (eviction policy, API parsing, drainer scheduling) are indirectly covered by NPU integration/interface tests

### Step 3: Test Type Classification Comparison

#### 3.1 Classify GPU tests by type and sub-category

For each GPU test, assign:
- **Test type**: Unit / Integration / Precision
- **Sub-category**: Kernel / API / Memory Management / Scheduling / Performance / Cache / Management / Batch / Parallelism / Model / Comparison

#### 3.2 Classify NPU tests by type and sub-category

For each NPU test, assign:
- **Test type**: Parameter / Integration / Interface
- **Sub-category**: Backend / Parameter / Memory Management / Performance / API / Comprehensive

#### 3.3 Generate sub-category comparison table

| Sub-category | GPU Count | GPU Files | NPU Count | NPU Files | Coverage Gap |
|-------------|-----------|-----------|-----------|-----------|-------------|

Coverage gap levels:
- ⬜ NPU does not need to cover (GPU kernel tests)
- ⚠️ Partial coverage or depth insufficient
- 🔴 Completely missing
- ✅ NPU unique coverage

#### 3.4 Generate coverage statistics

| Test Type | GPU Count | NPU Count | NPU Coverage Rate | Notes |
|-----------|-----------|-----------|-------------------|-------|

Include a row for "Tests requiring coverage (excluding unit tests)" with recalculated coverage rate.

### Step 4: Parameter Coverage Comparison

#### 4.1 Parameter overview table

For each parameter found in either knowledge base:

| Parameter | GPU Coverage | NPU Coverage | Gap Description |
|-----------|-------------|-------------|-----------------|

#### 4.2 Parameter coverage statistics

| Coverage Status | Count | Percentage |
|----------------|-------|-----------|
| ✅ Both covered | N | X% |
| ⚠️ Both covered but different depth | N | X% |
| ❌ Only GPU covered | N | X% |
| ✅ Only NPU covered | N | X% |

#### 4.3 NPU uncovered parameters detail

| Parameter | GPU Test Files | Impact | Priority |
|-----------|---------------|--------|----------|

Priority levels: 🔴 High / 🟡 Medium / 🟢 Low

#### 4.4 NPU unique parameters

| Parameter | NPU Test Files | Unique Verification Points |
|-----------|---------------|--------------------------|

### Step 5: NPU Covered GPU Test Mapping

Map each NPU test to its corresponding GPU test(s) and assess coverage level:

| NPU Test | Corresponding GPU Test | Coverage Level |
|----------|----------------------|----------------|

Coverage levels:
- ✅ Well covered
- ⚠️ Partial — describe what's missing
- ✅ NPU unique — no GPU equivalent

### Step 6: NPU Uncovered GPU Tests

List all GPU tests not covered by NPU, excluding unit tests. Add an exclusion note at the top:

> **Exclusion Note**: The following GPU unit tests do not need NPU coverage:
> - GPU kernel tests (architecture-specific)
> - Pure logic unit tests (indirectly covered by NPU integration/interface tests)

Organize uncovered tests by category:

#### Category 1: Precision/Regression Tests
#### Category 2: Parallelism & Comparison Tests
#### Category 3: Integration Tests
#### Category 4: Model Feature Tests
#### Category 5: API & Embedding Tests

For each test, provide:
| # | GPU Test | Test Type | Missing Function Points | Priority |

### Step 7: NPU Unique Tests

List NPU tests that have no GPU equivalent:

| NPU Test | Unique Function Points |
|----------|----------------------|

### Step 8: Prioritized Missing Test Summary

#### 🔴 High Priority (Core functionality missing)

| # | Missing Test Area | Suggested NPU Test Name | Key Verification Points |
|---|------------------|------------------------|------------------------|

#### 🟡 Medium Priority (Model coverage and feature supplement)

| # | Missing Test Area | Suggested NPU Test Name |
|---|------------------|------------------------|

#### 🟢 Low Priority

| # | Missing Test Area | Suggested NPU Test Name |
|---|------------------|------------------------|

### Step 9: Key Gap Summary

Summarize the most critical gaps in numbered list format, covering:
1. Precision test gaps
2. Unit test exclusion rationale
3. Dynamic management feature gaps
4. Multi-LoRA batch processing gaps
5. Tensor parallelism gaps
6. Model coverage breadth
7. Embedding model LoRA gaps

## Output Format

Generate a single markdown file named `NPU_vs_GPU_<Module>_Test_Gap_Analysis.md` in the NPU test directory (same location as the NPU knowledge base).

The report should use:
- Bilingual headers (English / Chinese) for major sections
- Emoji indicators for test types (🔬 Unit, 🔗 Integration, 📊 Precision)
- Color-coded priority indicators (🔴 High, 🟡 Medium, 🟢 Low)
- Coverage status indicators (✅, ⚠️, ❌, ⬜)
- Proper markdown tables for all comparison data

## Report Structure

```
# NPU vs GPU <Module> Test Gap Analysis Report

## 一、Test Scale Comparison
## 二、Test Type Classification Comparison
  ### 2.1 GPU Test Type Classification
  ### 2.2 NPU Test Type Classification
  ### 2.3 Sub-category Comparison
  ### 2.4 Coverage Statistics
## 三、Parameter Coverage Comparison
  ### 3.1 Parameter Overview
  ### 3.2 Parameter Coverage Statistics
  ### 3.3 NPU Uncovered Parameters Detail
  ### 3.4 NPU Unique Parameters
## 四、NPU Covered GPU Test Mapping
## 五、NPU Uncovered GPU Tests (excluding unit tests)
## 六、NPU Unique Tests
## 七、Prioritized Missing Test Summary
## 八、Key Gap Summary
```

## Notes

- Always exclude GPU unit tests from NPU coverage requirements
- GPU kernel tests are architecture-specific and not applicable to NPU
- Pure logic unit tests should be indirectly covered by NPU integration/interface tests
- Parameter coverage should account for NPU-specific backends (e.g., ascend, torch_native)
- Priority assessment should consider: (1) core functionality impact, (2) user-facing feature coverage, (3) regression risk
- When NPU has unique tests or parameters not present in GPU, highlight them as NPU advantages
