#!/usr/bin/env python3
"""
Privacy Policy Analyzer - Command Line Tool

Usage:
    python analyze_policy.py <input_file> [options]

Examples:
    python analyze_policy.py example_policy.txt
    python analyze_policy.py policy.txt --output report.md --format markdown
"""

import sys
import argparse
import json
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from analyzer import PrivacyPolicyAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="Privacy Policy Analyzer - Based on PIPEDA Framework and NLP Methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s privacy_policy.txt
  %(prog)s policy.txt -o report.md -f markdown
  %(prog)s policy.txt -o report.json -f json
  %(prog)s policy.txt --model en_core_web_trf

For more information, see README.md
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the privacy policy text file"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output report file path (default: input_filename_analysis.md)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["markdown", "text", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "-m", "--model",
        default="en_core_web_sm",
        help="spaCy model name (default: en_core_web_sm). "
             "Recommended: en_core_web_trf (most accurate) or en_core_web_lg (balanced)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output"
    )
    
    parser.add_argument(
        "--show-summary-only",
        action="store_true",
        help="Only display summary, don't generate full report"
    )
    
    parser.add_argument(
        "--no-enhanced-semantic",
        action="store_true",
        help="Disable enhanced semantic analysis (use basic analysis only)"
    )

    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Enable LLM-assisted extraction (requires API key, improves accuracy but costs money)"
    )

    parser.add_argument(
        "--llm-provider",
        default="deepseek",
        choices=["deepseek", "openai", "claude"],
        help="LLM provider (default: deepseek)"
    )

    parser.add_argument(
        "--llm-api-key",
        help="LLM API key (can also be set via environment variable)"
    )

    args = parser.parse_args()
    
    # Check input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: File not found: {args.input_file}")
        sys.exit(1)
    
    # Determine output file path
    if args.output:
        output_path = Path(args.output)
    else:
        ext = ".md" if args.format == "markdown" else ".txt" if args.format == "text" else ".json"
        output_path = input_path.with_name(f"{input_path.stem}_analysis{ext}")
    
    # Read input file
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            policy_text = f.read()
    except Exception as e:
        print(f"❌ Error: Unable to read file: {e}")
        sys.exit(1)
    
    if args.verbose:
        print(f"📄 Reading file: {input_path}")
        print(f"   File size: {len(policy_text)} characters")
        print(f"📊 Using model: {args.model}")
        if args.model == "en_core_web_sm":
            print("   ⚠️  Note: Small model detected. For better semantic analysis,")
            print("      consider using: --model en_core_web_trf (best) or --model en_core_web_lg")
        print(f"⚙️  Output format: {args.format}")
        print()
    
    # Initialize analyzer
    print("🔧 Initializing analyzer...")
    if args.verbose:
        semantic_mode = "basic" if args.no_enhanced_semantic else "enhanced"
        print(f"   Semantic analysis mode: {semantic_mode}")
    try:
        analyzer = PrivacyPolicyAnalyzer(
            model_name=args.model,
            use_enhanced_semantic=not args.no_enhanced_semantic,
            use_llm=args.use_llm,
            llm_provider=args.llm_provider,
            llm_api_key=args.llm_api_key
        )
    except Exception as e:
        print(f"❌ Error: Unable to initialize analyzer: {e}")
        print(f"\nTip: Make sure you have installed the spaCy model:")
        print(f"    python -m spacy download {args.model}")
        sys.exit(1)
    
    # Perform analysis
    print("🔍 Analyzing privacy policy...")
    try:
        results = analyzer.analyze(policy_text)
    except Exception as e:
        print(f"❌ Error: Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Display summary
    summary = results["summary"]
    print("\n" + "="*60)
    print("📋 Analysis Summary")
    print("="*60)
    print(f"Segments analyzed:   {summary['total_segments']}")
    print(f"Average risk score:  {summary['average_risk_score']:.2f}")
    print(f"Data types found:    {len(summary['total_data_types'])}")
    print(f"Third parties:       {len(summary['total_third_parties'])}")
    print()
    
    print("PIPEDA Category Distribution:")
    for category, count in sorted(summary['category_distribution'].items(), 
                                  key=lambda x: x[1], reverse=True):
        print(f"  • {category}: {count} segments")
    print()
    
    # Data collection by activity summary
    if summary.get('data_collection_by_activity'):
        print("📊 Data Collection by Activity:")
        print("   What data is collected on what activities, based on their privacy policy")
        print()
        data_collection = summary['data_collection_by_activity']
        for activity in sorted(data_collection.keys())[:10]:  # Show top 10 activities
            activity_info = data_collection[activity]
            data_types = activity_info.get('data_types', [])
            description = activity_info.get('description', activity)
            segment_count = activity_info.get('segment_count', 0)
            
            if data_types:
                data_list = ", ".join(data_types[:5])  # Show first 5 data types
                more_count = len(data_types) - 5
                print(f"  • {description}")
                print(f"    Segments: {segment_count} | Data: {data_list}", end="")
                if more_count > 0:
                    print(f" ... (+{more_count} more)")
                else:
                    print()
        if len(data_collection) > 10:
            print(f"  ... and {len(data_collection) - 10} more activities")
        print()
    
    # High risk warning
    high_risk_count = sum(1 for s in results['segment_analyses'] if s['risk_score'] > 0.5)
    if high_risk_count > 0:
        print(f"⚠️  Found {high_risk_count} high-risk segments")
        print()
    
    if args.show_summary_only:
        print("✓ Complete (summary only)")
        return
    
    # Generate report
    print(f"📝 Generating {args.format} format report...")
    
    if args.format == "json":
        # JSON format
        report_data = {
            "input_file": str(input_path),
            "analysis_results": results
        }
        output_content = json.dumps(report_data, ensure_ascii=False, indent=2)
    else:
        # Markdown or Text format
        output_content = analyzer.generate_report(results, output_format=args.format)
    
    # Save report
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f"✓ Report saved to: {output_path}")
    except Exception as e:
        print(f"❌ Error: Unable to save report: {e}")
        sys.exit(1)
    
    # If verbose mode, show additional information
    if args.verbose:
        print()
        print("Data types collected (top 10):")
        for dt in sorted(summary['total_data_types'])[:10]:
            print(f"  • {dt}")
        
        if summary['total_third_parties']:
            print()
            print("Third parties involved (top 10):")
            for tp in sorted(summary['total_third_parties'])[:10]:
                print(f"  • {tp}")
    
    print()
    print("="*60)
    print("✓ Analysis complete!")
    print("="*60)


if __name__ == "__main__":
    main()






