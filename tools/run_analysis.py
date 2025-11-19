import argparse
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import run_pipeline, run_comparison

def main():
    parser = argparse.ArgumentParser(description="Privacy Policy Analysis Pipeline")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a single policy")
    analyze_parser.add_argument("--url", required=True, help="URL of the policy")
    analyze_parser.add_argument("--product", required=True, help="Product name (e.g., meta_glasses)")
    analyze_parser.add_argument("--id", required=True, help="Unique ID for this version (e.g., meta_2024)")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two analyzed policies")
    compare_parser.add_argument("--id1", required=True, help="ID of the first policy")
    compare_parser.add_argument("--id2", required=True, help="ID of the second policy")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        run_pipeline(args.url, args.product, args.id)
    elif args.command == "compare":
        run_comparison(args.id1, args.id2)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
