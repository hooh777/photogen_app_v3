"""
Batch Test Results Analyzer
Analyzes and compares results from scientific batch prompt testing.
Provides detailed insights into prompt enhancement effectiveness.
"""
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class BatchTestAnalyzer:
    """Analyzes batch test results and generates comparative insights"""
    
    def __init__(self, test_session_dir: str):
        self.test_session_dir = test_session_dir
        self.session_logs_dir = os.path.join(test_session_dir, "session_logs")
        self.analysis_results_dir = os.path.join(test_session_dir, "analysis_results")
        self.reports_dir = os.path.join(test_session_dir, "comparison_reports")
        
    def load_session_data(self) -> Dict[str, Any]:
        """Load complete session data from JSON files"""
        
        # Find session results file
        session_files = [f for f in os.listdir(self.session_logs_dir) if f.startswith("session_results_")]
        
        if not session_files:
            raise FileNotFoundError("No session results file found")
        
        session_file = session_files[0]  # Take the first/latest session file
        session_path = os.path.join(self.session_logs_dir, session_file)
        
        with open(session_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Load individual test analyses
        test_analyses = {}
        for test_case in session_data.get("test_cases", []):
            if test_case.get("success", False):
                test_id = test_case["test_id"]
                analysis_file = f"test_{test_id:03d}_analysis.json"
                analysis_path = os.path.join(self.analysis_results_dir, analysis_file)
                
                if os.path.exists(analysis_path):
                    with open(analysis_path, 'r', encoding='utf-8') as f:
                        test_analyses[test_id] = json.load(f)
        
        session_data["detailed_analyses"] = test_analyses
        return session_data
    
    def analyze_enhancement_effectiveness(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze effectiveness of different prompt enhancement levels"""
        
        enhancement_analysis = {}
        detailed_analyses = session_data.get("detailed_analyses", {})
        
        # Group results by enhancement level
        enhancement_groups = {
            "baseline": [],
            "scale_optimized": [],
            "duplication_prevented": [],
            "fully_enhanced": []
        }
        
        for test_id, analysis in detailed_analyses.items():
            test_config = analysis.get("test_case_config", {})
            enhancement_name = test_config.get("enhancement_level", {}).get("name", "unknown")
            
            if enhancement_name in enhancement_groups:
                enhancement_groups[enhancement_name].append(analysis)
        
        # Analyze each enhancement level
        for enhancement_name, analyses in enhancement_groups.items():
            if not analyses:
                continue
            
            metrics = self._calculate_enhancement_metrics(analyses)
            enhancement_analysis[enhancement_name] = {
                "test_count": len(analyses),
                "metrics": metrics,
                "description": analyses[0].get("test_case_config", {}).get("enhancement_level", {}).get("description", "")
            }
        
        return enhancement_analysis
    
    def _calculate_enhancement_metrics(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate detailed metrics for a group of analyses"""
        
        metrics = {
            "success_rate": 0,
            "satisfactory_rate": 0,
            "duplication_rate": 0,
            "scale_accuracy_rate": 0,
            "integration_quality_rate": 0,
            "average_execution_time": 0,
            "detailed_scores": {}
        }
        
        if not analyses:
            return metrics
        
        successful_analyses = [a for a in analyses if a.get("success", False)]
        total_count = len(analyses)
        successful_count = len(successful_analyses)
        
        # Basic rates
        metrics["success_rate"] = (successful_count / total_count * 100) if total_count > 0 else 0
        metrics["average_execution_time"] = sum(a.get("execution_time", 0) for a in analyses) / total_count
        
        if not successful_analyses:
            return metrics
        
        # Quality metrics from post-generation analysis
        satisfactory_count = 0
        duplication_count = 0
        good_scale_count = 0
        good_integration_count = 0
        
        for analysis in successful_analyses:
            post_analysis = analysis.get("post_analysis", {})
            
            # Overall assessment
            overall_assessment = post_analysis.get("overall_assessment", {})
            if overall_assessment.get("recommendation") == "satisfactory":
                satisfactory_count += 1
            
            # Duplication detection
            comparison_analysis = post_analysis.get("comparison_analysis", {})
            if comparison_analysis.get("duplication_detected", False):
                duplication_count += 1
            
            # Scale accuracy
            assessment_categories = overall_assessment.get("assessment_categories", {})
            if assessment_categories.get("scale_accuracy") == "good":
                good_scale_count += 1
            
            # Integration quality
            if assessment_categories.get("integration_quality") == "good":
                good_integration_count += 1
        
        # Calculate rates
        metrics["satisfactory_rate"] = (satisfactory_count / successful_count * 100)
        metrics["duplication_rate"] = (duplication_count / successful_count * 100)
        metrics["scale_accuracy_rate"] = (good_scale_count / successful_count * 100)
        metrics["integration_quality_rate"] = (good_integration_count / successful_count * 100)
        
        return metrics
    
    def analyze_prompt_categories(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance across different prompt categories"""
        
        category_analysis = {}
        detailed_analyses = session_data.get("detailed_analyses", {})
        
        # Group by prompt category
        category_groups = {}
        for test_id, analysis in detailed_analyses.items():
            test_config = analysis.get("test_case_config", {})
            category = test_config.get("prompt_config", {}).get("category", "unknown")
            
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(analysis)
        
        # Analyze each category
        for category, analyses in category_groups.items():
            metrics = self._calculate_enhancement_metrics(analyses)
            category_analysis[category] = {
                "test_count": len(analyses),
                "metrics": metrics,
                "focus": analyses[0].get("test_case_config", {}).get("prompt_config", {}).get("focus", "")
            }
        
        return category_analysis
    
    def identify_problematic_patterns(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify problematic patterns in test results"""
        
        problems = {
            "duplication_issues": [],
            "scale_problems": [],
            "integration_failures": [],
            "prompt_misinterpretations": []
        }
        
        detailed_analyses = session_data.get("detailed_analyses", {})
        
        for test_id, analysis in detailed_analyses.items():
            if not analysis.get("success", False):
                continue
            
            post_analysis = analysis.get("post_analysis", {})
            test_config = analysis.get("test_case_config", {})
            
            # Check for duplication
            comparison_analysis = post_analysis.get("comparison_analysis", {})
            if comparison_analysis.get("duplication_detected", False):
                problems["duplication_issues"].append({
                    "test_id": test_id,
                    "enhancement": test_config.get("enhancement_level", {}).get("name"),
                    "category": test_config.get("prompt_config", {}).get("category"),
                    "details": comparison_analysis.get("object_count_analysis", "")
                })
            
            # Check for scale problems
            overall_assessment = post_analysis.get("overall_assessment", {})
            key_weaknesses = overall_assessment.get("key_weaknesses", [])
            
            if any("too small" in weakness or "too large" in weakness for weakness in key_weaknesses):
                problems["scale_problems"].append({
                    "test_id": test_id,
                    "enhancement": test_config.get("enhancement_level", {}).get("name"),
                    "category": test_config.get("prompt_config", {}).get("category"),
                    "weaknesses": key_weaknesses
                })
            
            # Check for integration failures
            if "Artificial appearance" in key_weaknesses or "Lighting inconsistency" in key_weaknesses:
                problems["integration_failures"].append({
                    "test_id": test_id,
                    "enhancement": test_config.get("enhancement_level", {}).get("name"),
                    "category": test_config.get("prompt_config", {}).get("category"),
                    "weaknesses": key_weaknesses
                })
        
        return problems
    
    def generate_comparison_insights(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights comparing different approaches"""
        
        enhancement_analysis = self.analyze_enhancement_effectiveness(session_data)
        category_analysis = self.analyze_prompt_categories(session_data)
        problems = self.identify_problematic_patterns(session_data)
        
        insights = {
            "key_findings": [],
            "enhancement_recommendations": [],
            "best_performing_combinations": [],
            "areas_for_improvement": []
        }
        
        # Compare enhancement levels
        if "baseline" in enhancement_analysis and "fully_enhanced" in enhancement_analysis:
            baseline_satisfactory = enhancement_analysis["baseline"]["metrics"]["satisfactory_rate"]
            enhanced_satisfactory = enhancement_analysis["fully_enhanced"]["metrics"]["satisfactory_rate"]
            
            improvement = enhanced_satisfactory - baseline_satisfactory
            insights["key_findings"].append(
                f"Full enhancement improves satisfaction rate by {improvement:.1f}% "
                f"({baseline_satisfactory:.1f}% → {enhanced_satisfactory:.1f}%)"
            )
        
        # Duplication prevention effectiveness
        duplication_rates = {}
        for enhancement, data in enhancement_analysis.items():
            duplication_rates[enhancement] = data["metrics"]["duplication_rate"]
        
        if duplication_rates:
            best_duplication = min(duplication_rates.items(), key=lambda x: x[1])
            insights["key_findings"].append(
                f"Best duplication prevention: {best_duplication[0]} ({best_duplication[1]:.1f}% duplication rate)"
            )
        
        # Scale accuracy insights
        scale_rates = {}
        for enhancement, data in enhancement_analysis.items():
            scale_rates[enhancement] = data["metrics"]["scale_accuracy_rate"]
        
        if scale_rates:
            best_scale = max(scale_rates.items(), key=lambda x: x[1])
            insights["key_findings"].append(
                f"Best scale accuracy: {best_scale[0]} ({best_scale[1]:.1f}% good scale rate)"
            )
        
        # Generate recommendations
        if len(problems["duplication_issues"]) > 2:
            insights["areas_for_improvement"].append(
                "Duplication prevention needs strengthening - consider more explicit single-object instructions"
            )
        
        if len(problems["scale_problems"]) > 2:
            insights["areas_for_improvement"].append(
                "Scale guidance effectiveness could be improved - review vision-based analysis accuracy"
            )
        
        # Best combinations
        for category, data in category_analysis.items():
            if data["metrics"]["satisfactory_rate"] > 80:
                insights["best_performing_combinations"].append(
                    f"{category} prompts perform well (satisfaction: {data['metrics']['satisfactory_rate']:.1f}%)"
                )
        
        return insights
    
    def create_visual_analysis_report(self, session_data: Dict[str, Any]) -> str:
        """Create comprehensive visual analysis report"""
        
        enhancement_analysis = self.analyze_enhancement_effectiveness(session_data)
        category_analysis = self.analyze_prompt_categories(session_data)
        insights = self.generate_comparison_insights(session_data)
        problems = self.identify_problematic_patterns(session_data)
        
        # Create visualizations
        self._create_performance_charts(enhancement_analysis, category_analysis)
        
        # Generate detailed report
        report_content = f"""# Scientific Batch Testing Analysis Report

## Executive Summary

**Test Session**: {session_data.get('session_id', 'Unknown')}
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Tests**: {session_data.get('test_configuration', {}).get('total_test_cases', 0)}

### Key Findings
"""
        
        for finding in insights["key_findings"]:
            report_content += f"- {finding}\n"
        
        report_content += f"""
## Enhancement Level Performance Analysis

| Enhancement Level | Tests | Success Rate | Satisfaction Rate | Duplication Rate | Scale Accuracy | Integration Quality |
|------------------|-------|--------------|-------------------|------------------|----------------|-------------------|
"""
        
        for enhancement, data in enhancement_analysis.items():
            metrics = data["metrics"]
            report_content += f"| {enhancement} | {data['test_count']} | {metrics['success_rate']:.1f}% | {metrics['satisfactory_rate']:.1f}% | {metrics['duplication_rate']:.1f}% | {metrics['scale_accuracy_rate']:.1f}% | {metrics['integration_quality_rate']:.1f}% |\n"
        
        report_content += f"""
## Prompt Category Performance

| Category | Tests | Success Rate | Satisfaction Rate | Focus Area |
|----------|-------|--------------|-------------------|------------|
"""
        
        for category, data in category_analysis.items():
            metrics = data["metrics"]
            report_content += f"| {category} | {data['test_count']} | {metrics['success_rate']:.1f}% | {metrics['satisfactory_rate']:.1f}% | {data['focus']} |\n"
        
        report_content += f"""
## Problem Pattern Analysis

### Duplication Issues ({len(problems['duplication_issues'])} cases)
"""
        
        for issue in problems["duplication_issues"]:
            report_content += f"- Test {issue['test_id']} ({issue['enhancement']}): {issue['category']} - {issue['details']}\n"
        
        report_content += f"""
### Scale Problems ({len(problems['scale_problems'])} cases)
"""
        
        for issue in problems["scale_problems"]:
            report_content += f"- Test {issue['test_id']} ({issue['enhancement']}): {issue['category']} - {', '.join(issue['weaknesses'])}\n"
        
        report_content += f"""
### Integration Issues ({len(problems['integration_failures'])} cases)
"""
        
        for issue in problems["integration_failures"]:
            report_content += f"- Test {issue['test_id']} ({issue['enhancement']}): {issue['category']} - {', '.join(issue['weaknesses'])}\n"
        
        report_content += f"""
## Recommendations

### Enhancement Strategy
"""
        
        for rec in insights["enhancement_recommendations"]:
            report_content += f"- {rec}\n"
        
        report_content += f"""
### Areas for Improvement
"""
        
        for area in insights["areas_for_improvement"]:
            report_content += f"- {area}\n"
        
        report_content += f"""
### Best Performing Combinations
"""
        
        for combo in insights["best_performing_combinations"]:
            report_content += f"- {combo}\n"
        
        # Save report
        report_filename = f"visual_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(self.reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 Visual analysis report generated: {report_path}")
        return report_path
    
    def _create_performance_charts(self, enhancement_analysis: Dict[str, Any], 
                                 category_analysis: Dict[str, Any]):
        """Create performance visualization charts"""
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Batch Testing Performance Analysis', fontsize=16, fontweight='bold')
        
        # Enhancement level comparison
        enhancement_names = list(enhancement_analysis.keys())
        satisfaction_rates = [data["metrics"]["satisfactory_rate"] for data in enhancement_analysis.values()]
        duplication_rates = [data["metrics"]["duplication_rate"] for data in enhancement_analysis.values()]
        
        axes[0, 0].bar(enhancement_names, satisfaction_rates, color='skyblue', alpha=0.7)
        axes[0, 0].set_title('Satisfaction Rate by Enhancement Level')
        axes[0, 0].set_ylabel('Satisfaction Rate (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        axes[0, 1].bar(enhancement_names, duplication_rates, color='salmon', alpha=0.7)
        axes[0, 1].set_title('Duplication Rate by Enhancement Level')
        axes[0, 1].set_ylabel('Duplication Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Category performance
        category_names = list(category_analysis.keys())
        category_satisfaction = [data["metrics"]["satisfactory_rate"] for data in category_analysis.values()]
        category_scale = [data["metrics"]["scale_accuracy_rate"] for data in category_analysis.values()]
        
        axes[1, 0].bar(category_names, category_satisfaction, color='lightgreen', alpha=0.7)
        axes[1, 0].set_title('Satisfaction Rate by Prompt Category')
        axes[1, 0].set_ylabel('Satisfaction Rate (%)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        axes[1, 1].bar(category_names, category_scale, color='orange', alpha=0.7)
        axes[1, 1].set_title('Scale Accuracy by Prompt Category')
        axes[1, 1].set_ylabel('Scale Accuracy Rate (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        chart_filename = f"performance_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = os.path.join(self.reports_dir, chart_filename)
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Performance charts saved: {chart_path}")


def main():
    """Command-line interface for batch test analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze batch testing results")
    parser.add_argument("--test-session-dir", required=True, help="Path to test session directory")
    
    args = parser.parse_args()
    
    try:
        analyzer = BatchTestAnalyzer(args.test_session_dir)
        session_data = analyzer.load_session_data()
        
        print("🔍 Analyzing batch test results...")
        
        # Generate comprehensive analysis
        report_path = analyzer.create_visual_analysis_report(session_data)
        
        print(f"✅ Analysis complete!")
        print(f"📋 Report: {report_path}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")


if __name__ == "__main__":
    main()
