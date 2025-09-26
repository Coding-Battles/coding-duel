#!/usr/bin/env python3
"""
Analysis of missing data types in question signatures
"""
import sys
import os
import json
import glob

sys.path.append("/Users/andriysapeha/Documents/coding_duel/coding-duel")


def analyze_question_signatures():
    """Analyze all question signatures to identify data types that need handling"""

    question_data_dir = "/Users/andriysapeha/Documents/coding_duel/coding-duel/backend/data/question-data"

    # Track all unique parameter types
    param_types = set()
    return_types = set()

    # Track specific type patterns
    complex_types = []

    print("=== ANALYZING ALL QUESTION SIGNATURES ===")

    json_files = glob.glob(os.path.join(question_data_dir, "*.json"))

    for json_file in json_files[:20]:  # Analyze first 20 for now
        try:
            with open(json_file, "r") as f:
                data = json.load(f)

            question_name = os.path.basename(json_file).replace(".json", "")
            signature = data.get("signature", {})

            if signature:
                # Collect parameter types
                params = signature.get("params", [])
                for param in params:
                    param_type = param.get("type", "")
                    param_types.add(param_type)

                    if (
                        "[]" in param_type
                        or "Node" in param_type
                        or "List" in param_type
                    ):
                        complex_types.append(
                            {
                                "question": question_name,
                                "param": param.get("name"),
                                "type": param_type,
                            }
                        )

                # Collect return types
                return_type = signature.get("return_type", "")
                return_types.add(return_type)

                if (
                    "[]" in return_type
                    or "Node" in return_type
                    or "List" in return_type
                ):
                    complex_types.append(
                        {
                            "question": question_name,
                            "param": "return",
                            "type": return_type,
                        }
                    )

        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    print(f"\n=== UNIQUE PARAMETER TYPES ({len(param_types)}) ===")
    for ptype in sorted(param_types):
        print(f"  - {ptype}")

    print(f"\n=== UNIQUE RETURN TYPES ({len(return_types)}) ===")
    for rtype in sorted(return_types):
        print(f"  - {rtype}")

    print(f"\n=== COMPLEX TYPES REQUIRING SPECIAL HANDLING ===")
    handled_types = {
        "int[]",
        "int[][]",
        "string[]",
        "ListNode",
        "TreeNode",
        "int",
        "string",
        "boolean",
    }

    missing_types = set()
    for item in complex_types:
        if item["type"] not in handled_types:
            missing_types.add(item["type"])
            print(f"  - {item['question']}: {item['param']} ({item['type']}) ⚠️ MISSING")
        else:
            print(
                f"  - {item['question']}: {item['param']} ({item['type']}) ✅ HANDLED"
            )

    print(f"\n=== IMPLEMENTATION PLAN FOR MISSING TYPES ===")
    print(f"Currently handled: {len(handled_types)} types")
    print(f"Missing types that need implementation: {len(missing_types)}")

    for mtype in sorted(missing_types):
        print(f"\n🔧 {mtype}:")
        if "List<" in mtype:
            print(f"   - Java: Convert from JSONArray to List<Type>")
            print(f"   - Needs: Generic list handling with type inference")
        elif "[][]" in mtype and mtype != "int[][]":
            print(f"   - Java: Convert from JSONArray to 2D array")
            print(f"   - Needs: 2D array converter for this type")
        elif "[]" in mtype and mtype not in ["int[]", "string[]"]:
            print(f"   - Java: Convert from JSONArray to array")
            print(f"   - Needs: 1D array converter for this type")
        else:
            print(f"   - Java: Handle as custom object or complex type")
            print(f"   - Needs: Custom conversion logic")


if __name__ == "__main__":
    analyze_question_signatures()
