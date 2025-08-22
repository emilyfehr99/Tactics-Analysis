"""
Tactical Weakness Detection Module for Hockey Analysis

This module analyzes the quality and effectiveness of hockey formations by detecting:
- Gaps in coverage and positioning
- Formation breakdowns and weaknesses
- Behavioral patterns that create vulnerabilities
- Tactical recommendations for improvement
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, NamedTuple
from dataclasses import dataclass
from enum import Enum
import logging
from scipy.spatial.distance import cdist
from scipy.stats import zscore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeaknessType(Enum):
    """Types of tactical weaknesses that can be detected."""
    COVERAGE_GAP = "coverage_gap"
    POOR_POSITIONING = "poor_positioning"
    FORMATION_BREAKDOWN = "formation_breakdown"
    ISOLATION = "isolation"
    OVERCOMMITMENT = "overcommitment"
    WEAK_SIDE_VULNERABILITY = "weak_side_vulnerability"
    TRANSITION_SLOW = "transition_slow"
    PRESSURE_INCONSISTENT = "pressure_inconsistent"
    CRITICAL = "critical"


class CoverageQuality(Enum):
    """Quality levels for defensive coverage."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class TacticalWeakness:
    """Represents a detected tactical weakness."""
    weakness_type: WeaknessType
    severity: float  # 0.0 to 1.0 (1.0 = most severe)
    description: str
    affected_players: List[int]
    zone: str
    frame_range: Tuple[int, int]
    recommendations: List[str]
    metrics: Dict[str, float]


@dataclass
class FormationQuality:
    """Overall quality assessment of a formation."""
    formation_name: str
    overall_score: float  # 0.0 to 1.0
    coverage_quality: CoverageQuality
    weaknesses: List[TacticalWeakness]
    strengths: List[str]
    improvement_areas: List[str]
    tactical_insights: List[str]


class TacticalWeaknessDetector:
    """
    Detects tactical weaknesses and analyzes formation quality.
    
    Analyzes player positioning, coverage gaps, and behavioral patterns
    to identify areas for tactical improvement.
    """
    
    def __init__(self, rink_dimensions: Tuple[int, int] = (1400, 600)):
        """
        Initialize the tactical weakness detector.
        
        Args:
            rink_dimensions: Tuple of (width, height) for the rink image
        """
        self.rink_width, self.rink_height = rink_dimensions
        
        # Define coverage standards for different formations
        self.coverage_standards = self._initialize_coverage_standards()
        
        # Define critical distances for analysis
        self.critical_distances = {
            'max_gap': 200,  # Maximum acceptable gap between players
            'min_coverage': 150,  # Minimum distance for effective coverage
            'isolation_threshold': 250,  # Distance that indicates isolation
            'transition_time': 3  # Frames to transition between formations
        }
    
    def _initialize_coverage_standards(self) -> Dict[str, Dict]:
        """Initialize coverage standards for different formations."""
        standards = {}
        
        # 1-2-2 Formation standards
        standards["1-2-2"] = {
            "defensive_coverage": {
                "max_gap": 180,  # Maximum gap between D-men
                "min_pressure": 120,  # Minimum pressure on puck carrier
                "weak_side_coverage": 160,  # Coverage on weak side
                "net_front_protection": 100  # Protection in front of net
            },
            "neutral_zone": {
                "gap_control": 200,  # Control gaps in neutral zone
                "pressure_points": 3  # Number of pressure points
            },
            "common_weaknesses": [
                "Gap between defensemen too wide",
                "Weak side forward not providing support",
                "Center not backchecking effectively",
                "Defensemen not communicating on switches"
            ]
        }
        
        # 2-1-2 Formation standards
        standards["2-1-2"] = {
            "neutral_zone": {
                "trap_efficiency": 0.8,  # Efficiency of neutral zone trap
                "pressure_coordination": 0.7,  # Coordination of pressure
                "gap_control": 180
            },
            "common_weaknesses": [
                "Forwards not maintaining trap pressure",
                "Center not reading play effectively",
                "Defensemen too aggressive in neutral zone",
                "Lack of coordinated pressure"
            ]
        }
        
        # 1-3-1 Formation standards
        standards["1-3-1"] = {
            "offensive_zone": {
                "pressure_maintenance": 0.8,  # Maintaining offensive pressure
                "puck_retrieval": 0.7,  # Efficiency of puck retrieval
                "net_front_presence": 0.9  # Presence in front of net
            },
            "common_weaknesses": [
                "Point man not moving enough",
                "Net front presence too static",
                "Wings not cycling effectively",
                "Lack of coordinated pressure"
            ]
        }
        
        return standards
    
    def analyze_formation_quality(
        self, 
        formation_name: str,
        players: List[Dict],
        frame_data: List[Dict],
        frame_range: Tuple[int, int]
    ) -> FormationQuality:
        """
        Analyze the overall quality of a formation execution.
        
        Args:
            formation_name: Name of the detected formation
            players: Current frame players
            frame_data: All frame data for analysis
            frame_range: Range of frames where formation is active
            
        Returns:
            FormationQuality object with detailed analysis
        """
        weaknesses = []
        strengths = []
        improvement_areas = []
        tactical_insights = []
        
        # Analyze coverage gaps
        coverage_gaps = self._detect_coverage_gaps(formation_name, players)
        weaknesses.extend(coverage_gaps)
        
        # Analyze positioning quality
        positioning_issues = self._analyze_positioning_quality(formation_name, players)
        weaknesses.extend(positioning_issues)
        
        # Analyze formation consistency
        consistency_issues = self._analyze_formation_consistency(
            formation_name, frame_data, frame_range
        )
        weaknesses.extend(consistency_issues)
        
        # Analyze pressure patterns
        pressure_analysis = self._analyze_pressure_patterns(
            formation_name, frame_data, frame_range
        )
        weaknesses.extend(pressure_analysis)
        
        # Calculate overall quality score
        overall_score = self._calculate_quality_score(weaknesses)
        
        # Determine coverage quality
        coverage_quality = self._determine_coverage_quality(overall_score)
        
        # Generate strengths and improvement areas
        strengths = self._identify_strengths(formation_name, players, weaknesses)
        improvement_areas = self._identify_improvement_areas(weaknesses)
        tactical_insights = self._generate_tactical_insights(formation_name, weaknesses)
        
        return FormationQuality(
            formation_name=formation_name,
            overall_score=overall_score,
            coverage_quality=coverage_quality,
            weaknesses=weaknesses,
            strengths=strengths,
            improvement_areas=improvement_areas,
            tactical_insights=tactical_insights
        )
    
    def _detect_coverage_gaps(
        self, 
        formation_name: str, 
        players: List[Dict]
    ) -> List[TacticalWeakness]:
        """Detect gaps in defensive coverage."""
        weaknesses = []
        
        if formation_name == "1-2-2":
            # Analyze defensive zone coverage gaps
            defensive_players = [p for p in players if p.get('zone') == 'defensive']
            
            if len(defensive_players) >= 2:
                # Check gap between defensemen
                d_positions = [(p['x'], p['y']) for p in defensive_players if p.get('type') == 'defense']
                
                if len(d_positions) >= 2:
                    distances = []
                    for i in range(len(d_positions)):
                        for j in range(i + 1, len(d_positions)):
                            dist = np.linalg.norm(
                                np.array(d_positions[i]) - np.array(d_positions[j])
                            )
                            distances.append(dist)
                    
                    max_gap = max(distances) if distances else 0
                    if max_gap > self.coverage_standards["1-2-2"]["defensive_coverage"]["max_gap"]:
                        weaknesses.append(TacticalWeakness(
                            weakness_type=WeaknessType.COVERAGE_GAP,
                            severity=min(max_gap / 300, 1.0),  # Normalize severity
                            description=f"Gap between defensemen too wide ({max_gap:.0f}px)",
                            affected_players=[p['player_id'] for p in defensive_players if p.get('type') == 'defense'],
                            zone="defensive",
                            frame_range=(0, 0),  # Will be updated by caller
                            recommendations=[
                                "Defensemen should communicate better on switches",
                                "Maintain tighter gap control in defensive zone",
                                "Use active stick positioning to control space"
                            ],
                            metrics={"max_gap": max_gap, "acceptable_gap": 180}
                        ))
        
        elif formation_name == "2-1-2":
            # Analyze neutral zone trap gaps
            neutral_players = [p for p in players if p.get('zone') == 'neutral']
            
            if len(neutral_players) >= 3:
                # Check if trap is properly set
                trap_efficiency = self._calculate_trap_efficiency(neutral_players)
                if trap_efficiency < self.coverage_standards["2-1-2"]["neutral_zone"]["trap_efficiency"]:
                    weaknesses.append(TacticalWeakness(
                        weakness_type=WeaknessType.FORMATION_BREAKDOWN,
                        severity=1.0 - trap_efficiency,
                        description="Neutral zone trap not properly executed",
                        affected_players=[p['player_id'] for p in neutral_players],
                        zone="neutral",
                        frame_range=(0, 0),
                        recommendations=[
                            "Forwards must maintain consistent pressure",
                            "Center should read play and adjust position",
                            "Coordinate pressure to maintain trap integrity"
                        ],
                        metrics={"trap_efficiency": trap_efficiency, "target": 0.8}
                    ))
        
        return weaknesses
    
    def _analyze_positioning_quality(
        self, 
        formation_name: str, 
        players: List[Dict]
    ) -> List[TacticalWeakness]:
        """Analyze the quality of player positioning within the formation."""
        weaknesses = []
        
        if formation_name == "1-2-2":
            # Check if forwards are providing proper support
            defensive_players = [p for p in players if p.get('zone') == 'defensive']
            weak_side_forward = None
            
            for player in defensive_players:
                if player.get('type') == 'forward' and player.get('side') == 'weak':
                    weak_side_forward = player
                    break
            
            if weak_side_forward:
                # Check if weak side forward is too far from play
                net_position = (self.rink_width * 0.85, self.rink_height * 0.5)
                forward_distance = np.linalg.norm(
                    np.array([weak_side_forward['x'], weak_side_forward['y']]) - 
                    np.array(net_position)
                )
                
                if forward_distance > self.coverage_standards["1-2-2"]["defensive_coverage"]["weak_side_coverage"]:
                    weaknesses.append(TacticalWeakness(
                        weakness_type=WeaknessType.POOR_POSITIONING,
                        severity=min(forward_distance / 300, 1.0),
                        description="Weak side forward not providing proper support",
                        affected_players=[weak_side_forward['player_id']],
                        zone="defensive",
                        frame_range=(0, 0),
                        recommendations=[
                            "Weak side forward should stay closer to net",
                            "Provide support for defensemen on switches",
                            "Maintain defensive zone awareness"
                        ],
                        metrics={"distance_to_net": forward_distance, "acceptable": 160}
                    ))
        
        return weaknesses
    
    def _analyze_formation_consistency(
        self, 
        formation_name: str, 
        frame_data: List[Dict], 
        frame_range: Tuple[int, int]
    ) -> List[TacticalWeakness]:
        """Analyze how consistently the formation is maintained over time."""
        weaknesses = []
        start_frame, end_frame = frame_range
        
        # Check formation stability
        formation_changes = 0
        for frame_idx in range(start_frame, min(end_frame + 1, len(frame_data))):
            if frame_idx < len(frame_data) and 'players' in frame_data[frame_idx]:
                players = frame_data[frame_idx]['players']
                detected_formation = self._quick_formation_check(formation_name, players)
                if not detected_formation:
                    formation_changes += 1
        
        total_frames = end_frame - start_frame + 1
        consistency_rate = 1.0 - (formation_changes / total_frames)
        
        if consistency_rate < 0.8:  # Less than 80% consistent
            weaknesses.append(TacticalWeakness(
                weakness_type=WeaknessType.FORMATION_BREAKDOWN,
                severity=1.0 - consistency_rate,
                description=f"Formation not consistently maintained ({consistency_rate:.1%} consistency)",
                affected_players=[],  # Affects entire team
                zone="all",
                frame_range=frame_range,
                recommendations=[
                    "Improve formation discipline and communication",
                    "Practice formation transitions more frequently",
                    "Ensure all players understand their roles"
                ],
                metrics={"consistency_rate": consistency_rate, "target": 0.8}
            ))
        
        return weaknesses
    
    def _analyze_pressure_patterns(
        self, 
        formation_name: str, 
        frame_data: List[Dict], 
        frame_range: Tuple[int, int]
    ) -> List[TacticalWeakness]:
        """Analyze pressure patterns and identify inconsistencies."""
        weaknesses = []
        start_frame, end_frame = frame_range
        
        if formation_name == "1-3-1":
            # Analyze offensive pressure consistency
            pressure_scores = []
            for frame_idx in range(start_frame, min(end_frame + 1, len(frame_data))):
                if frame_idx < len(frame_data) and 'players' in frame_data[frame_idx]:
                    players = frame_data[frame_idx]['players']
                    pressure_score = self._calculate_offensive_pressure(players)
                    pressure_scores.append(pressure_score)
            
            if pressure_scores:
                pressure_variance = np.var(pressure_scores)
                if pressure_variance > 0.1:  # High variance indicates inconsistency
                    weaknesses.append(TacticalWeakness(
                        weakness_type=WeaknessType.PRESSURE_INCONSISTENT,
                        severity=min(pressure_variance, 1.0),
                        description="Offensive pressure not consistently maintained",
                        affected_players=[],  # Affects entire offensive unit
                        zone="offensive",
                        frame_range=frame_range,
                        recommendations=[
                            "Maintain consistent pressure on defense",
                            "Coordinate offensive zone cycling",
                            "Avoid periods of low pressure"
                        ],
                        metrics={"pressure_variance": pressure_variance, "target": 0.05}
                    ))
        
        return weaknesses
    
    def _calculate_trap_efficiency(self, neutral_players: List[Dict]) -> float:
        """Calculate the efficiency of a neutral zone trap."""
        if len(neutral_players) < 3:
            return 0.0
        
        # Calculate how well players are positioned to control neutral zone
        positions = [(p['x'], p['y']) for p in neutral_players]
        
        # Check if players form a triangle (good trap formation)
        if len(positions) >= 3:
            # Calculate area of triangle formed by players
            # Simple area calculation for triangle
            x_coords = [pos[0] for pos in positions[:3]]
            y_coords = [pos[1] for pos in positions[:3]]
            
            # Area = 0.5 * |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|
            area = 0.5 * abs(
                x_coords[0] * (y_coords[1] - y_coords[2]) +
                x_coords[1] * (y_coords[2] - y_coords[0]) +
                x_coords[2] * (y_coords[0] - y_coords[1])
            )
            
            # Normalize area (smaller area = better trap)
            max_area = (self.rink_width * 0.34) * (self.rink_height * 0.8) * 0.5
            efficiency = max(0.0, 1.0 - (area / max_area))
            
            return efficiency
        
        return 0.5  # Default efficiency
    
    def _calculate_offensive_pressure(self, players: List[Dict]) -> float:
        """Calculate offensive pressure score."""
        offensive_players = [p for p in players if p.get('zone') == 'offensive']
        
        if not offensive_players:
            return 0.0
        
        # Calculate pressure based on proximity to net and puck
        pressure_scores = []
        net_position = (self.rink_width * 0.15, self.rink_height * 0.5)
        
        for player in offensive_players:
            # Distance to net (closer = higher pressure)
            distance_to_net = np.linalg.norm(
                np.array([player['x'], player['y']]) - np.array(net_position)
            )
            
            # Normalize distance (0 = at net, 1 = far from net)
            normalized_distance = distance_to_net / (self.rink_width * 0.33)
            pressure_score = max(0.0, 1.0 - normalized_distance)
            
            pressure_scores.append(pressure_score)
        
        return np.mean(pressure_scores) if pressure_scores else 0.0
    
    def _quick_formation_check(self, formation_name: str, players: List[Dict]) -> bool:
        """Quick check if formation is still active in a frame."""
        # Simplified formation check for consistency analysis
        zone_counts = {}
        for player in players:
            zone = player.get('zone', 'unknown')
            zone_counts[zone] = zone_counts.get(zone, 0) + 1
        
        if formation_name == "1-2-2":
            return zone_counts.get('defensive', 0) >= 3
        elif formation_name == "2-1-2":
            return zone_counts.get('neutral', 0) >= 3
        elif formation_name == "1-3-1":
            return zone_counts.get('offensive', 0) >= 3
        
        return False
    
    def _calculate_quality_score(self, weaknesses: List[TacticalWeakness]) -> float:
        """Calculate overall quality score based on detected weaknesses."""
        if not weaknesses:
            return 1.0
        
        # Weight weaknesses by severity and type
        total_penalty = 0.0
        for weakness in weaknesses:
            if weakness.weakness_type == WeaknessType.CRITICAL:
                penalty = weakness.severity * 0.4
            elif weakness.weakness_type == WeaknessType.COVERAGE_GAP:
                penalty = weakness.severity * 0.3
            elif weakness.weakness_type == WeaknessType.POOR_POSITIONING:
                penalty = weakness.severity * 0.2
            else:
                penalty = weakness.severity * 0.1
            
            total_penalty += penalty
        
        # Cap total penalty at 0.8 (minimum score of 0.2)
        total_penalty = min(total_penalty, 0.8)
        
        return 1.0 - total_penalty
    
    def _determine_coverage_quality(self, score: float) -> CoverageQuality:
        """Determine coverage quality based on overall score."""
        if score >= 0.9:
            return CoverageQuality.EXCELLENT
        elif score >= 0.8:
            return CoverageQuality.GOOD
        elif score >= 0.6:
            return CoverageQuality.FAIR
        elif score >= 0.4:
            return CoverageQuality.POOR
        else:
            return CoverageQuality.CRITICAL
    
    def _identify_strengths(
        self, 
        formation_name: str, 
        players: List[Dict], 
        weaknesses: List[TacticalWeakness]
    ) -> List[str]:
        """Identify strengths based on what weaknesses are NOT present."""
        strengths = []
        
        # Check for strengths based on formation type
        if formation_name == "1-2-2":
            if not any(w.weakness_type == WeaknessType.COVERAGE_GAP for w in weaknesses):
                strengths.append("Excellent gap control between defensemen")
            if not any(w.weakness_type == WeaknessType.WEAK_SIDE_VULNERABILITY for w in weaknesses):
                strengths.append("Strong weak side support and coverage")
        
        elif formation_name == "2-1-2":
            if not any(w.weakness_type == WeaknessType.FORMATION_BREAKDOWN for w in weaknesses):
                strengths.append("Neutral zone trap well executed")
            if not any(w.weakness_type == WeaknessType.PRESSURE_INCONSISTENT for w in weaknesses):
                strengths.append("Consistent pressure application")
        
        elif formation_name == "1-3-1":
            if not any(w.weakness_type == WeaknessType.PRESSURE_INCONSISTENT for w in weaknesses):
                strengths.append("Maintains consistent offensive pressure")
            if not any(w.weakness_type == WeaknessType.POOR_POSITIONING for w in weaknesses):
                strengths.append("Excellent offensive zone positioning")
        
        # General strengths
        if len(weaknesses) <= 1:
            strengths.append("Overall formation discipline is strong")
        if not any(w.severity > 0.7 for w in weaknesses):
            strengths.append("No critical tactical weaknesses detected")
        
        return strengths
    
    def _identify_improvement_areas(self, weaknesses: List[TacticalWeakness]) -> List[str]:
        """Identify specific areas for improvement based on weaknesses."""
        improvement_areas = []
        
        for weakness in weaknesses:
            if weakness.weakness_type == WeaknessType.COVERAGE_GAP:
                improvement_areas.append("Improve gap control and communication")
            elif weakness.weakness_type == WeaknessType.POOR_POSITIONING:
                improvement_areas.append("Work on positioning fundamentals")
            elif weakness.weakness_type == WeaknessType.FORMATION_BREAKDOWN:
                improvement_areas.append("Increase formation discipline and consistency")
            elif weakness.weakness_type == WeaknessType.ISOLATION:
                improvement_areas.append("Improve support and coverage coordination")
            elif weakness.weakness_type == WeaknessType.OVERCOMMITMENT:
                improvement_areas.append("Better decision making on when to commit")
            elif weakness.weakness_type == WeaknessType.WEAK_SIDE_VULNERABILITY:
                improvement_areas.append("Strengthen weak side coverage and support")
            elif weakness.weakness_type == WeaknessType.TRANSITION_SLOW:
                improvement_areas.append("Improve transition speed and efficiency")
            elif weakness.weakness_type == WeaknessType.PRESSURE_INCONSISTENT:
                improvement_areas.append("Maintain consistent pressure application")
        
        return improvement_areas
    
    def _generate_tactical_insights(
        self, 
        formation_name: str, 
        weaknesses: List[TacticalWeakness]
    ) -> List[str]:
        """Generate tactical insights based on analysis."""
        insights = []
        
        # Formation-specific insights
        if formation_name == "1-2-2":
            if any(w.weakness_type == WeaknessType.COVERAGE_GAP for w in weaknesses):
                insights.append("Consider tightening defensive zone coverage")
            if any(w.weakness_type == WeaknessType.WEAK_SIDE_VULNERABILITY for w in weaknesses):
                insights.append("Weak side forward needs to provide better support")
        
        elif formation_name == "2-1-2":
            if any(w.weakness_type == WeaknessType.FORMATION_BREAKDOWN for w in weaknesses):
                insights.append("Neutral zone trap requires better coordination")
            if any(w.weakness_type == WeaknessType.PRESSURE_INCONSISTENT for w in weaknesses):
                insights.append("Maintain consistent pressure to prevent breakdowns")
        
        elif formation_name == "1-3-1":
            if any(w.weakness_type == WeaknessType.PRESSURE_INCONSISTENT for w in weaknesses):
                insights.append("Offensive pressure must be maintained consistently")
            if any(w.weakness_type == WeaknessType.POOR_POSITIONING for w in weaknesses):
                insights.append("Improve offensive zone positioning and cycling")
        
        # General tactical insights
        if len(weaknesses) > 2:
            insights.append("Multiple tactical issues suggest need for fundamental work")
        if any(w.severity > 0.8 for w in weaknesses):
            insights.append("Critical weaknesses require immediate attention")
        
        return insights
