#!/usr/bin/env python3
"""
Test Enhanced Formation Detection System

This script demonstrates the enhanced formation detection that accounts for:
- Both teams playing simultaneously
- Period changes and attacking direction changes
- Advanced spatial analysis beyond simple zone counting
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.append('src')

from enhanced_formation_detector import EnhancedFormationDetector, GameState

def main():
    """Test the enhanced formation detection system."""
    
    print("🏒 Enhanced Hockey Formation Detection Test")
    print("=" * 60)
    
    # Initialize enhanced detector
    detector = EnhancedFormationDetector(rink_dimensions=(1400, 600))
    
    # Test with real tracking data
    test_file = "/Users/emilyfehr8/CascadeProjects/Computer-Vision-for-Hockey/output/tracking_results_20250910_092038/player_detection_data_20250910_092735.json"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📁 Loading test data: {Path(test_file).name}")
    
    # Load tracking data
    with open(test_file, 'r') as f:
        tracking_data = json.load(f)
    
    print(f"📊 Loaded {len(tracking_data['frames'])} frames of data")
    
    # Test period changes
    print("\n🔄 Testing Period Changes:")
    print("Period 1 - Team A attacks left-to-right:")
    detector.current_period = 1
    team_a_zones = detector.get_team_zones("Team A", 1)
    print(f"  Offensive zone: {team_a_zones.offensive_zone}")
    print(f"  Attacking direction: {team_a_zones.attacking_direction}")
    
    print("\nPeriod 2 - Team A attacks right-to-left:")
    detector.current_period = 2
    team_a_zones = detector.get_team_zones("Team A", 2)
    print(f"  Offensive zone: {team_a_zones.offensive_zone}")
    print(f"  Attacking direction: {team_a_zones.attacking_direction}")
    
    # Test formation detection for both teams
    print("\n🔍 Testing Formation Detection for Both Teams:")
    
    # Analyze first few frames
    test_frames = tracking_data['frames'][:10]
    
    for frame_idx, frame_data in enumerate(test_frames):
        if 'players' not in frame_data:
            continue
        
        print(f"\nFrame {frame_idx}:")
        
        # Analyze each team separately
        for team in ["Team A", "Team B"]:
            team_players = [p for p in frame_data['players'] if p.get('team', '').startswith(team)]
            
            if len(team_players) >= 5:
                print(f"  {team}: {len(team_players)} players")
                
                # Analyze spatial relationships
                player_analyses = detector.analyze_player_spatial_relationships(team_players, team)
                
                # Show zone distribution
                zone_counts = {}
                for pa in player_analyses:
                    zone_counts[pa.zone] = zone_counts.get(pa.zone, 0) + 1
                
                print(f"    Zone distribution: {zone_counts}")
                
                # Show isolation scores
                avg_isolation = sum(pa.isolation_score for pa in player_analyses) / len(player_analyses)
                print(f"    Average isolation score: {avg_isolation:.2f}")
                
                # Detect formation
                formation = detector.detect_formation_with_spatial_analysis(team_players, team)
                if formation:
                    print(f"    Detected formation: {formation.formation_name}")
                    print(f"    Confidence: {formation.confidence:.2f}")
                    print(f"    Tactical effectiveness: {formation.tactical_effectiveness:.2f}")
                    print(f"    Spatial clusters: {len(formation.spatial_clusters)}")
                    print(f"    Coverage gaps: {len(formation.coverage_gaps)}")
                else:
                    print(f"    No clear formation detected")
    
    # Test comprehensive analysis
    print("\n📊 Comprehensive Formation Analysis:")
    results = detector.detect_formations_both_teams(test_frames, min_frames=2)
    
    for team, formations in results.items():
        print(f"\n{team}:")
        if formations:
            for formation in formations:
                print(f"  Formation: {formation.formation_name}")
                print(f"  Confidence: {formation.confidence:.2f}")
                print(f"  Effectiveness: {formation.tactical_effectiveness:.2f}")
                print(f"  Player roles: {len(formation.player_roles)}")
                print(f"  Clusters: {len(formation.spatial_clusters)}")
                print(f"  Gaps: {len(formation.coverage_gaps)}")
        else:
            print("  No formations detected")
    
    print("\n✅ Enhanced formation detection test complete!")
    print("\nKey Improvements:")
    print("  • Both teams analyzed simultaneously")
    print("  • Period-based attacking direction changes")
    print("  • Advanced spatial analysis beyond zone counting")
    print("  • Player role assignment and clustering")
    print("  • Coverage gap and pressure point identification")
    print("  • Tactical effectiveness scoring")

if __name__ == "__main__":
    main()
