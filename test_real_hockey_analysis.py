#!/usr/bin/env python3
"""
Test Real Hockey Analysis System

This script demonstrates the real hockey analysis system that understands
the game as hockey players and coaches do.
"""

import sys
import json
from pathlib import Path
import time

# Add src to path
sys.path.append('src')

from real_hockey_analyzer import (
    RealHockeyAnalyzer, PuckEvent, PlayerSkills, TeamSystem,
    GameState, ZoneEntry, ShotType, PlayerRole
)

def create_realistic_hockey_scenario():
    """Create a realistic hockey scenario with actual game events."""
    
    analyzer = RealHockeyAnalyzer()
    
    # Set up player skills
    player_skills = {
        "A1": PlayerSkills("A1", skating_speed=0.9, shot_accuracy=0.8, passing_accuracy=0.7, 
                          defensive_awareness=0.6, physical_presence=0.8, hockey_iq=0.9,
                          power_play_specialist=True, face_off_percentage=0.65, shooting_percentage=0.15),
        "A2": PlayerSkills("A2", skating_speed=0.7, shot_accuracy=0.6, passing_accuracy=0.8,
                          defensive_awareness=0.9, physical_presence=0.7, hockey_iq=0.8,
                          penalty_kill_specialist=True, face_off_percentage=0.55, shooting_percentage=0.12),
        "B1": PlayerSkills("B1", skating_speed=0.8, shot_accuracy=0.7, passing_accuracy=0.6,
                          defensive_awareness=0.8, physical_presence=0.9, hockey_iq=0.7,
                          face_off_percentage=0.60, shooting_percentage=0.13),
        "B2": PlayerSkills("B2", skating_speed=0.6, shot_accuracy=0.9, passing_accuracy=0.7,
                          defensive_awareness=0.7, physical_presence=0.6, hockey_iq=0.8,
                          face_off_percentage=0.50, shooting_percentage=0.18)
    }
    
    analyzer.set_player_skills(player_skills)
    
    # Set up team systems
    team_systems = {
        "Team A": TeamSystem(
            team_id="Team A",
            offensive_system="cycle",
            defensive_system="zone",
            power_play_formation="1-3-1",
            penalty_kill_formation="diamond",
            neutral_zone_strategy="trap",
            face_off_strategy="situational",
            line_change_frequency=0.8,
            shot_selection="balanced"
        ),
        "Team B": TeamSystem(
            team_id="Team B",
            offensive_system="rush",
            defensive_system="man_to_man",
            power_play_formation="2-1-2",
            penalty_kill_formation="box",
            neutral_zone_strategy="pressure",
            face_off_strategy="aggressive",
            line_change_frequency=1.0,
            shot_selection="high_volume"
        )
    }
    
    analyzer.set_team_systems(team_systems)
    
    return analyzer

def simulate_hockey_events(analyzer):
    """Simulate realistic hockey events."""
    
    current_time = 0.0
    
    # Power play sequence for Team A
    print("🏒 Simulating Power Play Sequence...")
    
    # Face-off win
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="face_off",
        player_id="A1",
        team="Team A",
        location=(150.0, 42.5),
        success=True,
        details={"face_off_zone": "offensive", "won_by": "A1"}
    ))
    current_time += 1.0
    
    # Puck movement in offensive zone
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="pass",
        player_id="A1",
        team="Team A",
        location=(150.0, 42.5),
        target_location=(140.0, 30.0),
        success=True,
        details={"pass_type": "cross_ice", "target_player": "A2"}
    ))
    current_time += 0.5
    
    # Shot from half-wall
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="shot",
        player_id="A2",
        team="Team A",
        location=(140.0, 30.0),
        success=True,
        details={"shot_type": "wrist", "distance": 45.0, "angle": 30.0}
    ))
    current_time += 1.0
    
    # Shot blocked, puck recovered
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="recovery",
        player_id="A3",
        team="Team A",
        location=(135.0, 35.0),
        success=True,
        details={"recovery_type": "rebound"}
    ))
    current_time += 0.5
    
    # Another shot
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="shot",
        player_id="A3",
        team="Team A",
        location=(135.0, 35.0),
        success=True,
        details={"shot_type": "snap", "distance": 40.0, "angle": 25.0}
    ))
    current_time += 2.0
    
    # Penalty kill sequence for Team B
    print("🏒 Simulating Penalty Kill Sequence...")
    
    # Clear attempt
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="dump",
        player_id="B1",
        team="Team B",
        location=(80.0, 42.5),
        target_location=(180.0, 42.5),
        success=True,
        details={"clear_type": "glass_and_out"}
    ))
    current_time += 1.0
    
    # Even strength sequence
    print("🏒 Simulating Even Strength Sequence...")
    
    # Zone entry
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="carry",
        player_id="A1",
        team="Team A",
        location=(100.0, 42.5),
        success=True,
        details={"entry_type": "carry", "zone": "neutral_to_offensive"}
    ))
    current_time += 1.5
    
    # Shot from slot
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="shot",
        player_id="A1",
        team="Team A",
        location=(160.0, 42.5),
        success=True,
        details={"shot_type": "wrist", "distance": 25.0, "angle": 0.0}
    ))
    current_time += 1.0
    
    # Turnover
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="turnover",
        player_id="A2",
        team="Team A",
        location=(155.0, 40.0),
        success=False,
        details={"turnover_type": "bad_pass", "intercepted_by": "B2"}
    ))
    current_time += 0.5
    
    # Counter-attack
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="rush",
        player_id="B2",
        team="Team B",
        location=(155.0, 40.0),
        success=True,
        details={"rush_type": "2_on_1", "speed": "fast"}
    ))
    current_time += 2.0
    
    # Shot on counter-attack
    analyzer.add_puck_event(PuckEvent(
        timestamp=current_time,
        event_type="shot",
        player_id="B2",
        team="Team B",
        location=(120.0, 42.5),
        success=True,
        details={"shot_type": "snap", "distance": 35.0, "angle": 15.0}
    ))
    current_time += 1.0
    
    return analyzer

def test_real_hockey_analysis():
    """Test the real hockey analysis system."""
    
    print("🏒 Real Hockey Analysis System Test")
    print("=" * 60)
    
    # Create realistic hockey scenario
    analyzer = create_realistic_hockey_scenario()
    
    # Simulate hockey events
    analyzer = simulate_hockey_events(analyzer)
    
    print(f"\n📊 Game Flow Analysis (Last 60 seconds):")
    analysis = analyzer.analyze_game_flow(time_window=60.0)
    
    # Display team metrics
    print(f"\n🏆 Team Metrics:")
    team_metrics = analysis.get("team_metrics", {})
    for team, metrics in team_metrics.items():
        print(f"  {team}:")
        print(f"    Shots: {metrics.get('shots', 0)}")
        print(f"    Goals: {metrics.get('goals', 0)}")
        print(f"    Possession Time: {metrics.get('possession_time', 0):.1f}s")
        print(f"    Zone Entries: {metrics.get('zone_entries', 0)}")
        print(f"    Turnovers: {metrics.get('turnovers', 0)}")
        print(f"    Shot Percentage: {metrics.get('shot_percentage', 0):.1%}")
        print(f"    Possession Percentage: {metrics.get('possession_percentage', 0):.1%}")
    
    # Display formation analysis
    print(f"\n🎯 Formation Analysis:")
    formation_analysis = analysis.get("formation_analysis", {})
    for team, formation_data in formation_analysis.items():
        print(f"  {team}:")
        print(f"    Offensive Sequences: {formation_data.get('offensive_sequences', 0)}")
        print(f"    Shots Generated: {formation_data.get('shots_generated', 0)}")
        print(f"    Goals Scored: {formation_data.get('goals_scored', 0)}")
        print(f"    Effectiveness: {formation_data.get('effectiveness', 0):.1%}")
        print(f"    Average Sequence Length: {formation_data.get('average_sequence_length', 0):.1f}s")
        print(f"    Formation Type: {formation_data.get('formation_type', 'unknown')}")
    
    # Display shot quality analysis
    print(f"\n🎯 Shot Quality Analysis:")
    shot_quality = analysis.get("shot_quality", {})
    print(f"  Total Shots: {shot_quality.get('total', 0)}")
    print(f"  High Quality Shots: {shot_quality.get('high_quality', 0)}")
    print(f"  Average Quality: {shot_quality.get('average_quality', 0):.2f}")
    
    for team, quality_data in shot_quality.get("by_team", {}).items():
        print(f"  {team}:")
        print(f"    Total Shots: {quality_data.get('total', 0)}")
        print(f"    Average Quality: {quality_data.get('average_quality', 0):.2f}")
    
    # Display zone entry analysis
    print(f"\n🚪 Zone Entry Analysis:")
    zone_entries = analysis.get("zone_entries", {})
    print(f"  Total Entries: {zone_entries.get('total', 0)}")
    print(f"  Successful Entries: {zone_entries.get('successful', 0)}")
    print(f"  Success Rate: {zone_entries.get('success_rate', 0):.1%}")
    
    # Display turnover analysis
    print(f"\n🔄 Turnover Analysis:")
    turnovers = analysis.get("turnover_analysis", {})
    print(f"  Total Turnovers: {turnovers.get('total', 0)}")
    print(f"  By Zone: {turnovers.get('by_zone', {})}")
    print(f"  By Team: {turnovers.get('by_team', {})}")
    
    # Display game flow analysis
    print(f"\n🌊 Game Flow Analysis:")
    game_flow = analysis.get("game_flow", {})
    print(f"  Momentum Shifts: {game_flow.get('momentum_shifts', 0)}")
    print(f"  Average Sequence Effectiveness: {game_flow.get('average_sequence_effectiveness', 0):.2f}")
    print(f"  Sequence Variability: {game_flow.get('sequence_variability', 0):.2f}")
    print(f"  Dominant Team: {game_flow.get('dominant_team', 'even')}")
    
    # Get actionable insights
    print(f"\n💡 Actionable Insights:")
    insights = analyzer.get_actionable_insights(time_window=60.0)
    
    print(f"\n🎯 Coaching Recommendations:")
    for recommendation in insights.get("coaching_recommendations", []):
        print(f"  • {recommendation}")
    
    print(f"\n👥 Player Adjustments:")
    for adjustment in insights.get("player_adjustments", []):
        print(f"  • {adjustment}")
    
    print(f"\n🎯 Tactical Opportunities:")
    for opportunity in insights.get("tactical_opportunities", []):
        print(f"  • {opportunity}")
    
    print(f"\n⚠️  Vulnerability Assessment:")
    for vulnerability in insights.get("vulnerability_assessment", []):
        print(f"  • {vulnerability}")
    
    print(f"\n📈 Momentum Analysis:")
    momentum = insights.get("momentum_analysis", {})
    print(f"  Current Momentum: {momentum.get('current_momentum', 'even')}")
    print(f"  Momentum Shifts: {momentum.get('momentum_shifts', 0)}")
    print(f"  Sequence Effectiveness: {momentum.get('sequence_effectiveness', 0):.2f}")
    print(f"  Momentum Stability: {momentum.get('momentum_stability', 0):.2f}")
    
    print(f"\n✅ Real Hockey Analysis Complete!")
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"  • Real puck events and sequences")
    print(f"  • Outcome-based effectiveness metrics")
    print(f"  • Player skills and team systems integration")
    print(f"  • Actionable coaching recommendations")
    print(f"  • Momentum and game flow analysis")
    print(f"  • Vulnerability and opportunity identification")
    print(f"  • Shot quality and zone entry analysis")
    print(f"  • Turnover and possession analysis")

if __name__ == "__main__":
    test_real_hockey_analysis()
