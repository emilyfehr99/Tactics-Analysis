"""
Formation Detection Module for Hockey Tactical Analysis

This module identifies hockey formations and systems from player tracking data
by analyzing player positions relative to rink zones and applying pattern recognition.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RinkZone(Enum):
    """Enumeration of rink zones for analysis."""
    OFFENSIVE = "offensive"
    NEUTRAL = "neutral"
    DEFENSIVE = "defensive"


@dataclass
class FormationPattern:
    """Represents a hockey formation pattern."""
    name: str
    description: str
    zone_distribution: Dict[RinkZone, List[int]]
    confidence_threshold: float = 0.7
    min_frames: int = 10


class FormationDetector:
    """
    Detects hockey formations from player tracking data.
    
    Analyzes player positions across rink zones to identify common
    hockey systems like 1-3-1, 2-1-2, 1-2-2, etc.
    """
    
    def __init__(self, rink_dimensions: Tuple[int, int] = (1400, 600)):
        """
        Initialize the formation detector.
        
        Args:
            rink_dimensions: Tuple of (width, height) for the rink image
        """
        self.rink_width, self.rink_height = rink_dimensions
        
        # Define rink zone boundaries (normalized coordinates)
        self.zone_boundaries = {
            RinkZone.OFFENSIVE: (0.0, 0.33),      # 0-33% of rink width
            RinkZone.NEUTRAL: (0.33, 0.67),       # 33-67% of rink width  
            RinkZone.DEFENSIVE: (0.67, 1.0)       # 67-100% of rink width
        }
        
        # Initialize standard hockey formations
        self.standard_formations = self._initialize_standard_formations()
        
    def _initialize_standard_formations(self) -> Dict[str, FormationPattern]:
        """Initialize standard hockey formation patterns."""
        formations = {}
        
        # 1-3-1 Formation (Power play, offensive zone)
        formations["1-3-1"] = FormationPattern(
            name="1-3-1",
            description="Power play formation with 1 forward, 3 midfield, 1 defense",
            zone_distribution={
                RinkZone.OFFENSIVE: [1, 3, 1],
                RinkZone.NEUTRAL: [0, 0, 0],
                RinkZone.DEFENSIVE: [0, 0, 0]
            },
            confidence_threshold=0.7,
            min_frames=8
        )
        
        # 2-1-2 Formation (Neutral zone trap)
        formations["2-1-2"] = FormationPattern(
            name="2-1-2", 
            description="Neutral zone trap with 2 forwards, 1 center, 2 defense",
            zone_distribution={
                RinkZone.OFFENSIVE: [0, 0, 0],
                RinkZone.NEUTRAL: [2, 1, 2],
                RinkZone.DEFENSIVE: [0, 0, 0]
            },
            confidence_threshold=0.75,
            min_frames=10
        )
        
        # 1-2-2 Formation (Standard defensive coverage)
        formations["1-2-2"] = FormationPattern(
            name="1-2-2",
            description="Standard defensive zone coverage",
            zone_distribution={
                RinkZone.OFFENSIVE: [0, 0, 0],
                RinkZone.NEUTRAL: [0, 0, 0],
                RinkZone.DEFENSIVE: [1, 2, 2]
            },
            confidence_threshold=0.7,
            min_frames=8
        )
        
        # 2-2-1 Formation (Aggressive forechecking)
        formations["2-2-1"] = FormationPattern(
            name="2-2-1",
            description="Aggressive forechecking formation",
            zone_distribution={
                RinkZone.OFFENSIVE: [2, 2, 1],
                RinkZone.NEUTRAL: [0, 0, 0],
                RinkZone.DEFENSIVE: [0, 0, 0]
            },
            confidence_threshold=0.7,
            min_frames=8
        )
        
        # 1-4 Formation (Defensive zone collapse)
        formations["1-4"] = FormationPattern(
            name="1-4",
            description="Defensive zone collapse formation",
            zone_distribution={
                RinkZone.OFFENSIVE: [0, 0, 0],
                RinkZone.NEUTRAL: [0, 0, 0],
                RinkZone.DEFENSIVE: [1, 4, 0]
            },
            confidence_threshold=0.8,
            min_frames=12
        )
        
        # 0-5 Formation (Full defensive collapse)
        formations["0-5"] = FormationPattern(
            name="0-5",
            description="Full defensive zone collapse",
            zone_distribution={
                RinkZone.OFFENSIVE: [0, 0, 0],
                RinkZone.NEUTRAL: [0, 0, 0],
                RinkZone.DEFENSIVE: [0, 5, 0]
            },
            confidence_threshold=0.8,
            min_frames=10
        )
        
        return formations
    
    def classify_player_zone(self, x: float, y: float) -> RinkZone:
        """
        Classify a player's position into a rink zone.
        
        Args:
            x: Normalized x-coordinate (0.0 to 1.0)
            y: Normalized y-coordinate (0.0 to 1.0)
            
        Returns:
            RinkZone enum value
        """
        # Normalize x coordinate to 0-1 range
        normalized_x = x / self.rink_width
        
        # Determine zone based on x-coordinate
        if normalized_x <= self.zone_boundaries[RinkZone.OFFENSIVE][1]:
            return RinkZone.OFFENSIVE
        elif normalized_x <= self.zone_boundaries[RinkZone.NEUTRAL][1]:
            return RinkZone.NEUTRAL
        else:
            return RinkZone.DEFENSIVE
    
    def count_players_by_zone(self, players: List[Dict]) -> Dict[RinkZone, int]:
        """
        Count players in each rink zone.
        
        Args:
            players: List of player dictionaries with 'rink_position' key
            
        Returns:
            Dictionary mapping zones to player counts
        """
        zone_counts = {zone: 0 for zone in RinkZone}
        
        for player in players:
            if 'rink_position' in player and 'x' in player['rink_position']:
                x = player['rink_position']['x']
                y = player['rink_position']['y']
                zone = self.classify_player_zone(x, y)
                zone_counts[zone] += 1
        
        return zone_counts
    
    def calculate_formation_similarity(
        self, 
        actual_distribution: Dict[RinkZone, int], 
        expected_distribution: Dict[RinkZone, List[int]]
    ) -> float:
        """
        Calculate similarity between actual and expected player distributions.
        
        Args:
            actual_distribution: Actual player counts by zone
            expected_distribution: Expected player counts by zone (from formation pattern)
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        total_similarity = 0.0
        total_weight = 0.0
        
        for zone in RinkZone:
            if zone in expected_distribution:
                expected = expected_distribution[zone]
                actual = actual_distribution[zone]
                
                # Calculate similarity for this zone
                if len(expected) == 1:
                    # Single expected count
                    expected_count = expected[0]
                    similarity = 1.0 - min(abs(actual - expected_count) / max(expected_count, 1), 1.0)
                else:
                    # Range of expected counts
                    min_expected, max_expected = min(expected), max(expected)
                    if min_expected <= actual <= max_expected:
                        similarity = 1.0
                    else:
                        # Calculate distance from range
                        distance = min(abs(actual - min_expected), abs(actual - max_expected))
                        max_range = max(max_expected - min_expected, 1)
                        similarity = max(0.0, 1.0 - distance / max_range)
                
                # Weight by zone importance (neutral zone is most important)
                weight = 2.0 if zone == RinkZone.NEUTRAL else 1.0
                total_similarity += similarity * weight
                total_weight += weight
        
        return total_similarity / total_weight if total_weight > 0 else 0.0
    
    def detect_formation_in_frame(
        self, 
        players: List[Dict], 
        min_confidence: float = 0.6
    ) -> Optional[Tuple[str, float]]:
        """
        Detect the most likely formation in a single frame.
        
        Args:
            players: List of player dictionaries
            min_confidence: Minimum confidence threshold
            
        Returns:
            Tuple of (formation_name, confidence_score) or None if no match
        """
        if not players:
            return None
        
        # Count players by zone
        zone_counts = self.count_players_by_zone(players)
        
        best_formation = None
        best_confidence = 0.0
        
        # Check each standard formation
        for formation_name, pattern in self.standard_formations.items():
            confidence = self.calculate_formation_similarity(
                zone_counts, pattern.zone_distribution
            )
            
            if confidence > best_confidence and confidence >= min_confidence:
                best_confidence = confidence
                best_formation = formation_name
        
        if best_formation:
            return (best_formation, best_confidence)
        
        return None
    
    def detect_formations_over_time(
        self, 
        tracking_data: List[Dict], 
        min_frames: int = 5
    ) -> List[Dict]:
        """
        Detect formations over a sequence of frames.
        
        Args:
            tracking_data: List of frame data dictionaries
            min_frames: Minimum consecutive frames to confirm formation
            
        Returns:
            List of detected formations with timing information
        """
        detected_formations = []
        current_formation = None
        formation_start = None
        formation_frames = 0
        
        for frame_idx, frame_data in enumerate(tracking_data):
            if 'players' not in frame_data:
                continue
            
            # Detect formation in current frame
            frame_result = self.detect_formation_in_frame(frame_data['players'])
            
            if frame_result:
                formation_name, confidence = frame_result
                
                if current_formation == formation_name:
                    # Continue current formation
                    formation_frames += 1
                else:
                    # New formation detected
                    if current_formation and formation_frames >= min_frames:
                        # Record previous formation
                        detected_formations.append({
                            'formation': current_formation,
                            'start_frame': formation_start,
                            'end_frame': frame_idx - 1,
                            'duration_frames': formation_frames,
                            'start_time': tracking_data[formation_start].get('timestamp', 0),
                            'end_time': tracking_data[frame_idx - 1].get('timestamp', 0),
                            'avg_confidence': confidence  # This will be updated
                        })
                    
                    # Start new formation
                    current_formation = formation_name
                    formation_start = frame_idx
                    formation_frames = 1
            else:
                # No formation detected
                if current_formation and formation_frames >= min_frames:
                    # Record previous formation
                    detected_formations.append({
                        'formation': current_formation,
                        'start_frame': formation_start,
                        'end_frame': frame_idx - 1,
                        'duration_frames': formation_frames,
                        'start_time': tracking_data[formation_start].get('timestamp', 0),
                        'end_time': tracking_data[frame_idx - 1].get('timestamp', 0),
                        'avg_confidence': 0.0  # Will be calculated
                    })
                
                current_formation = None
                formation_start = None
                formation_frames = 0
        
        # Handle final formation
        if current_formation and formation_frames >= min_frames:
            detected_formations.append({
                'formation': current_formation,
                'start_frame': formation_start,
                'end_frame': len(tracking_data) - 1,
                'duration_frames': formation_frames,
                'start_time': tracking_data[formation_start].get('timestamp', 0),
                'end_time': tracking_data[-1].get('timestamp', 0),
                'avg_confidence': 0.0  # Will be calculated
            })
        
        # Calculate average confidence for each formation
        for formation in detected_formations:
            start_frame = formation['start_frame']
            end_frame = formation['end_frame']
            confidences = []
            
            for i in range(start_frame, end_frame + 1):
                if i < len(tracking_data) and 'players' in tracking_data[i]:
                    frame_result = self.detect_formation_in_frame(tracking_data[i]['players'])
                    if frame_result:
                        confidences.append(frame_result[1])
            
            formation['avg_confidence'] = np.mean(confidences) if confidences else 0.0
        
        return detected_formations
    
    def analyze_formation_transitions(
        self, 
        detected_formations: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze transitions between different formations.
        
        Args:
            detected_formations: List of detected formations
            
        Returns:
            Dictionary with transition analysis
        """
        if len(detected_formations) < 2:
            return {"transitions": [], "most_common": None, "total_transitions": 0}
        
        transitions = []
        for i in range(len(detected_formations) - 1):
            current = detected_formations[i]['formation']
            next_formation = detected_formations[i + 1]['formation']
            
            transitions.append({
                'from': current,
                'to': next_formation,
                'transition_frame': detected_formations[i]['end_frame'],
                'transition_time': detected_formations[i]['end_time']
            })
        
        # Count transition frequencies
        transition_counts = {}
        for transition in transitions:
            key = f"{transition['from']} → {transition['to']}"
            transition_counts[key] = transition_counts.get(key, 0) + 1
        
        most_common = max(transition_counts.items(), key=lambda x: x[1]) if transition_counts else None
        
        return {
            "transitions": transitions,
            "transition_counts": transition_counts,
            "most_common": most_common,
            "total_transitions": len(transitions)
        }
    
    def get_formation_statistics(
        self, 
        detected_formations: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate statistics about detected formations.
        
        Args:
            detected_formations: List of detected formations
            
        Returns:
            Dictionary with formation statistics
        """
        if not detected_formations:
            return {}
        
        # Count formations by type
        formation_counts = {}
        total_duration = 0
        
        for formation in detected_formations:
            formation_name = formation['formation']
            duration = formation['duration_frames']
            
            if formation_name not in formation_counts:
                formation_counts[formation_name] = {
                    'count': 0,
                    'total_duration': 0,
                    'avg_confidence': 0.0,
                    'confidences': []
                }
            
            formation_counts[formation_name]['count'] += 1
            formation_counts[formation_name]['total_duration'] += duration
            formation_counts[formation_name]['confidences'].append(formation['avg_confidence'])
            total_duration += duration
        
        # Calculate averages
        for formation_name, stats in formation_counts.items():
            stats['avg_confidence'] = np.mean(stats['confidences'])
            stats['percentage_of_game'] = (stats['total_duration'] / total_duration) * 100
        
        return {
            "formation_counts": formation_counts,
            "total_formations": len(detected_formations),
            "total_duration": total_duration,
            "most_common": max(formation_counts.items(), key=lambda x: x[1]['count'])[0] if formation_counts else None
        }
