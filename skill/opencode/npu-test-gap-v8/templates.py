"""
NPU Test Template Generator
NPU测试模板生成器

This module provides template functions for generating NPU integration tests.
Test files use English docstrings only. Chinese translations go in README_GENERATED.md.
"""

import os
from datetime import datetime

IMPORTS_BASE = '''
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
'''

IMPORTS_LORA = '''
from sglang.test.ascend.test_ascend_utils import (
    LLAMA_3_2_1B_INSTRUCT_WEIGHTS_PATH,
    LLAMA_3_2_1B_INSTRUCT_TOOL_CALLING_LORA_WEIGHTS_PATH,
)
'''

IMPORTS_EP = '''
from sglang.test.ascend.test_ascend_utils import (
    DEEPSEEK_V3_2_W8A8_WEIGHTS_PATH,
    QWEN3_30B_A3B_W8A8_WEIGHTS_PATH,
)
'''

IMPORTS_CP = '''
from sglang.test.ascend.test_ascend_utils import (
    DEEPSEEK_V3_2_W8A8_WEIGHTS_PATH,
    QWEN3_30B_A3B_WEIGHTS_PATH,
)
'''

NPU_CI_REGISTER = '''
register_npu_ci(est_time=400, suite="nightly-2-npu-a3", nightly=True)
'''

CLASS_TEMPLATE = '''
class Test{ClassName}(CustomTestCase):
    """Test {Feature} on NPU.

    [Test Category] {Category}
    [Test Target] {TestTarget}
    """
    
    base_model = {ModelPath}
    
    @classmethod
    def setUpClass(cls):
        other_args = [
            "--attention-backend", "ascend",
            "--disable-cuda-graph",
            "--mem-fraction-static", "0.3",
            {ExtraArgs}
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
    
    def test_{test_name}(self):
        response = requests.post(
            DEFAULT_URL_FOR_TEST + "/generate",
            json={{
                "text": "{prompt}",
                "sampling_params": {{'temperature': 0, 'max_new_tokens': 32}},
            }},
        )
        self.assertEqual(response.status_code, 200)
'''

CLASS_TEMPLATE_PARAM = '''
class Test{ClassName}(CustomTestCase):
    """Test {Feature} parameter on NPU.

    [Test Category] Parameter
    [Test Target] {ParamName}
    """
    
    base_model = {ModelPath}
    
    @classmethod
    def setUpClass(cls):
        other_args = [
            "--attention-backend", "ascend",
            "--disable-cuda-graph",
            "--mem-fraction-static", "0.3",
            "{ParamName}", "{ParamValue}",
            {ExtraArgs}
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
    
    def test_{test_name}(self):
        response = requests.post(
            DEFAULT_URL_FOR_TEST + "/generate",
            json={{
                "text": "{prompt}",
                "sampling_params": {{'temperature': 0, 'max_new_tokens': 32}},
            }},
        )
        self.assertEqual(response.status_code, 200)
'''

CLASS_TEMPLATE_MODEL = '''
class Test{ClassName}(CustomTestCase):
    """Test {ModelName} model inference on NPU.

    [Test Category] Model
    [Test Target] {ModelPath}
    """
    
    model = {ModelVar}
    
    @classmethod
    def setUpClass(cls):
        other_args = [
            "--attention-backend", "ascend",
            "--disable-cuda-graph",
            "--mem-fraction-static", "0.3",
            {ExtraArgs}
        ]
        cls.process = popen_launch_server(
            cls.model,
            DEFAULT_URL_FOR_TEST,
            timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
            other_args=other_args,
        )
    
    @classmethod
    def tearDownClass(cls):
        kill_process_tree(cls.process.pid)
    
    def test_{test_name}(self):
        response = requests.post(
            DEFAULT_URL_FOR_TEST + "/generate",
            json={{
                "text": "{prompt}",
                "sampling_params": {{'temperature': 0, 'max_new_tokens': 32}},
            }},
        )
        self.assertEqual(response.status_code, 200)
'''

CLASS_TEMPLATE_INTERFACE = '''
class Test{ClassName}(CustomTestCase):
    """Test {InterfaceName} endpoint on NPU.

    [Test Category] Interface
    [Test Target] {InterfacePath}
    """
    
    @classmethod
    def setUpClass(cls):
        cls.base_url = DEFAULT_URL_FOR_TEST
        cls.process = popen_launch_server(
            {ModelPath},
            DEFAULT_URL_FOR_TEST,
            timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
            other_args=[
                "--attention-backend", "ascend",
                "--disable-cuda-graph",
                "--mem-fraction-static", "0.3",
                {ExtraArgs}
            ],
        )
    
    @classmethod
    def tearDownClass(cls):
        kill_process_tree(cls.process.pid)
    
    def test_{test_name}(self):
        response = requests.get(self.base_url + "{InterfacePath}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("{ExpectedKey}", response.json())
'''

MAIN_BLOCK = '''
if __name__ == "__main__":
    unittest.main()
'''

README_TEMPLATE_BILINGUAL = '''# Generated NPU Tests - {Feature}
# 生成的NPU测试 - {FeatureCn}

**Generated Date**: {Date}
**生成日期**: {Date}

**Generator**: npu-test-gap-v8 skill
**生成器**: npu-test-gap-v8 skill

**Analyzed Scope**: test/registered/{feature}/ (only this directory)
**分析范围**: test/registered/{feature}/ (仅此目录)

## Corresponding GPU Tests
## 对应的GPU测试
{GpuTestsList}

## Generated NPU Tests
## 生成的NPU测试
{NpuTestsList}

## GPU-NPU Test Mapping
## GPU-NPU测试映射表

{MappingTable}

**映射状态说明**:
- ⚠️ ADAPTED: 已适配 - NPU测试存在但需要适配GPU特性
- ❌ MISSING: 缺失 - 无对应NPU测试

## Key Adaptations for NPU
## NPU关键适配说明

{AdaptationsList}

## Coverage Statistics
## 覆盖率统计

- **Before**: {BeforeCoverage} / **生成前**: {BeforeCoverage}
- **After**: {AfterCoverage} / **生成后**: {AfterCoverage}

## Test Scenarios
## 测试场景

{TestScenariosList}
'''


def generate_lora_test(feature_name: str, test_scenarios: list) -> str:
    """Generate NPU LoRA test file.
    Test files use English docstrings only.
    """
    
    content = IMPORTS_BASE.rstrip()
    content += IMPORTS_LORA
    content += NPU_CI_REGISTER
    
    for scenario in test_scenarios:
        class_name = f"NPULoRA{scenario['name']}"
        extra_args = generate_lora_args(scenario)
        
        content += CLASS_TEMPLATE.format(
            ClassName=class_name,
            Feature=scenario['feature'],
            Category=scenario['category'],
            TestTarget=scenario['test_target'],
            ModelPath="LLAMA_3_2_1B_INSTRUCT_WEIGHTS_PATH",
            ExtraArgs=extra_args,
            test_name=scenario['test_method'],
            prompt=scenario.get('prompt', "The capital of France is"),
        )
    
    content += MAIN_BLOCK
    return content


def generate_ep_test(feature_name: str, test_scenarios: list) -> str:
    """Generate NPU EP test file.
    Test files use English docstrings only.
    """
    
    content = IMPORTS_BASE.rstrip()
    content += IMPORTS_EP
    content += NPU_CI_REGISTER
    
    for scenario in test_scenarios:
        class_name = f"NPU{scenario['name']}"
        extra_args = generate_ep_args(scenario)
        
        content += CLASS_TEMPLATE.format(
            ClassName=class_name,
            Feature=scenario['feature'],
            Category=scenario['category'],
            TestTarget=scenario['test_target'],
            ModelPath=scenario.get('model', "QWEN3_30B_A3B_W8A8_WEIGHTS_PATH"),
            ExtraArgs=extra_args,
            test_name=scenario['test_method'],
            prompt=scenario.get('prompt', "The capital of France is"),
        )
    
    content += MAIN_BLOCK
    return content


def generate_cp_test(feature_name: str, test_scenarios: list) -> str:
    """Generate NPU Context Parallelism test file.
    Test files use English docstrings only.
    """
    
    content = IMPORTS_BASE.rstrip()
    content += IMPORTS_CP
    content += NPU_CI_REGISTER
    
    for scenario in test_scenarios:
        class_name = f"NPU{scenario['name']}"
        extra_args = generate_cp_args(scenario)
        
        content += CLASS_TEMPLATE.format(
            ClassName=class_name,
            Feature=scenario['feature'],
            Category=scenario['category'],
            TestTarget=scenario['test_target'],
            ModelPath=scenario.get('model', "DEEPSEEK_V3_2_W8A8_WEIGHTS_PATH"),
            ExtraArgs=extra_args,
            test_name=scenario['test_method'],
            prompt=scenario.get('prompt', "The capital of France is"),
        )
    
    content += MAIN_BLOCK
    return content


def generate_lora_args(scenario: dict) -> str:
    """Generate LoRA-specific server args.
    生成LoRA特有的服务器参数。
    """
    args = [
        '"--enable-lora",',
        '"--lora-path", f"lora_a={LLAMA_3_2_1B_INSTRUCT_TOOL_CALLING_LORA_WEIGHTS_PATH}",',
        '"--max-loaded-loras", "2",',
        '"--max-loras-per-batch", "2",',
        '"--lora-target-modules", "all",',
    ]
    
    if scenario.get('tp_size'):
        args.append(f'"--tp-size", "{scenario["tp_size"]}",')
    
    if scenario.get('disable_radix_cache'):
        args.append('"--disable-radix-cache",')
    
    return "\n            " + "\n            ".join(args)


def generate_ep_args(scenario: dict) -> str:
    """Generate EP-specific server args.
    生成EP特有的服务器参数。
    """
    args = [
        '"--moe-a2a-backend", "deepep",',
    ]
    
    if scenario.get('deepep_mode'):
        args.append(f'"--deepep-mode", "{scenario["deepep_mode"]}",')
    
    if scenario.get('tp_size'):
        args.append(f'"--tp-size", "{scenario["tp_size"]}",')
    
    if scenario.get('ep_size'):
        args.append(f'"--ep-size", "{scenario["ep_size"]}",')
    
    if scenario.get('dp_size'):
        args.append(f'"--dp-size", "{scenario["dp_size"]}",')
        args.append('"--enable-dp-attention",')
    
    return "\n            " + "\n            ".join(args)


def generate_cp_args(scenario: dict) -> str:
    """Generate Context Parallelism-specific server args.
    生成上下文并行特有的服务器参数。
    """
    args = []
    
    if scenario.get('tp_size'):
        args.append(f'"--tp-size", "{scenario["tp_size"]}",')
    
    if scenario.get('attn_cp_size'):
        args.append(f'"--attn-cp-size", "{scenario["attn_cp_size"]}",')
    
    if scenario.get('dp_size'):
        args.append(f'"--dp-size", "{scenario["dp_size"]}",')
        args.append('"--enable-dp-attention",')
    
    if scenario.get('enable_prefill_cp'):
        args.append('"--enable-prefill-context-parallel",')
    
    return "\n            " + "\n            ".join(args)


def generate_readme_bilingual(feature: str, feature_cn: str, data: dict) -> str:
    """Generate bilingual README_GENERATED.md.
    生成双语README_GENERATED.md。
    """
    date = datetime.now().strftime("%Y-%m-%d")
    
    gpu_tests_list = "\n".join([f"- {t}" for t in data.get('gpu_tests', [])])
    npu_tests_list = "\n".join([f"- {t}" for t in data.get('npu_tests', [])])
    
    mapping_table = format_mapping_table_bilingual(data.get('mapping', []))
    adaptations_list = format_adaptations_section_bilingual(data.get('adaptations', []))
    test_scenarios_list = format_test_scenarios_bilingual(data.get('scenarios', []))
    
    return README_TEMPLATE_BILINGUAL.format(
        Feature=feature,
        FeatureCn=feature_cn,
        Date=date,
        feature=feature,
        GpuTestsList=gpu_tests_list,
        NpuTestsList=npu_tests_list,
        MappingTable=mapping_table,
        AdaptationsList=adaptations_list,
        BeforeCoverage=data.get('before_coverage', '0%'),
        AfterCoverage=data.get('after_coverage', '100%'),
        TestScenariosList=test_scenarios_list,
    )


def format_mapping_table_bilingual(mapping_data: list) -> str:
    """Format GPU-NPU mapping table with bilingual headers.
    格式化包含双语表头的GPU-NPU映射表。
    """
    if not mapping_data:
        return "No mapping data / 无映射数据"
    
    header = "| GPU Test File | GPU Test Class | GPU Config | NPU Test File | NPU Test Class | NPU Config | Mapping Status | Adaptation Notes |"
    separator = "|---------------|----------------|------------|---------------|----------------|------------|----------------|------------------|"
    
    rows = []
    for item in mapping_data:
        row = f"| {item['gpu_file']} | {item['gpu_class']} | {item['gpu_config']} | {item['npu_file']} | {item['npu_class']} | {item['npu_config']} | {item['status']} | {item['notes']} |"
        rows.append(row)
    
    return "\n".join([header, separator] + rows)


def format_adaptations_section_bilingual(adaptations: list) -> str:
    """Format adaptations section in bilingual format.
    格式化双语适配说明部分。
    """
    if not adaptations:
        return "1. None / 无"
    
    lines = []
    for i, adapt in enumerate(adaptations, 1):
        if isinstance(adapt, dict):
            lines.append(f"{i}. **{adapt['feature_en']}**: {adapt['desc_en']} / **{adapt['feature_cn']}: {adapt['desc_cn']}")
        else:
            lines.append(f"{i}. {adapt} / {adapt}")
    
    return "\n".join(lines)


def format_test_scenarios_bilingual(scenarios: list) -> str:
    """Format test scenarios in bilingual format.
    格式化双语测试场景。
    """
    if not scenarios:
        return "No scenarios / 无测试场景"
    
    lines = []
    for scenario in scenarios:
        if isinstance(scenario, dict):
            lines.append(f"### {scenario['class']}")
            lines.append(f"- {scenario['desc_en']}")
            lines.append(f"- {scenario['desc_cn']}")
        else:
            lines.append(f"### {scenario}")
    
    return "\n".join(lines)


# Predefined test scenarios
# Chinese info kept for README generation, not for test files

LORA_TP_SCENARIO = {
    "name": "LoRATP",
    "feature": "LoRA with Tensor Parallelism",
    "feature_cn": "LoRA张量并行",  # For README only
    "category": "Parameter",
    "test_target": "--tp-size 2, --enable-lora",
    "category_cn": "参数",  # For README only
    "target_cn": "TP=2 LoRA参数",  # For README only
    "test_method": "lora_tp_inference",
    "test_desc": "LoRA TP inference",
    "tp_size": 2,
    "gpu_test": "test_lora_tp.py",
    "adaptations": [
        {"en": "Attention backend changed to ascend", "cn": "注意力后端改为ascend"}
    ]
}

LORA_RADIX_CACHE_SCENARIO = {
    "name": "LoRARadixCache",
    "feature": "LoRA with Radix Cache",
    "feature_cn": "LoRA与Radix缓存",
    "category": "Parameter",
    "test_target": "--disable-radix-cache",
    "category_cn": "参数",
    "target_cn": "禁用Radix缓存参数",
    "test_method": "kv_cache_reuse",
    "test_desc": "KV cache reuse",
    "gpu_test": "test_lora_radix_cache.py",
    "adaptations": [
        {"en": "CUDA graph disabled", "cn": "CUDA graph已禁用"}
    ]
}

EP_AUTO_SCENARIO = {
    "name": "DeepEPAuto",
    "feature": "DeepEP Auto Mode",
    "feature_cn": "DeepEP自动模式",
    "category": "Model",
    "test_target": "Qwen3-30B-A3B-W8A8",
    "category_cn": "模型",
    "target_cn": "Qwen3-30B模型",
    "test_method": "deepep_auto_inference",
    "test_desc": "DeepEP auto inference",
    "deepep_mode": "auto",
    "tp_size": 16,
    "ep_size": 16,
    "model": "QWEN3_30B_A3B_W8A8_WEIGHTS_PATH",
    "gpu_test": "test_ep_auto.py",
    "adaptations": [
        {"en": "Model path changed to NPU weights", "cn": "模型路径改为NPU权重"}
    ]
}

CP_ATTN_CP4_SCENARIO = {
    "name": "DeepseekV32CPAttnCP4",
    "feature": "DeepSeek-V3.2 Context Parallelism with ATTN_CP=4",
    "feature_cn": "DeepSeek-V3.2上下文并行 ATTENTION_CP=4",
    "category": "Model",
    "test_target": "vllm-ascend/DeepSeek-V3.2-W8A8",
    "category_cn": "模型",
    "target_cn": "DeepSeek-V3.2模型",
    "test_method": "gsm8k_accuracy",
    "test_desc": "GSM8K accuracy test",
    "tp_size": 8,
    "dp_size": 2,
    "attn_cp_size": 4,
    "enable_prefill_cp": True,
    "model": "DEEPSEEK_V3_2_W8A8_WEIGHTS_PATH",
    "gpu_test": "test_deepseek_v32_cp_single_node.py::TestDeepseekV32CPInSeqSplit",
    "adaptations": [
        {"en": "EAGLE removed (not supported on NPU)", "cn": "EAGLE已移除（NPU不支持）"},
        {"en": "NSA prefill CP changed to standard prefill CP", "cn": "NSA prefill CP改为标准prefill CP"},
        {"en": "Model path changed to NPU weights", "cn": "模型路径改为NPU权重"}
    ]
}

SERVER_INFO_SCENARIO = {
    "name": "ServerInfoEndpoint",
    "feature": "Server Info Endpoint",
    "feature_cn": "服务器信息接口",
    "category": "Interface",
    "test_target": "/server_info",
    "category_cn": "接口",
    "target_cn": "/server_info接口",
    "test_method": "server_info_endpoint",
    "test_desc": "Server info endpoint test",
    "interface_path": "/server_info",
    "expected_key": "model_path",
    "gpu_test": "test_server_info.py",
    "adaptations": []
}


if __name__ == "__main__":
    # Example: Generate LoRA TP test (English only in test file)
    test_content = generate_lora_test("tp", [LORA_TP_SCENARIO])
    print(test_content)
    
    # Example: Generate CP test (English only in test file)
    cp_content = generate_cp_test("cp", [CP_ATTN_CP4_SCENARIO])
    print(cp_content)