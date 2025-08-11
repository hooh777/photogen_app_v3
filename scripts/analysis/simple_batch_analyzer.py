"""
Simple Batch Test Results Analyzer (No Dependencies)
Analyzes batch test results without requiring matplotlib/pandas.
Provides text-based analysis and insights.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any


class SimpleBatchAnalyzer:
    """Simple analyzer for batch test results without external dependencies"""
    
    def __init__(self, test_session_dir: str):
        self.test_session_dir = test_session_dir
        self.session_logs_dir = os.path.join(test_session_dir, "session_logs")
        self.analysis_results_dir = os.path.join(test_session_dir, "analysis_results")
        self.reports_dir = os.path.join(test_session_dir, "comparison_reports")
        
    def load_and_analyze(self) -> Dict[str, Any]:
        """Load session data and perform comprehensive analysis"""
        
        print("📊 Loading batch test results...")
        
        # Load session data
        session_data = self._load_session_data()
        
        print(f"✅ Loaded {len(session_data.get('test_cases', []))} test cases")
        
        # Perform analyses
        enhancement_analysis = self._analyze_enhancement_effectiveness(session_data)
        category_analysis = self._analyze_prompt_categories(session_data)
        problems = self._identify_problems(session_data)
        insights = self._generate_insights(enhancement_analysis, category_analysis, problems)
        
        # Generate report
        report_path = self._create_detailed_report(session_data, enhancement_analysis, 
                                                 category_analysis, problems, insights)
        
        return {
            "session_data": session_data,
            "enhancement_analysis": enhancement_analysis,
            "category_analysis": category_analysis,
            "problems": problems,
            "insights": insights,
            "report_path": report_path
        }
    
    def _load_session_data(self) -> Dict[str, Any]:
        """Load complete session data"""
        
        # Find session results file
        session_files = [f for f in os.listdir(self.session_logs_dir) 
                        if f.startswith("session_results_")]
        
        if not session_files:
            raise FileNotFoundError("No session results file found")
        
        session_file = session_files[0]
        session_path = os.path.join(self.session_logs_dir, session_file)
        
        with open(session_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Load detailed analyses
        detailed_analyses = {}
        for test_case in session_data.get("test_cases", []):
            if test_case.get("success", False):
                test_id = test_case["test_id"]
                analysis_file = f"test_{test_id:03d}_analysis.json"
                analysis_path = os.path.join(self.analysis_results_dir, analysis_file)
                
                if os.path.exists(analysis_path):
                    with open(analysis_path, 'r', encoding='utf-8') as f:
                        detailed_analyses[test_id] = json.load(f)
        
        session_data["detailed_analyses"] = detailed_analyses
        return session_data
    
    def _analyze_enhancement_effectiveness(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze effectiveness of different enhancement levels"""
        
        enhancement_analysis = {}
        detailed_analyses = session_data.get("detailed_analyses", {})
        
        # Group by enhancement level
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
        
        # Calculate metrics for each group
        for enhancement_name, analyses in enhancement_groups.items():
            if not analyses:
                continue
            
            total = len(analyses)
            satisfactory = 0
            duplication_cases = 0
            good_scale = 0
            good_integration = 0
            avg_time = 0
            
            for analysis in analyses:
                avg_time += analysis.get("execution_time", 0)
                
                post_analysis = analysis.get("post_analysis", {})
                if not post_analysis:
                    continue
                
                # Check satisfaction
                overall_assessment = post_analysis.get("overall_assessment", {})
                if overall_assessment.get("recommendation") == "satisfactory":
                    satisfactory += 1
                
                # Check duplication
                comparison_analysis = post_analysis.get("comparison_analysis", {})
                if comparison_analysis.get("duplication_detected", False):
                    duplication_cases += 1
                
                # Check quality metrics
                assessment_categories = overall_assessment.get("assessment_categories", {})
                if assessment_categories.get("scale_accuracy") == "good":
                    good_scale += 1
                if assessment_categories.get("integration_quality") == "good":
                    good_integration += 1
            
            enhancement_analysis[enhancement_name] = {
                "total_tests": total,
                "satisfactory_rate": (satisfactory / total * 100) if total > 0 else 0,
                "duplication_rate": (duplication_cases / total * 100) if total > 0 else 0,
                "scale_accuracy_rate": (good_scale / total * 100) if total > 0 else 0,
                "integration_quality_rate": (good_integration / total * 100) if total > 0 else 0,
                "avg_execution_time": (avg_time / total) if total > 0 else 0,
                "description": analyses[0].get("test_case_config", {}).get("enhancement_level", {}).get("description", "")
            }
        
        return enhancement_analysis
    
    def _analyze_prompt_categories(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance by prompt category"""
        
        category_analysis = {}
        detailed_analyses = session_data.get("detailed_analyses", {})
        
        # Group by category
        category_groups = {}
        for test_id, analysis in detailed_analyses.items():
            test_config = analysis.get("test_case_config", {})
            category = test_config.get("prompt_config", {}).get("category", "unknown")
            
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(analysis)
        
        # Calculate metrics for each category
        for category, analyses in category_groups.items():
            total = len(analyses)
            satisfactory = 0
            problems = []
            
            for analysis in analyses:
                post_analysis = analysis.get("post_analysis", {})
                if not post_analysis:
                    continue
                
                overall_assessment = post_analysis.get("overall_assessment", {})
                if overall_assessment.get("recommendation") == "satisfactory":
                    satisfactory += 1
                else:
                    test_id = analysis.get("test_id")
                    enhancement = analysis.get("test_case_config", {}).get("enhancement_level", {}).get("name", "unknown")
                    problems.append(f"Test {test_id} ({enhancement})")
            
            category_analysis[category] = {
                "total_tests": total,
                "satisfactory_rate": (satisfactory / total * 100) if total > 0 else 0,
                "problematic_tests": problems,
                "focus": analyses[0].get("test_case_config", {}).get("prompt_config", {}).get("focus", "")
            }
        
        return category_analysis
    
    def _identify_problems(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify specific problems in test results"""
        
        problems = {
            "duplication_issues": [],
            "scale_problems": [],
            "integration_failures": [],
            "general_failures": []
        }
        
        detailed_analyses = session_data.get("detailed_analyses", {})
        
        for test_id, analysis in detailed_analyses.items():
            post_analysis = analysis.get("post_analysis", {})
            if not post_analysis:
                continue
            
            test_config = analysis.get("test_case_config", {})
            enhancement = test_config.get("enhancement_level", {}).get("name", "unknown")
            category = test_config.get("prompt_config", {}).get("category", "unknown")
            
            # Check duplication
            comparison_analysis = post_analysis.get("comparison_analysis", {})
            if comparison_analysis.get("duplication_detected", False):
                problems["duplication_issues"].append({
                    "test_id": test_id,
                    "enhancement": enhancement,
                    "category": category,
                    "details": comparison_analysis.get("object_count_analysis", "Multiple objects detected")
                })
            
            # Check weaknesses
            overall_assessment = post_analysis.get("overall_assessment", {})
            weaknesses = overall_assessment.get("key_weaknesses", [])
            
            for weakness in weaknesses:
                if "too small" in weakness or "too large" in weakness:
                    problems["scale_problems"].append({
                        "test_id": test_id,
                        "enhancement": enhancement,
                        "category": category,
                        "issue": weakness
                    })
                elif "artificial" in weakness.lower() or "lighting" in weakness.lower():
                    problems["integration_failures"].append({
                        "test_id": test_id,
                        "enhancement": enhancement,
                        "category": category,
                        "issue": weakness
                    })
        
        return problems
    
    def _generate_insights(self, enhancement_analysis: Dict[str, Any], 
                          category_analysis: Dict[str, Any], 
                          problems: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights from the analysis"""
        
        insights = {
            "key_findings": [],
            "recommendations": [],
            "performance_summary": {}
        }
        
        # Compare enhancement levels
        if "baseline" in enhancement_analysis and "fully_enhanced" in enhancement_analysis:
            baseline = enhancement_analysis["baseline"]
            enhanced = enhancement_analysis["fully_enhanced"]
            
            satisfaction_improvement = enhanced["satisfactory_rate"] - baseline["satisfactory_rate"]
            duplication_improvement = baseline["duplication_rate"] - enhanced["duplication_rate"]
            
            insights["key_findings"].append(
                f"Full enhancement improves satisfaction by {satisfaction_improvement:.1f}% "
                f"({baseline['satisfactory_rate']:.1f}% → {enhanced['satisfactory_rate']:.1f}%)"
            )
            
            if duplication_improvement > 0:
                insights["key_findings"].append(
                    f"Duplication prevention reduces duplication by {duplication_improvement:.1f}% "
                    f"({baseline['duplication_rate']:.1f}% → {enhanced['duplication_rate']:.1f}%)"
                )
        
        # Best performing enhancement
        best_enhancement = max(enhancement_analysis.items(), 
                             key=lambda x: x[1]["satisfactory_rate"])
        insights["performance_summary"]["best_enhancement"] = {
            "name": best_enhancement[0],
            "satisfaction_rate": best_enhancement[1]["satisfactory_rate"]
        }
        
        # Best performing category
        best_category = max(category_analysis.items(), 
                          key=lambda x: x[1]["satisfactory_rate"])
        insights["performance_summary"]["best_category"] = {
            "name": best_category[0],
            "satisfaction_rate": best_category[1]["satisfactory_rate"]
        }
        
        # Generate recommendations
        if len(problems["duplication_issues"]) > 2:
            insights["recommendations"].append(
                "HIGH PRIORITY: Strengthen duplication prevention - multiple cases detected"
            )
        
        if len(problems["scale_problems"]) > 2:
            insights["recommendations"].append(
                "MEDIUM PRIORITY: Improve scale guidance effectiveness"
            )
        
        if len(problems["integration_failures"]) > 1:
            insights["recommendations"].append(
                "MEDIUM PRIORITY: Enhance integration quality prompts"
            )
        
        # Success rate analysis
        overall_success_rate = sum(data["satisfactory_rate"] for data in enhancement_analysis.values()) / len(enhancement_analysis)
        if overall_success_rate < 70:
            insights["recommendations"].append(
                "LOW SUCCESS RATE: Review prompt enhancement strategy"
            )
        elif overall_success_rate > 85:
            insights["recommendations"].append(
                "HIGH SUCCESS RATE: Current approach is effective"
            )
        
        return insights
    
    def _create_detailed_report(self, session_data: Dict[str, Any], 
                              enhancement_analysis: Dict[str, Any],
                              category_analysis: Dict[str, Any], 
                              problems: Dict[str, Any], 
                              insights: Dict[str, Any]) -> str:
        """Create comprehensive text-based report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"detailed_analysis_report_{timestamp}.md"
        report_path = os.path.join(self.reports_dir, report_filename)
        
        report_content = f"""# Scientific Batch Testing - Detailed Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Session: {session_data.get('session_id', 'Unknown')}

## Executive Summary

**Total Tests**: {session_data.get('test_configuration', {}).get('total_test_cases', 0)}
**Success Rate**: {session_data.get('summary_statistics', {}).get('success_rate', 0):.1f}%
**Best Enhancement**: {insights['performance_summary']['best_enhancement']['name']} ({insights['performance_summary']['best_enhancement']['satisfaction_rate']:.1f}% satisfaction)
**Best Category**: {insights['performance_summary']['best_category']['name']} ({insights['performance_summary']['best_category']['satisfaction_rate']:.1f}% satisfaction)

## Key Findings

"""
        
        for finding in insights["key_findings"]:
            report_content += f"- {finding}\n"
        
        report_content += f"""
## Enhancement Level Performance

| Enhancement | Tests | Satisfaction % | Duplication % | Scale Accuracy % | Integration % | Avg Time (s) |
|------------|-------|----------------|---------------|------------------|---------------|--------------|
"""
        
        for name, data in enhancement_analysis.items():
            report_content += f"| {name} | {data['total_tests']} | {data['satisfactory_rate']:.1f} | {data['duplication_rate']:.1f} | {data['scale_accuracy_rate']:.1f} | {data['integration_quality_rate']:.1f} | {data['avg_execution_time']:.1f} |\n"
        
        report_content += f"""
### Enhancement Descriptions

"""
        
        for name, data in enhancement_analysis.items():
            report_content += f"**{name}**: {data['description']}\n\n"
        
        report_content += f"""
## Prompt Category Performance

| Category | Tests | Satisfaction % | Focus Area |
|----------|-------|----------------|------------|
"""
        
        for name, data in category_analysis.items():
            report_content += f"| {name} | {data['total_tests']} | {data['satisfactory_rate']:.1f} | {data['focus']} |\n"
        
        report_content += f"""
## Problem Analysis

### Duplication Issues ({len(problems['duplication_issues'])} cases)

"""
        
        if problems["duplication_issues"]:
            for issue in problems["duplication_issues"]:
                report_content += f"- **Test {issue['test_id']}** ({issue['enhancement']}, {issue['category']}): {issue['details']}\n"
        else:
            report_content += "✅ No duplication issues detected!\n"
        
        report_content += f"""
### Scale Problems ({len(problems['scale_problems'])} cases)

"""
        
        if problems["scale_problems"]:
            for issue in problems["scale_problems"]:
                report_content += f"- **Test {issue['test_id']}** ({issue['enhancement']}, {issue['category']}): {issue['issue']}\n"
        else:
            report_content += "✅ No scale problems detected!\n"
        
        report_content += f"""
### Integration Issues ({len(problems['integration_failures'])} cases)

"""
        
        if problems["integration_failures"]:
            for issue in problems["integration_failures"]:
                report_content += f"- **Test {issue['test_id']}** ({issue['enhancement']}, {issue['category']}): {issue['issue']}\n"
        else:
            report_content += "✅ No integration issues detected!\n"
        
        report_content += f"""
## Recommendations

"""
        
        for rec in insights["recommendations"]:
            report_content += f"- {rec}\n"
        
        report_content += f"""
## Detailed Test Results

"""
        
        for test_case in session_data.get("test_cases", []):
            if test_case.get("success", False) and str(test_case["test_id"]) in session_data.get("detailed_analyses", {}):
                test_id = test_case["test_id"]
                analysis = session_data["detailed_analyses"][str(test_id)]
                
                test_config = analysis.get("test_case_config", {})
                enhancement = test_config.get("enhancement_level", {}).get("name", "unknown")
                category = test_config.get("prompt_config", {}).get("category", "unknown")
                
                post_analysis = analysis.get("post_analysis", {})
                overall_assessment = post_analysis.get("overall_assessment", {})
                recommendation = overall_assessment.get("recommendation", "unknown")
                
                report_content += f"""### Test {test_id} - {enhancement}

- **Category**: {category}
- **Quality**: {recommendation}
- **Time**: {analysis.get('execution_time', 0):.1f}s
- **Generated Image**: `{os.path.basename(analysis.get('generated_image_path', ''))}`

"""
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Detailed analysis report saved: {report_path}")
        return report_path


def main():
    """Command-line interface for simple batch test analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple analysis of batch test results")
    parser.add_argument("--test-session-dir", required=True, help="Path to test session directory")
    
    args = parser.parse_args()
    
    try:
        analyzer = SimpleBatchAnalyzer(args.test_session_dir)
        results = analyzer.load_and_analyze()
        
        print("\n🎉 ANALYSIS COMPLETE!")
        print(f"📋 Detailed report: {results['report_path']}")
        
        # Show quick summary
        insights = results["insights"]
        print(f"\n📊 QUICK SUMMARY:")
        print(f"   Best Enhancement: {insights['performance_summary']['best_enhancement']['name']}")
        print(f"   Best Category: {insights['performance_summary']['best_category']['name']}")
        print(f"   Recommendations: {len(insights['recommendations'])}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")


if __name__ == "__main__":
    main()
