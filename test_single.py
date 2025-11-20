#!/usr/bin/env python3
"""
Test script to run orchestrator on a single repository
"""

import os
from orchestrator import run_skill_on_repo

def main():
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("export ANTHROPIC_API_KEY='your-api-key-here'")
        return 1

    # Test on the orchestrator repo itself
    test_repo = "/Users/mpaz/workspace/orchestrator"

    print(f"\nTesting orchestrator on: {test_repo}")
    print("This will generate a PROJECT.md for the orchestrator itself\n")

    result = run_skill_on_repo(test_repo)

    if result["status"] == "success":
        print(f"\nSuccess! Generated PROJECT.md")
        print(f"Location: {result['output_file']}")
        return 0
    else:
        print(f"\nFailed: {result.get('message', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    exit(main())
