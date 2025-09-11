"""
REAL Hockey Analysis System - No BS Version
==========================================

This system analyzes REAL hockey data without making up fake insights.
Based on actual Roboflow computer vision data.
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RealPlayer:
    """Real player data from Roboflow."""
    player_id: str
    position: Tuple[float, float]
    speed: float
    team: str
    team_confidence: float
    roboflow_class: str
    is_goalkeeper: bool = False


@dataclass
class RealPuck:
    """Real puck data from Roboflow."""
    position: Tuple[float, float]
    speed: float
    roboflow_class: str
    is_on_stick: bool = False


@dataclass
class RealFrame:
    """Real frame data from Roboflow."""
    frame_id: int
    timestamp: float
    players: List[RealPlayer]
    puck: Optional[RealPuck] = None
    stick_blades: List[RealPuck] = None


class RealHockeyAnalyzer:
    """
    REAL Hockey Analysis System - No BS Version
    
    This system analyzes actual hockey data without making up fake insights.
    """
    
    def __init__(self):
        self.frames: List[RealFrame] = []
        self.rink_length = 200  # Standard hockey rink length in feet
        self.rink_width = 85    # Standard hockey rink width in feet
        
        # Real rink dimensions (based on NHL standards)
        self.blue_line_distance = 60  # Distance from goal line to blue line
        self.goal_line_distance = 11  # Distance from end boards to goal line
        self.net_width = 6  # Goal width in feet
        self.net_height = 4  # Goal height in feet
        
        # Real hockey metrics
        self.analysis_results = {
            "player_movement": {},
            "puck_movement": {},
            "team_possession": {},
            "spatial_analysis": {},
            "real_insights": {}
        }
    
    def load_roboflow_data(self, file_path: str) -> bool:
        """Load real Roboflow data."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.frames = []
            
            for frame_data in data.get('frames', []):
                frame_id = frame_data.get('frame_id', 0)
                timestamp = frame_data.get('timestamp', 0.0)
                
                # Process real players
                players = []
                puck = None
                stick_blades = []
                
                for player_data in frame_data.get('players', []):
                    roboflow_class = player_data.get('roboflow_class', '')
                    
                    if roboflow_class in ['home', 'away', 'player']:
                        # Real player
                        rink_pos = player_data.get('rink_position', {})
                        position = (rink_pos.get('x', 0), rink_pos.get('y', 0))
                        
                        player = RealPlayer(
                            player_id=player_data.get('player_id', ''),
                            position=position,
                            speed=player_data.get('speed', 0.0),
                            team=player_data.get('team', 'Unknown'),
                            team_confidence=player_data.get('team_confidence', 0.0),
                            roboflow_class=roboflow_class,
                            is_goalkeeper=roboflow_class == 'goalkeeper'
                        )
                        players.append(player)
                    
                    elif roboflow_class == 'puck':
                        # Real puck
                        rink_pos = player_data.get('rink_position', {})
                        position = (rink_pos.get('x', 0), rink_pos.get('y', 0))
                        
                        puck = RealPuck(
                            position=position,
                            speed=player_data.get('speed', 0.0),
                            roboflow_class=roboflow_class,
                            is_on_stick=False
                        )
                    
                    elif roboflow_class == 'stick_blade':
                        # Stick blade (puck on stick)
                        rink_pos = player_data.get('rink_position', {})
                        position = (rink_pos.get('x', 0), rink_pos.get('y', 0))
                        
                        stick_blade = RealPuck(
                            position=position,
                            speed=player_data.get('speed', 0.0),
                            roboflow_class=roboflow_class,
                            is_on_stick=True
                        )
                        stick_blades.append(stick_blade)
                
                frame = RealFrame(
                    frame_id=frame_id,
                    timestamp=timestamp,
                    players=players,
                    puck=puck,
                    stick_blades=stick_blades
                )
                self.frames.append(frame)
            
            logger.info(f"Loaded {len(self.frames)} frames of real hockey data")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Roboflow data: {e}")
            return False
    
    def analyze_real_player_movement(self) -> Dict[str, Any]:
        """Analyze REAL player movement patterns."""
        if not self.frames:
            return {"error": "No frames loaded"}
        
        player_tracking = defaultdict(list)
        
        # Track each player across frames
        for frame in self.frames:
            for player in frame.players:
                player_tracking[player.player_id].append({
                    'frame_id': frame.frame_id,
                    'timestamp': frame.timestamp,
                    'position': player.position,
                    'speed': player.speed,
                    'team': player.team,
                    'team_confidence': player.team_confidence
                })
        
        # Analyze REAL movement patterns
        movement_analysis = {}
        
        for player_id, tracking_data in player_tracking.items():
            if len(tracking_data) < 2:
                continue
            
            # Calculate REAL distance traveled
            total_distance = 0.0
            speeds = [data['speed'] for data in tracking_data]
            positions = [data['position'] for data in tracking_data]
            
            for i in range(1, len(positions)):
                prev_pos = np.array(positions[i-1])
                curr_pos = np.array(positions[i])
                distance = np.linalg.norm(curr_pos - prev_pos)
                total_distance += distance
            
            # REAL movement analysis
            avg_speed = np.mean(speeds) if speeds else 0.0
            max_speed = np.max(speeds) if speeds else 0.0
            speed_variance = np.std(speeds) if speeds else 0.0
            
            # REAL zone analysis based on actual positions
            offensive_time = sum(1 for pos in positions if pos[0] > self.blue_line_distance)
            neutral_time = sum(1 for pos in positions 
                             if self.blue_line_distance <= pos[0] <= (self.rink_length - self.blue_line_distance))
            defensive_time = sum(1 for pos in positions if pos[0] < (self.rink_length - self.blue_line_distance))
            
            total_time = len(positions)
            
            movement_analysis[player_id] = {
                'team': tracking_data[0]['team'],
                'total_distance': total_distance,
                'average_speed': avg_speed,
                'max_speed': max_speed,
                'speed_variance': speed_variance,
                'zone_distribution': {
                    'offensive': offensive_time / total_time if total_time > 0 else 0.0,
                    'neutral': neutral_time / total_time if total_time > 0 else 0.0,
                    'defensive': defensive_time / total_time if total_time > 0 else 0.0
                },
                'frames_tracked': len(tracking_data),
                'team_confidence_avg': np.mean([data['team_confidence'] for data in tracking_data])
            }
        
        return movement_analysis
    
    def analyze_real_puck_movement(self) -> Dict[str, Any]:
        """Analyze REAL puck movement patterns."""
        if not self.frames:
            return {"error": "No frames loaded"}
        
        puck_positions = []
        stick_blade_positions = []
        
        for frame in self.frames:
            if frame.puck:
                puck_positions.append({
                    'frame_id': frame.frame_id,
                    'timestamp': frame.timestamp,
                    'position': frame.puck.position,
                    'speed': frame.puck.speed,
                    'is_on_stick': frame.puck.is_on_stick
                })
            
            if frame.stick_blades:
                for stick_blade in frame.stick_blades:
                    stick_blade_positions.append({
                        'frame_id': frame.frame_id,
                        'timestamp': frame.timestamp,
                        'position': stick_blade.position,
                        'speed': stick_blade.speed,
                        'is_on_stick': True
                    })
        
        # REAL puck analysis
        puck_analysis = {
            'puck_detections': len(puck_positions),
            'stick_blade_detections': len(stick_blade_positions),
            'total_puck_events': len(puck_positions) + len(stick_blade_positions),
            'puck_possession_rate': len(stick_blade_positions) / (len(puck_positions) + len(stick_blade_positions)) if (puck_positions or stick_blade_positions) else 0.0
        }
        
        # Calculate REAL puck movement
        if puck_positions:
            puck_speeds = [p['speed'] for p in puck_positions]
            puck_analysis.update({
                'puck_average_speed': np.mean(puck_speeds),
                'puck_max_speed': np.max(puck_speeds),
                'puck_speed_variance': np.std(puck_speeds)
            })
        
        if stick_blade_positions:
            stick_speeds = [s['speed'] for s in stick_blade_positions]
            puck_analysis.update({
                'stick_blade_average_speed': np.mean(stick_speeds),
                'stick_blade_max_speed': np.max(stick_speeds),
                'stick_blade_speed_variance': np.std(stick_speeds)
            })
        
        return puck_analysis
    
    def analyze_real_team_possession(self) -> Dict[str, Any]:
        """Analyze REAL team possession based on actual data."""
        if not self.frames:
            return {"error": "No frames loaded"}
        
        team_stats = defaultdict(lambda: {
            'frames_with_players': 0,
            'total_players': 0,
            'total_team_confidence': 0.0,
            'frames_with_puck_proximity': 0
        })
        
        for frame in self.frames:
            # Count players by team
            team_players = defaultdict(list)
            for player in frame.players:
                team_players[player.team].append(player)
            
            # Update team stats
            for team, players in team_players.items():
                team_stats[team]['frames_with_players'] += 1
                team_stats[team]['total_players'] += len(players)
                team_stats[team]['total_team_confidence'] += sum(p.team_confidence for p in players)
            
            # Analyze puck proximity to teams
            if frame.puck:
                puck_pos = np.array(frame.puck.position)
                
                for team, players in team_players.items():
                    # Find closest player to puck
                    min_distance = float('inf')
                    for player in players:
                        player_pos = np.array(player.position)
                        distance = np.linalg.norm(puck_pos - player_pos)
                        min_distance = min(min_distance, distance)
                    
                    # If a player is close to puck (within 50 feet), count as possession
                    if min_distance < 50:
                        team_stats[team]['frames_with_puck_proximity'] += 1
        
        # Calculate REAL possession metrics
        possession_analysis = {}
        total_frames = len(self.frames)
        
        for team, stats in team_stats.items():
            possession_analysis[team] = {
                'player_frequency': stats['frames_with_players'] / total_frames if total_frames > 0 else 0.0,
                'average_players_per_frame': stats['total_players'] / stats['frames_with_players'] if stats['frames_with_players'] > 0 else 0.0,
                'average_team_confidence': stats['total_team_confidence'] / stats['total_players'] if stats['total_players'] > 0 else 0.0,
                'puck_proximity_rate': stats['frames_with_puck_proximity'] / total_frames if total_frames > 0 else 0.0
            }
        
        return possession_analysis
    
    def analyze_real_spatial_patterns(self) -> Dict[str, Any]:
        """Analyze REAL spatial patterns without making up formations."""
        if not self.frames:
            return {"error": "No frames loaded"}
        
        spatial_analysis = {
            'player_density_by_zone': defaultdict(int),
            'puck_location_by_zone': defaultdict(int),
            'team_spatial_distribution': defaultdict(lambda: defaultdict(int))
        }
        
        for frame in self.frames:
            # Analyze player spatial distribution
            for player in frame.players:
                x, y = player.position
                
                # Determine zone based on REAL rink dimensions
                if x > self.blue_line_distance:
                    zone = 'offensive_zone'
                elif x < (self.rink_length - self.blue_line_distance):
                    zone = 'defensive_zone'
                else:
                    zone = 'neutral_zone'
                
                spatial_analysis['player_density_by_zone'][zone] += 1
                spatial_analysis['team_spatial_distribution'][player.team][zone] += 1
            
            # Analyze puck spatial distribution
            if frame.puck:
                x, y = frame.puck.position
                
                if x > self.blue_line_distance:
                    zone = 'offensive_zone'
                elif x < (self.rink_length - self.blue_line_distance):
                    zone = 'defensive_zone'
                else:
                    zone = 'neutral_zone'
                
                spatial_analysis['puck_location_by_zone'][zone] += 1
        
        # Convert to percentages
        total_players = sum(spatial_analysis['player_density_by_zone'].values())
        total_puck_events = sum(spatial_analysis['puck_location_by_zone'].values())
        
        for zone in spatial_analysis['player_density_by_zone']:
            spatial_analysis['player_density_by_zone'][zone] = (
                spatial_analysis['player_density_by_zone'][zone] / total_players * 100
                if total_players > 0 else 0
            )
        
        for zone in spatial_analysis['puck_location_by_zone']:
            spatial_analysis['puck_location_by_zone'][zone] = (
                spatial_analysis['puck_location_by_zone'][zone] / total_puck_events * 100
                if total_puck_events > 0 else 0
            )
        
        return spatial_analysis
    
    def generate_real_insights(self) -> Dict[str, Any]:
        """Generate REAL insights based on actual data analysis."""
        if not self.frames:
            return {"error": "No frames loaded"}
        
        # Get all analyses
        player_movement = self.analyze_real_player_movement()
        puck_movement = self.analyze_real_puck_movement()
        team_possession = self.analyze_real_team_possession()
        spatial_patterns = self.analyze_real_spatial_patterns()
        
        # Generate REAL insights
        insights = {
            'data_quality': {
                'total_frames': len(self.frames),
                'total_players_detected': len(player_movement),
                'puck_detection_rate': puck_movement.get('puck_detections', 0) / len(self.frames) if self.frames else 0,
                'stick_blade_detection_rate': puck_movement.get('stick_blade_detections', 0) / len(self.frames) if self.frames else 0
            },
            'movement_analysis': {
                'most_active_player': max(player_movement.items(), key=lambda x: x[1]['total_distance']) if player_movement else None,
                'fastest_player': max(player_movement.items(), key=lambda x: x[1]['max_speed']) if player_movement else None,
                'average_player_speed': np.mean([p['average_speed'] for p in player_movement.values()]) if player_movement else 0
            },
            'puck_analysis': {
                'puck_possession_rate': puck_movement.get('puck_possession_rate', 0),
                'puck_average_speed': puck_movement.get('puck_average_speed', 0),
                'stick_blade_average_speed': puck_movement.get('stick_blade_average_speed', 0)
            },
            'team_analysis': {
                'team_with_most_players': max(team_possession.items(), key=lambda x: x[1]['average_players_per_frame']) if team_possession else None,
                'team_with_highest_confidence': max(team_possession.items(), key=lambda x: x[1]['average_team_confidence']) if team_possession else None,
                'team_with_most_puck_proximity': max(team_possession.items(), key=lambda x: x[1]['puck_proximity_rate']) if team_possession else None
            },
            'spatial_analysis': {
                'most_crowded_zone': max(spatial_patterns['player_density_by_zone'].items(), key=lambda x: x[1]) if spatial_patterns['player_density_by_zone'] else None,
                'puck_most_common_zone': max(spatial_patterns['puck_location_by_zone'].items(), key=lambda x: x[1]) if spatial_patterns['puck_location_by_zone'] else None
            }
        }
        
        return insights
    
    def generate_real_report(self, output_file: str = None) -> Dict[str, Any]:
        """Generate a REAL analysis report based on actual data."""
        if not self.frames:
            return {"error": "No frames loaded"}
        
        # Perform all REAL analyses
        report = {
            'metadata': {
                'analysis_type': 'REAL_HOCKEY_ANALYSIS',
                'data_source': 'Roboflow_Computer_Vision',
                'total_frames': len(self.frames),
                'analysis_timestamp': self.frames[0].timestamp if self.frames else 0
            },
            'player_movement': self.analyze_real_player_movement(),
            'puck_movement': self.analyze_real_puck_movement(),
            'team_possession': self.analyze_real_team_possession(),
            'spatial_patterns': self.analyze_real_spatial_patterns(),
            'real_insights': self.generate_real_insights()
        }
        
        # Save report if requested
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Real analysis report saved to {output_file}")
            except Exception as e:
                logger.error(f"Error saving report: {e}")
        
        return report


def main():
    """Test the REAL hockey analysis system."""
    print("🏒 REAL Hockey Analysis System - No BS Version")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = RealHockeyAnalyzer()
    
    # Load real data
    data_file = "/Users/emilyfehr8/CascadeProjects/Computer-Vision-for-Hockey/output/tracking_results_20250910_092038/player_detection_data_20250910_092735.json"
    
    print(f"📁 Loading real Roboflow data from: {data_file}")
    if not analyzer.load_roboflow_data(data_file):
        print("❌ Failed to load data")
        return
    
    print(f"✅ Loaded {len(analyzer.frames)} frames of real hockey data")
    
    # Generate real report
    print("📊 Generating REAL analysis report...")
    report = analyzer.generate_real_report("real_hockey_analysis_v2.json")
    
    print("✅ REAL analysis complete!")
    print(f"📊 Report saved to: real_hockey_analysis_v2.json")
    
    # Print summary
    insights = report.get('real_insights', {})
    data_quality = insights.get('data_quality', {})
    
    print("\n🎯 REAL Analysis Summary:")
    print(f"  • Total frames analyzed: {data_quality.get('total_frames', 0)}")
    print(f"  • Players detected: {data_quality.get('total_players_detected', 0)}")
    print(f"  • Puck detection rate: {data_quality.get('puck_detection_rate', 0):.1%}")
    print(f"  • Stick blade detection rate: {data_quality.get('stick_blade_detection_rate', 0):.1%}")
    
    movement = insights.get('movement_analysis', {})
    if movement.get('most_active_player'):
        player_id, data = movement['most_active_player']
        print(f"  • Most active player: {player_id} ({data['total_distance']:.1f} feet)")
    
    puck = insights.get('puck_analysis', {})
    print(f"  • Puck possession rate: {puck.get('puck_possession_rate', 0):.1%}")
    
    print("\n🏒 This is REAL hockey analysis based on actual data!")


if __name__ == "__main__":
    main()
