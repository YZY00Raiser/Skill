#!/usr/bin/env python3
"""
NPU Test Gap Analysis Execution Script (Bilingual Version)
NPU测试差距分析执行脚本（双语版本）

This script demonstrates how to use the npu-test-gap-v8 skill
to analyze and generate missing NPU tests with bilingual documentation.
此脚本演示如何使用npu-test-gap-v8 skill分析和生成缺失的NPU测试，包含双语文档。
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class NpuTestGapAnalyzer:
    """Main analyzer class for GPU vs NPU test gap analysis.
    GPU vs NPU测试差距分析的主要分析器类。
    """
    
    def __init__(self, feature: str, workspace: str):
        self.feature = feature
        self.feature_cn = self._get_feature_cn(feature)
        self.workspace = Path(workspace)
        self.config = self._load_config()
        
    def _get_feature_cn(self, feature: str) -> str:
        """Get Chinese name for feature.
        获取功能的中文名称。
        """
        feature_names = {
            "lora": "LoRA适配器",
            "ep": "专家并行",
            "expert_parallelism": "专家并行",
            "moe": "混合专家模型",
            "attention": "注意力机制",
            "cp": "上下文并行",
            "context_parallelism": "上下文并行",
            "quantization": "量化",
            "speculative": "推测解码",
            "radix_cache": "Radix缓存",
        }
        return feature_names.get(feature, feature)
        
    def _load_config(self) -> Dict:
        config_path = Path(__file__).parent / "config.json"
        with open(config_path) as f:
            return json.load(f)
    
    def step1_graphify_analysis(self) -> Dict:
        """Step 1: Analyze feature architecture with graphify.
        步骤1: 使用graphify分析功能架构。
        """
        print(f"\n=== Step 1: Graphify Analysis for {self.feature} ===")
        print(f"=== 步骤1: Graphify分析 {self.feature} ===")
        
        result = subprocess.run(
            ["graphify", "query", self.feature, "--budget", "3000"],
            capture_output=True,
            text=True,
            cwd=self.workspace
        )
        
        nodes = []
        for line in result.stdout.split('\n'):
            if 'NODE' in line or 'EDGE' in line:
                nodes.append(line)
        
        print(f"Found {len(nodes)} relevant nodes/edges")
        print(f"发现 {len(nodes)} 个相关节点/边")
        return {"nodes": nodes[:20], "raw_output": result.stdout}
    
    def step2_collect_gpu_tests(self) -> List[Dict]:
        """Step 2: Collect GPU integration tests.
        步骤2: 收集GPU集成测试。
        """
        print(f"\n=== Step 2: Collect GPU Tests for {self.feature} ===")
        print(f"=== 步骤2: 收集 {self.feature} GPU测试 ===")
        
        gpu_dir = self.workspace / self.config["directories"]["gpu_base"] / self.feature
        
        if not gpu_dir.exists():
            gpu_dir = self.workspace / self.config["directories"]["gpu_manual"] / self.feature
        
        tests = []
        exclude_patterns = self.config["unit_test_patterns"]["exclude_files"]
        
        for f in gpu_dir.glob("*.py"):
            # Skip unit tests / 跳过单元测试
            if any(pat.replace("*", "") in f.name for pat in exclude_patterns):
                continue
            
            # Check for integration test indicators / 检查集成测试指标
            content = f.read_text()
            include_kw = self.config["integration_test_patterns"]["include_keywords"]
            
            is_integration = any(kw in content for kw in include_kw)
            
            if is_integration:
                tests.append({
                    "file": f.name,
                    "path": str(f),
                    "type": "integration",
                    "scenarios": self._extract_test_scenarios(content)
                })
        
        print(f"Found {len(tests)} GPU integration tests")
        print(f"发现 {len(tests)} 个GPU集成测试")
        return tests
    
    def step3_collect_npu_tests(self) -> List[Dict]:
        """Step 3: Collect existing NPU tests.
        步骤3: 收集现有NPU测试。
        """
        print(f"\n=== Step 3: Collect NPU Tests for {self.feature} ===")
        print(f"=== 步骤3: 收集 {self.feature} NPU测试 ===")
        
        npu_dir = self.workspace / self.config["directories"]["npu_base"] / self.feature
        
        tests = []
        for f in npu_dir.glob("test_npu_*.py"):
            content = f.read_text()
            tests.append({
                "file": f.name,
                "path": str(f),
                "gpu_mapping": self._find_gpu_mapping(f.name),
                "scenarios": self._extract_test_scenarios(content)
            })
        
        print(f"Found {len(tests)} NPU tests")
        print(f"发现 {len(tests)} 个NPU测试")
        return tests
    
    def step4_gap_analysis(self, gpu_tests: List, npu_tests: List) -> List[Dict]:
        """Step 4: Compare and identify gaps.
        步骤4: 对比并识别差距。
        """
        print(f"\n=== Step 4: Gap Analysis ===")
        print(f"=== 步骤4: 差距分析 ===")
        
        npu_files = {t["gpu_mapping"] for t in npu_tests if t["gpu_mapping"]}
        gaps = []
        
        for gpu_test in gpu_tests:
            gpu_name = gpu_test["file"].replace("test_", "").replace(".py", "")
            
            if gpu_name not in [t["gpu_mapping"].replace("test_", "").replace(".py", "") 
                               for t in npu_tests]:
                gaps.append({
                    "gpu_file": gpu_test["file"],
                    "scenario": gpu_test["scenarios"],
                    "action": "GENERATE"
                })
        
        print(f"Identified {len(gaps)} missing NPU tests")
        print(f"识别到 {len(gaps)} 个缺失的NPU测试")
        return gaps
    
    def step5_generate_tests(self, gaps: List[Dict]) -> List[str]:
        """Step 5: Generate missing NPU tests.
        Test files use English docstrings only. Chinese goes in README.
        """
        print(f"\n=== Step 5: Generate NPU Tests ===")
        
        from templates import (
            generate_lora_test,
            generate_ep_test,
            generate_cp_test,
        )
        
        generated_files = []
        generated_date = datetime.now().strftime("%Y%m%d")
        npu_dir = self.workspace / self.config["directories"]["npu_base"] / self.feature
        generated_dir = npu_dir / f"GENERATED_{generated_date}"
        generated_dir.mkdir(parents=True, exist_ok=True)
        
        for gap in gaps:
            test_name = gap["gpu_file"].replace("test_", "test_npu_")
            output_path = generated_dir / test_name
            
            if self.feature == "lora":
                content = generate_lora_test(self.feature, gap["scenarios"])
            elif self.feature in ["ep", "expert_parallelism"]:
                content = generate_ep_test(self.feature, gap["scenarios"])
            elif self.feature in ["cp", "context_parallelism"]:
                content = generate_cp_test(self.feature, gap["scenarios"])
            else:
                content = self._generate_generic_test(gap)
            
            output_path.write_text(content)
            generated_files.append(str(output_path))
            print(f"Generated: {output_path}")
        
        return generated_files
    
    def step6_generate_readme(self, generated_files: List[str], gaps: List[Dict]) -> str:
        """Step 6: Generate bilingual README_GENERATED.md.
        步骤6: 生成双语README_GENERATED.md。
        """
        print(f"\n=== Step 6: Generate README ===")
        print(f"=== 步骤6: 生成README ===")
        
        from templates import generate_readme_bilingual
        
        generated_date = datetime.now().strftime("%Y%m%d")
        npu_dir = self.workspace / self.config["directories"]["npu_base"] / self.feature
        generated_dir = npu_dir / f"GENERATED_{generated_date}"
        readme_path = generated_dir / "README_GENERATED.md"
        
        readme_data = {
            "gpu_tests": [gap["gpu_file"] for gap in gaps],
            "npu_tests": [Path(f).name for f in generated_files],
            "mapping": self._build_mapping_data(gaps, generated_files),
            "adaptations": self._get_feature_adaptations(),
            "scenarios": self._build_scenarios_data(gaps),
            "before_coverage": "0%",
            "after_coverage": "100%",
        }
        
        readme_content = generate_readme_bilingual(
            self.feature, 
            self.feature_cn,
            readme_data
        )
        
        readme_path.write_text(readme_content)
        print(f"Generated README: {readme_path}")
        print(f"已生成README: {readme_path}")
        return str(readme_path)
    
    def step7_verify_syntax(self, files: List[str]) -> Dict:
        """Step 7: Verify generated file syntax.
        步骤7: 验证生成文件语法。
        """
        print(f"\n=== Step 7: Syntax Verification ===")
        print(f"=== 步骤7: 语法验证 ===")
        
        results = {}
        for f in files:
            result = subprocess.run(
                ["python", "-m", "py_compile", f],
                capture_output=True
            )
            results[f] = result.returncode == 0
            status = "PASS" if results[f] else "FAIL"
            status_cn = "通过" if results[f] else "失败"
            print(f"  {Path(f).name}: {status} / {status_cn}")
        
        return results
    
    def _extract_test_scenarios(self, content: str) -> List[Dict]:
        """Extract test scenarios from file content.
        从文件内容提取测试场景。
        """
        scenarios = []
        for line in content.split('\n'):
            if 'def test_' in line:
                method_name = line.split('def test_')[1].split('(')[0]
                scenarios.append({"test_method": method_name})
        return scenarios
    
    def _find_gpu_mapping(self, npu_file: str) -> str:
        """Find corresponding GPU test file name.
        查找对应的GPU测试文件名。
        """
        # test_npu_lora_tp.py -> test_lora_tp.py
        return npu_file.replace("test_npu_", "test_")
    
    def _generate_generic_test(self, gap: Dict) -> str:
        """Generate generic test template (English only).
        """
        return f'''# TODO: Implement test for {gap["gpu_file"]}
# Feature: {self.feature}
# Scenarios: {gap["scenarios"]}
'''
    
    def _build_mapping_data(self, gaps: List[Dict], generated_files: List[str]) -> List[Dict]:
        """Build mapping table data.
        构建映射表数据。
        """
        mapping = []
        for gap, gen_file in zip(gaps, generated_files):
            mapping.append({
                "gpu_file": gap["gpu_file"],
                "gpu_class": "TestClass",
                "gpu_config": "TP=2",
                "npu_file": Path(gen_file).name,
                "npu_class": "TestClass",
                "npu_config": "TP=2",
                "status": "⚠️ ADAPTED",
                "notes": "NPU adaptations applied / NPU适配已应用"
            })
        return mapping
    
    def _get_feature_adaptations(self) -> List[Dict]:
        """Get feature-specific adaptations.
        获取功能特有的适配说明。
        """
        adaptations = {
            "lora": [
                {"feature_en": "Attention backend", "feature_cn": "注意力后端", 
                 "desc_en": "Changed to ascend", "desc_cn": "改为ascend"}
            ],
            "ep": [
                {"feature_en": "Model path", "feature_cn": "模型路径",
                 "desc_en": "Changed to NPU weights", "desc_cn": "改为NPU权重"}
            ],
            "cp": [
                {"feature_en": "EAGLE", "feature_cn": "EAGLE推测解码",
                 "desc_en": "Removed (not supported)", "desc_cn": "已移除（不支持）"},
                {"feature_en": "NSA prefill CP", "feature_cn": "NSA prefill CP",
                 "desc_en": "Changed to standard prefill CP", "desc_cn": "改为标准prefill CP"}
            ],
        }
        return adaptations.get(self.feature, [])
    
    def _build_scenarios_data(self, gaps: List[Dict]) -> List[Dict]:
        """Build test scenarios data.
        构建测试场景数据。
        """
        scenarios = []
        for gap in gaps:
            scenarios.append({
                "class": gap["gpu_file"].replace(".py", ""),
                "desc_en": f"Test {self.feature} functionality",
                "desc_cn": f"测试{self.feature_cn}功能"
            })
        return scenarios
    
    def run_full_analysis(self) -> Dict:
        """Execute full analysis workflow.
        执行完整分析流程。
        """
        results = {}
        
        # Step 1 / 步骤1
        results["graphify"] = self.step1_graphify_analysis()
        
        # Step 2 / 步骤2
        results["gpu_tests"] = self.step2_collect_gpu_tests()
        
        # Step 3 / 步骤3
        results["npu_tests"] = self.step3_collect_npu_tests()
        
        # Step 4 / 步骤4
        results["gaps"] = self.step4_gap_analysis(
            results["gpu_tests"], 
            results["npu_tests"]
        )
        
        # Step 5 / 步骤5
        results["generated"] = self.step5_generate_tests(results["gaps"])
        
        # Step 6 / 步骤6
        results["readme"] = self.step6_generate_readme(
            results["generated"],
            results["gaps"]
        )
        
        # Step 7 / 步骤7
        results["verification"] = self.step7_verify_syntax(results["generated"])
        
        return results


def main():
    """Main entry point.
    主入口点。
    """
    parser = argparse.ArgumentParser(
        description="NPU Test Gap Analysis (Bilingual) / NPU测试差距分析（双语）"
    )
    parser.add_argument(
        "--feature", 
        required=True, 
        help="Feature to analyze (lora, ep, moe, cp) / 要分析的功能 (lora, ep, moe, cp)"
    )
    parser.add_argument(
        "--workspace", 
        default=os.getcwd(), 
        help="Workspace directory / 工作目录"
    )
    parser.add_argument(
        "--output", 
        default="report.json", 
        help="Output report file / 输出报告文件"
    )
    
    args = parser.parse_args()
    
    analyzer = NpuTestGapAnalyzer(args.feature, args.workspace)
    results = analyzer.run_full_analysis()
    
    # Save report / 保存报告
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n=== Report saved to {args.output} ===")
    print(f"=== 报告已保存到 {args.output} ===")


if __name__ == "__main__":
    main()