"""
隐私政策版本对比工具 (Privacy Policy Version Comparator)

这个工具可以智能对比两个版本的隐私政策，基于语义理解而非简单的文本diff。

功能：
1. 按PIPEDA类别对比两个版本
2. 识别新增、删除、修改的条款
3. 对比数据收集、第三方共享、用户权利等关键信息的变化
4. 分析风险变化
"""

import difflib
from typing import Dict, List, Tuple, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from analyzer import PrivacyPolicyAnalyzer
import json


class PolicyVersionComparator:
    """隐私政策版本对比器"""

    def __init__(self):
        self.analyzer = PrivacyPolicyAnalyzer()

    def analyze_policy_version(self, policy_text: str) -> Dict[str, Any]:
        """
        分析单个版本的隐私政策

        参数:
            policy_text: 隐私政策文本

        返回:
            按类别组织的分析结果
        """
        segments = self.analyzer.segment_policy(policy_text)

        # 按PIPEDA类别组织结果
        categorized_results = {category: [] for category in self.analyzer.PIPEDA_CATEGORIES.keys()}

        for segment in segments:
            result = self.analyzer.analyze_segment(segment)
            category = result["category"]
            categorized_results[category].append({
                "text": segment,
                "parameters": result["parameters"],
                "risk_score": result["risk_score"],
                "explanation": result["explanation"]
            })

        # 提取整体摘要
        summary = self._extract_summary(categorized_results)

        return {
            "categorized_results": categorized_results,
            "summary": summary
        }

    def _extract_summary(self, categorized_results: Dict) -> Dict[str, Any]:
        """提取隐私政策的关键信息摘要"""
        all_data_types = set()
        all_third_parties = set()
        all_user_rights = set()
        all_security_measures = set()
        all_purposes = set()

        for category, segments in categorized_results.items():
            for segment in segments:
                params = segment["parameters"]
                all_data_types.update(params.get("data_types", []))
                all_third_parties.update(params.get("third_parties", []))
                all_user_rights.update(params.get("user_rights", []))
                all_security_measures.update(params.get("security_measures", []))
                all_purposes.update(params.get("purposes", []))

        return {
            "data_types": sorted(list(all_data_types)),
            "third_parties": sorted(list(all_third_parties)),
            "user_rights": sorted(list(all_user_rights)),
            "security_measures": sorted(list(all_security_measures)),
            "purposes": sorted(list(all_purposes))
        }

    def compare_versions(self, old_policy: str, new_policy: str) -> Dict[str, Any]:
        """
        对比两个版本的隐私政策

        参数:
            old_policy: 旧版本政策文本
            new_policy: 新版本政策文本

        返回:
            详细的对比结果
        """
        print("📊 正在分析旧版本...")
        old_analysis = self.analyze_policy_version(old_policy)

        print("📊 正在分析新版本...")
        new_analysis = self.analyze_policy_version(new_policy)

        print("🔍 正在对比版本差异...")

        # 1. 对比摘要信息
        summary_changes = self._compare_summaries(
            old_analysis["summary"],
            new_analysis["summary"]
        )

        # 2. 对比PIPEDA类别的内容
        category_changes = self._compare_categories(
            old_analysis["categorized_results"],
            new_analysis["categorized_results"]
        )

        # 3. 对比整体风险
        risk_change = self._compare_overall_risk(
            old_analysis["categorized_results"],
            new_analysis["categorized_results"]
        )

        return {
            "summary_changes": summary_changes,
            "category_changes": category_changes,
            "risk_change": risk_change,
            "old_analysis": old_analysis,
            "new_analysis": new_analysis
        }

    def _compare_summaries(self, old_summary: Dict, new_summary: Dict) -> Dict[str, Any]:
        """对比两个版本的摘要信息"""
        changes = {}

        for key in old_summary.keys():
            old_set = set(old_summary[key])
            new_set = set(new_summary[key])

            added = new_set - old_set
            removed = old_set - new_set
            unchanged = old_set & new_set

            changes[key] = {
                "added": sorted(list(added)),
                "removed": sorted(list(removed)),
                "unchanged": sorted(list(unchanged)),
                "has_changes": len(added) > 0 or len(removed) > 0
            }

        return changes

    def _compare_categories(self, old_cats: Dict, new_cats: Dict) -> Dict[str, Any]:
        """对比各个PIPEDA类别的变化"""
        category_changes = {}

        for category in old_cats.keys():
            old_segments = old_cats[category]
            new_segments = new_cats[category]

            # 统计每个类别的段落数量变化
            old_count = len(old_segments)
            new_count = len(new_segments)

            # 使用文本相似度匹配段落
            matched, added, removed = self._match_segments(old_segments, new_segments)

            category_changes[category] = {
                "old_count": old_count,
                "new_count": new_count,
                "count_change": new_count - old_count,
                "matched_segments": len(matched),
                "added_segments": added,
                "removed_segments": removed,
                "modified_segments": [m for m in matched if m["is_modified"]]
            }

        return category_changes

    def _match_segments(self, old_segments: List[Dict], new_segments: List[Dict]) -> Tuple[List, List, List]:
        """
        使用文本相似度匹配新旧版本的段落

        返回:
            (匹配的段落, 新增的段落, 删除的段落)
        """
        matched = []
        added = []
        removed = []

        # 跟踪哪些段落已经被匹配
        old_matched = [False] * len(old_segments)
        new_matched = [False] * len(new_segments)

        # 对每个新段落找最相似的旧段落
        for new_idx, new_seg in enumerate(new_segments):
            best_match_idx = -1
            best_similarity = 0.0

            for old_idx, old_seg in enumerate(old_segments):
                if old_matched[old_idx]:
                    continue

                # 计算文本相似度
                similarity = self._calculate_similarity(
                    old_seg["text"],
                    new_seg["text"]
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_idx = old_idx

            # 如果相似度超过阈值（60%），认为是同一条款
            if best_similarity >= 0.6:
                old_matched[best_match_idx] = True
                new_matched[new_idx] = True

                old_seg = old_segments[best_match_idx]

                # 检查参数是否有变化
                param_changes = self._compare_parameters(
                    old_seg["parameters"],
                    new_seg["parameters"]
                )

                matched.append({
                    "old_text": old_seg["text"],
                    "new_text": new_seg["text"],
                    "similarity": best_similarity,
                    "is_modified": param_changes["has_changes"],
                    "parameter_changes": param_changes,
                    "old_risk": old_seg["risk_score"],
                    "new_risk": new_seg["risk_score"],
                    "risk_change": new_seg["risk_score"] - old_seg["risk_score"]
                })

        # 未匹配的新段落 = 新增
        for idx, is_matched in enumerate(new_matched):
            if not is_matched:
                added.append({
                    "text": new_segments[idx]["text"],
                    "parameters": new_segments[idx]["parameters"],
                    "risk_score": new_segments[idx]["risk_score"]
                })

        # 未匹配的旧段落 = 删除
        for idx, is_matched in enumerate(old_matched):
            if not is_matched:
                removed.append({
                    "text": old_segments[idx]["text"],
                    "parameters": old_segments[idx]["parameters"],
                    "risk_score": old_segments[idx]["risk_score"]
                })

        return matched, added, removed

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的相似度（0-1）"""
        # 使用difflib的SequenceMatcher
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _compare_parameters(self, old_params: Dict, new_params: Dict) -> Dict[str, Any]:
        """对比两个段落的参数变化"""
        changes = {}
        has_changes = False

        for key in ["data_types", "third_parties", "user_rights", "security_measures", "purposes"]:
            old_set = set(old_params.get(key, []))
            new_set = set(new_params.get(key, []))

            added = new_set - old_set
            removed = old_set - new_set

            if len(added) > 0 or len(removed) > 0:
                has_changes = True
                changes[key] = {
                    "added": list(added),
                    "removed": list(removed)
                }

        return {
            "has_changes": has_changes,
            "details": changes
        }

    def _compare_overall_risk(self, old_cats: Dict, new_cats: Dict) -> Dict[str, float]:
        """对比整体风险变化"""
        old_risks = []
        new_risks = []

        for category in old_cats.keys():
            old_risks.extend([seg["risk_score"] for seg in old_cats[category]])
            new_risks.extend([seg["risk_score"] for seg in new_cats[category]])

        old_avg = sum(old_risks) / len(old_risks) if old_risks else 0.0
        new_avg = sum(new_risks) / len(new_risks) if new_risks else 0.0

        return {
            "old_average_risk": old_avg,
            "new_average_risk": new_avg,
            "risk_change": new_avg - old_avg,
            "risk_increased": new_avg > old_avg
        }

    def generate_comparison_report(self, comparison_result: Dict, output_file: str = None) -> str:
        """
        生成版本对比报告

        参数:
            comparison_result: compare_versions的返回结果
            output_file: 输出文件路径（可选）

        返回:
            报告文本
        """
        lines = []

        lines.append("=" * 80)
        lines.append("隐私政策版本对比报告 (Privacy Policy Version Comparison Report)")
        lines.append("=" * 80)
        lines.append("")

        # 1. 整体风险变化
        lines.append("## 📊 整体风险评估 (Overall Risk Assessment)")
        lines.append("")
        risk = comparison_result["risk_change"]
        lines.append(f"旧版本平均风险: {risk['old_average_risk']:.2%}")
        lines.append(f"新版本平均风险: {risk['new_average_risk']:.2%}")
        lines.append(f"风险变化:       {risk['risk_change']:+.2%}")

        if risk["risk_increased"]:
            lines.append("⚠️  警告: 新版本的隐私风险增加了！")
        else:
            lines.append("✅ 新版本的隐私风险降低或保持不变")
        lines.append("")

        # 2. 关键信息变化摘要
        lines.append("=" * 80)
        lines.append("## 🔑 关键信息变化 (Key Changes Summary)")
        lines.append("=" * 80)
        lines.append("")

        summary_changes = comparison_result["summary_changes"]

        self._add_change_section(lines, "数据类型 (Data Types)", summary_changes["data_types"])
        self._add_change_section(lines, "第三方共享 (Third Parties)", summary_changes["third_parties"])
        self._add_change_section(lines, "用户权利 (User Rights)", summary_changes["user_rights"])
        self._add_change_section(lines, "安全措施 (Security Measures)", summary_changes["security_measures"])
        self._add_change_section(lines, "使用目的 (Purposes)", summary_changes["purposes"])

        # 3. PIPEDA类别变化
        lines.append("=" * 80)
        lines.append("## 📋 PIPEDA类别详细变化 (PIPEDA Category Changes)")
        lines.append("=" * 80)
        lines.append("")

        category_changes = comparison_result["category_changes"]

        for category, changes in category_changes.items():
            category_name = self.analyzer.PIPEDA_CATEGORIES[category]

            # 只显示有变化的类别
            if (changes["count_change"] != 0 or
                len(changes["added_segments"]) > 0 or
                len(changes["removed_segments"]) > 0 or
                len(changes["modified_segments"]) > 0):

                lines.append(f"### {category_name} ({category})")
                lines.append("")
                lines.append(f"段落数变化: {changes['old_count']} → {changes['new_count']} ({changes['count_change']:+d})")
                lines.append(f"新增段落: {len(changes['added_segments'])}")
                lines.append(f"删除段落: {len(changes['removed_segments'])}")
                lines.append(f"修改段落: {len(changes['modified_segments'])}")
                lines.append("")

                # 显示新增的段落
                if changes["added_segments"]:
                    lines.append("**新增内容:**")
                    for idx, seg in enumerate(changes["added_segments"][:3], 1):  # 最多显示3个
                        lines.append(f"{idx}. {self._truncate(seg['text'], 150)}")
                        if seg["parameters"]["data_types"]:
                            lines.append(f"   数据类型: {', '.join(seg['parameters']['data_types'])}")
                        if seg["parameters"]["third_parties"]:
                            lines.append(f"   第三方: {', '.join(seg['parameters']['third_parties'])}")
                        lines.append(f"   风险分数: {seg['risk_score']:.2%}")
                        lines.append("")

                # 显示删除的段落
                if changes["removed_segments"]:
                    lines.append("**删除内容:**")
                    for idx, seg in enumerate(changes["removed_segments"][:3], 1):
                        lines.append(f"{idx}. {self._truncate(seg['text'], 150)}")
                        lines.append("")

                # 显示修改的段落
                if changes["modified_segments"]:
                    lines.append("**修改内容:**")
                    for idx, seg in enumerate(changes["modified_segments"][:3], 1):
                        lines.append(f"{idx}. 相似度: {seg['similarity']:.0%}, 风险变化: {seg['risk_change']:+.2%}")
                        lines.append(f"   旧版: {self._truncate(seg['old_text'], 100)}")
                        lines.append(f"   新版: {self._truncate(seg['new_text'], 100)}")

                        # 显示参数变化
                        param_changes = seg["parameter_changes"]["details"]
                        if param_changes:
                            lines.append("   参数变化:")
                            for param_key, param_change in param_changes.items():
                                if param_change["added"]:
                                    lines.append(f"      {param_key} 新增: {', '.join(param_change['added'])}")
                                if param_change["removed"]:
                                    lines.append(f"      {param_key} 删除: {', '.join(param_change['removed'])}")
                        lines.append("")

                lines.append("-" * 80)
                lines.append("")

        # 4. 总结与建议
        lines.append("=" * 80)
        lines.append("## 💡 总结与建议 (Summary and Recommendations)")
        lines.append("=" * 80)
        lines.append("")

        self._add_recommendations(lines, comparison_result)

        report_text = "\n".join(lines)

        # 保存到文件
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_text)
            print(f"\n✅ 报告已保存到: {output_file}")

        return report_text

    def _add_change_section(self, lines: List[str], title: str, changes: Dict):
        """添加变化部分的格式化输出"""
        lines.append(f"### {title}")

        if not changes["has_changes"]:
            lines.append("   无变化 (No changes)")
        else:
            if changes["added"]:
                lines.append(f"   ➕ 新增: {', '.join(changes['added'])}")
            if changes["removed"]:
                lines.append(f"   ➖ 删除: {', '.join(changes['removed'])}")
        lines.append("")

    def _truncate(self, text: str, max_length: int) -> str:
        """截断长文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def _add_recommendations(self, lines: List[str], comparison_result: Dict):
        """添加建议部分"""
        summary_changes = comparison_result["summary_changes"]
        risk_change = comparison_result["risk_change"]

        recommendations = []

        # 检查风险增加
        if risk_change["risk_increased"]:
            recommendations.append("⚠️  隐私风险增加：建议审查新增的数据收集和第三方共享条款")

        # 检查新增的数据类型
        if summary_changes["data_types"]["added"]:
            recommendations.append(f"📊 新增数据收集类型: {', '.join(summary_changes['data_types']['added'])} - 确保用户知情同意")

        # 检查新增的第三方
        if summary_changes["third_parties"]["added"]:
            recommendations.append(f"🤝 新增第三方共享: {', '.join(summary_changes['third_parties']['added'])} - 确保符合数据保护法规")

        # 检查删除的用户权利
        if summary_changes["user_rights"]["removed"]:
            recommendations.append(f"❌ 删除的用户权利: {', '.join(summary_changes['user_rights']['removed'])} - 可能违反PIPEDA/GDPR要求")

        # 检查新增的用户权利
        if summary_changes["user_rights"]["added"]:
            recommendations.append(f"✅ 新增用户权利: {', '.join(summary_changes['user_rights']['added'])} - 改善了用户控制")

        # 检查新增的安全措施
        if summary_changes["security_measures"]["added"]:
            recommendations.append(f"🔒 新增安全措施: {', '.join(summary_changes['security_measures']['added'])} - 增强了数据保护")

        if not recommendations:
            recommendations.append("✅ 没有发现重大的隐私风险变化")

        for rec in recommendations:
            lines.append(f"- {rec}")

        lines.append("")


def main():
    """命令行入口"""
    import argparse
    import os
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description="隐私政策版本对比工具 - 智能对比两个版本的隐私政策变化"
    )
    parser.add_argument("old_policy", help="旧版本隐私政策文件路径")
    parser.add_argument("new_policy", help="新版本隐私政策文件路径")
    parser.add_argument("-o", "--output", help="输出报告文件路径（如果不指定，将自动生成基于输入文件名的唯一文件名）", default=None)
    parser.add_argument("--json", help="同时输出JSON格式的详细结果", action="store_true")

    args = parser.parse_args()

    # 读取文件
    print(f"📄 读取旧版本: {args.old_policy}")
    with open(args.old_policy, "r", encoding="utf-8") as f:
        old_policy_text = f.read()

    print(f"📄 读取新版本: {args.new_policy}")
    with open(args.new_policy, "r", encoding="utf-8") as f:
        new_policy_text = f.read()

    # 如果没有指定输出文件，自动生成唯一的文件名
    if args.output is None:
        # 获取输入文件的基本名称（不带扩展名）
        old_name = os.path.splitext(os.path.basename(args.old_policy))[0]
        new_name = os.path.splitext(os.path.basename(args.new_policy))[0]

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 生成输出文件名：comparison_[旧文件名]_vs_[新文件名]_[时间戳].md
        args.output = f"comparison_{old_name}_vs_{new_name}_{timestamp}.md"
        print(f"📝 自动生成输出文件名: {args.output}")

    # 创建对比器
    comparator = PolicyVersionComparator()

    # 执行对比
    print("\n" + "=" * 80)
    comparison_result = comparator.compare_versions(old_policy_text, new_policy_text)

    # 生成报告
    print("\n📝 生成对比报告...")
    report = comparator.generate_comparison_report(comparison_result, args.output)

    # 输出JSON（如果需要）
    if args.json:
        json_output = args.output.replace(".md", ".json")
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(comparison_result, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON结果已保存到: {json_output}")

    # 打印摘要
    print("\n" + "=" * 80)
    print("📊 对比摘要:")
    print("=" * 80)
    risk = comparison_result["risk_change"]
    print(f"风险变化: {risk['old_average_risk']:.2%} → {risk['new_average_risk']:.2%} ({risk['risk_change']:+.2%})")

    summary = comparison_result["summary_changes"]
    print(f"\n新增数据类型: {len(summary['data_types']['added'])}")
    print(f"新增第三方: {len(summary['third_parties']['added'])}")
    print(f"新增用户权利: {len(summary['user_rights']['added'])}")
    print(f"删除的用户权利: {len(summary['user_rights']['removed'])}")

    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
