"""
Enhanced Hockey Formation Detection System

This module provides accurate hockey formation detection that accounts for:
- Both teams playing simultaneously
- Period changes and attacking direction changes
- Advanced spatial analysis beyond simple zone counting
- Player roles, responsibilities, and relationships
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, NamedTuple
from dataclasses import dataclass
from enum import Enum
import logging
from scipy.spatial.distance import cdist
from scipy.spatial import ConvexHull
from sklearn.cluster import DBSCAN
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameState(Enum):
    """Current game state affecting formation analysis."""
    EVEN_STRENGTH = "even_strength"
    POWER_PLAY = "power_play"
    PENALTY_KILL = "penalty_kill"
    EMPTY_NET = "empty_net"
    PULLED_GOALIE = "pulled_goalie"


class PlayerRole(Enum):
    """Player roles within formations."""
    CENTER = "center"
    LEFT_WING = "left_wing"
    RIGHT_WING = "right_wing"
    LEFT_DEFENSE = "left_defense"
    RIGHT_DEFENSE = "right_defense"
    GOALIE = "goalie"


@dataclass
class TeamZones:
    """Zone definitions for a specific team."""
    offensive_zone: Tuple[float, float, float, float]  # (x_min, x_max, y_min, y_max)
    neutral_zone: Tuple[float, float, float, float]
    defensive_zone: Tuple[float, float, float, float]
    attacking_direction: int  # 1 for left-to-right, -1 for right-to-left


@dataclass
class PlayerAnalysis:
    """Detailed analysis of a player's position and role."""
    player_id: str
    team: str
    position: Tuple[float, float]
    zone: str
    role: Optional[PlayerRole]
    coverage_area: List[Tuple[float, float]]
    nearest_teammates: List[str]
    nearest_opponents: List[str]
    isolation_score: float  # 0.0 = surrounded, 1.0 = isolated


@dataclass
class FormationStructure:
    """Detailed formation structure analysis."""
    formation_name: str
    team: str
    confidence: float
    player_roles: Dict[str, PlayerRole]
    spatial_clusters: List[List[str]]  # Groups of players working together
    coverage_gaps: List[Tuple[float, float]]
    pressure_points: List[Tuple[float, float]]
    tactical_effectiveness: float


class EnhancedFormationDetector:
    """
    Enhanced hockey formation detector that accounts for both teams,
    period changes, and provides detailed spatial analysis.
    """
    
    def __init__(self, rink_dimensions: Tuple[int, int] = (1400, 600)):
        """
        Initialize the enhanced formation detector.
        
        Args:
            rink_dimensions: Tuple of (width, height) for the rink
        """
        self.rink_width, self.rink_height = rink_dimensions
        
        # Standard hockey rink proportions
        self.zone_length = self.rink_width / 3  # Each zone is 1/3 of rink width
        
        # Initialize formation templates with both teams
        self.formation_templates = self._initialize_enhanced_formations()
        
        # Game state tracking
        self.current_period = 1
        self.game_state = GameState.EVEN_STRENGTH
        
    def _initialize_enhanced_formations(self) -> Dict[str, Dict]:
        """Initialize enhanced formation templates for both teams."""
        
        formations = {}
        
        # 1-3-1 Formation (Power Play)
        formations["1-3-1"] = {
            "description": "Power play formation with 1 forward, 3 midfield, 1 defense",
            "player_roles": {
                "high_forward": PlayerRole.CENTER,
                "left_midfield": PlayerRole.LEFT_WING,
                "center_midfield": PlayerRole.CENTER,
                "right_midfield": PlayerRole.RIGHT_WING,
                "low_defense": PlayerRole.LEFT_DEFENSE
            },
            "spatial_requirements": {
                "high_forward_zone": "offensive",
                "midfield_cluster": "offensive_to_neutral",
                "defense_zone": "offensive"
            },
            "coverage_areas": {
                "net_front": ["high_forward"],
                "point": ["low_defense"],
                "half_wall": ["left_midfield", "right_midfield"],
                "center": ["center_midfield"]
            },
            "confidence_threshold": 0.75,
            "min_frames": 8
        }
        
        # 2-1-2 Formation (Neutral Zone Trap)
        formations["2-1-2"] = {
            "description": "Neutral zone trap with 2 forwards, 1 center, 2 defense",
            "player_roles": {
                "left_forward": PlayerRole.LEFT_WING,
                "right_forward": PlayerRole.RIGHT_WING,
                "center_midfield": PlayerRole.CENTER,
                "left_defense": PlayerRole.LEFT_DEFENSE,
                "right_defense": PlayerRole.RIGHT_DEFENSE
            },
            "spatial_requirements": {
                "forward_pressure": "neutral",
                "center_control": "neutral",
                "defensive_support": "neutral_to_defensive"
            },
            "coverage_areas": {
                "neutral_zone": ["left_forward", "right_forward", "center_midfield"],
                "blue_line": ["left_defense", "right_defense"],
                "center_ice": ["center_midfield"]
            },
            "confidence_threshold": 0.8,
            "min_frames": 10
        }
        
        # 1-2-2 Formation (Defensive Coverage)
        formations["1-2-2"] = {
            "description": "Standard defensive zone coverage",
            "player_roles": {
                "high_forward": PlayerRole.CENTER,
                "left_midfield": PlayerRole.LEFT_WING,
                "right_midfield": PlayerRole.RIGHT_WING,
                "left_defense": PlayerRole.LEFT_DEFENSE,
                "right_defense": PlayerRole.RIGHT_DEFENSE
            },
            "spatial_requirements": {
                "pressure_point": "defensive",
                "coverage_zone": "defensive",
                "support_zone": "defensive"
            },
            "coverage_areas": {
                "net_front": ["high_forward"],
                "boards": ["left_midfield", "right_midfield"],
                "point": ["left_defense", "right_defense"],
                "slot": ["high_forward", "left_defense", "right_defense"]
            },
            "confidence_threshold": 0.7,
            "min_frames": 8
        }
        
        return formations
    
    def determine_attacking_direction(self, period: int) -> int:
        """
        Determine attacking direction based on period.
        
        Args:
            period: Current period number
            
        Returns:
            1 for left-to-right attacking, -1 for right-to-left
        """
        # Period 1 & 3: Team A attacks left-to-right
        # Period 2: Team A attacks right-to-left
        return 1 if period % 2 == 1 else -1
    
    def get_team_zones(self, team: str, period: int) -> TeamZones:
        """
        Get zone definitions for a specific team and period.
        
        Args:
            team: Team identifier
            period: Current period
            
        Returns:
            TeamZones object with zone boundaries
        """
        attacking_direction = self.determine_attacking_direction(period)
        
        if attacking_direction == 1:  # Left-to-right attacking
            offensive_zone = (2 * self.zone_length, self.rink_width, 0, self.rink_height)
            neutral_zone = (self.zone_length, 2 * self.zone_length, 0, self.rink_height)
            defensive_zone = (0, self.zone_length, 0, self.rink_height)
        else:  # Right-to-left attacking
            offensive_zone = (0, self.zone_length, 0, self.rink_height)
            neutral_zone = (self.zone_length, 2 * self.zone_length, 0, self.rink_height)
            defensive_zone = (2 * self.zone_length, self.rink_width, 0, self.rink_height)
        
        return TeamZones(
            offensive_zone=offensive_zone,
            neutral_zone=neutral_zone,
            defensive_zone=defensive_zone,
            attacking_direction=attacking_direction
        )
    
    def classify_player_zone(self, position: Tuple[float, float], team_zones: TeamZones) -> str:
        """
        Classify player position into team-specific zone.
        
        Args:
            position: (x, y) coordinates
            team_zones: Zone definitions for the team
            
        Returns:
            Zone name: 'offensive', 'neutral', or 'defensive'
        """
        x, y = position
        
        # Check offensive zone
        if (team_zones.offensive_zone[0] <= x <= team_zones.offensive_zone[1] and
            team_zones.offensive_zone[2] <= y <= team_zones.offensive_zone[3]):
            return "offensive"
        
        # Check neutral zone
        if (team_zones.neutral_zone[0] <= x <= team_zones.neutral_zone[1] and
            team_zones.neutral_zone[2] <= y <= team_zones.neutral_zone[3]):
            return "neutral"
        
        # Check defensive zone
        if (team_zones.defensive_zone[0] <= x <= team_zones.defensive_zone[1] and
            team_zones.defensive_zone[2] <= y <= team_zones.defensive_zone[3]):
            return "defensive"
        
        return "neutral"  # Default fallback
    
    def analyze_player_spatial_relationships(self, players: List[Dict], team: str) -> List[PlayerAnalysis]:
        """
        Analyze spatial relationships and roles for players on a team.
        
        Args:
            players: List of player dictionaries
            team: Team identifier
            
        Returns:
            List of PlayerAnalysis objects
        """
        team_players = [p for p in players if p.get('team', '').startswith(team)]
        team_zones = self.get_team_zones(team, self.current_period)
        
        player_analyses = []
        
        for player in team_players:
            position = (player['rink_position']['x'], player['rink_position']['y'])
            zone = self.classify_player_zone(position, team_zones)
            
            # Calculate distances to other players
            distances = []
            for other_player in players:
                other_pos = (other_player['rink_position']['x'], other_player['rink_position']['y'])
                dist = np.sqrt((position[0] - other_pos[0])**2 + (position[1] - other_pos[1])**2)
                distances.append((other_player['player_id'], dist, other_player.get('team', '')))
            
            # Sort by distance
            distances.sort(key=lambda x: x[1])
            
            # Find nearest teammates and opponents
            nearest_teammates = [pid for pid, dist, t in distances[:6] if t.startswith(team) and pid != player['player_id']]
            nearest_opponents = [pid for pid, dist, t in distances[:6] if not t.startswith(team)]
            
            # Calculate isolation score (distance to nearest teammate)
            nearest_teammate_dist = next((dist for pid, dist, t in distances if t.startswith(team) and pid != player['player_id']), float('inf'))
            isolation_score = min(nearest_teammate_dist / 200.0, 1.0)  # Normalize to 0-1
            
            # Estimate coverage area (simplified - would be more complex in reality)
            coverage_area = self._estimate_coverage_area(position, team_zones)
            
            player_analysis = PlayerAnalysis(
                player_id=player['player_id'],
                team=team,
                position=position,
                zone=zone,
                role=None,  # Will be determined during formation analysis
                coverage_area=coverage_area,
                nearest_teammates=nearest_teammates[:3],
                nearest_opponents=nearest_opponents[:2],
                isolation_score=isolation_score
            )
            
            player_analyses.append(player_analysis)
        
        return player_analyses
    
    def _estimate_coverage_area(self, position: Tuple[float, float], team_zones: TeamZones) -> List[Tuple[float, float]]:
        """Estimate a player's coverage area based on position and zone."""
        x, y = position
        coverage_radius = 100  # pixels
        
        # Create a simple circular coverage area
        coverage_area = []
        for angle in np.linspace(0, 2*np.pi, 8):
            cx = x + coverage_radius * np.cos(angle)
            cy = y + coverage_radius * np.sin(angle)
            
            # Ensure coverage stays within rink bounds
            cx = max(0, min(cx, self.rink_width))
            cy = max(0, min(cy, self.rink_height))
            
            coverage_area.append((cx, cy))
        
        return coverage_area
    
    def detect_formation_with_spatial_analysis(
        self, 
        players: List[Dict], 
        team: str,
        min_confidence: float = 0.6
    ) -> Optional[FormationStructure]:
        """
        Detect formation using advanced spatial analysis.
        
        Args:
            players: List of player dictionaries
            team: Team identifier
            min_confidence: Minimum confidence threshold
            
        Returns:
            FormationStructure object or None if no formation detected
        """
        if len(players) < 5:  # Need at least 5 skaters for formation
            return None
        
        # Analyze player spatial relationships
        player_analyses = self.analyze_player_spatial_relationships(players, team)
        
        best_formation = None
        best_confidence = 0.0
        
        # Test each formation template
        for formation_name, template in self.formation_templates.items():
            confidence = self._analyze_formation_match(player_analyses, template, formation_name)
            
            if confidence > best_confidence and confidence >= template['confidence_threshold']:
                best_confidence = confidence
                best_formation = formation_name
        
        if best_formation:
            return self._create_formation_structure(
                player_analyses, 
                best_formation, 
                best_confidence, 
                team
            )
        
        return None
    
    def _analyze_formation_match(
        self, 
        player_analyses: List[PlayerAnalysis], 
        template: Dict, 
        formation_name: str
    ) -> float:
        """
        Analyze how well players match a formation template.
        
        Args:
            player_analyses: List of analyzed players
            template: Formation template
            formation_name: Name of formation
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if len(player_analyses) < 5:
            return 0.0
        
        # Spatial clustering analysis
        positions = np.array([pa.position for pa in player_analyses])
        clustering_score = self._analyze_spatial_clusters(positions, formation_name)
        
        # Zone distribution analysis
        zone_distribution = {}
        for pa in player_analyses:
            zone_distribution[pa.zone] = zone_distribution.get(pa.zone, 0) + 1
        
        zone_score = self._analyze_zone_distribution(zone_distribution, formation_name)
        
        # Role assignment analysis
        role_score = self._analyze_role_assignments(player_analyses, template)
        
        # Coverage analysis
        coverage_score = self._analyze_coverage_patterns(player_analyses, template)
        
        # Weighted combination of scores
        total_confidence = (
            clustering_score * 0.3 +
            zone_score * 0.25 +
            role_score * 0.25 +
            coverage_score * 0.2
        )
        
        return total_confidence
    
    def _analyze_spatial_clusters(self, positions: np.ndarray, formation_name: str) -> float:
        """Analyze spatial clustering patterns."""
        if len(positions) < 3:
            return 0.0
        
        # Use DBSCAN to find clusters
        clustering = DBSCAN(eps=150, min_samples=2).fit(positions)
        n_clusters = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
        
        # Different formations have different expected cluster patterns
        if formation_name == "1-3-1":
            # Should have 2-3 clusters: high forward, midfield group, defense
            expected_clusters = 3
        elif formation_name == "2-1-2":
            # Should have 3 clusters: two forward groups, center, two defense
            expected_clusters = 3
        elif formation_name == "1-2-2":
            # Should have 2-3 clusters: forward, midfield, defense
            expected_clusters = 2
        else:
            expected_clusters = 2
        
        # Calculate similarity to expected clustering
        cluster_similarity = 1.0 - abs(n_clusters - expected_clusters) / max(expected_clusters, 1)
        return max(0.0, cluster_similarity)
    
    def _analyze_zone_distribution(self, zone_distribution: Dict[str, int], formation_name: str) -> float:
        """Analyze if zone distribution matches formation expectations."""
        total_players = sum(zone_distribution.values())
        if total_players == 0:
            return 0.0
        
        # Expected zone distributions for different formations
        expected_distributions = {
            "1-3-1": {"offensive": 0.8, "neutral": 0.2, "defensive": 0.0},
            "2-1-2": {"offensive": 0.0, "neutral": 1.0, "defensive": 0.0},
            "1-2-2": {"offensive": 0.0, "neutral": 0.0, "defensive": 1.0}
        }
        
        if formation_name not in expected_distributions:
            return 0.5  # Default score for unknown formations
        
        expected = expected_distributions[formation_name]
        actual = {zone: count / total_players for zone, count in zone_distribution.items()}
        
        # Calculate similarity
        similarity = 0.0
        for zone in ["offensive", "neutral", "defensive"]:
            expected_pct = expected.get(zone, 0.0)
            actual_pct = actual.get(zone, 0.0)
            similarity += 1.0 - abs(expected_pct - actual_pct)
        
        return similarity / 3.0
    
    def _analyze_role_assignments(self, player_analyses: List[PlayerAnalysis], template: Dict) -> float:
        """Analyze if player roles can be assigned according to template."""
        # This is simplified - in reality would need more sophisticated role detection
        role_requirements = template.get("player_roles", {})
        
        # For now, return a base score based on player count
        if len(player_analyses) >= len(role_requirements):
            return 0.8
        else:
            return 0.4
    
    def _analyze_coverage_patterns(self, player_analyses: List[PlayerAnalysis], template: Dict) -> float:
        """Analyze coverage patterns and gaps."""
        # Calculate total coverage area
        total_coverage = 0
        coverage_overlap = 0
        
        for i, pa1 in enumerate(player_analyses):
            for pa2 in player_analyses[i+1:]:
                # Calculate distance between players
                dist = np.sqrt(
                    (pa1.position[0] - pa2.position[0])**2 + 
                    (pa1.position[1] - pa2.position[1])**2
                )
                
                if dist < 200:  # Overlapping coverage
                    coverage_overlap += 1
        
        # Good coverage has some overlap but not too much
        optimal_overlap = len(player_analyses) * 0.3
        overlap_score = 1.0 - abs(coverage_overlap - optimal_overlap) / max(optimal_overlap, 1)
        
        return max(0.0, overlap_score)
    
    def _create_formation_structure(
        self, 
        player_analyses: List[PlayerAnalysis], 
        formation_name: str, 
        confidence: float, 
        team: str
    ) -> FormationStructure:
        """Create detailed formation structure analysis."""
        
        # Assign roles based on formation and player positions
        player_roles = self._assign_player_roles(player_analyses, formation_name)
        
        # Identify spatial clusters
        spatial_clusters = self._identify_spatial_clusters(player_analyses)
        
        # Find coverage gaps
        coverage_gaps = self._identify_coverage_gaps(player_analyses)
        
        # Identify pressure points
        pressure_points = self._identify_pressure_points(player_analyses, formation_name)
        
        # Calculate tactical effectiveness
        tactical_effectiveness = self._calculate_tactical_effectiveness(
            player_analyses, formation_name
        )
        
        return FormationStructure(
            formation_name=formation_name,
            team=team,
            confidence=confidence,
            player_roles=player_roles,
            spatial_clusters=spatial_clusters,
            coverage_gaps=coverage_gaps,
            pressure_points=pressure_points,
            tactical_effectiveness=tactical_effectiveness
        )
    
    def _assign_player_roles(self, player_analyses: List[PlayerAnalysis], formation_name: str) -> Dict[str, PlayerRole]:
        """Assign roles to players based on formation and positioning."""
        roles = {}
        
        if formation_name == "1-3-1":
            # Sort players by zone and position
            offensive_players = [pa for pa in player_analyses if pa.zone == "offensive"]
            offensive_players.sort(key=lambda p: p.position[1])  # Sort by y-coordinate
            
            if len(offensive_players) >= 5:
                roles[offensive_players[0].player_id] = PlayerRole.CENTER  # Highest forward
                roles[offensive_players[1].player_id] = PlayerRole.LEFT_WING
                roles[offensive_players[2].player_id] = PlayerRole.CENTER
                roles[offensive_players[3].player_id] = PlayerRole.RIGHT_WING
                roles[offensive_players[4].player_id] = PlayerRole.LEFT_DEFENSE
        
        elif formation_name == "2-1-2":
            neutral_players = [pa for pa in player_analyses if pa.zone == "neutral"]
            neutral_players.sort(key=lambda p: p.position[0])  # Sort by x-coordinate
            
            if len(neutral_players) >= 5:
                roles[neutral_players[0].player_id] = PlayerRole.LEFT_WING
                roles[neutral_players[1].player_id] = PlayerRole.RIGHT_WING
                roles[neutral_players[2].player_id] = PlayerRole.CENTER
                roles[neutral_players[3].player_id] = PlayerRole.LEFT_DEFENSE
                roles[neutral_players[4].player_id] = PlayerRole.RIGHT_DEFENSE
        
        return roles
    
    def _identify_spatial_clusters(self, player_analyses: List[PlayerAnalysis]) -> List[List[str]]:
        """Identify groups of players working together."""
        if len(player_analyses) < 3:
            return []
        
        positions = np.array([pa.position for pa in player_analyses])
        clustering = DBSCAN(eps=150, min_samples=2).fit(positions)
        
        clusters = []
        for cluster_id in set(clustering.labels_):
            if cluster_id == -1:  # Noise points
                continue
            
            cluster_players = [
                player_analyses[i].player_id 
                for i, label in enumerate(clustering.labels_) 
                if label == cluster_id
            ]
            clusters.append(cluster_players)
        
        return clusters
    
    def _identify_coverage_gaps(self, player_analyses: List[PlayerAnalysis]) -> List[Tuple[float, float]]:
        """Identify areas with poor coverage."""
        # Simplified gap detection - would be more sophisticated in reality
        gaps = []
        
        # Find areas between players that might be gaps
        for i, pa1 in enumerate(player_analyses):
            for pa2 in player_analyses[i+1:]:
                distance = np.sqrt(
                    (pa1.position[0] - pa2.position[0])**2 + 
                    (pa1.position[1] - pa2.position[1])**2
                )
                
                if distance > 300:  # Large gap between players
                    # Calculate midpoint as potential gap
                    gap_x = (pa1.position[0] + pa2.position[0]) / 2
                    gap_y = (pa1.position[1] + pa2.position[1]) / 2
                    gaps.append((gap_x, gap_y))
        
        return gaps
    
    def _identify_pressure_points(self, player_analyses: List[PlayerAnalysis], formation_name: str) -> List[Tuple[float, float]]:
        """Identify areas where pressure is being applied."""
        pressure_points = []
        
        # Different formations apply pressure in different areas
        if formation_name == "1-3-1":
            # Pressure at net front and point
            for pa in player_analyses:
                if pa.zone == "offensive" and pa.position[0] > self.rink_width * 0.8:
                    pressure_points.append(pa.position)
        
        elif formation_name == "2-1-2":
            # Pressure in neutral zone
            for pa in player_analyses:
                if pa.zone == "neutral":
                    pressure_points.append(pa.position)
        
        return pressure_points
    
    def _calculate_tactical_effectiveness(self, player_analyses: List[PlayerAnalysis], formation_name: str) -> float:
        """Calculate overall tactical effectiveness of the formation."""
        if not player_analyses:
            return 0.0
        
        # Factors contributing to effectiveness
        isolation_penalty = np.mean([pa.isolation_score for pa in player_analyses])
        coverage_score = 1.0 - len(self._identify_coverage_gaps(player_analyses)) / len(player_analyses)
        cluster_score = len(self._identify_spatial_clusters(player_analyses)) / 3.0  # Normalize to 0-1
        
        effectiveness = (1.0 - isolation_penalty * 0.3 + coverage_score * 0.4 + cluster_score * 0.3)
        return max(0.0, min(1.0, effectiveness))
    
    def detect_formations_both_teams(
        self, 
        tracking_data: List[Dict], 
        min_frames: int = 5
    ) -> Dict[str, List[FormationStructure]]:
        """
        Detect formations for both teams simultaneously.
        
        Args:
            tracking_data: List of frame data
            min_frames: Minimum frames for formation confirmation
            
        Returns:
            Dictionary with formations for each team
        """
        results = {"Team A": [], "Team B": []}
        
        for frame_idx, frame_data in enumerate(tracking_data):
            if 'players' not in frame_data:
                continue
            
            # Detect formations for both teams
            for team in ["Team A", "Team B"]:
                team_players = [p for p in frame_data['players'] if p.get('team', '').startswith(team)]
                
                if len(team_players) >= 5:  # Need at least 5 skaters
                    formation = self.detect_formation_with_spatial_analysis(team_players, team)
                    
                    if formation:
                        # Add temporal information
                        formation.start_frame = frame_idx
                        formation.end_frame = frame_idx
                        formation.timestamp = frame_data.get('timestamp', 0)
                        
                        results[team].append(formation)
        
        return results
