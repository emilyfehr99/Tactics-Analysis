#!/usr/bin/env python3
"""
Enhanced Hockey Tactical Analysis Demo

This script demonstrates the new enhanced analysis capabilities that include:
- Detailed weakness detection within formations
- Coverage gap analysis
- Formation quality assessment
- Behavioral pattern recognition
- Specific tactical recommendations

Example: python3 enhanced_analysis_demo.py your_tracking_data.json
"""

import sys
import json
from pathlib import Path
from src.tactical_analyzer import TacticalAnalyzer

def main():
    """Run enhanced tactical analysis with weakness detection."""
    
    if len(sys.argv) != 2:
        print("Usage: python3 enhanced_analysis_demo.py <tracking_data_file>")
        print("Example: python3 enhanced_analysis_demo.py tracking_data.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    print("🏒 ENHANCED HOCKEY TACTICAL ANALYSIS WITH WEAKNESS DETECTION")
    print("=" * 70)
    print(f"Analyzing: {input_file}")
    print()
    
    try:
        # Initialize enhanced analyzer
        analyzer = TacticalAnalyzer(input_file)
        
        print("🔍 Running enhanced analysis with weakness detection...")
        print("This will analyze:")
        print("  • Formation quality and effectiveness")
        print("  • Coverage gaps and positioning issues")
        print("  • Formation breakdowns and consistency")
        print("  • Behavioral patterns and vulnerabilities")
        print("  • Specific tactical recommendations")
        print()
        
        # Run enhanced analysis
        results = analyzer.run_enhanced_analysis_with_weaknesses()
        
        # Display results
        display_enhanced_results(results)
        
        print("\n✅ Enhanced analysis completed successfully!")
        print(f"📁 Results saved to: {analyzer.output_dir}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)

def display_enhanced_results(results):
    """Display enhanced analysis results in a user-friendly format."""
    
    print("📊 ENHANCED ANALYSIS RESULTS")
    print("-" * 40)
    
    # Display weakness summary
    weakness_summary = results["enhanced_tactical_insights"]["weakness_analysis"]
    print(f"🔴 Total Weaknesses Detected: {weakness_summary['total_weaknesses']}")
    print(f"🚨 Critical Issues: {weakness_summary['critical_issues']}")
    print(f"⚠️  Formation Breakdowns: {weakness_summary['formation_breakdowns']}")
    print()
    
    # Display quality summary
    quality_summary = results["enhanced_tactical_insights"]["quality_summary"]
    if "average_quality_score" in quality_summary:
        print("📈 FORMATION QUALITY SUMMARY")
        print("-" * 30)
        print(f"Average Quality Score: {quality_summary['average_quality_score']:.3f}")
        print(f"Excellent Formations: {quality_summary['excellent_formations']}")
        print(f"Good Formations: {quality_summary['good_formations']}")
        print(f"Fair Formations: {quality_summary['fair_formations']}")
        print(f"Poor Formations: {quality_summary['poor_formations']}")
        print()
    
    # Display formation-specific insights
    formation_insights = results["enhanced_tactical_insights"]["formation_insights"]
    if formation_insights:
        print("🏗️  FORMATION-SPECIFIC INSIGHTS")
        print("-" * 35)
        
        for formation_name, insights in formation_insights.items():
            print(f"\n{formation_name.upper()}:")
            print(f"  Quality Score: {insights['quality_score']:.3f}")
            print(f"  Coverage Quality: {insights['coverage_quality']}")
            print(f"  Improvement Priority: {insights['improvement_priority'].upper()}")
            
            if insights['key_weaknesses']:
                print("  Key Weaknesses:")
                for weakness in insights['key_weaknesses'][:2]:  # Show top 2
                    print(f"    • {weakness}")
            
            if insights['key_strengths']:
                print("  Key Strengths:")
                for strength in insights['key_strengths'][:2]:  # Show top 2
                    print(f"    • {strength}")
    
    # Display tactical priorities
    tactical_priorities = results["enhanced_tactical_insights"]["tactical_priorities"]
    if tactical_priorities:
        print(f"\n🎯 TACTICAL PRIORITIES")
        print("-" * 25)
        for priority in tactical_priorities:
            print(f"• {priority}")
    
    # Display strategic recommendations
    strategic_recommendations = results["enhanced_tactical_insights"]["strategic_recommendations"]
    if strategic_recommendations:
        print(f"\n💡 STRATEGIC RECOMMENDATIONS")
        print("-" * 35)
        for category, recommendation in strategic_recommendations.items():
            print(f"{category.replace('_', ' ').title()}: {recommendation}")

def display_detailed_weaknesses(results):
    """Display detailed weakness information."""
    
    enhanced_formations = results["enhanced_formation_analysis"]["detected_formations"]
    
    print("\n🔍 DETAILED WEAKNESS ANALYSIS")
    print("-" * 35)
    
    for formation in enhanced_formations:
        formation_name = formation["formation"]
        quality = formation["quality_analysis"]
        
        if quality["weaknesses"]:
            print(f"\n{formation_name.upper()} - Weaknesses:")
            for i, weakness in enumerate(quality["weaknesses"], 1):
                severity_emoji = "🔴" if weakness["severity"] > 0.7 else "🟡" if weakness["severity"] > 0.4 else "🟢"
                print(f"  {i}. {severity_emoji} {weakness['description']}")
                print(f"     Severity: {weakness['severity']:.2f}")
                print(f"     Zone: {weakness['zone']}")
                if weakness["recommendations"]:
                    print(f"     Recommendations:")
                    for rec in weakness["recommendations"][:2]:  # Show top 2
                        print(f"       • {rec}")
                print()

if __name__ == "__main__":
    main()
