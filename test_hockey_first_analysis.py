#!/usr/bin/env python3
"""
Test Hockey-First Tactical Analysis System

This script demonstrates the hockey-first approach that addresses all the fundamental flaws
by understanding the actual game of hockey.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.append('src')

from hockey_first_analyzer import (
    HockeyFirstAnalyzer, HockeyRink, PlayerData, PuckData, GameContext,
    GameSituation, ZoneType, PlayerPosition, PuckStatus
)

def create_realistic_hockey_data():
    """Create realistic hockey data that reflects actual game situations."""
    
    # Create realistic rink dimensions (NHL standard)
    rink = HockeyRink(width=200.0, height=85.0)  # feet
    
    # Create realistic player data
    players = []
    
    # Team A - Power Play Unit (5 skaters + goalie)
    team_a_players = [
        PlayerData("A1", "Team A", (150.0, 42.5), (0, 0), PlayerPosition.CENTER, False, True, 45.0, 0.8, 0.9),  # High forward
        PlayerData("A2", "Team A", (140.0, 30.0), (0, 0), PlayerPosition.LEFT_WING, False, True, 45.0, 0.8, 0.8),  # Left half-wall
        PlayerData("A3", "Team A", (140.0, 55.0), (0, 0), PlayerPosition.RIGHT_WING, False, True, 45.0, 0.8, 0.8),  # Right half-wall
        PlayerData("A4", "Team A", (130.0, 42.5), (0, 0), PlayerPosition.CENTER, False, True, 45.0, 0.8, 0.7),  # Center point
        PlayerData("A5", "Team A", (120.0, 42.5), (0, 0), PlayerPosition.LEFT_DEFENSE, False, True, 45.0, 0.8, 0.8),  # Point
        PlayerData("A6", "Team A", (10.0, 42.5), (0, 0), PlayerPosition.GOALIE, True, True, 0.0, 1.0, 0.9),  # Goalie
    ]
    
    # Team B - Penalty Kill Unit (4 skaters + goalie)
    team_b_players = [
        PlayerData("B1", "Team B", (80.0, 42.5), (0, 0), PlayerPosition.CENTER, False, True, 45.0, 0.7, 0.8),  # Diamond center
        PlayerData("B2", "Team B", (70.0, 30.0), (0, 0), PlayerPosition.LEFT_DEFENSE, False, True, 45.0, 0.7, 0.8),  # Left side
        PlayerData("B3", "Team B", (70.0, 55.0), (0, 0), PlayerPosition.RIGHT_DEFENSE, False, True, 45.0, 0.7, 0.8),  # Right side
        PlayerData("B4", "Team B", (60.0, 42.5), (0, 0), PlayerPosition.LEFT_WING, False, True, 45.0, 0.7, 0.7),  # Low forward
        PlayerData("B5", "Team B", (190.0, 42.5), (0, 0), PlayerPosition.GOALIE, True, True, 0.0, 1.0, 0.9),  # Goalie
    ]
    
    players.extend(team_a_players)
    players.extend(team_b_players)
    
    # Create realistic puck data
    puck_data = PuckData(
        position=(145.0, 42.5),  # In Team A's offensive zone
        velocity=(5.0, 0.0),     # Moving toward net
        status=PuckStatus.TEAM_A_POSSESSION,
        last_touch_team="Team A",
        time_since_last_touch=0.5
    )
    
    # Create game context
    game_context = GameContext(
        period=1,
        time_remaining=1200.0,  # 20 minutes
        score=(2, 1),  # Team A leading
        game_situation=GameSituation.POWER_PLAY,
        puck_data=puck_data,
        face_off_location=None,
        power_play_teams=["Team A"],
        penalty_time_remaining={"Team B": 120.0}  # 2 minutes remaining
    )
    
    return rink, players, puck_data, game_context

def test_hockey_first_analysis():
    """Test the hockey-first analysis system."""
    
    print("🏒 Hockey-First Tactical Analysis Test")
    print("=" * 60)
    
    # Create realistic hockey data
    rink, players, puck_data, game_context = create_realistic_hockey_data()
    
    # Initialize hockey-first analyzer
    analyzer = HockeyFirstAnalyzer(rink)
    
    print(f"📏 Rink Dimensions: {rink.width}' x {rink.height}'")
    print(f"🏒 Blue Line Distance: {rink.blue_line_distance}' from each goal line")
    print(f"⏱️  Game Situation: {game_context.game_situation.value}")
    print(f"🏆 Score: Team A {game_context.score[0]} - {game_context.score[1]} Team B")
    print(f"⏰ Penalty Time Remaining: {game_context.penalty_time_remaining['Team B']} seconds")
    
    # Analyze game situation
    detected_situation = analyzer.analyze_game_situation(players, puck_data)
    print(f"🔍 Detected Game Situation: {detected_situation.value}")
    
    # Determine zones based on puck location
    print(f"\n📍 Puck Location: ({puck_data.position[0]:.1f}, {puck_data.position[1]:.1f})")
    print(f"🏃 Puck Status: {puck_data.status.value}")
    
    team_a_zone = analyzer.determine_zone_from_puck(puck_data.position, "Team A")
    team_b_zone = analyzer.determine_zone_from_puck(puck_data.position, "Team B")
    
    print(f"🎯 Team A Zone: {team_a_zone.value}")
    print(f"🎯 Team B Zone: {team_b_zone.value}")
    
    # Detect formations
    print(f"\n🔍 Formation Detection:")
    formations = analyzer.detect_hockey_formations(players, puck_data, game_context)
    
    for formation in formations:
        print(f"\n  📋 {formation.team} - {formation.name}")
        print(f"     Confidence: {formation.confidence:.2f}")
        print(f"     Game Situation: {formation.game_situation.value}")
        print(f"     Puck Zone: {formation.puck_zone.value}")
        print(f"     Tactical Purpose: {formation.tactical_purpose}")
        print(f"     Effectiveness Score: {formation.effectiveness_score:.2f}")
        
        print(f"     Player Roles:")
        for player_id, role in formation.player_roles.items():
            print(f"       {player_id}: {role.value}")
        
        print(f"     Vulnerabilities:")
        for vulnerability in formation.vulnerabilities:
            print(f"       • {vulnerability}")
        
        print(f"     Exploitation Opportunities:")
        for opportunity in formation.exploitation_opportunities:
            print(f"       • {opportunity}")
    
    # Test different game situations
    print(f"\n🔄 Testing Different Game Situations:")
    
    # Test even strength
    even_strength_context = GameContext(
        period=1,
        time_remaining=1200.0,
        score=(2, 1),
        game_situation=GameSituation.EVEN_STRENGTH,
        puck_data=puck_data,
        face_off_location=None,
        power_play_teams=[],
        penalty_time_remaining={}
    )
    
    even_strength_formations = analyzer.detect_hockey_formations(players, puck_data, even_strength_context)
    print(f"  Even Strength: {len(even_strength_formations)} formations detected")
    
    # Test penalty kill
    penalty_kill_context = GameContext(
        period=1,
        time_remaining=1200.0,
        score=(2, 1),
        game_situation=GameSituation.PENALTY_KILL,
        puck_data=puck_data,
        face_off_location=None,
        power_play_teams=[],
        penalty_time_remaining={"Team A": 120.0}
    )
    
    penalty_kill_formations = analyzer.detect_hockey_formations(players, puck_data, penalty_kill_context)
    print(f"  Penalty Kill: {len(penalty_kill_formations)} formations detected")
    
    # Test neutral zone trap
    print(f"\n🎯 Testing Neutral Zone Trap Detection:")
    
    # Create neutral zone trap scenario
    trap_players = [
        PlayerData("A1", "Team A", (100.0, 20.0), (0, 0), PlayerPosition.LEFT_WING, False, True, 45.0, 0.8, 0.8),
        PlayerData("A2", "Team A", (100.0, 65.0), (0, 0), PlayerPosition.RIGHT_WING, False, True, 45.0, 0.8, 0.8),
        PlayerData("A3", "Team A", (90.0, 42.5), (0, 0), PlayerPosition.CENTER, False, True, 45.0, 0.8, 0.8),
        PlayerData("A4", "Team A", (80.0, 30.0), (0, 0), PlayerPosition.LEFT_DEFENSE, False, True, 45.0, 0.8, 0.8),
        PlayerData("A5", "Team A", (80.0, 55.0), (0, 0), PlayerPosition.RIGHT_DEFENSE, False, True, 45.0, 0.8, 0.8),
    ]
    
    trap_puck = PuckData(
        position=(95.0, 42.5),  # In neutral zone
        velocity=(10.0, 0.0),   # Moving toward Team A's defensive zone
        status=PuckStatus.TEAM_B_POSSESSION,
        last_touch_team="Team B",
        time_since_last_touch=0.2
    )
    
    trap_context = GameContext(
        period=1,
        time_remaining=1200.0,
        score=(2, 1),
        game_situation=GameSituation.EVEN_STRENGTH,
        puck_data=trap_puck,
        face_off_location=None,
        power_play_teams=[],
        penalty_time_remaining={}
    )
    
    trap_formations = analyzer.detect_hockey_formations(trap_players, trap_puck, trap_context)
    
    for formation in trap_formations:
        print(f"  📋 {formation.team} - {formation.name}")
        print(f"     Confidence: {formation.confidence:.2f}")
        print(f"     Tactical Purpose: {formation.tactical_purpose}")
        print(f"     Effectiveness Score: {formation.effectiveness_score:.2f}")
    
    print(f"\n✅ Hockey-First Analysis Complete!")
    print(f"\n🎯 Key Improvements:")
    print(f"  • Puck location determines zones (not static divisions)")
    print(f"  • Game situation awareness (power play, penalty kill, even strength)")
    print(f"  • Proper hockey rink geometry with blue lines")
    print(f"  • Player roles based on actual hockey positions")
    print(f"  • Tactical purpose and effectiveness scoring")
    print(f"  • Vulnerability and opportunity identification")
    print(f"  • Realistic formation detection based on hockey knowledge")

if __name__ == "__main__":
    test_hockey_first_analysis()
