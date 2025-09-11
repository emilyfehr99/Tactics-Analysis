"""
Micro Tactical Analysis Module for Hockey

This module provides granular, player-level tactical analysis within formations,
including individual player behavior patterns, positioning vulnerabilities,
and specific tactical recommendations for exploiting weaknesses.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, NamedTuple
from dataclasses import dataclass
from enum import Enum
import logging
from scipy.spatial.distance import cdist
from scipy.stats import zscore
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlayerBehaviorType(Enum):
    """Types of player behaviors within formations."""
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    REACTIVE = "reactive"
    PROACTIVE = "proactive"
    STATIONARY = "stationary"
    ERRATIC = "erratic"
    PREDICTABLE = "predictable"


class VulnerabilityType(Enum):
    """Types of tactical vulnerabilities."""
    POSITIONING_GAP = "positioning_gap"
    SPEED_MISMATCH = "speed_mismatch"
    COVERAGE_WEAKNESS = "coverage_weakness"
    PREDICTABLE_MOVEMENT = "predictable_movement"
    ISOLATION = "isolation"
    OVERCOMMITMENT = "overcommitment"
    UNDERCOMMITMENT = "undercommitment"
    TRANSITION_SLOW = "transition_slow"
    ANTICIPATION_POOR = "anticipation_poor"


@dataclass
class PlayerMicroAnalysis:
    """Detailed analysis of individual player within formation."""
    player_id: str
    position_in_formation: str  # e.g., "center_forward", "left_defense"
    behavior_type: PlayerBehaviorType
    movement_pattern: str
    speed_consistency: float  # 0.0 to 1.0
    positioning_accuracy: float  # 0.0 to 1.0
    vulnerability_score: float  # 0.0 to 1.0 (higher = more vulnerable)
    vulnerabilities: List[VulnerabilityType]
    tactical_notes: List[str]
    exploitation_opportunities: List[str]


@dataclass
class FormationMicroAnalysis:
    """Micro-level analysis of entire formation."""
    formation_name: str
    player_analyses: List[PlayerMicroAnalysis]
    formation_cohesion: float  # 0.0 to 1.0
    tactical_effectiveness: float  # 0.0 to 1.0
    key_vulnerabilities: List[str]
    exploitation_strategies: List[str]
    specific_recommendations: List[str]


class MicroTacticalAnalyzer:
    """
    Provides granular tactical analysis at the player level within formations.
    
    Analyzes individual player behaviors, positioning, and vulnerabilities
    to provide specific tactical insights and exploitation opportunities.
    """
    
    def __init__(self, rink_dimensions: Tuple[int, int] = (1400, 600)):
        """
        Initialize the micro tactical analyzer.
        
        Args:
            rink_dimensions: Tuple of (width, height) for the rink image
        """
        self.rink_width, self.rink_height = rink_dimensions
        
        # Define behavioral thresholds
        self.behavior_thresholds = {
            'aggressive_speed': 0.7,  # High movement speed
            'conservative_speed': 0.3,  # Low movement speed
            'erratic_variance': 0.4,  # High variance in movement
            'predictable_variance': 0.1  # Low variance in movement
        }
        
        # Define vulnerability thresholds
        self.vulnerability_thresholds = {
            'isolation_distance': 300,  # Distance indicating isolation
            'coverage_gap': 200,  # Gap in coverage
            'speed_mismatch': 0.5,  # Speed difference threshold
            'positioning_error': 150  # Positioning accuracy threshold
        }
    
    def analyze_formation_micro_details(
        self, 
        formation_data: Dict[str, Any],
        player_positions: List[Dict[str, Any]],
        team_id: str = "Team B"
    ) -> FormationMicroAnalysis:
        """
        Perform micro-level analysis of a formation.
        
        Args:
            formation_data: Formation detection results
            player_positions: List of player position data
            team_id: Team to analyze
            
        Returns:
            Detailed micro-analysis of the formation
        """
        logger.info(f"Performing micro analysis of {formation_data['formation']} formation")
        
        # Filter players by team
        team_players = [p for p in player_positions if p.get('team', '').startswith(team_id)]
        
        if not team_players:
            logger.warning(f"No players found for team {team_id}")
            return None
        
        # Analyze each player individually
        player_analyses = []
        for player in team_players:
            player_analysis = self._analyze_individual_player(player, formation_data)
            if player_analysis:
                player_analyses.append(player_analysis)
        
        # Analyze formation-level patterns
        formation_cohesion = self._calculate_formation_cohesion(team_players)
        tactical_effectiveness = self._calculate_tactical_effectiveness(player_analyses)
        
        # Generate specific tactical insights
        key_vulnerabilities = self._identify_key_vulnerabilities(player_analyses)
        exploitation_strategies = self._generate_exploitation_strategies(player_analyses, formation_data)
        specific_recommendations = self._generate_specific_recommendations(player_analyses, formation_data)
        
        return FormationMicroAnalysis(
            formation_name=formation_data['formation'],
            player_analyses=player_analyses,
            formation_cohesion=formation_cohesion,
            tactical_effectiveness=tactical_effectiveness,
            key_vulnerabilities=key_vulnerabilities,
            exploitation_strategies=exploitation_strategies,
            specific_recommendations=specific_recommendations
        )
    
    def _analyze_individual_player(
        self, 
        player_data: Dict[str, Any], 
        formation_data: Dict[str, Any]
    ) -> PlayerMicroAnalysis:
        """Analyze individual player behavior and positioning."""
        
        player_id = player_data.get('player_id', 'unknown')
        position = player_data.get('rink_position', {})
        x, y = position.get('x', 0), position.get('y', 0)
        
        # Determine position within formation
        position_in_formation = self._determine_position_in_formation(x, y, formation_data)
        
        # Analyze behavior type
        behavior_type = self._analyze_player_behavior(player_data)
        
        # Calculate movement patterns
        movement_pattern = self._analyze_movement_pattern(player_data)
        
        # Calculate consistency metrics
        speed_consistency = self._calculate_speed_consistency(player_data)
        positioning_accuracy = self._calculate_positioning_accuracy(player_data, formation_data)
        
        # Identify vulnerabilities
        vulnerabilities = self._identify_player_vulnerabilities(player_data, formation_data)
        vulnerability_score = len(vulnerabilities) / len(list(VulnerabilityType))
        
        # Generate tactical notes
        tactical_notes = self._generate_tactical_notes(player_data, behavior_type, vulnerabilities)
        
        # Generate exploitation opportunities
        exploitation_opportunities = self._generate_exploitation_opportunities(
            player_data, behavior_type, vulnerabilities, formation_data
        )
        
        return PlayerMicroAnalysis(
            player_id=player_id,
            position_in_formation=position_in_formation,
            behavior_type=behavior_type,
            movement_pattern=movement_pattern,
            speed_consistency=speed_consistency,
            positioning_accuracy=positioning_accuracy,
            vulnerability_score=vulnerability_score,
            vulnerabilities=vulnerabilities,
            tactical_notes=tactical_notes,
            exploitation_opportunities=exploitation_opportunities
        )
    
    def _determine_position_in_formation(self, x: float, y: float, formation_data: Dict[str, Any]) -> str:
        """Determine player's role within the formation."""
        formation = formation_data.get('formation', '')
        
        # Normalize coordinates
        norm_x = x / self.rink_width
        norm_y = y / self.rink_height
        
        if formation == "1-3-1":
            if norm_x > 0.7:  # Offensive zone
                if norm_y < 0.3:
                    return "high_forward"
                elif norm_y > 0.7:
                    return "low_forward"
                else:
                    return "center_forward"
            elif 0.3 <= norm_x <= 0.7:  # Neutral zone
                if norm_y < 0.3:
                    return "left_midfield"
                elif norm_y > 0.7:
                    return "right_midfield"
                else:
                    return "center_midfield"
            else:  # Defensive zone
                return "defense"
        
        elif formation == "2-1-2":
            if norm_x > 0.6:  # Offensive side of neutral
                if norm_y < 0.4:
                    return "left_forward"
                elif norm_y > 0.6:
                    return "right_forward"
                else:
                    return "center_forward"
            elif norm_x < 0.4:  # Defensive side of neutral
                if norm_y < 0.4:
                    return "left_defense"
                elif norm_y > 0.6:
                    return "right_defense"
                else:
                    return "center_defense"
            else:  # Center neutral
                return "center_midfield"
        
        return "unknown_position"
    
    def _analyze_player_behavior(self, player_data: Dict[str, Any]) -> PlayerBehaviorType:
        """Analyze player behavior type based on movement patterns."""
        speed = abs(player_data.get('speed', 0))
        speed_ma = abs(player_data.get('speed_ma', 0))
        
        # Calculate movement variance (would need multiple frames for this)
        # For now, use speed as proxy
        if speed > self.behavior_thresholds['aggressive_speed']:
            return PlayerBehaviorType.AGGRESSIVE
        elif speed < self.behavior_thresholds['conservative_speed']:
            return PlayerBehaviorType.CONSERVATIVE
        elif abs(speed - speed_ma) > 0.3:  # High variance
            return PlayerBehaviorType.ERRATIC
        elif abs(speed - speed_ma) < 0.1:  # Low variance
            return PlayerBehaviorType.PREDICTABLE
        else:
            return PlayerBehaviorType.REACTIVE
    
    def _analyze_movement_pattern(self, player_data: Dict[str, Any]) -> str:
        """Analyze player movement pattern."""
        speed = abs(player_data.get('speed', 0))
        
        if speed < 0.1:
            return "stationary"
        elif speed < 0.3:
            return "slow_controlled"
        elif speed < 0.6:
            return "moderate_movement"
        else:
            return "aggressive_movement"
    
    def _calculate_speed_consistency(self, player_data: Dict[str, Any]) -> float:
        """Calculate speed consistency (higher = more consistent)."""
        speed = abs(player_data.get('speed', 0))
        speed_ma = abs(player_data.get('speed_ma', 0))
        
        if speed_ma == 0:
            return 1.0
        
        variance = abs(speed - speed_ma) / speed_ma
        return max(0.0, 1.0 - variance)
    
    def _calculate_positioning_accuracy(self, player_data: Dict[str, Any], formation_data: Dict[str, Any]) -> float:
        """Calculate positioning accuracy within formation."""
        # This would require comparing to ideal formation positions
        # For now, return a placeholder based on team confidence
        team_confidence = player_data.get('team_confidence', 0.5)
        return team_confidence
    
    def _identify_player_vulnerabilities(
        self, 
        player_data: Dict[str, Any], 
        formation_data: Dict[str, Any]
    ) -> List[VulnerabilityType]:
        """Identify specific vulnerabilities for this player."""
        vulnerabilities = []
        
        speed = abs(player_data.get('speed', 0))
        position = player_data.get('rink_position', {})
        x, y = position.get('x', 0), position.get('y', 0)
        
        # Check for isolation
        if self._is_player_isolated(player_data, formation_data):
            vulnerabilities.append(VulnerabilityType.ISOLATION)
        
        # Check for speed mismatch
        if speed < 0.2:  # Very slow
            vulnerabilities.append(VulnerabilityType.SPEED_MISMATCH)
        
        # Check for predictable movement
        if self._is_movement_predictable(player_data):
            vulnerabilities.append(VulnerabilityType.PREDICTABLE_MOVEMENT)
        
        # Check for poor positioning
        if not self._is_position_optimal(player_data, formation_data):
            vulnerabilities.append(VulnerabilityType.POSITIONING_GAP)
        
        return vulnerabilities
    
    def _is_player_isolated(self, player_data: Dict[str, Any], formation_data: Dict[str, Any]) -> bool:
        """Check if player is isolated from teammates."""
        # This would require distance calculations to other players
        # For now, use a simple heuristic
        position = player_data.get('rink_position', {})
        x, y = position.get('x', 0), position.get('y', 0)
        
        # Check if player is in extreme positions
        norm_x = x / self.rink_width
        norm_y = y / self.rink_height
        
        # Players at rink edges might be isolated
        return norm_x < 0.1 or norm_x > 0.9 or norm_y < 0.1 or norm_y > 0.9
    
    def _is_movement_predictable(self, player_data: Dict[str, Any]) -> bool:
        """Check if player movement is predictable."""
        speed = abs(player_data.get('speed', 0))
        speed_ma = abs(player_data.get('speed_ma', 0))
        
        # Low variance in speed suggests predictable movement
        if speed_ma > 0:
            variance = abs(speed - speed_ma) / speed_ma
            return variance < 0.1
        
        return True  # If no movement data, assume predictable
    
    def _is_position_optimal(self, player_data: Dict[str, Any], formation_data: Dict[str, Any]) -> bool:
        """Check if player position is optimal for formation."""
        # This would require comparing to ideal formation positions
        # For now, return True as placeholder
        return True
    
    def _generate_tactical_notes(
        self, 
        player_data: Dict[str, Any], 
        behavior_type: PlayerBehaviorType,
        vulnerabilities: List[VulnerabilityType]
    ) -> List[str]:
        """Generate specific tactical notes about the player."""
        notes = []
        
        player_id = player_data.get('player_id', 'unknown')
        position = player_data.get('rink_position', {})
        x, y = position.get('x', 0), position.get('y', 0)
        
        # Behavior-based notes
        if behavior_type == PlayerBehaviorType.CONSERVATIVE:
            notes.append(f"Player {player_id} shows conservative positioning - opportunities to exploit with speed")
        elif behavior_type == PlayerBehaviorType.AGGRESSIVE:
            notes.append(f"Player {player_id} is aggressive - potential to draw them out of position")
        elif behavior_type == PlayerBehaviorType.ERRATIC:
            notes.append(f"Player {player_id} shows erratic movement - unpredictable but potentially exploitable")
        
        # Vulnerability-based notes
        for vuln in vulnerabilities:
            if vuln == VulnerabilityType.ISOLATION:
                notes.append(f"Player {player_id} appears isolated - opportunity for quick passing play")
            elif vuln == VulnerabilityType.SPEED_MISMATCH:
                notes.append(f"Player {player_id} moving slowly - can be beaten with speed through neutral zone")
            elif vuln == VulnerabilityType.PREDICTABLE_MOVEMENT:
                notes.append(f"Player {player_id} shows predictable patterns - easy to anticipate and counter")
        
        return notes
    
    def _generate_exploitation_opportunities(
        self,
        player_data: Dict[str, Any],
        behavior_type: PlayerBehaviorType,
        vulnerabilities: List[VulnerabilityType],
        formation_data: Dict[str, Any]
    ) -> List[str]:
        """Generate specific exploitation opportunities."""
        opportunities = []
        
        player_id = player_data.get('player_id', 'unknown')
        formation = formation_data.get('formation', '')
        
        # Conservative player exploitation
        if behavior_type == PlayerBehaviorType.CONSERVATIVE:
            if formation == "1-3-1":
                opportunities.append(f"Conservative center in 1-3-1 neutral zone - beat him with quick lateral passes")
                opportunities.append(f"Player {player_id} holds position - exploit with speed through his zone")
        
        # Aggressive player exploitation
        elif behavior_type == PlayerBehaviorType.AGGRESSIVE:
            opportunities.append(f"Aggressive player {player_id} - draw them out of position with puck movement")
            opportunities.append(f"Use player {player_id}'s aggression against them - create 2-on-1 situations")
        
        # Vulnerability-specific opportunities
        for vuln in vulnerabilities:
            if vuln == VulnerabilityType.ISOLATION:
                opportunities.append(f"Isolated player {player_id} - quick passing play to exploit gap")
            elif vuln == VulnerabilityType.SPEED_MISMATCH:
                opportunities.append(f"Slow player {player_id} - speed through neutral zone to beat him")
            elif vuln == VulnerabilityType.PREDICTABLE_MOVEMENT:
                opportunities.append(f"Predictable player {player_id} - use misdirection to create scoring chances")
        
        return opportunities
    
    def _calculate_formation_cohesion(self, team_players: List[Dict[str, Any]]) -> float:
        """Calculate how well players work together as a unit."""
        if len(team_players) < 2:
            return 1.0
        
        # Calculate average distance between players (lower = more cohesive)
        positions = [(p.get('rink_position', {}).get('x', 0), p.get('rink_position', {}).get('y', 0)) 
                    for p in team_players]
        
        total_distance = 0
        count = 0
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = np.sqrt((positions[i][0] - positions[j][0])**2 + 
                              (positions[i][1] - positions[j][1])**2)
                total_distance += dist
                count += 1
        
        if count == 0:
            return 1.0
        
        avg_distance = total_distance / count
        # Normalize to 0-1 scale (closer players = higher cohesion)
        max_expected_distance = np.sqrt(self.rink_width**2 + self.rink_height**2)
        cohesion = max(0.0, 1.0 - (avg_distance / max_expected_distance))
        
        return cohesion
    
    def _calculate_tactical_effectiveness(self, player_analyses: List[PlayerMicroAnalysis]) -> float:
        """Calculate overall tactical effectiveness of the formation."""
        if not player_analyses:
            return 0.0
        
        # Average of individual player effectiveness
        total_effectiveness = 0.0
        for analysis in player_analyses:
            # Effectiveness = high positioning accuracy + low vulnerability
            effectiveness = (analysis.positioning_accuracy + (1.0 - analysis.vulnerability_score)) / 2.0
            total_effectiveness += effectiveness
        
        return total_effectiveness / len(player_analyses)
    
    def _identify_key_vulnerabilities(self, player_analyses: List[PlayerMicroAnalysis]) -> List[str]:
        """Identify the most critical vulnerabilities in the formation."""
        vulnerabilities = []
        
        for analysis in player_analyses:
            if analysis.vulnerability_score > 0.7:  # High vulnerability
                vuln_desc = f"Player {analysis.player_id} ({analysis.position_in_formation}) shows high vulnerability"
                if VulnerabilityType.ISOLATION in analysis.vulnerabilities:
                    vuln_desc += " - isolated positioning creates gaps"
                if VulnerabilityType.SPEED_MISMATCH in analysis.vulnerabilities:
                    vuln_desc += " - slow movement creates speed advantages"
                if VulnerabilityType.PREDICTABLE_MOVEMENT in analysis.vulnerabilities:
                    vuln_desc += " - predictable patterns are easily countered"
                
                vulnerabilities.append(vuln_desc)
        
        return vulnerabilities
    
    def _generate_exploitation_strategies(
        self, 
        player_analyses: List[PlayerMicroAnalysis], 
        formation_data: Dict[str, Any]
    ) -> List[str]:
        """Generate specific strategies to exploit formation weaknesses."""
        strategies = []
        formation = formation_data.get('formation', '')
        
        # Analyze conservative players
        conservative_players = [p for p in player_analyses if p.behavior_type == PlayerBehaviorType.CONSERVATIVE]
        if conservative_players:
            strategies.append(f"Conservative players detected - use speed and quick passing to exploit their positioning")
        
        # Analyze isolated players
        isolated_players = [p for p in player_analyses if VulnerabilityType.ISOLATION in p.vulnerabilities]
        if isolated_players:
            strategies.append(f"Isolated players create passing lanes - exploit with quick puck movement")
        
        # Formation-specific strategies
        if formation == "1-3-1":
            center_midfield = [p for p in player_analyses if p.position_in_formation == "center_midfield"]
            if center_midfield and center_midfield[0].behavior_type == PlayerBehaviorType.CONSERVATIVE:
                strategies.append(f"Conservative center in 1-3-1 neutral zone - beat him with quick lateral passes and speed through the middle")
        
        elif formation == "2-1-2":
            slow_players = [p for p in player_analyses if VulnerabilityType.SPEED_MISMATCH in p.vulnerabilities]
            if slow_players:
                strategies.append(f"Slow players in 2-1-2 trap - use speed through neutral zone to break the trap")
        
        return strategies
    
    def _generate_specific_recommendations(
        self, 
        player_analyses: List[PlayerMicroAnalysis], 
        formation_data: Dict[str, Any]
    ) -> List[str]:
        """Generate specific tactical recommendations."""
        recommendations = []
        
        for analysis in player_analyses:
            if analysis.vulnerability_score > 0.6:
                rec = f"Target player {analysis.player_id} ({analysis.position_in_formation}) - "
                
                if VulnerabilityType.SPEED_MISMATCH in analysis.vulnerabilities:
                    rec += "use speed to beat them through neutral zone"
                elif VulnerabilityType.ISOLATION in analysis.vulnerabilities:
                    rec += "exploit their isolated positioning with quick passes"
                elif VulnerabilityType.PREDICTABLE_MOVEMENT in analysis.vulnerabilities:
                    rec += "use misdirection to counter their predictable patterns"
                
                recommendations.append(rec)
        
        return recommendations
