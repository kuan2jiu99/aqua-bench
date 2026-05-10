"""Dual Accuracy: standard + conditional (given Solvable correct)."""

import re
import json
import argparse
from typing import Dict, Optional


def extract_mcq_answer(model_response: str, options: Dict[str, str]) -> Optional[str]:
    response = model_response.strip().lower()
    max_letter = chr(ord('a') + len(options) - 1)

    pattern_choice = re.search(rf'\(?([a-{max_letter}])\)?\b', response)
    if pattern_choice:
        choice_letter = pattern_choice.group(1).upper()
        if choice_letter in options:
            return choice_letter

    for key, text in options.items():
        if text.strip().lower() in response:
            return key

    return None


def build_options(item: dict) -> tuple[Dict[str, str], str]:
    opts = item["options"]
    options_dict = {chr(65 + i): opts[i] for i in range(len(opts))}
    answer = item["answer"]
    ground_truth = next((k for k, v in options_dict.items() if v == answer), None)
    return options_dict, ground_truth


def is_correct(item: dict) -> bool:
    options_dict, gt = build_options(item)
    pred = extract_mcq_answer(item["response"], options_dict)
    return pred == gt


def evaluate(results_path: str):
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) % 4 == 0, f"Expected multiple of 4, got {len(data)}"

    correct = {"Solvable": [], "AAD": [], "IASD": [], "IAQD": []}
    cond_correct = {"AAD": [], "IASD": [], "IAQD": []}

    for i in range(0, len(data), 4):
        results = {
            "Solvable": is_correct(data[i]),
            "AAD": is_correct(data[i + 1]),
            "IASD": is_correct(data[i + 2]),
            "IAQD": is_correct(data[i + 3]),
        }

        for key in correct:
            correct[key].append(int(results[key]))

        if results["Solvable"]:
            for key in cond_correct:
                cond_correct[key].append(int(results[key]))

    print("=== Standard Accuracy ===")
    for key, vals in correct.items():
        print(f"  {key}: {sum(vals) / len(vals):.3f} ({sum(vals)}/{len(vals)})")

    print("=== Conditional Accuracy (given Solvable correct) ===")
    if cond_correct["AAD"]:
        for key, vals in cond_correct.items():
            print(f"  {key}: {sum(vals) / len(vals):.3f} ({sum(vals)}/{len(vals)})")
    else:
        print("  No solvable questions answered correctly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AQUA-Bench dual accuracy evaluation")
    parser.add_argument("-r", "--results_path", type=str, help="Path to model results JSON")
    args = parser.parse_args()
    evaluate(args.results_path)