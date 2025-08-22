#!/usr/bin/env python3
"""
Basic Example: Hockey Tactical Analysis

This example demonstrates how to use the hockey tactical analysis system
to analyze formations and tactics from player tracking data.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tactical_analyzer import TacticalAnalyzer

def main():
    """Run basic tactical analysis example."""
    
    # Example 1: Basic Formation Analysis
    print("=" * 60)
    print("EXAMPLE 1: BASIC FORMATION ANALYSIS")
    print("=" * 60)
    
    # Initialize analyzer with your tracking data
    # Replace this path with your actual tracking data file
    input_file = "data/player_tracking.json"  # or .csv file
    
    try:
        analyzer = TacticalAnalyzer(
            input_path=input_file,
            output_dir="results/basic_analysis"
        )
        
        # Analyze formations
        formation_results = analyzer.analyze_formations(
            min_frames=5,      # Minimum frames to confirm formation
            min_confidence=0.6  # Minimum confidence threshold
        )
        
        # Print results
        if formation_results["detected_formations"]:
            print(f"\nDetected {len(formation_results['detected_formations'])} formations:")
            
            for formation in formation_results["detected_formations"]:
                print(f"\n  Formation: {formation['formation']}")
                print(f"    Duration: {formation['duration_frames']} frames")
                print(f"    Confidence: {formation['avg_confidence']:.2f}")
                print(f"    Time: {formation['start_time']:.1f}s - {formation['end_time']:.1f}s")
            
            # Print statistics
            stats = formation_results["formation_statistics"]
            print(f"\nFormation Statistics:")
            print(f"  Total formations: {stats['total_formations']}")
            print(f"  Most common: {stats['most_common']}")
            
            # Print transitions
            transitions = formation_results["transition_analysis"]
            if transitions["transitions"]:
                print(f"\nFormation Transitions:")
                print(f"  Total transitions: {transitions['total_transitions']}")
                if transitions["most_common"]:
                    most_common = transitions["most_common"]
                    print(f"  Most common: {most_common[0]} ({most_common[1]} times)")
        else:
            print("No formations detected with current parameters.")
            print("Try adjusting min_frames or min_confidence parameters.")
    
    except FileNotFoundError:
        print(f"Example data file not found: {input_file}")
        print("Please update the input_file path to point to your tracking data.")
        return
    except Exception as e:
        print(f"Analysis failed: {e}")
        return
    
    # Example 2: Zone Analysis
    print("\n" + "=" * 60)
    print("EXAMPLE 2: ZONE ANALYSIS")
    print("=" * 60)
    
    try:
        # Analyze zone distribution and tactics
        zone_results = analyzer.analyze_zones()
        
        print("\nZone Distribution Analysis:")
        for zone_name, zone_data in zone_results["zone_distribution"].items():
            print(f"\n  {zone_name.title()} Zone:")
            print(f"    Average players: {zone_data['avg_players']:.1f}")
            print(f"    Max players: {zone_data['max_players']}")
            print(f"    Formation consistency: {zone_data['formation_consistency']:.2f}")
        
        # Check for specific tactics
        if zone_results["trap_analysis"]["trap_detected"]:
            trap = zone_results["trap_analysis"]
            print(f"\nNeutral Zone Trap Detected:")
            print(f"  Usage: {trap['percentage_of_game']:.1f}% of game time")
            print(f"  Average confidence: {trap['avg_confidence']:.2f}")
        
        if zone_results["forecheck_analysis"]["forecheck_detected"]:
            forecheck = zone_results["forecheck_analysis"]
            print(f"\nForechecking Analysis:")
            print(f"  Total instances: {forecheck['total_instances']}")
            print(f"  Average pressure: {forecheck['avg_pressure']:.2f}")
        
        if zone_results["defensive_analysis"]["defensive_coverage"]:
            defensive = zone_results["defensive_analysis"]
            print(f"\nDefensive Coverage:")
            print(f"  Total instances: {defensive['total_instances']}")
            print(f"  Average coverage: {defensive['avg_coverage']:.2f}")
    
    except Exception as e:
        print(f"Zone analysis failed: {e}")
        return
    
    # Example 3: Complete Tactical Analysis
    print("\n" + "=" * 60)
    print("EXAMPLE 3: COMPLETE TACTICAL ANALYSIS")
    print("=" * 60)
    
    try:
        # Generate comprehensive tactical insights
        tactical_insights = analyzer.generate_tactical_insights()
        
        print("\nTactical Summary:")
        print(f"  {tactical_insights['summary']}")
        
        print("\nStrategic Recommendations:")
        for category, recommendation in tactical_insights["strategic_recommendations"].items():
            print(f"  • {category.replace('_', ' ').title()}: {recommendation}")
        
        # Print detailed tactical patterns
        patterns = tactical_insights["tactical_patterns"]
        
        if "formation_effectiveness" in patterns:
            print("\nFormation Effectiveness:")
            for formation, effectiveness in patterns["formation_effectiveness"].items():
                print(f"  • {formation}: {effectiveness['effectiveness_level']} "
                      f"(confidence: {effectiveness['consistency']:.2f})")
        
        if "zone_tactics" in patterns:
            zone_tactics = patterns["zone_tactics"]
            if "offensive_tactics" in zone_tactics:
                offensive = zone_tactics["offensive_tactics"]
                print(f"\nOffensive Tactics:")
                print(f"  • Forechecking style: {offensive['forechecking_style']}")
                print(f"  • Pressure consistency: {offensive['pressure_consistency']:.2f}")
            
            if "defensive_tactics" in zone_tactics:
                defensive = zone_tactics["defensive_tactics"]
                print(f"\nDefensive Tactics:")
                print(f"  • Coverage style: {defensive['coverage_style']}")
                print(f"  • Formation preference: {defensive['collapse_patterns']['formation_preference']}")
    
    except Exception as e:
        print(f"Tactical insights generation failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"Detailed results saved to: {analyzer.output_dir}")
    print("\nYou can also run the command-line interface:")
    print(f"  python src/analyze_formations.py {input_file} --complete")

if __name__ == "__main__":
    main()
