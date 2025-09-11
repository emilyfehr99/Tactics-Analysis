"""
Roboflow Hockey Integration System

This module integrates real Roboflow computer vision data with our hockey tactics analysis system.
It converts Roboflow tracking data into hockey events and formations for professional analysis.
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict, deque
from pathlib import Path

# Import our hockey analysis components
from real_hockey_analyzer import (
    RealHockeyAnalyzer, PuckEvent, PlayerSkills, TeamSystem,
    GameState, ZoneEntry, ShotType, PlayerRole
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RoboflowObjectType(Enum):
    """Complete Roboflow object types."""
    # Players
    PLAYER = "player"
    GOALKEEPER = "goalkeeper"
    AWAY_PLAYER = "away"
    HOME_PLAYER = "home"
    
    # Puck
    PUCK = "puck"
    STICK_BLADE = "stick_blade"
    
    # Rink Features
    FIELD = "field"
    BLUE_LINE = "blue_line"
    CENTER_LINE = "center_line"
    GOAL_LINE = "goalline"
    GOAL_ZONE = "goalzone"
    
    # Face-off Circles
    CENTER_CIRCLE = "center__circle"
    RED_CIRCLE = "red_circle"


@dataclass
class RoboflowFrame:
    """Roboflow frame data."""
    frame_id: int
    timestamp: float
    players: List[Dict]
    puck: Optional[Dict] = None
    rink_features: List[Dict] = None


@dataclass
class RoboflowPlayer:
    """Roboflow player data."""
    player_id: str
    position: Tuple[float, float]
    team: str
    team_confidence: float
    roboflow_class: str
    speed: float
    orientation: float
    bbox: List[float]
    is_goalkeeper: bool = False


class RoboflowHockeyIntegrator:
    """
    Integrates Roboflow computer vision data with hockey tactics analysis.
    """
    
    def __init__(self, rink_dimensions: Tuple[float, float] = (200.0, 85.0)):
        """
        Initialize the integrator.
        
        Args:
            rink_dimensions: Tuple of (length, width) in feet
        """
        self.rink_length, self.rink_width = rink_dimensions
        self.blue_line_distance = 75.0  # feet from each goal line
        
        # Initialize hockey analyzer
        self.hockey_analyzer = RealHockeyAnalyzer()
        
        # Tracking data
        self.roboflow_frames = []
        self.player_tracking = defaultdict(list)
        self.puck_tracking = []
        self.rink_features = []
        
        # Conversion mappings
        self.team_mapping = {
            "home": "Team A",
            "away": "Team B"
        }
        
    def load_roboflow_data(self, json_file_path: str) -> bool:
        """
        Load Roboflow tracking data from JSON file.
        
        Args:
            json_file_path: Path to the Roboflow JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loading Roboflow data from {json_file_path}")
            
            # Process frames
            for frame_data in data.get('frames', []):
                frame = self._process_roboflow_frame(frame_data)
                if frame:
                    self.roboflow_frames.append(frame)
                    self._update_tracking_data(frame)
            
            logger.info(f"Loaded {len(self.roboflow_frames)} frames of Roboflow data")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Roboflow data: {e}")
            return False
    
    def _process_roboflow_frame(self, frame_data: Dict) -> Optional[RoboflowFrame]:
        """Process a single Roboflow frame."""
        try:
            frame_id = frame_data.get('frame_id', 0)
            timestamp = frame_data.get('timestamp', 0.0)
            players_data = frame_data.get('players', [])
            
            # Process players
            players = []
            puck = None
            rink_features = []
            
            for player_data in players_data:
                player_type = player_data.get('type', '')
                roboflow_class = player_data.get('roboflow_class', '')
                
                # Handle all player types
                if player_type == 'player' or roboflow_class in ['player', 'goalkeeper', 'home', 'away']:
                    player = self._process_player_data(player_data)
                    if player:
                        players.append(player)
                
                # Handle puck and stick blade
                elif player_type == 'puck' or roboflow_class in ['puck', 'stick_blade']:
                    puck = self._process_puck_data(player_data)
                
                # Handle all rink features
                elif roboflow_class in ['field', 'blue_line', 'center_line', 'goalline', 'goalzone', 
                                       'center__circle', 'red_circle']:
                    feature = self._process_rink_feature(player_data)
                    if feature:
                        rink_features.append(feature)
            
            return RoboflowFrame(
                frame_id=frame_id,
                timestamp=timestamp,
                players=players,
                puck=puck,
                rink_features=rink_features
            )
            
        except Exception as e:
            logger.error(f"Error processing frame {frame_data.get('frame_id', 'unknown')}: {e}")
            return None
    
    def _process_player_data(self, player_data: Dict) -> Optional[RoboflowPlayer]:
        """Process player data from Roboflow."""
        try:
            player_id = player_data.get('player_id', '')
            rink_pos = player_data.get('rink_position', {})
            position = (rink_pos.get('x', 0), rink_pos.get('y', 0))
            
            # Team classification
            roboflow_class = player_data.get('roboflow_class', '')
            team_confidence = player_data.get('team_confidence', 0.0)
            team = self._determine_team(roboflow_class, team_confidence)
            
            # Movement data
            speed = player_data.get('speed', 0.0)
            orientation = player_data.get('orientation', 0.0)
            bbox = player_data.get('bbox', [])
            
            # Check if goalkeeper
            is_goalkeeper = roboflow_class.lower() in ['goalkeeper', 'goalie']
            
            # If it's a goalkeeper, determine team based on position
            if is_goalkeeper:
                team = self._determine_goalkeeper_team(position)
            
            return RoboflowPlayer(
                player_id=player_id,
                position=position,
                team=team,
                team_confidence=team_confidence,
                roboflow_class=roboflow_class,
                speed=speed,
                orientation=orientation,
                bbox=bbox,
                is_goalkeeper=is_goalkeeper
            )
            
        except Exception as e:
            logger.error(f"Error processing player data: {e}")
            return None
    
    def _process_puck_data(self, puck_data: Dict) -> Optional[Dict]:
        """Process puck data from Roboflow."""
        try:
            rink_pos = puck_data.get('rink_position', {})
            position = (rink_pos.get('x', 0), rink_pos.get('y', 0))
            roboflow_class = puck_data.get('roboflow_class', 'puck')
            
            return {
                'position': position,
                'speed': puck_data.get('speed', 0.0),
                'orientation': puck_data.get('orientation', 0.0),
                'bbox': puck_data.get('bbox', []),
                'confidence': puck_data.get('team_confidence', 1.0),
                'type': roboflow_class,  # 'puck' or 'stick_blade'
                'is_on_stick': roboflow_class == 'stick_blade'
            }
            
        except Exception as e:
            logger.error(f"Error processing puck data: {e}")
            return None
    
    def _process_rink_feature(self, feature_data: Dict) -> Optional[Dict]:
        """Process rink feature data from Roboflow."""
        try:
            feature_type = feature_data.get('type', '')
            roboflow_class = feature_data.get('roboflow_class', '')
            rink_pos = feature_data.get('rink_position', {})
            position = (rink_pos.get('x', 0), rink_pos.get('y', 0))
            
            # Determine feature importance and role
            feature_role = self._determine_feature_role(roboflow_class, position)
            
            return {
                'type': feature_type,
                'class': roboflow_class,
                'position': position,
                'bbox': feature_data.get('bbox', []),
                'confidence': feature_data.get('team_confidence', 1.0),
                'role': feature_role,
                'zone': self._determine_feature_zone(position)
            }
            
        except Exception as e:
            logger.error(f"Error processing rink feature: {e}")
            return None
    
    def _determine_team(self, roboflow_class: str, confidence: float) -> str:
        """Determine team from Roboflow classification."""
        class_lower = roboflow_class.lower()
        
        if class_lower in ['home', 'home_player']:
            return "Team A"
        elif class_lower in ['away', 'away_player']:
            return "Team B"
        elif class_lower == 'goalkeeper':
            # Need to determine which team's goalie based on position
            return "Team A"  # Will be refined based on position
        else:
            # Default to Team A for unknown classifications
            return "Team A"
    
    def _determine_goalkeeper_team(self, position: Tuple[float, float]) -> str:
        """Determine goalkeeper team based on position on rink."""
        x, y = position
        
        # Goalies are typically in defensive zones
        # Team A defends the left side (x < rink_length/2)
        # Team B defends the right side (x > rink_length/2)
        if x < self.rink_length / 2:
            return "Team A"
        else:
            return "Team B"
    
    def _determine_feature_role(self, roboflow_class: str, position: Tuple[float, float]) -> str:
        """Determine the role of a rink feature in hockey analysis."""
        class_lower = roboflow_class.lower()
        
        if class_lower == 'blue_line':
            return "zone_boundary"
        elif class_lower == 'center_line':
            return "neutral_divider"
        elif class_lower == 'goalline':
            return "goal_boundary"
        elif class_lower == 'goalzone':
            return "scoring_area"
        elif class_lower in ['center__circle', 'red_circle']:
            return "face_off_location"
        elif class_lower == 'field':
            return "playing_surface"
        else:
            return "unknown"
    
    def _determine_feature_zone(self, position: Tuple[float, float]) -> str:
        """Determine which zone a rink feature is in."""
        x, y = position
        
        if x > self.blue_line_distance:
            return "offensive_zone"
        elif x < (self.rink_length - self.blue_line_distance):
            return "defensive_zone"
        else:
            return "neutral_zone"
    
    def _update_tracking_data(self, frame: RoboflowFrame):
        """Update tracking data with new frame."""
        # Update player tracking
        for player in frame.players:
            self.player_tracking[player.player_id].append({
                'frame_id': frame.frame_id,
                'timestamp': frame.timestamp,
                'position': player.position,
                'team': player.team,
                'speed': player.speed,
                'orientation': player.orientation,
                'is_goalkeeper': player.is_goalkeeper
            })
        
        # Update puck tracking
        if frame.puck:
            self.puck_tracking.append({
                'frame_id': frame.frame_id,
                'timestamp': frame.timestamp,
                'position': frame.puck['position'],
                'speed': frame.puck['speed'],
                'orientation': frame.puck['orientation']
            })
        
        # Update rink features
        if frame.rink_features:
            self.rink_features.extend(frame.rink_features)
    
    def convert_to_hockey_events(self) -> List[PuckEvent]:
        """
        Convert Roboflow tracking data to hockey events.
        
        Returns:
            List of PuckEvent objects
        """
        events = []
        
        if not self.puck_tracking:
            logger.warning("No puck tracking data available")
            return events
        
        # Analyze puck movement to detect events
        for i in range(1, len(self.puck_tracking)):
            prev_puck = self.puck_tracking[i-1]
            curr_puck = self.puck_tracking[i]
            
            # Calculate puck movement
            prev_pos = np.array(prev_puck['position'])
            curr_pos = np.array(curr_puck['position'])
            movement = curr_pos - prev_pos
            distance = np.linalg.norm(movement)
            
            # Determine event type based on movement and context
            event_type = self._determine_event_type(prev_puck, curr_puck, distance)
            
            # Determine team possession
            team_with_puck = self._determine_puck_possession(curr_puck['frame_id'])
            
            # Create puck event
            event = PuckEvent(
                timestamp=curr_puck['timestamp'],
                event_type=event_type,
                player_id=f"puck_{curr_puck['frame_id']}",
                team=team_with_puck,
                location=curr_puck['position'],
                success=True,  # Would need more context to determine
                details={
                    'distance_moved': distance,
                    'velocity': (movement[0], movement[1]),
                    'speed': curr_puck['speed'],
                    'orientation': curr_puck['orientation']
                }
            )
            
            events.append(event)
        
        logger.info(f"Converted Roboflow data to {len(events)} hockey events")
        return events
    
    def _determine_event_type(self, prev_puck: Dict, curr_puck: Dict, distance: float) -> str:
        """Determine event type based on puck movement."""
        # Simple heuristics for event detection
        if distance < 5:  # Minimal movement
            return "carry"
        elif distance > 50:  # Large movement
            return "pass"
        elif curr_puck['speed'] > 20:  # High speed
            return "shot"
        else:
            return "carry"
    
    def _determine_puck_possession(self, frame_id: int) -> str:
        """Determine which team has puck possession."""
        # Find the frame data
        frame = next((f for f in self.roboflow_frames if f.frame_id == frame_id), None)
        if not frame:
            return "Unknown Team"
        
        # Find closest player to puck
        if not frame.puck:
            return "Unknown Team"
        
        puck_pos = np.array(frame.puck['position'])
        closest_player = None
        min_distance = float('inf')
        
        for player in frame.players:
            player_pos = np.array(player.position)
            distance = np.linalg.norm(puck_pos - player_pos)
            
            if distance < min_distance:
                min_distance = distance
                closest_player = player
        
        if closest_player and min_distance < 50:  # Within 50 units
            return closest_player.team
        else:
            return "Team A"  # Default to Team A
    
    def analyze_real_hockey_data(self, time_window: float = 60.0) -> Dict[str, Any]:
        """
        Analyze real hockey data from Roboflow tracking.
        
        Args:
            time_window: Time window for analysis in seconds
            
        Returns:
            Analysis results dictionary
        """
        if not self.roboflow_frames:
            return {"error": "No Roboflow data loaded"}
        
        # Convert to hockey events
        hockey_events = self.convert_to_hockey_events()
        
        # Add events to hockey analyzer
        for event in hockey_events:
            self.hockey_analyzer.add_puck_event(event)
        
        # Generate player skills from real data
        real_player_skills = self._generate_real_player_skills()
        self.hockey_analyzer.set_player_skills(real_player_skills)
        
        # Set up team systems
        team_systems = self._generate_team_systems()
        self.hockey_analyzer.set_team_systems(team_systems)
        
        # Perform analysis
        analysis = self.hockey_analyzer.analyze_game_flow(time_window)
        
        # Add Roboflow-specific insights
        analysis['roboflow_insights'] = self._generate_roboflow_insights()
        analysis['formation_analysis'] = self._analyze_real_formations()
        analysis['player_performance'] = self._analyze_player_performance()
        
        return analysis
    
    def _generate_real_player_skills(self) -> Dict[str, PlayerSkills]:
        """Generate real player skills from Roboflow tracking data."""
        player_skills = {}
        
        for player_id, tracking_data in self.player_tracking.items():
            if not tracking_data:
                continue
            
            # Calculate real performance metrics
            positions = [data['position'] for data in tracking_data]
            speeds = [data['speed'] for data in tracking_data]
            
            # Skating speed (normalized)
            max_speed = max(speeds) if speeds else 0
            skating_speed = min(max_speed / 50.0, 1.0)  # Normalize to 0-1
            
            # Shot accuracy (placeholder - would need shot detection)
            shot_accuracy = 0.5  # Default
            
            # Passing accuracy (placeholder - would need pass detection)
            passing_accuracy = 0.5  # Default
            
            # Defensive awareness (based on positioning)
            defensive_awareness = self._calculate_defensive_awareness(positions)
            
            # Physical presence (based on team classification)
            physical_presence = 0.7  # Default
            
            # Hockey IQ (placeholder)
            hockey_iq = 0.6  # Default
            
            # Check if goalkeeper
            is_goalkeeper = any(data['is_goalkeeper'] for data in tracking_data)
            
            player_skills[player_id] = PlayerSkills(
                player_id=player_id,
                skating_speed=skating_speed,
                shot_accuracy=shot_accuracy,
                passing_accuracy=passing_accuracy,
                defensive_awareness=defensive_awareness,
                physical_presence=physical_presence,
                hockey_iq=hockey_iq,
                power_play_specialist=False,  # Would need more analysis
                penalty_kill_specialist=False,  # Would need more analysis
                face_off_percentage=0.5,  # Default
                shooting_percentage=0.1,  # Default
                plus_minus=0,  # Default
                time_on_ice_per_game=0.0  # Default
            )
        
        return player_skills
    
    def _calculate_defensive_awareness(self, positions: List[Tuple[float, float]]) -> float:
        """Calculate defensive awareness based on positioning."""
        if not positions:
            return 0.5
        
        # Calculate how often player is in defensive zone
        defensive_positions = 0
        for x, y in positions:
            if x < (self.rink_length - self.blue_line_distance):  # Defensive zone
                defensive_positions += 1
        
        return min(defensive_positions / len(positions), 1.0)
    
    def _generate_team_systems(self) -> Dict[str, TeamSystem]:
        """Generate team systems based on observed play patterns."""
        # Analyze team behavior to determine systems
        team_a_behavior = self._analyze_team_behavior("Team A")
        team_b_behavior = self._analyze_team_behavior("Team B")
        
        return {
            "Team A": TeamSystem(
                team_id="Team A",
                offensive_system=team_a_behavior['offensive_system'],
                defensive_system=team_a_behavior['defensive_system'],
                power_play_formation="1-3-1",  # Default
                penalty_kill_formation="diamond",  # Default
                neutral_zone_strategy=team_a_behavior['neutral_zone_strategy'],
                face_off_strategy="situational",
                line_change_frequency=0.8,
                shot_selection="balanced"
            ),
            "Team B": TeamSystem(
                team_id="Team B",
                offensive_system=team_b_behavior['offensive_system'],
                defensive_system=team_b_behavior['defensive_system'],
                power_play_formation="2-1-2",  # Default
                penalty_kill_formation="box",  # Default
                neutral_zone_strategy=team_b_behavior['neutral_zone_strategy'],
                face_off_strategy="aggressive",
                line_change_frequency=1.0,
                shot_selection="high_volume"
            )
        }
    
    def _analyze_team_behavior(self, team: str) -> Dict[str, str]:
        """Analyze team behavior to determine systems."""
        # Get team players
        team_players = []
        for player_id, tracking_data in self.player_tracking.items():
            if tracking_data and tracking_data[0]['team'] == team:
                team_players.extend(tracking_data)
        
        if not team_players:
            return {
                'offensive_system': 'unknown',
                'defensive_system': 'unknown',
                'neutral_zone_strategy': 'unknown'
            }
        
        # Analyze positioning patterns
        positions = [data['position'] for data in team_players]
        
        # Determine offensive system based on positioning
        offensive_system = self._determine_offensive_system(positions)
        
        # Determine defensive system
        defensive_system = self._determine_defensive_system(positions)
        
        # Determine neutral zone strategy
        neutral_zone_strategy = self._determine_neutral_zone_strategy(positions)
        
        return {
            'offensive_system': offensive_system,
            'defensive_system': defensive_system,
            'neutral_zone_strategy': neutral_zone_strategy
        }
    
    def _determine_offensive_system(self, positions: List[Tuple[float, float]]) -> str:
        """Determine offensive system based on positioning."""
        if not positions:
            return "unknown"
        
        # Calculate average position in offensive zone
        offensive_positions = [pos for pos in positions if pos[0] > self.blue_line_distance]
        
        if not offensive_positions:
            return "unknown"
        
        avg_x = np.mean([pos[0] for pos in offensive_positions])
        avg_y = np.mean([pos[1] for pos in offensive_positions])
        
        # Simple heuristics
        if avg_x > self.rink_length * 0.8:
            return "crash_net"
        elif avg_y > self.rink_width * 0.7 or avg_y < self.rink_width * 0.3:
            return "rush"
        else:
            return "cycle"
    
    def _determine_defensive_system(self, positions: List[Tuple[float, float]]) -> str:
        """Determine defensive system based on positioning."""
        if not positions:
            return "unknown"
        
        # Calculate spread in defensive zone
        defensive_positions = [pos for pos in positions if pos[0] < (self.rink_length - self.blue_line_distance)]
        
        if not defensive_positions:
            return "unknown"
        
        x_positions = [pos[0] for pos in defensive_positions]
        y_positions = [pos[1] for pos in defensive_positions]
        
        x_spread = max(x_positions) - min(x_positions) if x_positions else 0
        y_spread = max(y_positions) - min(y_positions) if y_positions else 0
        
        # Tight zone if players are close together
        if x_spread < 50 and y_spread < 50:
            return "zone"
        else:
            return "man_to_man"
    
    def _determine_neutral_zone_strategy(self, positions: List[Tuple[float, float]]) -> str:
        """Determine neutral zone strategy based on positioning."""
        if not positions:
            return "unknown"
        
        # Calculate neutral zone positioning
        neutral_positions = [pos for pos in positions 
                           if self.blue_line_distance <= pos[0] <= (self.rink_length - self.blue_line_distance)]
        
        if not neutral_positions:
            return "unknown"
        
        # Calculate spread
        x_positions = [pos[0] for pos in neutral_positions]
        x_spread = max(x_positions) - min(x_positions) if x_positions else 0
        
        # Trap if players are spread wide
        if x_spread > 100:
            return "trap"
        else:
            return "pressure"
    
    def _generate_roboflow_insights(self) -> Dict[str, Any]:
        """Generate insights specific to Roboflow data."""
        insights = {
            "total_frames": len(self.roboflow_frames),
            "total_players_detected": len(self.player_tracking),
            "total_puck_events": len(self.puck_tracking),
            "team_distribution": self._calculate_team_distribution(),
            "tracking_quality": self._assess_tracking_quality(),
            "rink_feature_detection": self._analyze_rink_features(),
            "class_detection_summary": self._analyze_class_detection(),
            "goalkeeper_analysis": self._analyze_goalkeepers(),
            "stick_blade_detection": self._analyze_stick_blades()
        }
        
        return insights
    
    def _calculate_team_distribution(self) -> Dict[str, int]:
        """Calculate team distribution."""
        team_counts = defaultdict(int)
        
        for player_id, tracking_data in self.player_tracking.items():
            if tracking_data:
                team = tracking_data[0]['team']
                team_counts[team] += 1
        
        return dict(team_counts)
    
    def _assess_tracking_quality(self) -> Dict[str, float]:
        """Assess the quality of tracking data."""
        if not self.roboflow_frames:
            return {"overall_quality": 0.0}
        
        # Calculate average confidence
        total_confidence = 0
        total_players = 0
        
        for frame in self.roboflow_frames:
            for player in frame.players:
                total_confidence += player.team_confidence
                total_players += 1
        
        avg_confidence = total_confidence / total_players if total_players > 0 else 0
        
        return {
            "overall_quality": avg_confidence,
            "average_team_confidence": avg_confidence,
            "frames_with_puck": len([f for f in self.roboflow_frames if f.puck]),
            "puck_detection_rate": len([f for f in self.roboflow_frames if f.puck]) / len(self.roboflow_frames)
        }
    
    def _analyze_rink_features(self) -> Dict[str, Any]:
        """Analyze detected rink features."""
        if not self.rink_features:
            return {"features_detected": 0}
        
        feature_types = defaultdict(int)
        feature_roles = defaultdict(int)
        feature_zones = defaultdict(int)
        
        for feature in self.rink_features:
            feature_types[feature['class']] += 1
            feature_roles[feature.get('role', 'unknown')] += 1
            feature_zones[feature.get('zone', 'unknown')] += 1
        
        return {
            "features_detected": len(self.rink_features),
            "feature_types": dict(feature_types),
            "feature_roles": dict(feature_roles),
            "feature_zones": dict(feature_zones),
            "average_confidence": np.mean([f['confidence'] for f in self.rink_features])
        }
    
    def _analyze_class_detection(self) -> Dict[str, Any]:
        """Analyze detection of different Roboflow classes."""
        class_counts = defaultdict(int)
        
        # Count all detected classes across all frames
        for frame in self.roboflow_frames:
            for player in frame.players:
                class_counts[player.roboflow_class] += 1
            
            if frame.puck:
                class_counts[frame.puck.get('type', 'puck')] += 1
            
            if frame.rink_features:
                for feature in frame.rink_features:
                    class_counts[feature['class']] += 1
        
        return {
            "detected_classes": dict(class_counts),
            "total_unique_classes": len(class_counts),
            "most_detected_class": max(class_counts.items(), key=lambda x: x[1]) if class_counts else None
        }
    
    def _analyze_goalkeepers(self) -> Dict[str, Any]:
        """Analyze goalkeeper detection and positioning."""
        goalkeepers = []
        
        for player_id, tracking_data in self.player_tracking.items():
            if tracking_data and any(data['is_goalkeeper'] for data in tracking_data):
                goalkeepers.append({
                    'player_id': player_id,
                    'team': tracking_data[0]['team'],
                    'positions': [data['position'] for data in tracking_data],
                    'average_position': (
                        np.mean([pos[0] for pos in [data['position'] for data in tracking_data]]),
                        np.mean([pos[1] for pos in [data['position'] for data in tracking_data]])
                    )
                })
        
        return {
            "goalkeepers_detected": len(goalkeepers),
            "goalkeeper_details": goalkeepers,
            "goalkeeper_coverage": self._analyze_goalkeeper_coverage(goalkeepers)
        }
    
    def _analyze_goalkeeper_coverage(self, goalkeepers: List[Dict]) -> Dict[str, Any]:
        """Analyze goalkeeper positioning and coverage."""
        if not goalkeepers:
            return {"coverage_analysis": "no_goalkeepers"}
        
        coverage_analysis = {}
        for goalie in goalkeepers:
            positions = goalie['positions']
            if positions:
                x_positions = [pos[0] for pos in positions]
                y_positions = [pos[1] for pos in positions]
                
                coverage_analysis[goalie['player_id']] = {
                    'team': goalie['team'],
                    'x_range': max(x_positions) - min(x_positions),
                    'y_range': max(y_positions) - min(y_positions),
                    'average_x': np.mean(x_positions),
                    'average_y': np.mean(y_positions),
                    'movement_pattern': self._determine_goalkeeper_pattern(positions)
                }
        
        return coverage_analysis
    
    def _determine_goalkeeper_pattern(self, positions: List[Tuple[float, float]]) -> str:
        """Determine goalkeeper movement pattern."""
        if len(positions) < 3:
            return "insufficient_data"
        
        x_movement = np.std([pos[0] for pos in positions])
        y_movement = np.std([pos[1] for pos in positions])
        
        if x_movement > 20:
            return "lateral_movement"
        elif y_movement > 20:
            return "depth_movement"
        else:
            return "stationary"
    
    def _analyze_stick_blades(self) -> Dict[str, Any]:
        """Analyze stick blade detection for puck tracking."""
        stick_blade_events = []
        
        for puck_event in self.puck_tracking:
            if puck_event.get('is_on_stick', False):
                stick_blade_events.append(puck_event)
        
        return {
            "stick_blade_events": len(stick_blade_events),
            "puck_on_stick_percentage": len(stick_blade_events) / len(self.puck_tracking) if self.puck_tracking else 0,
            "stick_blade_positions": [event['position'] for event in stick_blade_events]
        }
    
    def _analyze_real_formations(self) -> Dict[str, Any]:
        """Analyze formations from real player positions."""
        formations = {}
        
        for frame in self.roboflow_frames:
            if not frame.players:
                continue
            
            # Group players by team
            team_players = defaultdict(list)
            for player in frame.players:
                team_players[player.team].append(player)
            
            # Analyze formations for each team
            for team, players in team_players.items():
                if len(players) >= 5:  # Need at least 5 players
                    formation = self._detect_formation_from_positions(players, frame.puck)
                    if formation:
                        formations[f"{team}_frame_{frame.frame_id}"] = formation
        
        return formations
    
    def _detect_formation_from_positions(self, players: List[RoboflowPlayer], puck: Optional[Dict]) -> Optional[Dict]:
        """Detect formation from player positions with enhanced Roboflow accuracy."""
        if not players:
            return None
        
        # Separate players by type for enhanced analysis
        field_players = [p for p in players if not p.is_goalkeeper]
        goalkeepers = [p for p in players if p.is_goalkeeper]
        
        if not field_players:
            return None
        
        positions = [player.position for player in field_players]
        
        # Enhanced formation detection using complete Roboflow data
        if len(field_players) >= 4:
            # Analyze spatial distribution with zone awareness
            x_positions = [pos[0] for pos in positions]
            y_positions = [pos[1] for pos in positions]
            
            x_spread = max(x_positions) - min(x_positions)
            y_spread = max(y_positions) - min(y_positions)
            
            # Determine zone context using rink features
            zone_context = self._determine_zone_context(positions, puck)
            
            # Enhanced formation detection with goalkeeper positioning
            formation_type = self._determine_formation_type_enhanced(
                field_players, goalkeepers, x_spread, y_spread, zone_context
            )
            
            # Calculate confidence based on player classification accuracy
            confidence = self._calculate_formation_confidence(field_players, goalkeepers)
            
            return {
                "formation_type": formation_type,
                "confidence": confidence,
                "player_count": len(field_players),
                "goalkeeper_count": len(goalkeepers),
                "spatial_spread": {"x": x_spread, "y": y_spread},
                "zone_context": zone_context,
                "puck_in_formation": puck is not None,
                "puck_on_stick": puck.get('is_on_stick', False) if puck else False,
                "team_classification": self._analyze_team_classification(field_players),
                "defensive_coverage": self._analyze_defensive_coverage_enhanced(field_players, goalkeepers)
            }
        
        return None
    
    def _determine_zone_context(self, positions: List[Tuple[float, float]], puck: Optional[Dict]) -> str:
        """Determine zone context using rink features and player positions."""
        if not positions:
            return "unknown"
        
        # Calculate average position
        avg_x = np.mean([pos[0] for pos in positions])
        avg_y = np.mean([pos[1] for pos in positions])
        
        # Determine zone based on rink features
        if avg_x > self.blue_line_distance:
            return "offensive_zone"
        elif avg_x < (self.rink_length - self.blue_line_distance):
            return "defensive_zone"
        else:
            return "neutral_zone"
    
    def _determine_formation_type_enhanced(self, field_players: List[RoboflowPlayer], 
                                         goalkeepers: List[RoboflowPlayer], 
                                         x_spread: float, y_spread: float, 
                                         zone_context: str) -> str:
        """Determine formation type with enhanced Roboflow accuracy."""
        player_count = len(field_players)
        
        # Enhanced formation detection based on player count and spatial distribution
        if player_count == 5:
            # 5-on-5 even strength
            if zone_context == "offensive_zone":
                if x_spread > y_spread * 1.5:
                    return "offensive_zone_pressure"
                else:
                    return "offensive_zone_cycle"
            elif zone_context == "defensive_zone":
                if y_spread > x_spread * 1.5:
                    return "defensive_zone_coverage"
                else:
                    return "defensive_zone_press"
            else:
                if x_spread > y_spread * 1.5:
                    return "neutral_zone_trap"
                else:
                    return "neutral_zone_transition"
        elif player_count == 4:
            # 4-on-5 penalty kill
            return "penalty_kill_formation"
        elif player_count == 6:
            # 5-on-4 power play
            return "power_play_formation"
        else:
            # Default based on spatial distribution
            if x_spread > y_spread * 1.5:
                return "spread_formation"
            elif y_spread > x_spread * 1.5:
                return "stacked_formation"
            else:
                return "balanced_formation"
    
    def _calculate_formation_confidence(self, field_players: List[RoboflowPlayer], 
                                      goalkeepers: List[RoboflowPlayer]) -> float:
        """Calculate formation confidence based on player classification accuracy."""
        total_confidence = 0.0
        total_players = 0
        
        # Calculate confidence from field players
        for player in field_players:
            total_confidence += player.team_confidence
            total_players += 1
        
        # Calculate confidence from goalkeepers
        for goalie in goalkeepers:
            total_confidence += goalie.team_confidence
            total_players += 1
        
        if total_players == 0:
            return 0.0
        
        return total_confidence / total_players
    
    def _analyze_team_classification(self, field_players: List[RoboflowPlayer]) -> Dict[str, Any]:
        """Analyze team classification accuracy."""
        team_counts = defaultdict(int)
        team_confidence = defaultdict(list)
        
        for player in field_players:
            team_counts[player.team] += 1
            team_confidence[player.team].append(player.team_confidence)
        
        classification_analysis = {}
        for team, count in team_counts.items():
            classification_analysis[team] = {
                "player_count": count,
                "average_confidence": np.mean(team_confidence[team]) if team_confidence[team] else 0.0,
                "confidence_range": [min(team_confidence[team]), max(team_confidence[team])] if team_confidence[team] else [0.0, 0.0]
            }
        
        return classification_analysis
    
    def _analyze_defensive_coverage_enhanced(self, field_players: List[RoboflowPlayer], 
                                           goalkeepers: List[RoboflowPlayer]) -> Dict[str, Any]:
        """Analyze defensive coverage with enhanced Roboflow accuracy."""
        coverage_analysis = {
            "field_player_coverage": self._analyze_field_player_coverage(field_players),
            "goalkeeper_coverage": self._analyze_goalkeeper_coverage_enhanced(goalkeepers),
            "overall_coverage_score": 0.0
        }
        
        # Calculate overall coverage score
        if field_players:
            coverage_analysis["overall_coverage_score"] = coverage_analysis["field_player_coverage"]["coverage_score"]
        
        return coverage_analysis
    
    def _analyze_field_player_coverage(self, field_players: List[RoboflowPlayer]) -> Dict[str, Any]:
        """Analyze field player defensive coverage."""
        if not field_players:
            return {"coverage_score": 0.0}
        
        positions = [player.position for player in field_players]
        x_positions = [pos[0] for pos in positions]
        y_positions = [pos[1] for pos in positions]
        
        # Calculate coverage metrics
        x_coverage = max(x_positions) - min(x_positions)
        y_coverage = max(y_positions) - min(y_positions)
        
        # Coverage score based on spatial distribution
        coverage_score = min(1.0, (x_coverage + y_coverage) / 200.0)
        
        return {
            "coverage_score": coverage_score,
            "x_coverage": x_coverage,
            "y_coverage": y_coverage,
            "player_density": len(field_players) / (x_coverage * y_coverage + 1)
        }
    
    def _analyze_goalkeeper_coverage_enhanced(self, goalkeepers: List[RoboflowPlayer]) -> Dict[str, Any]:
        """Analyze goalkeeper coverage with enhanced Roboflow accuracy."""
        if not goalkeepers:
            return {"coverage_score": 0.0, "goalkeeper_count": 0}
        
        coverage_analysis = {
            "goalkeeper_count": len(goalkeepers),
            "coverage_score": 0.0,
            "goalkeeper_details": []
        }
        
        for goalie in goalkeepers:
            goalie_analysis = {
                "player_id": goalie.player_id,
                "team": goalie.team,
                "position": goalie.position,
                "confidence": goalie.team_confidence,
                "coverage_zone": self._determine_goalkeeper_coverage_zone(goalie.position)
            }
            coverage_analysis["goalkeeper_details"].append(goalie_analysis)
        
        # Calculate overall coverage score
        if goalkeepers:
            avg_confidence = np.mean([goalie.team_confidence for goalie in goalkeepers])
            coverage_analysis["coverage_score"] = avg_confidence
        
        return coverage_analysis
    
    def _determine_goalkeeper_coverage_zone(self, position: Tuple[float, float]) -> str:
        """Determine goalkeeper coverage zone."""
        x, y = position
        
        # Determine which goal the goalkeeper is defending
        if x < self.rink_length / 2:
            return "left_goal_coverage"
        else:
            return "right_goal_coverage"
    
    def _analyze_player_performance(self) -> Dict[str, Any]:
        """Analyze individual player performance with enhanced Roboflow accuracy."""
        performance = {}
        
        for player_id, tracking_data in self.player_tracking.items():
            if not tracking_data:
                continue
            
            # Enhanced performance analysis with complete Roboflow data
            positions = [data['position'] for data in tracking_data]
            speeds = [data['speed'] for data in tracking_data]
            is_goalkeeper = tracking_data[0].get('is_goalkeeper', False)
            
            # Distance covered with enhanced accuracy
            total_distance = 0
            for i in range(1, len(positions)):
                prev_pos = np.array(positions[i-1])
                curr_pos = np.array(positions[i])
                total_distance += np.linalg.norm(curr_pos - prev_pos)
            
            # Enhanced performance metrics
            avg_speed = np.mean(speeds) if speeds else 0
            max_speed = max(speeds) if speeds else 0
            speed_consistency = 1.0 - (np.std(speeds) / (avg_speed + 1e-6)) if speeds else 0.0
            
            # Enhanced zone distribution with rink features
            zone_distribution = self._analyze_zone_distribution_enhanced(positions, is_goalkeeper)
            
            # Player role analysis
            player_role = self._determine_player_role(positions, speeds, is_goalkeeper)
            
            # Performance classification
            performance_class = self._classify_player_performance(avg_speed, max_speed, total_distance, is_goalkeeper)
            
            performance[player_id] = {
                "total_distance": total_distance,
                "average_speed": avg_speed,
                "max_speed": max_speed,
                "speed_consistency": speed_consistency,
                "is_goalkeeper": is_goalkeeper,
                "player_role": player_role,
                "performance_class": performance_class,
                "zone_distribution": zone_distribution,
                "team": tracking_data[0]['team'] if tracking_data else "Unknown",
                "tracking_quality": self._assess_player_tracking_quality(tracking_data)
            }
        
        return performance
    
    def _analyze_zone_distribution_enhanced(self, positions: List[Tuple[float, float]], is_goalkeeper: bool) -> Dict[str, float]:
        """Enhanced zone distribution analysis with rink features."""
        if not positions:
            return {"offensive": 0.0, "neutral": 0.0, "defensive": 0.0}
        
        # Enhanced zone analysis using rink features
        offensive_time = sum(1 for pos in positions if pos[0] > self.blue_line_distance)
        neutral_time = sum(1 for pos in positions 
                         if self.blue_line_distance <= pos[0] <= (self.rink_length - self.blue_line_distance))
        defensive_time = sum(1 for pos in positions if pos[0] < (self.rink_length - self.blue_line_distance))
        
        total_time = len(positions)
        
        zone_distribution = {
            "offensive": offensive_time / total_time if total_time > 0 else 0.0,
            "neutral": neutral_time / total_time if total_time > 0 else 0.0,
            "defensive": defensive_time / total_time if total_time > 0 else 0.0
        }
        
        # Adjust for goalkeepers (they should primarily be in defensive zone)
        if is_goalkeeper:
            zone_distribution["defensive"] = max(zone_distribution["defensive"], 0.7)
            zone_distribution["offensive"] = min(zone_distribution["offensive"], 0.1)
        
        return zone_distribution
    
    def _determine_player_role(self, positions: List[Tuple[float, float]], speeds: List[float], is_goalkeeper: bool) -> str:
        """Determine player role based on enhanced Roboflow data."""
        if is_goalkeeper:
            return "goalkeeper"
        
        if not positions or not speeds:
            return "unknown"
        
        # Analyze player behavior patterns
        avg_speed = np.mean(speeds)
        max_speed = max(speeds)
        speed_variance = np.std(speeds)
        
        # Calculate position variance
        x_positions = [pos[0] for pos in positions]
        y_positions = [pos[1] for pos in positions]
        x_variance = np.std(x_positions)
        y_variance = np.std(y_positions)
        
        # Determine role based on movement patterns
        if max_speed > 50 and speed_variance > 10:
            return "forward"  # High speed, variable movement
        elif x_variance > y_variance * 1.5:
            return "defenseman"  # More lateral movement
        elif avg_speed > 20:
            return "center"  # Moderate speed, balanced movement
        else:
            return "utility"  # Low movement, utility player
    
    def _classify_player_performance(self, avg_speed: float, max_speed: float, total_distance: float, is_goalkeeper: bool) -> str:
        """Classify player performance level."""
        if is_goalkeeper:
            # Different criteria for goalkeepers
            if total_distance > 100:
                return "high_activity_goalkeeper"
            elif total_distance > 50:
                return "moderate_activity_goalkeeper"
            else:
                return "low_activity_goalkeeper"
        
        # Field player classification
        if max_speed > 100 and total_distance > 200:
            return "high_performance"
        elif max_speed > 50 and total_distance > 100:
            return "moderate_performance"
        elif max_speed > 20 and total_distance > 50:
            return "low_performance"
        else:
            return "minimal_activity"
    
    def _assess_player_tracking_quality(self, tracking_data: List[Dict]) -> Dict[str, Any]:
        """Assess the quality of player tracking data."""
        if not tracking_data:
            return {"quality_score": 0.0, "data_completeness": 0.0}
        
        # Calculate data completeness
        total_frames = len(tracking_data)
        valid_positions = sum(1 for data in tracking_data if data.get('position') is not None)
        valid_speeds = sum(1 for data in tracking_data if data.get('speed') is not None)
        
        position_completeness = valid_positions / total_frames if total_frames > 0 else 0.0
        speed_completeness = valid_speeds / total_frames if total_frames > 0 else 0.0
        
        # Calculate quality score
        quality_score = (position_completeness * 0.7 + speed_completeness * 0.3)
        
        return {
            "quality_score": quality_score,
            "data_completeness": position_completeness,
            "speed_completeness": speed_completeness,
            "total_frames": total_frames,
            "valid_positions": valid_positions,
            "valid_speeds": valid_speeds
        }
    
    def generate_comprehensive_report(self, output_file: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis report.
        
        Args:
            output_file: Optional file to save the report
            
        Returns:
            Comprehensive report dictionary
        """
        # Perform analysis
        analysis = self.analyze_real_hockey_data()
        
        # Get actionable insights
        insights = self.hockey_analyzer.get_actionable_insights()
        
        # Combine into comprehensive report
        report = {
            "analysis_timestamp": np.datetime64('now').astype(str),
            "roboflow_data_summary": {
                "total_frames": len(self.roboflow_frames),
                "total_players": len(self.player_tracking),
                "total_puck_events": len(self.puck_tracking),
                "tracking_duration": self.roboflow_frames[-1].timestamp - self.roboflow_frames[0].timestamp if self.roboflow_frames else 0
            },
            "hockey_analysis": analysis,
            "actionable_insights": insights,
            "formation_analysis": self._analyze_real_formations(),
            "player_performance": self._analyze_player_performance(),
            "recommendations": self._generate_recommendations(analysis, insights)
        }
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_file}")
        
        return report
    
    def _generate_recommendations(self, analysis: Dict[str, Any], insights: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on analysis."""
        recommendations = []
        
        # Add coaching recommendations
        recommendations.extend(insights.get("coaching_recommendations", []))
        
        # Add player adjustments
        recommendations.extend(insights.get("player_adjustments", []))
        
        # Add tactical opportunities
        recommendations.extend(insights.get("tactical_opportunities", []))
        
        # Add Roboflow-specific recommendations
        roboflow_insights = analysis.get("roboflow_insights", {})
        tracking_quality = roboflow_insights.get("tracking_quality", {})
        
        if tracking_quality.get("overall_quality", 0) < 0.7:
            recommendations.append("Improve tracking quality - consider better lighting or camera positioning")
        
        if tracking_quality.get("puck_detection_rate", 0) < 0.8:
            recommendations.append("Enhance puck tracking - puck detection rate is below optimal")
        
        return recommendations
