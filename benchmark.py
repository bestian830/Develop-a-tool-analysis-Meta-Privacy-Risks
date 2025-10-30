"""
基准测试工具 - 比较人工标注与工具分析结果

这个脚本用于评估隐私政策分析器的性能，通过比较：
1. 人工标注结果
2. 工具自动分析结果

评估指标包括：
- 类别一致性（Cohen's Kappa）
- 参数提取的精确率、召回率、F1分数
- 风险评分的相关性
"""

import json
from typing import Dict, List, Tuple
import statistics
from pathlib import Path
from privacy_analyzer_example import PrivacyPolicyAnalyzer


class BenchmarkEvaluator:
    """基准测试评估器"""
    
    def __init__(self):
        self.analyzer = PrivacyPolicyAnalyzer()
    
    def calculate_set_metrics(self, human_set: set, tool_set: set) -> Dict[str, float]:
        """
        计算集合类指标（用于数据类型、第三方等）
        
        返回精确率、召回率、F1分数
        """
        if len(tool_set) == 0:
            precision = 0.0
        else:
            intersection = len(human_set & tool_set)
            precision = intersection / len(tool_set)
        
        if len(human_set) == 0:
            recall = 1.0 if len(tool_set) == 0 else 0.0
        else:
            intersection = len(human_set & tool_set)
            recall = intersection / len(human_set)
        
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
    
    def evaluate_segment(self, human_annotation: Dict, segment_text: str) -> Dict:
        """
        评估单个段落的分析结果
        
        参数:
            human_annotation: 人工标注结果
            segment_text: 段落文本
            
        返回:
            评估结果字典
        """
        # 使用工具分析
        tool_result = self.analyzer.analyze_segment(segment_text)
        
        # 1. 类别一致性
        category_match = (human_annotation.get("category") == tool_result["category"])
        
        # 2. 数据类型匹配
        human_data_types = set(human_annotation.get("data_types", []))
        tool_data_types = set(tool_result["parameters"]["data_types"])
        data_type_metrics = self.calculate_set_metrics(human_data_types, tool_data_types)
        
        # 3. 第三方匹配
        human_third_parties = set(human_annotation.get("third_parties", []))
        tool_third_parties = set(tool_result["parameters"]["third_parties"])
        third_party_metrics = self.calculate_set_metrics(human_third_parties, tool_third_parties)
        
        # 4. 用户权利匹配
        human_rights = set(human_annotation.get("user_rights", []))
        tool_rights = set(tool_result["parameters"]["user_rights"])
        rights_metrics = self.calculate_set_metrics(human_rights, tool_rights)
        
        # 5. 风险分数差异
        human_risk = human_annotation.get("risk_score", 0.5)
        tool_risk = tool_result["risk_score"]
        risk_difference = abs(human_risk - tool_risk)
        
        return {
            "segment_text": segment_text[:100] + "..." if len(segment_text) > 100 else segment_text,
            "category_match": category_match,
            "human_category": human_annotation.get("category"),
            "tool_category": tool_result["category"],
            "data_type_metrics": data_type_metrics,
            "third_party_metrics": third_party_metrics,
            "rights_metrics": rights_metrics,
            "risk_difference": risk_difference,
            "human_risk": human_risk,
            "tool_risk": tool_risk,
            "tool_result": tool_result
        }
    
    def evaluate_dataset(self, annotations_file: str) -> Dict:
        """
        评估整个数据集
        
        参数:
            annotations_file: 人工标注文件路径（JSON格式）
            
        返回:
            总体评估结果
        """
        # 加载人工标注
        with open(annotations_file, "r", encoding="utf-8") as f:
            annotations = json.load(f)
        
        segment_results = []
        
        for annotation in annotations:
            segment_text = annotation["text"]
            result = self.evaluate_segment(annotation, segment_text)
            segment_results.append(result)
        
        # 计算总体指标
        total_segments = len(segment_results)
        
        # 类别一致性
        category_matches = sum(1 for r in segment_results if r["category_match"])
        category_accuracy = category_matches / total_segments if total_segments > 0 else 0
        
        # 数据类型的平均指标
        avg_data_type_precision = statistics.mean([r["data_type_metrics"]["precision"] for r in segment_results])
        avg_data_type_recall = statistics.mean([r["data_type_metrics"]["recall"] for r in segment_results])
        avg_data_type_f1 = statistics.mean([r["data_type_metrics"]["f1"] for r in segment_results])
        
        # 第三方的平均指标
        avg_third_party_precision = statistics.mean([r["third_party_metrics"]["precision"] for r in segment_results])
        avg_third_party_recall = statistics.mean([r["third_party_metrics"]["recall"] for r in segment_results])
        avg_third_party_f1 = statistics.mean([r["third_party_metrics"]["f1"] for r in segment_results])
        
        # 风险评分相关性
        avg_risk_difference = statistics.mean([r["risk_difference"] for r in segment_results])
        
        # 计算Pearson相关系数（风险分数）
        human_risks = [r["human_risk"] for r in segment_results]
        tool_risks = [r["tool_risk"] for r in segment_results]
        
        if len(human_risks) > 1:
            # 简单的Pearson相关系数计算
            mean_human = statistics.mean(human_risks)
            mean_tool = statistics.mean(tool_risks)
            
            numerator = sum((h - mean_human) * (t - mean_tool) for h, t in zip(human_risks, tool_risks))
            
            denom_human = sum((h - mean_human) ** 2 for h in human_risks)
            denom_tool = sum((t - mean_tool) ** 2 for t in tool_risks)
            
            if denom_human > 0 and denom_tool > 0:
                correlation = numerator / ((denom_human ** 0.5) * (denom_tool ** 0.5))
            else:
                correlation = 0.0
        else:
            correlation = 0.0
        
        return {
            "total_segments": total_segments,
            "category_accuracy": category_accuracy,
            "data_type_metrics": {
                "precision": avg_data_type_precision,
                "recall": avg_data_type_recall,
                "f1": avg_data_type_f1
            },
            "third_party_metrics": {
                "precision": avg_third_party_precision,
                "recall": avg_third_party_recall,
                "f1": avg_third_party_f1
            },
            "risk_correlation": correlation,
            "avg_risk_difference": avg_risk_difference,
            "segment_results": segment_results
        }
    
    def generate_report(self, evaluation_results: Dict, output_file: str = None):
        """
        生成评估报告
        
        参数:
            evaluation_results: evaluate_dataset的返回结果
            output_file: 输出文件路径（可选）
        """
        report_lines = []
        
        report_lines.append("=" * 70)
        report_lines.append("隐私政策分析器 - 基准测试报告")
        report_lines.append("=" * 70)
        report_lines.append("")
        
        report_lines.append("## 总体评估指标\n")
        report_lines.append(f"测试段落数: {evaluation_results['total_segments']}")
        report_lines.append("")
        
        report_lines.append("### 类别分类准确性")
        report_lines.append(f"准确率: {evaluation_results['category_accuracy']:.2%}")
        report_lines.append("")
        
        report_lines.append("### 数据类型提取")
        dt = evaluation_results['data_type_metrics']
        report_lines.append(f"精确率 (Precision): {dt['precision']:.2%}")
        report_lines.append(f"召回率 (Recall):    {dt['recall']:.2%}")
        report_lines.append(f"F1 分数:            {dt['f1']:.2%}")
        report_lines.append("")
        
        report_lines.append("### 第三方识别")
        tp = evaluation_results['third_party_metrics']
        report_lines.append(f"精确率 (Precision): {tp['precision']:.2%}")
        report_lines.append(f"召回率 (Recall):    {tp['recall']:.2%}")
        report_lines.append(f"F1 分数:            {tp['f1']:.2%}")
        report_lines.append("")
        
        report_lines.append("### 风险评分")
        report_lines.append(f"与人工标注的相关性: {evaluation_results['risk_correlation']:.3f}")
        report_lines.append(f"平均分数差异:       {evaluation_results['avg_risk_difference']:.3f}")
        report_lines.append("")
        
        report_lines.append("=" * 70)
        report_lines.append("## 详细结果\n")
        
        # 按类别一致性排序，显示不一致的案例
        mismatched = [r for r in evaluation_results['segment_results'] if not r['category_match']]
        
        if mismatched:
            report_lines.append(f"### 类别不一致的段落 ({len(mismatched)} 个):\n")
            for i, result in enumerate(mismatched[:10], 1):  # 最多显示10个
                report_lines.append(f"段落 {i}:")
                report_lines.append(f"  文本: {result['segment_text']}")
                report_lines.append(f"  人工标注: {result['human_category']}")
                report_lines.append(f"  工具分析: {result['tool_category']}")
                report_lines.append("")
        
        # 高风险分数差异的案例
        high_diff = sorted(evaluation_results['segment_results'], 
                          key=lambda x: x['risk_difference'], reverse=True)[:5]
        
        if high_diff:
            report_lines.append("### 风险评分差异最大的段落 (前5个):\n")
            for i, result in enumerate(high_diff, 1):
                report_lines.append(f"段落 {i}:")
                report_lines.append(f"  文本: {result['segment_text']}")
                report_lines.append(f"  人工评分: {result['human_risk']:.2f}")
                report_lines.append(f"  工具评分: {result['tool_risk']:.2f}")
                report_lines.append(f"  差异: {result['risk_difference']:.2f}")
                report_lines.append("")
        
        report_lines.append("=" * 70)
        report_lines.append("评估完成")
        report_lines.append("=" * 70)
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_text)
            print(f"报告已保存到: {output_file}")
        
        return report_text


def create_sample_annotations():
    """
    创建示例标注文件（用于演示）
    """
    sample_annotations = [
        {
            "text": "We collect your name, email address, and location data when you use our services.",
            "category": "limiting_collection",
            "data_types": ["name", "email", "address", "location", "data"],
            "third_parties": [],
            "user_rights": [],
            "risk_score": 0.3
        },
        {
            "text": "We share your information with advertising partners and analytics companies.",
            "category": "limiting_use",
            "data_types": ["information"],
            "third_parties": ["partners", "companies"],
            "user_rights": [],
            "risk_score": 0.6
        },
        {
            "text": "You have the right to access, correct, and delete your personal information.",
            "category": "individual_access",
            "data_types": ["information"],
            "third_parties": [],
            "user_rights": ["access", "correct", "delete"],
            "risk_score": 0.2
        },
        {
            "text": "By using our services, you consent to our collection and use of your data.",
            "category": "consent",
            "data_types": ["data"],
            "third_parties": [],
            "user_rights": [],
            "risk_score": 0.4
        },
        {
            "text": "We implement encryption and secure servers to protect your data.",
            "category": "safeguards",
            "data_types": ["data"],
            "third_parties": [],
            "user_rights": [],
            "risk_score": 0.2
        }
    ]
    
    output_file = "sample_annotations.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sample_annotations, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 示例标注文件已创建: {output_file}")
    return output_file


def main():
    """主函数 - 运行基准测试"""
    import argparse
    
    parser = argparse.ArgumentParser(description="隐私政策分析器基准测试工具")
    parser.add_argument(
        "annotations_file",
        nargs="?",
        help="人工标注JSON文件路径（如果不提供，将创建示例文件）"
    )
    parser.add_argument(
        "-o", "--output",
        default="benchmark_report.txt",
        help="输出报告文件路径"
    )
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="创建示例标注文件"
    )
    
    args = parser.parse_args()
    
    # 如果请求创建示例或没有提供文件
    if args.create_sample or not args.annotations_file:
        annotations_file = create_sample_annotations()
        if args.create_sample:
            print("\n提示: 请编辑 sample_annotations.json 添加您的人工标注")
            print("然后运行: python benchmark.py sample_annotations.json")
            return
    else:
        annotations_file = args.annotations_file
    
    # 检查文件是否存在
    if not Path(annotations_file).exists():
        print(f"❌ 错误: 文件不存在: {annotations_file}")
        print("提示: 使用 --create-sample 创建示例文件")
        return
    
    print("🔧 初始化基准测试评估器...")
    evaluator = BenchmarkEvaluator()
    
    print(f"📄 加载标注文件: {annotations_file}")
    print("🔍 正在评估...")
    
    # 运行评估
    results = evaluator.evaluate_dataset(annotations_file)
    
    print("\n" + "=" * 70)
    print("评估完成！主要指标：")
    print("=" * 70)
    print(f"类别准确率:         {results['category_accuracy']:.2%}")
    print(f"数据类型 F1:        {results['data_type_metrics']['f1']:.2%}")
    print(f"第三方识别 F1:      {results['third_party_metrics']['f1']:.2%}")
    print(f"风险评分相关性:     {results['risk_correlation']:.3f}")
    print("=" * 70)
    
    # 生成报告
    print(f"\n📝 生成详细报告...")
    evaluator.generate_report(results, args.output)
    
    print(f"\n✓ 完成！详细报告已保存到: {args.output}")


if __name__ == "__main__":
    main()




