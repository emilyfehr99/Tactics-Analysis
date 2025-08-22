#!/usr/bin/env python3
"""
Quick Analysis Script for Any Hockey Tracking Data

Just run this script with your data file and it will analyze everything automatically!
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append('src')

from tactical_analyzer import TacticalAnalyzer

def main():
    """Analyze any hockey tracking data file."""
    
    print("🏒 Hockey Tactical Analysis - Quick Analysis Tool")
    print("=" * 60)
    
    # Check if file was provided
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_any_data.py [your_tracking_data.json]")
        print("\nExample:")
        print("  python3 analyze_any_data.py my_game_data.json")
        print("  python3 analyze_any_data.py ../Computer-Vision-for-Hockey/output/tracking_results_*/player_detection_data_*.json")
        print("\nThe script will:")
        print("  1. Load your tracking data")
        print("  2. Analyze formations and tactics")
        print("  3. Generate insights and recommendations")
        print("  4. Save results to results/ directory")
        return
    
    # Get input file
    input_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        print("\nMake sure the file path is correct.")
        print("You can use wildcards like:")
        print("  python3 analyze_any_data.py ../Computer-Vision-for-Hockey/output/*/player_detection_data_*.json")
        return
    
    print(f"📁 Analyzing: {input_file}")
    print("⏳ This may take a few seconds...")
    
    try:
        # Create output directory with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"results/analysis_{timestamp}"
        
        # Initialize analyzer
        print("\n🔍 Initializing tactical analyzer...")
        analyzer = TacticalAnalyzer(
            input_path=input_file,
            output_dir=output_dir
        )
        
        # Run complete analysis
        print("📊 Running complete tactical analysis...")
        results = analyzer.run_complete_analysis()
        
        print("\n🎉 ANALYSIS COMPLETE!")
        print("=" * 60)
        
        # Print summary
        if results["formation_analysis"]["detected_formations"]:
            formations = results["formation_analysis"]["detected_formations"]
            print(f"\n📋 Detected {len(formations)} formations:")
            
            for formation in formations:
                print(f"  • {formation['formation']} (confidence: {formation['avg_confidence']:.2f})")
                print(f"    Duration: {formation['duration_frames']} frames")
                print(f"    Time: {formation['start_time']:.1f}s - {formation['end_time']:.1f}s")
        
        # Print tactical summary
        if "summary" in results["tactical_insights"]:
            print(f"\n🏒 Tactical Summary:")
            print(f"  {results['tactical_insights']['summary']}")
        
        # Print key recommendations
        if "strategic_recommendations" in results["tactical_insights"]:
            print(f"\n💡 Key Recommendations:")
            for category, recommendation in results["tactical_insights"]["strategic_recommendations"].items():
                print(f"  • {category.replace('_', ' ').title()}: {recommendation}")
        
        print(f"\n📁 Detailed results saved to: {output_dir}")
        print(f"📊 Files generated:")
        
        # List generated files
        for file_path in Path(output_dir).glob("*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size / 1024  # KB
                print(f"  • {file_path.name} ({file_size:.1f} KB)")
        
        print("\n🎯 Next Steps:")
        print("  1. Review the tactical report")
        print("  2. Analyze formation effectiveness")
        print("  3. Use insights for coaching decisions")
        print("  4. Compare with other games/teams")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("  • Check that your file is valid JSON")
        print("  • Ensure the file has the expected structure")
        print("  • Try running with --verbose for more details")
        print("  • Check the README.md for file format requirements")
        
        # Print detailed error for debugging
        import traceback
        print(f"\n📋 Detailed error:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
