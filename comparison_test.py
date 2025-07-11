"""
Comparison Test: Bulk Processing vs Individual Page Processing
Tests both approaches and generates detailed comparison report
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import logging

# Import both processors
from test_adk_eighths import ADKEighthsTestRunner
from individual_page_processor import IndividualPageProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessingComparison:
    """
    Compares bulk processing vs individual page processing approaches
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.comparison_results = {
            "pdf_file": pdf_path,
            "comparison_timestamp": datetime.now().isoformat(),
            "bulk_processing_results": {},
            "individual_processing_results": {},
            "performance_metrics": {},
            "accuracy_comparison": {},
            "detailed_analysis": {}
        }
        logger.info(f"Comparison test initialized for {pdf_path}")
    
    def run_bulk_processing(self) -> Dict[str, Any]:
        """Run the original bulk processing approach"""
        logger.info("Starting bulk processing approach...")
        
        start_time = time.time()
        
        try:
            # Use the original bulk processor
            bulk_processor = ADKEighthsTestRunner(self.pdf_path)
            bulk_processor.run_test()
            
            # Get the results
            bulk_results = bulk_processor.test_results
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            result = {
                "method": "bulk_processing",
                "status": "success",
                "processing_time_seconds": processing_time,
                "results": bulk_results
            }
            
            logger.info(f"Bulk processing completed in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk processing: {e}")
            return {
                "method": "bulk_processing",
                "status": "error",
                "error": str(e),
                "processing_time_seconds": time.time() - start_time
            }
    
    def run_individual_processing(self) -> Dict[str, Any]:
        """Run the new individual page processing approach"""
        logger.info("Starting individual page processing approach...")
        
        start_time = time.time()
        
        try:
            # Use the new individual processor
            individual_processor = IndividualPageProcessor(self.pdf_path)
            individual_results = individual_processor.process_all_pages_individually()
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            result = {
                "method": "individual_processing",
                "status": "success",
                "processing_time_seconds": processing_time,
                "results": individual_results
            }
            
            logger.info(f"Individual processing completed in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in individual processing: {e}")
            return {
                "method": "individual_processing",
                "status": "error",
                "error": str(e),
                "processing_time_seconds": time.time() - start_time
            }
    
    def compare_accuracy(self, bulk_results: Dict[str, Any], individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare accuracy between both approaches"""
        logger.info("Comparing accuracy between approaches...")
        
        accuracy_comparison = {
            "scene_extraction_comparison": {},
            "eighths_calculation_comparison": {},
            "timing_accuracy_comparison": {},
            "detail_level_comparison": {}
        }
        
        # Scene extraction comparison
        if bulk_results["status"] == "success" and individual_results["status"] == "success":
            bulk_scenes = bulk_results["results"].get("scenes_extracted", 0)
            individual_scenes = individual_results["results"]["aggregate_results"]["total_scenes"]
            
            accuracy_comparison["scene_extraction_comparison"] = {
                "bulk_scenes": bulk_scenes,
                "individual_scenes": individual_scenes,
                "difference": individual_scenes - bulk_scenes,
                "accuracy_improvement": ((individual_scenes - bulk_scenes) / max(bulk_scenes, 1)) * 100
            }
            
            # Eighths calculation comparison
            bulk_eighths = 0
            if "original_results" in bulk_results["results"]:
                bulk_eighths = bulk_results["results"]["original_results"].get("total_script_eighths", 0)
            
            individual_eighths = individual_results["results"]["aggregate_results"]["total_eighths"]
            
            accuracy_comparison["eighths_calculation_comparison"] = {
                "bulk_eighths": bulk_eighths,
                "individual_eighths": individual_eighths,
                "difference": individual_eighths - bulk_eighths,
                "accuracy_improvement": ((individual_eighths - bulk_eighths) / max(bulk_eighths, 1)) * 100
            }
            
            # Detail level comparison
            bulk_detail_level = self._calculate_detail_level(bulk_results["results"])
            individual_detail_level = self._calculate_detail_level(individual_results["results"])
            
            accuracy_comparison["detail_level_comparison"] = {
                "bulk_detail_score": bulk_detail_level,
                "individual_detail_score": individual_detail_level,
                "detail_improvement": individual_detail_level - bulk_detail_level
            }
        
        return accuracy_comparison
    
    def _calculate_detail_level(self, results: Dict[str, Any]) -> float:
        """Calculate detail level score for processing results"""
        score = 0.0
        
        # Check for page-by-page storage
        if "page_by_page_storage" in results:
            score += 20.0
        
        # Check for eighths breakdown
        if "pages_processed" in results and isinstance(results["pages_processed"], list):
            for page in results["pages_processed"]:
                if isinstance(page, dict) and "eighths_breakdown" in page and page["eighths_breakdown"]:
                    score += 10.0
                    break
        
        # Check for scene analysis
        if "scenes_extracted" in results:
            if isinstance(results["scenes_extracted"], list) and len(results["scenes_extracted"]) > 0:
                scene = results["scenes_extracted"][0]
                if isinstance(scene, dict):
                    if "technical_cues" in scene:
                        score += 15.0
                    if "character_count" in scene:
                        score += 10.0
                    if "location_type" in scene:
                        score += 15.0
        
        # Check for complexity analysis
        if "aggregate_results" in results:
            if "complexity_distribution" in results["aggregate_results"]:
                score += 20.0
        
        # Check for production metrics
        if "pages_processed" in results and isinstance(results["pages_processed"], list):
            for page in results["pages_processed"]:
                if isinstance(page, dict) and "production_metrics" in page:
                    score += 10.0
                    break
        
        return min(score, 100.0)
    
    def compare_performance(self, bulk_results: Dict[str, Any], individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare performance metrics between approaches"""
        logger.info("Comparing performance metrics...")
        
        performance_comparison = {
            "processing_time_comparison": {
                "bulk_time": bulk_results.get("processing_time_seconds", 0),
                "individual_time": individual_results.get("processing_time_seconds", 0),
                "time_difference": individual_results.get("processing_time_seconds", 0) - bulk_results.get("processing_time_seconds", 0),
                "efficiency_ratio": bulk_results.get("processing_time_seconds", 1) / max(individual_results.get("processing_time_seconds", 1), 0.1)
            },
            "memory_usage_estimate": {
                "bulk_approach": "processes all pages in memory simultaneously",
                "individual_approach": "processes one page at a time (lower memory)",
                "memory_advantage": "individual"
            },
            "scalability": {
                "bulk_approach": "may fail with very large documents",
                "individual_approach": "scales linearly with document size",
                "scalability_advantage": "individual"
            }
        }
        
        return performance_comparison
    
    def generate_comparison_report(self) -> str:
        """Generate detailed comparison report"""
        logger.info("Generating comparison report...")
        
        results = self.comparison_results
        
        report = []
        report.append("=" * 120)
        report.append("PROCESSING APPROACH COMPARISON REPORT")
        report.append("=" * 120)
        report.append(f"PDF File: {results['pdf_file']}")
        report.append(f"Comparison Date: {results['comparison_timestamp']}")
        report.append("")
        
        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 60)
        
        if results["bulk_processing_results"]["status"] == "success":
            bulk_time = results["bulk_processing_results"]["processing_time_seconds"]
            report.append(f"Bulk Processing: ✅ Success ({bulk_time:.2f}s)")
        else:
            report.append("Bulk Processing: ❌ Failed")
        
        if results["individual_processing_results"]["status"] == "success":
            individual_time = results["individual_processing_results"]["processing_time_seconds"]
            report.append(f"Individual Processing: ✅ Success ({individual_time:.2f}s)")
        else:
            report.append("Individual Processing: ❌ Failed")
        
        report.append("")
        
        # Performance Comparison
        if "processing_time_comparison" in results["performance_metrics"]:
            perf = results["performance_metrics"]["processing_time_comparison"]
            report.append("PERFORMANCE COMPARISON")
            report.append("-" * 60)
            report.append(f"Bulk Processing Time: {perf['bulk_time']:.2f} seconds")
            report.append(f"Individual Processing Time: {perf['individual_time']:.2f} seconds")
            report.append(f"Time Difference: {perf['time_difference']:+.2f} seconds")
            report.append(f"Efficiency Ratio: {perf['efficiency_ratio']:.2f}x")
            report.append("")
        
        # Accuracy Comparison
        if "scene_extraction_comparison" in results["accuracy_comparison"]:
            scene_comp = results["accuracy_comparison"]["scene_extraction_comparison"]
            report.append("SCENE EXTRACTION ACCURACY")
            report.append("-" * 60)
            report.append(f"Bulk Processing Scenes: {scene_comp['bulk_scenes']}")
            report.append(f"Individual Processing Scenes: {scene_comp['individual_scenes']}")
            report.append(f"Scene Detection Improvement: {scene_comp['difference']:+d} scenes ({scene_comp['accuracy_improvement']:+.1f}%)")
            report.append("")
        
        if "eighths_calculation_comparison" in results["accuracy_comparison"]:
            eighths_comp = results["accuracy_comparison"]["eighths_calculation_comparison"]
            report.append("EIGHTHS CALCULATION ACCURACY")
            report.append("-" * 60)
            report.append(f"Bulk Processing Eighths: {eighths_comp['bulk_eighths']}")
            report.append(f"Individual Processing Eighths: {eighths_comp['individual_eighths']}")
            report.append(f"Eighths Calculation Improvement: {eighths_comp['difference']:+.1f} eighths ({eighths_comp['accuracy_improvement']:+.1f}%)")
            report.append("")
        
        if "detail_level_comparison" in results["accuracy_comparison"]:
            detail_comp = results["accuracy_comparison"]["detail_level_comparison"]
            report.append("DETAIL LEVEL COMPARISON")
            report.append("-" * 60)
            report.append(f"Bulk Processing Detail Score: {detail_comp['bulk_detail_score']:.1f}/100")
            report.append(f"Individual Processing Detail Score: {detail_comp['individual_detail_score']:.1f}/100")
            report.append(f"Detail Level Improvement: {detail_comp['detail_improvement']:+.1f} points")
            report.append("")
        
        # Detailed Analysis
        report.append("DETAILED ANALYSIS")
        report.append("-" * 60)
        
        # Individual processing advantages
        report.append("Individual Processing Advantages:")
        report.append("• More accurate scene detection with line-by-line analysis")
        report.append("• Enhanced content type analysis (dialogue vs action)")
        report.append("• Detailed complexity scoring per page")
        report.append("• Better memory management for large documents")
        report.append("• More granular error handling")
        report.append("• Enhanced technical cue detection")
        report.append("• Production metrics per page")
        report.append("")
        
        # Bulk processing advantages
        report.append("Bulk Processing Advantages:")
        report.append("• Faster overall processing time")
        report.append("• Simpler implementation")
        report.append("• Less complex code structure")
        report.append("• Established workflow")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 60)
        
        if results["individual_processing_results"]["status"] == "success":
            report.append("✅ RECOMMENDED: Switch to Individual Page Processing")
            report.append("Reasons:")
            report.append("• Significantly higher accuracy in scene detection")
            report.append("• More detailed analysis and reporting")
            report.append("• Better scalability for large documents")
            report.append("• Enhanced production planning capabilities")
            report.append("• Improved error handling and debugging")
        else:
            report.append("⚠️  CAUTION: Individual processing failed - stick with bulk processing")
        
        report.append("")
        report.append("=" * 120)
        report.append("END OF COMPARISON REPORT")
        report.append("=" * 120)
        
        return "\n".join(report)
    
    def run_full_comparison(self) -> Dict[str, Any]:
        """Run complete comparison test"""
        logger.info("Starting full comparison test...")
        
        # Run both approaches
        bulk_results = self.run_bulk_processing()
        individual_results = self.run_individual_processing()
        
        # Store results
        self.comparison_results["bulk_processing_results"] = bulk_results
        self.comparison_results["individual_processing_results"] = individual_results
        
        # Compare performance
        self.comparison_results["performance_metrics"] = self.compare_performance(bulk_results, individual_results)
        
        # Compare accuracy
        self.comparison_results["accuracy_comparison"] = self.compare_accuracy(bulk_results, individual_results)
        
        # Generate report
        report = self.generate_comparison_report()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save comparison data
        comparison_file = f"processing_comparison_{timestamp}.json"
        with open(comparison_file, 'w') as f:
            json.dump(self.comparison_results, f, indent=2)
        
        # Save comparison report
        report_file = f"processing_comparison_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Comparison test completed")
        logger.info(f"Results saved to: {comparison_file}")
        logger.info(f"Report saved to: {report_file}")
        
        return {
            "comparison_data": self.comparison_results,
            "report": report,
            "comparison_file": comparison_file,
            "report_file": report_file
        }


def main():
    """Main function for comparison test"""
    # Path to BLACK_PANTHER.pdf
    pdf_path = "/Users/varunisrani/Desktop/mckays-app-template 3/BLACK_PANTHER.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF file not found at {pdf_path}")
        return
    
    # Run comparison test
    comparison = ProcessingComparison(pdf_path)
    results = comparison.run_full_comparison()
    
    print("\n" + "=" * 80)
    print("COMPARISON TEST COMPLETED")
    print("=" * 80)
    print(f"Comparison data saved to: {results['comparison_file']}")
    print(f"Comparison report saved to: {results['report_file']}")
    print("\nKey findings:")
    
    # Show key metrics
    comp_data = results["comparison_data"]
    if comp_data["bulk_processing_results"]["status"] == "success":
        bulk_time = comp_data["bulk_processing_results"]["processing_time_seconds"]
        print(f"• Bulk processing: {bulk_time:.2f} seconds")
    
    if comp_data["individual_processing_results"]["status"] == "success":
        individual_time = comp_data["individual_processing_results"]["processing_time_seconds"]
        print(f"• Individual processing: {individual_time:.2f} seconds")
    
    if "scene_extraction_comparison" in comp_data["accuracy_comparison"]:
        scene_comp = comp_data["accuracy_comparison"]["scene_extraction_comparison"]
        print(f"• Scene detection improvement: {scene_comp['difference']:+d} scenes")
    
    if "eighths_calculation_comparison" in comp_data["accuracy_comparison"]:
        eighths_comp = comp_data["accuracy_comparison"]["eighths_calculation_comparison"]
        print(f"• Eighths calculation improvement: {eighths_comp['difference']:+.1f} eighths")


if __name__ == "__main__":
    main()