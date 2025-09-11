"""
Roboflow-Based Formation Detector

This system analyzes formations PER TEAM using actual Roboflow classes
for zone context instead of hard-coded rink dimensions.
"""

import numpy as np
import math
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

class FormationType(Enum):
    """Even strength formation types."""
    TWO_ONE_TWO = "2-1-2"
    ONE_TWO_TWO = "1-2-2" 
    TWO_TWO_ONE = "2-2-1"
    ONE_THREE_ONE = "1-3-1"
    THREE_TWO = "3-2"
    UNKNOWN = "Unknown"

class ZoneContext(Enum):
    """Rink zone contexts based on Roboflow features."""
    OFFENSIVE = "offensive"
    NEUTRAL = "neutral" 
    DEFENSIVE = "defensive"

@dataclass
class RoboflowPlayer:
    """Player data from Roboflow with all available information."""
    player_id: str
    team: str  # 'home' or 'away' from Roboflow
    x: float
    y: float
    is_goalkeeper: bool = False
    roboflow_class: str = "player"

@dataclass
class RoboflowFeature:
    """Rink feature detected by Roboflow."""
    feature_type: str  # 'Blue_line', 'GoalLine', 'Center__circle', etc.
    x: float
    y: float
    roboflow_class: str

@dataclass
class TeamFormation:
    """Formation detection for a single team."""
    team: str
    formation_type: FormationType
    confidence: float
    zone_context: ZoneContext
    player_roles: Dict[str, str]
    formation_shape: List[Tuple[float, float]]
    analysis_details: Dict

class RoboflowFormationDetector:
    """
    Formation detector that uses Roboflow classes for zone context
    and analyzes formations PER TEAM.
    """
    
    def __init__(self):
        # Formation thresholds calibrated for real hockey data
        self.formation_thresholds = {
            FormationType.TWO_ONE_TWO: {
                'min_linearity': 0.3,
                'min_compactness': 0.2,
                'max_spread': 150
            },
            FormationType.ONE_TWO_TWO: {
                'min_linearity': 0.4,
                'min_compactness': 0.1,
                'max_spread': 200
            },
            FormationType.TWO_TWO_ONE: {
                'min_linearity': 0.35,
                'min_compactness': 0.15,
                'max_spread': 180
            },
            FormationType.ONE_THREE_ONE: {
                'min_circularity': 0.6,
                'min_compactness': 0.25,
                'max_spread': 120
            }
        }
        
        # Zone detection using Roboflow features
        self.zone_feature_mapping = {
            'offensive': ['GoalLine', 'GoalZone'],
            'neutral': ['Blue_line', 'Center__circle', 'Center_line'],
            'defensive': ['GoalLine', 'GoalZone']
        }
    
    def detect_team_formations(self, players: List[RoboflowPlayer], 
                              rink_features: List[RoboflowFeature],
                              puck_location: Optional[Tuple[float, float]] = None) -> Dict[str, TeamFormation]:
        """
        Detect formations for each team separately using Roboflow data.
        
        Args:
            players: All players with Roboflow team classification
            rink_features: Rink features detected by Roboflow
            puck_location: Optional puck location
            
        Returns:
            Dict mapping team names to their detected formations
        """
        # Separate players by team
        team_players = defaultdict(list)
        for player in players:
            if player.roboflow_class in ['home', 'away']:
                team_players[player.roboflow_class].append(player)
        
        formations = {}
        
        # Analyze each team separately
        for team, team_player_list in team_players.items():
            if len(team_player_list) >= 4:  # Minimum for formation
                formation = self._detect_single_team_formation(
                    team, team_player_list, rink_features, puck_location
                )
                formations[team] = formation
            else:
                formations[team] = self._create_unknown_team_formation(team, "Not enough players")
        
        return formations
    
    def _detect_single_team_formation(self, team: str, players: List[RoboflowPlayer],
                                    rink_features: List[RoboflowFeature],
                                    puck_location: Optional[Tuple[float, float]]) -> TeamFormation:
        """Detect formation for a single team."""
        
        # Filter out goalkeepers
        field_players = [p for p in players if not p.is_goalkeeper]
        
        if len(field_players) < 4:
            return self._create_unknown_team_formation(team, "Not enough field players")
        
        # Determine zone context using Roboflow features
        zone_context = self._determine_zone_from_roboflow_features(
            field_players, rink_features, puck_location
        )
        
        # Analyze formation shape
        formation_result = self._analyze_team_formation_shape(field_players, zone_context)
        
        return TeamFormation(
            team=team,
            formation_type=formation_result["formation_type"],
            confidence=formation_result["confidence"],
            zone_context=zone_context,
            player_roles=formation_result["player_roles"],
            formation_shape=formation_result["formation_shape"],
            analysis_details=formation_result["analysis_details"]
        )
    
    def _determine_zone_from_roboflow_features(self, players: List[RoboflowPlayer],
                                             rink_features: List[RoboflowFeature],
                                             puck_location: Optional[Tuple[float, float]]) -> ZoneContext:
        """Determine zone context using actual Roboflow-detected features."""
        
        # If we have puck location, use it as primary indicator
        if puck_location:
            puck_x = puck_location[0]
            
            # Check for nearby rink features
            nearby_features = []
            for feature in rink_features:
                distance = math.sqrt((feature.x - puck_x)**2 + (feature.y - puck_location[1])**2)
                if distance < 50:  # Within 50 units
                    nearby_features.append(feature.feature_type)
            
            # Determine zone based on nearby features
            if any(f in self.zone_feature_mapping['offensive'] for f in nearby_features):
                return ZoneContext.OFFENSIVE
            elif any(f in self.zone_feature_mapping['neutral'] for f in nearby_features):
                return ZoneContext.NEUTRAL
            elif any(f in self.zone_feature_mapping['defensive'] for f in nearby_features):
                return ZoneContext.DEFENSIVE
        
        # Fallback: use average player position relative to rink features
        if not players:
            return ZoneContext.NEUTRAL
            
        avg_x = sum(p.x for p in players) / len(players)
        
        # Find closest rink feature
        if rink_features:
            closest_feature = min(rink_features, 
                                key=lambda f: abs(f.x - avg_x))
            
            if closest_feature.feature_type in self.zone_feature_mapping['offensive']:
                return ZoneContext.OFFENSIVE
            elif closest_feature.feature_type in self.zone_feature_mapping['neutral']:
                return ZoneContext.NEUTRAL
            elif closest_feature.feature_type in self.zone_feature_mapping['defensive']:
                return ZoneContext.DEFENSIVE
        
        # Default to neutral if no features available
        return ZoneContext.NEUTRAL
    
    def _analyze_team_formation_shape(self, players: List[RoboflowPlayer], 
                                    zone_context: ZoneContext) -> Dict:
        """Analyze formation shape for a team using relaxed thresholds."""
        
        positions = [(p.x, p.y) for p in players]
        
        # Calculate formation characteristics
        formation_center = self._calculate_formation_center(positions)
        formation_spread = self._calculate_formation_spread(positions)
        
        # Analyze geometric patterns with relaxed thresholds
        geometric_patterns = self._analyze_geometric_patterns_relaxed(positions, formation_center)
        
        # Match to formations using relaxed criteria
        formation_match = self._match_formation_pattern_relaxed(geometric_patterns, zone_context, formation_spread)
        
        # Calculate confidence
        confidence = self._calculate_formation_confidence_relaxed(formation_match, positions, zone_context)
        
        # Assign player roles
        player_roles = self._assign_player_roles_relaxed(players, formation_match, formation_center)
        
        return {
            "formation_type": formation_match["formation_type"],
            "confidence": confidence,
            "player_roles": player_roles,
            "formation_shape": positions,
            "analysis_details": {
                "formation_center": formation_center,
                "formation_spread": formation_spread,
                "geometric_patterns": geometric_patterns,
                "pattern_match": formation_match
            }
        }
    
    def _analyze_geometric_patterns_relaxed(self, positions: List[Tuple[float, float]], 
                                          center: Tuple[float, float]) -> Dict:
        """Analyze geometric patterns with relaxed thresholds for real hockey data."""
        
        patterns = {
            "shape_type": "unknown",
            "symmetry": 0.0,
            "compactness": 0.0,
            "linearity": 0.0,
            "circularity": 0.0
        }
        
        if len(positions) < 3:
            return patterns
        
        # Calculate patterns using actual data ranges
        patterns["compactness"] = self._calculate_compactness_relaxed(positions, center)
        patterns["linearity"] = self._calculate_linearity_relaxed(positions)
        patterns["circularity"] = self._calculate_circularity_relaxed(positions, center)
        patterns["symmetry"] = self._calculate_symmetry_relaxed(positions, center)
        
        # Determine shape type with relaxed thresholds
        patterns["shape_type"] = self._determine_shape_type_relaxed(patterns)
        
        return patterns
    
    def _calculate_compactness_relaxed(self, positions: List[Tuple[float, float]], 
                                     center: Tuple[float, float]) -> float:
        """Calculate compactness using actual data ranges."""
        if not positions:
            return 0.0
            
        distances_from_center = []
        for pos in positions:
            dist = math.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
            distances_from_center.append(dist)
            
        avg_distance = sum(distances_from_center) / len(distances_from_center)
        
        # Use actual data range instead of hard-coded rink size
        max_distance = max(distances_from_center) if distances_from_center else 1
        min_distance = min(distances_from_center) if distances_from_center else 0
        
        # Normalize by actual data range
        if max_distance > 0:
            compactness = 1.0 - (avg_distance / max_distance)
            return max(0.0, min(1.0, compactness))
        
        return 0.0
    
    def _calculate_linearity_relaxed(self, positions: List[Tuple[float, float]]) -> float:
        """Calculate linearity with relaxed thresholds."""
        if len(positions) < 3:
            return 0.0
            
        try:
            positions_array = np.array(positions)
            centered = positions_array - np.mean(positions_array, axis=0)
            cov_matrix = np.cov(centered.T)
            eigenvalues, _ = np.linalg.eigh(cov_matrix)
            
            if len(eigenvalues) >= 2 and eigenvalues[1] > 0:
                linearity = eigenvalues[0] / eigenvalues[1]
                return min(linearity / 10.0, 1.0)  # Scale down for real data
                
        except:
            pass
            
        return 0.0
    
    def _calculate_circularity_relaxed(self, positions: List[Tuple[float, float]], 
                                     center: Tuple[float, float]) -> float:
        """Calculate circularity with relaxed thresholds."""
        if len(positions) < 3:
            return 0.0
            
        distances_from_center = []
        for pos in positions:
            dist = math.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
            distances_from_center.append(dist)
            
        if not distances_from_center:
            return 0.0
            
        avg_distance = sum(distances_from_center) / len(distances_from_center)
        variance = sum((d - avg_distance)**2 for d in distances_from_center) / len(distances_from_center)
        
        # Use actual variance range
        max_variance = max(distances_from_center)**2 if distances_from_center else 1
        
        return max(0.0, 1.0 - (variance / max_variance))
    
    def _calculate_symmetry_relaxed(self, positions: List[Tuple[float, float]], 
                                  center: Tuple[float, float]) -> float:
        """Calculate symmetry with relaxed thresholds."""
        if len(positions) < 2:
            return 0.0
            
        symmetry_scores = []
        
        for pos in positions:
            mirror_y = center[1] + (center[1] - pos[1])
            mirror_pos = (pos[0], mirror_y)
            
            min_distance = float('inf')
            for other_pos in positions:
                if other_pos != pos:
                    dist = math.sqrt((other_pos[0] - mirror_pos[0])**2 + (other_pos[1] - mirror_pos[1])**2)
                    min_distance = min(min_distance, dist)
            
            # Use actual data range
            max_distance = max(abs(p[1] - center[1]) for p in positions) * 2 if positions else 1
            symmetry_score = max(0.0, 1.0 - (min_distance / max_distance))
            symmetry_scores.append(symmetry_score)
            
        return sum(symmetry_scores) / len(symmetry_scores)
    
    def _determine_shape_type_relaxed(self, patterns: Dict) -> str:
        """Determine shape type with relaxed thresholds."""
        compactness = patterns.get("compactness", 0.0)
        linearity = patterns.get("linearity", 0.0)
        circularity = patterns.get("circularity", 0.0)
        symmetry = patterns.get("symmetry", 0.0)
        
        # Relaxed thresholds for real hockey data
        if linearity > 0.3:
            return "linear"
        elif circularity > 0.4:
            return "circular"
        elif compactness > 0.4:
            return "compact"
        elif symmetry > 0.3:
            return "symmetric"
        else:
            return "irregular"
    
    def _match_formation_pattern_relaxed(self, patterns: Dict, zone_context: ZoneContext, 
                                       formation_spread: float) -> Dict:
        """Match formation patterns with relaxed thresholds for real hockey data."""
        
        shape_type = patterns.get("shape_type", "unknown")
        compactness = patterns.get("compactness", 0.0)
        linearity = patterns.get("linearity", 0.0)
        symmetry = patterns.get("symmetry", 0.0)
        circularity = patterns.get("circularity", 0.0)
        
        # Relaxed formation matching for real hockey data
        if zone_context == ZoneContext.DEFENSIVE:
            if linearity > 0.3 and formation_spread < 150:
                return {"formation_type": FormationType.ONE_TWO_TWO, "confidence": 0.6}
            elif compactness > 0.2 and symmetry > 0.2:
                return {"formation_type": FormationType.TWO_ONE_TWO, "confidence": 0.5}
                
        elif zone_context == ZoneContext.NEUTRAL:
            if linearity > 0.4 and formation_spread < 200:
                return {"formation_type": FormationType.ONE_TWO_TWO, "confidence": 0.7}
            elif symmetry > 0.3:
                return {"formation_type": FormationType.TWO_TWO_ONE, "confidence": 0.6}
                
        elif zone_context == ZoneContext.OFFENSIVE:
            if circularity > 0.6 and formation_spread < 120:
                return {"formation_type": FormationType.ONE_THREE_ONE, "confidence": 0.7}
            elif linearity > 0.35 and formation_spread < 180:
                return {"formation_type": FormationType.TWO_TWO_ONE, "confidence": 0.6}
        
        # More generous fallback
        if linearity > 0.2:
            return {"formation_type": FormationType.ONE_TWO_TWO, "confidence": 0.4}
        elif circularity > 0.3:
            return {"formation_type": FormationType.ONE_THREE_ONE, "confidence": 0.4}
        
        return {"formation_type": FormationType.UNKNOWN, "confidence": 0.3}
    
    def _calculate_formation_confidence_relaxed(self, formation_match: Dict, 
                                              positions: List[Tuple[float, float]], 
                                              zone_context: ZoneContext) -> float:
        """Calculate confidence with relaxed scoring for real hockey data."""
        base_confidence = formation_match.get("confidence", 0.0)
        
        # Boost confidence based on player count
        player_count = len(positions)
        if player_count >= 5:
            completeness_score = 1.0
        elif player_count >= 4:
            completeness_score = 0.8
        else:
            completeness_score = 0.5
        
        # Zone appropriateness (relaxed)
        zone_scores = {
            FormationType.TWO_ONE_TWO: {ZoneContext.DEFENSIVE: 0.8, ZoneContext.NEUTRAL: 0.6, ZoneContext.OFFENSIVE: 0.4},
            FormationType.ONE_TWO_TWO: {ZoneContext.DEFENSIVE: 0.7, ZoneContext.NEUTRAL: 0.9, ZoneContext.OFFENSIVE: 0.6},
            FormationType.TWO_TWO_ONE: {ZoneContext.DEFENSIVE: 0.5, ZoneContext.NEUTRAL: 0.7, ZoneContext.OFFENSIVE: 0.8},
            FormationType.ONE_THREE_ONE: {ZoneContext.DEFENSIVE: 0.4, ZoneContext.NEUTRAL: 0.6, ZoneContext.OFFENSIVE: 0.9}
        }
        
        formation_type = formation_match["formation_type"]
        zone_score = zone_scores.get(formation_type, {}).get(zone_context, 0.5)
        
        # Combine scores with more weight to base confidence
        final_confidence = (base_confidence * 0.6 + completeness_score * 0.2 + zone_score * 0.2)
        
        return min(final_confidence, 1.0)
    
    def _assign_player_roles_relaxed(self, players: List[RoboflowPlayer], 
                                   formation_match: Dict, 
                                   formation_center: Tuple[float, float]) -> Dict[str, str]:
        """Assign player roles with relaxed criteria."""
        roles = {}
        
        formation_type = formation_match["formation_type"]
        
        # Sort players by distance from formation center
        player_distances = []
        for player in players:
            dist = math.sqrt((player.x - formation_center[0])**2 + (player.y - formation_center[1])**2)
            player_distances.append((player, dist))
        
        player_distances.sort(key=lambda x: x[1])
        
        # Assign roles based on formation type
        if formation_type == FormationType.TWO_ONE_TWO:
            roles = self._assign_2_1_2_roles_relaxed(player_distances)
        elif formation_type == FormationType.ONE_TWO_TWO:
            roles = self._assign_1_2_2_roles_relaxed(player_distances)
        elif formation_type == FormationType.TWO_TWO_ONE:
            roles = self._assign_2_2_1_roles_relaxed(player_distances)
        elif formation_type == FormationType.ONE_THREE_ONE:
            roles = self._assign_1_3_1_roles_relaxed(player_distances)
        else:
            # Default role assignment
            for i, (player, _) in enumerate(player_distances):
                roles[player.player_id] = f"Player_{i+1}"
        
        return roles
    
    def _assign_2_1_2_roles_relaxed(self, player_distances: List[Tuple[RoboflowPlayer, float]]) -> Dict[str, str]:
        """Assign roles for 2-1-2 formation with flexible player count."""
        roles = {}
        
        if len(player_distances) >= 5:
            roles[player_distances[0][0].player_id] = "Center"
            roles[player_distances[1][0].player_id] = "Defenseman_1"
            roles[player_distances[2][0].player_id] = "Defenseman_2"
            roles[player_distances[3][0].player_id] = "Wing_1"
            roles[player_distances[4][0].player_id] = "Wing_2"
        elif len(player_distances) >= 4:
            roles[player_distances[0][0].player_id] = "Center"
            roles[player_distances[1][0].player_id] = "Defenseman"
            roles[player_distances[2][0].player_id] = "Wing_1"
            roles[player_distances[3][0].player_id] = "Wing_2"
        
        return roles
    
    def _assign_1_2_2_roles_relaxed(self, player_distances: List[Tuple[RoboflowPlayer, float]]) -> Dict[str, str]:
        """Assign roles for 1-2-2 formation with flexible player count."""
        roles = {}
        
        if len(player_distances) >= 5:
            roles[player_distances[0][0].player_id] = "Center"
            roles[player_distances[1][0].player_id] = "Defenseman_1"
            roles[player_distances[2][0].player_id] = "Defenseman_2"
            roles[player_distances[3][0].player_id] = "Wing_1"
            roles[player_distances[4][0].player_id] = "Wing_2"
        elif len(player_distances) >= 4:
            roles[player_distances[0][0].player_id] = "Center"
            roles[player_distances[1][0].player_id] = "Defenseman"
            roles[player_distances[2][0].player_id] = "Wing_1"
            roles[player_distances[3][0].player_id] = "Wing_2"
        
        return roles
    
    def _assign_2_2_1_roles_relaxed(self, player_distances: List[Tuple[RoboflowPlayer, float]]) -> Dict[str, str]:
        """Assign roles for 2-2-1 formation with flexible player count."""
        roles = {}
        
        if len(player_distances) >= 5:
            roles[player_distances[0][0].player_id] = "Center"
            roles[player_distances[1][0].player_id] = "Defenseman_1"
            roles[player_distances[2][0].player_id] = "Defenseman_2"
            roles[player_distances[3][0].player_id] = "Wing_1"
            roles[player_distances[4][0].player_id] = "Wing_2"
        elif len(player_distances) >= 4:
            roles[player_distances[0][0].player_id] = "Center"
            roles[player_distances[1][0].player_id] = "Defenseman"
            roles[player_distances[2][0].player_id] = "Wing_1"
            roles[player_distances[3][0].player_id] = "Wing_2"
        
        return roles
    
    def _assign_1_3_1_roles_relaxed(self, player_distances: List[Tuple[RoboflowPlayer, float]]) -> Dict[str, str]:
        """Assign roles for 1-3-1 formation with flexible player count."""
        roles = {}
        
        if len(player_distances) >= 5:
            roles[player_distances[0][0].player_id] = "Center"
            roles[player_distances[1][0].player_id] = "Middle_1"
            roles[player_distances[2][0].player_id] = "Middle_2"
            roles[player_distances[3][0].player_id] = "Middle_3"
            roles[player_distances[4][0].player_id] = "Defenseman"
        elif len(player_distances) >= 4:
            roles[player_distances[0][0].player_id] = "Center"
            roles[player_distances[1][0].player_id] = "Middle_1"
            roles[player_distances[2][0].player_id] = "Middle_2"
            roles[player_distances[3][0].player_id] = "Defenseman"
        
        return roles
    
    def _calculate_formation_center(self, positions: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate the geometric center of the formation."""
        if not positions:
            return (0, 0)
            
        avg_x = sum(pos[0] for pos in positions) / len(positions)
        avg_y = sum(pos[1] for pos in positions) / len(positions)
        
        return (avg_x, avg_y)
    
    def _calculate_formation_spread(self, positions: List[Tuple[float, float]]) -> float:
        """Calculate how spread out the formation is."""
        if len(positions) < 2:
            return 0.0
            
        center = self._calculate_formation_center(positions)
        
        distances = []
        for pos in positions:
            distance = math.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
            distances.append(distance)
            
        return sum(distances) / len(distances)
    
    def _create_unknown_team_formation(self, team: str, reason: str) -> TeamFormation:
        """Create an unknown formation detection result for a team."""
        return TeamFormation(
            team=team,
            formation_type=FormationType.UNKNOWN,
            confidence=0.0,
            zone_context=ZoneContext.NEUTRAL,
            player_roles={},
            formation_shape=[],
            analysis_details={"reason": reason}
        )
