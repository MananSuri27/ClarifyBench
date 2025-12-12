#!/usr/bin/env python
"""
Script to calculate metrics for simulation results, comparing against ground truth data.
"""

import os
import sys
import glob
import json
import argparse
import logging
from typing import Dict, List, Any, Optional

# Add the project root to the Python path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the evaluation module from simulation
from simulation.evaluation import SimulationEvaluator, SimulationVisualizer
from utils.json_utils import load_json, save_json
from utils.logger import setup_logger

def get_matching_ground_truth_file(result_file: str, gt_dir: str) -> Optional[str]:
    """
    Find the matching ground truth file for a result file.
    
    Args:
        result_file: Path to the result file
        gt_dir: Directory containing ground truth files
        
    Returns:
        Path to the matching ground truth file, or None if not found
    """
    # Extract the base result filename without _RESULT suffix
    result_filename = os.path.basename(result_file)
    if "_RESULT" in result_filename:
        gt_filename = result_filename.replace("_RESULT", "")
    else:
        # If the filename doesn't follow the expected pattern, try to match by removing extension
        base_name = os.path.splitext(result_filename)[0]
        gt_filename = f"{base_name}.json"
    
    # Check if the ground truth file exists
    gt_file_path = os.path.join(gt_dir, gt_filename)
    if os.path.exists(gt_file_path):
        return gt_file_path
    
    # Try to find a file with a similar name
    for gt_file in glob.glob(os.path.join(gt_dir, "*.json")):
        if os.path.basename(gt_file).startswith(base_name.replace("_RESULT", "")):
            return gt_file
    
    return None

def calculate_metrics(result_file: str, gt_file: str) -> Dict[str, Any]:
    """
    Calculate metrics for a single result file against ground truth.
    
    Args:
        result_file: Path to the result file
        gt_file: Path to the ground truth file
        
    Returns:
        Updated result data with metrics
    """
    # Load result and ground truth data
    result_data = load_json(result_file)
    gt_data = load_json(gt_file)
    
    # Initialize the evaluator
    evaluator = SimulationEvaluator()
    
    # Calculate metrics
    metrics = evaluator.evaluate_simulation(gt_data, result_data)
    
    # Update the result data with metrics
    result_data["evaluation"] = metrics
    
    return result_data

def update_result_file(result_file: str, updated_data: Dict[str, Any]) -> bool:
    """
    Update a result file with new data.
    
    Args:
        result_file: Path to the result file
        updated_data: Updated data to save
        
    Returns:
        True if successful, False otherwise
    """
    return save_json(updated_data, result_file, pretty=True)

def print_metrics_summary(all_metrics: List[Dict[str, Any]], visualizer: SimulationVisualizer) -> None:
    """
    Print a summary of metrics for all evaluated files.
    
    Args:
        all_metrics: List of evaluation metrics
        visualizer: SimulationVisualizer instance for formatting
    """
    # Calculate summary statistics
    total_files = len(all_metrics)
    if total_files == 0:
        print("No metrics to summarize.")
        return
    
    # Success metrics
    successful_simulations = sum(1 for m in all_metrics if m.get("success", False))
    
    # Correctness metrics - only for final calls
    avg_correctness_tool_match = sum(
        m.get("correctness", {}).get("tool_match_rate", 0.0)
        for m in all_metrics
    ) / total_files
    avg_correctness_param_match = sum(
        m.get("correctness", {}).get("param_match_rate", 0.0)
        for m in all_metrics
    ) / total_files
    exact_match_count = sum(
        1 for m in all_metrics
        if m.get("correctness", {}).get("exact_match", False)
    )
    
    # Coverage metrics - only for final calls
    avg_coverage_rate = sum(
        m.get("coverage", {}).get("coverage_rate", 0.0)
        for m in all_metrics
    ) / total_files
    coverage_success_count = sum(
        1 for m in all_metrics
        if m.get("coverage", {}).get("coverage_success", False)
    )
    
    # Execution metrics
    avg_execution_rate = sum(m.get("execution", {}).get("execution_rate", 0.0) for m in all_metrics) / total_files
    avg_success_rate = sum(m.get("execution", {}).get("success_rate", 0.0) for m in all_metrics) / total_files
    execution_success_count = sum(1 for m in all_metrics if m.get("execution", {}).get("execution_success", False))
    
    # Conversation metrics
    avg_turns = sum(m.get("conversation", {}).get("total_turns", 0) for m in all_metrics) / total_files
    avg_questions = sum(m.get("conversation", {}).get("clarification_questions", 0) for m in all_metrics) / total_files
    avg_user_turns = sum(m.get("conversation", {}).get("user_turns", 0) for m in all_metrics) / total_files
    avg_agent_turns = sum(m.get("conversation", {}).get("agent_turns", 0) for m in all_metrics) / total_files
    
    # Print summary
    print("\n" + "="*80)
    print("METRICS SUMMARY")
    print("="*80)
    print(f"Total files evaluated: {total_files}")
    print(f"Successful simulations: {successful_simulations} ({successful_simulations/total_files*100:.2f}%)")

    print(f"\nCorrectness Metrics:")
    print(f"  Average tool match rate: {avg_correctness_tool_match:.4f}")
    print(f"  Average param match rate: {avg_correctness_param_match:.4f}")
    print(f"  Exact match count: {exact_match_count} ({exact_match_count/total_files*100:.2f}%)")

    print(f"\nCoverage Metrics:")
    print(f"  Average coverage rate: {avg_coverage_rate:.4f}")
    print(f"  Coverage success count: {coverage_success_count} ({coverage_success_count/total_files*100:.2f}%)")

    print(f"\nExecution Metrics:")
    print(f"  Average execution rate: {avg_execution_rate:.4f}")
    print(f"  Average success rate: {avg_success_rate:.4f}")
    print(f"  Execution success count: {execution_success_count} ({execution_success_count/total_files*100:.2f}%)")

    print(f"\nConversation Metrics:")
    print(f"  Average conversation turns: {avg_turns:.2f}")
    print(f"  Average clarification questions: {avg_questions:.2f}")
    print(f"  Average user turns: {avg_user_turns:.2f}")
    print(f"  Average agent turns: {avg_agent_turns:.2f}")

    print("="*80)
    
    # Save comprehensive summary to file
    summary = {
        "total_files": total_files,
        "success_metrics": {
            "successful": successful_simulations,
            "success_rate": successful_simulations / total_files
        },
        "correctness_metrics": {
            "average_tool_match_rate": avg_correctness_tool_match,
            "average_param_match_rate": avg_correctness_param_match,
            "exact_match_count": exact_match_count,
            "exact_match_rate": exact_match_count / total_files
        },
        "coverage_metrics": {
            "average_coverage_rate": avg_coverage_rate,
            "coverage_success_count": coverage_success_count,
            "coverage_success_rate": coverage_success_count / total_files
        },
        "execution_metrics": {
            "average_execution_rate": avg_execution_rate,
            "average_success_rate": avg_success_rate,
            "execution_success_count": execution_success_count,
            "execution_success_rate": execution_success_count / total_files
        },
        "conversation_metrics": {
            "average_turns": avg_turns,
            "average_clarification_questions": avg_questions,
            "average_user_turns": avg_user_turns,
            "average_agent_turns": avg_agent_turns
        }
    }
    
    return summary

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Calculate metrics for simulation results")
    parser.add_argument("--results_dir", type=str, required=True, help="Directory containing result files")
    parser.add_argument("--gt_dir", type=str, required=True, help="Directory containing ground truth files")
    parser.add_argument("--output", type=str, default="metrics_summary.json", help="Output file for metrics summary")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    args = parser.parse_args()

    # Setup logging
    log_file = "metrics_calculation.log"
    logger = setup_logger(log_file=log_file)
    
    # Find all result files
    result_files = glob.glob(os.path.join(args.results_dir, "*.json"))
    
    if not result_files:
        logger.error(f"No result files found in {args.results_dir}")
        print(f"No result files found in {args.results_dir}")
        return
    
    # Process each result file
    all_metrics = []
    processed_files = 0
    
    for result_file in result_files:
        # Skip summary files
        if os.path.basename(result_file) in ["summary.json", "metrics_summary.json"]:
            continue

        logger.info(f"Processing {result_file}")

        # Check if file has error key
        try:
            result_data = load_json(result_file)
            if "error" in result_data:
                logger.info(f"Skipping {result_file}: contains 'error' key")
                print(f"SKIPPING: {os.path.basename(result_file)} contains 'error' key")
                continue
        except Exception as e:
            logger.error(f"Error loading {result_file} for error check: {e}")
            continue

        # Find matching ground truth file
        gt_file = get_matching_ground_truth_file(result_file, args.gt_dir)

        if not gt_file:
            logger.warning(f"No matching ground truth file found for {result_file}")
            print(f"WARNING: No matching ground truth file found for {os.path.basename(result_file)}")
            continue

        try:
            # Calculate metrics
            updated_data = calculate_metrics(result_file, gt_file)

            # Save metrics to separate file instead of overwriting
            metrics_file = result_file.replace('.json', '_metrics.json')
            if save_json({"file": result_file, "metrics": updated_data.get("evaluation", {})}, metrics_file, pretty=True):
                logger.info(f"Saved metrics to {metrics_file}")
                processed_files += 1

                # Store metrics for summary
                if "evaluation" in updated_data:
                    all_metrics.append(updated_data["evaluation"])

                # Print metrics if verbose
                if args.verbose:
                    print("\n" + "="*80)
                    print(f"METRICS FOR {os.path.basename(result_file)}")
            else:
                logger.error(f"Failed to save metrics to {metrics_file}")
                
        except Exception as e:
            logger.exception(f"Error processing {result_file}")
            print(f"ERROR: Failed to process {os.path.basename(result_file)}: {str(e)}")
    
    # Save and print summary
    if all_metrics:
        summary = print_metrics_summary(all_metrics, None)
        if save_json(summary, args.output, pretty=True):
            print(f"Comprehensive summary saved to {args.output}")
        print(f"Processed {processed_files} out of {len(result_files)} result files")
    else:
        print("No metrics were calculated. Check the log file for details.")

    print(f"Log file: {log_file}")

if __name__ == "__main__":
    main()