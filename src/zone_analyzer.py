"""
Zone Analysis Module for Hockey Tactical Analysis

This module analyzes player positioning and distribution across rink zones
to provide insights into team tactics and defensive/offensive strategies.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from formation_detector import RinkZone

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ZoneMetrics:
    """Metrics for a specific rink zone."""
    zone: RinkZone
    avg_players: float
    max_players: int
    min_players: int
    player_density: float
    formation_consistency: float
    transition_frequency: float


class ZoneAnalyzer:
    """
    Analyzes player positioning and distribution across rink zones.
    
    Provides insights into team tactics, defensive strategies, and
    offensive positioning patterns.
    """
    
    def __init__(self, rink_dimensions: Tuple[int, int] = (1400, 600)):
        """
        Initialize the zone analyzer.
        
        Args:
            rink_dimensions: Tuple of (width, height) for the rink image
        """
        self.rink_width, self.rink_height = rink_dimensions
        
        # Define detailed zone boundaries (normalized coordinates)
        self.zone_boundaries = {
            RinkZone.OFFENSIVE: (0.0, 0.33),      # 0-33% of rink width
            RinkZone.NEUTRAL: (0.33, 0.67),       # 33-67% of rink width  
            RinkZone.DEFENSIVE: (0.67, 1.0)       # 67-100% of rink width
        }
        
        # Define sub-zones for more detailed analysis
        self.sub_zone_boundaries = {
            'offensive_high': (0.0, 0.17),        # 0-17% (deep offensive)
            'offensive_low': (0.17, 0.33),        # 17-33% (near blue line)
            'neutral_center': (0.33, 0.67),       # 33-67% (center ice)
            'defensive_high': (0.67, 0.83),       # 67-83% (near blue line)
            'defensive_low': (0.83, 1.0),         # 83-100% (deep defensive)
        }
    
    def classify_player_subzone(self, x: float, y: float) -> str:
        """
        Classify a player's position into a detailed sub-zone.
        
        Args:
            x: X-coordinate in rink coordinates
            y: Y-coordinate in rink coordinates
            
        Returns:
            Sub-zone identifier string
        """
        # Normalize x coordinate to 0-1 range
        normalized_x = x / self.rink_width
        
        # Determine sub-zone based on x-coordinate
        if normalized_x <= 0.17:
            return 'offensive_high'
        elif normalized_x <= 0.33:
            return 'offensive_low'
        elif normalized_x <= 0.67:
            return 'neutral_center'
        elif normalized_x <= 0.83:
            return 'defensive_high'
        else:
            return 'defensive_low'
    
    def analyze_zone_distribution(
        self, 
        tracking_data: List[Dict]
    ) -> Dict[RinkZone, ZoneMetrics]:
        """
        Analyze player distribution across all rink zones.
        
        Args:
            tracking_data: List of frame data dictionaries
            
        Returns:
            Dictionary mapping zones to ZoneMetrics objects
        """
        zone_data = {zone: [] for zone in RinkZone}
        
        # Collect player counts for each zone over time
        for frame_data in tracking_data:
            if 'players' not in frame_data:
                continue
            
            # Count players in each zone for this frame
            frame_zone_counts = {zone: 0 for zone in RinkZone}
            
            for player in frame_data['players']:
                if 'rink_position' in player and 'x' in player['rink_position']:
                    x = player['rink_position']['x']
                    y = player['rink_position']['y']
                    zone = self._classify_player_zone(x, y)
                    frame_zone_counts[zone] += 1
            
            # Store zone counts for this frame
            for zone in RinkZone:
                zone_data[zone].append(frame_zone_counts[zone])
        
        # Calculate metrics for each zone
        zone_metrics = {}
        for zone in RinkZone:
            if zone_data[zone]:
                zone_metrics[zone] = self._calculate_zone_metrics(zone, zone_data[zone])
            else:
                zone_metrics[zone] = ZoneMetrics(
                    zone=zone,
                    avg_players=0.0,
                    max_players=0,
                    min_players=0,
                    player_density=0.0,
                    formation_consistency=0.0,
                    transition_frequency=0.0
                )
        
        return zone_metrics
    
    def _classify_player_zone(self, x: float, y: float) -> RinkZone:
        """Helper method to classify player zone."""
        normalized_x = x / self.rink_width
        
        if normalized_x <= self.zone_boundaries[RinkZone.OFFENSIVE][1]:
            return RinkZone.OFFENSIVE
        elif normalized_x <= self.zone_boundaries[RinkZone.NEUTRAL][1]:
            return RinkZone.NEUTRAL
        else:
            return RinkZone.DEFENSIVE
    
    def _calculate_zone_metrics(self, zone: RinkZone, player_counts: List[int]) -> ZoneMetrics:
        """
        Calculate comprehensive metrics for a specific zone.
        
        Args:
            zone: The rink zone to analyze
            player_counts: List of player counts over time
            
        Returns:
            ZoneMetrics object with calculated metrics
        """
        if not player_counts:
            return ZoneMetrics(
                zone=zone,
                avg_players=0.0,
                max_players=0,
                min_players=0,
                player_density=0.0,
                formation_consistency=0.0,
                transition_frequency=0.0
            )
        
        # Basic statistics
        avg_players = np.mean(player_counts)
        max_players = max(player_counts)
        min_players = min(player_counts)
        
        # Calculate zone area (normalized)
        zone_start, zone_end = self.zone_boundaries[zone]
        zone_area = (zone_end - zone_start) * self.rink_height
        player_density = avg_players / zone_area if zone_area > 0 else 0.0
        
        # Formation consistency (how stable the player count is)
        if len(player_counts) > 1:
            consistency = 1.0 - (np.std(player_counts) / max(avg_players, 1))
            formation_consistency = max(0.0, min(1.0, consistency))
        else:
            formation_consistency = 1.0
        
        # Transition frequency (how often player count changes)
        transitions = 0
        for i in range(1, len(player_counts)):
            if player_counts[i] != player_counts[i-1]:
                transitions += 1
        
        transition_frequency = transitions / max(len(player_counts) - 1, 1)
        
        return ZoneMetrics(
            zone=zone,
            avg_players=avg_players,
            max_players=max_players,
            min_players=min_players,
            player_density=player_density,
            formation_consistency=formation_consistency,
            transition_frequency=transition_frequency
        )
    
    def analyze_trap_formation(
        self, 
        tracking_data: List[Dict],
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze neutral zone trap formations.
        
        Args:
            tracking_data: List of frame data dictionaries
            min_confidence: Minimum confidence for trap detection
            
        Returns:
            Dictionary with trap formation analysis
        """
        trap_instances = []
        total_frames = 0
        
        for frame_idx, frame_data in enumerate(tracking_data):
            if 'players' not in frame_data:
                continue
            
            total_frames += 1
            
            # Count players in neutral zone
            neutral_zone_players = 0
            for player in frame_data['players']:
                if 'rink_position' in player and 'x' in player['rink_position']:
                    x = player['rink_position']['x']
                    y = player['rink_position']['y']
                    if self._classify_player_zone(x, y) == RinkZone.NEUTRAL:
                        neutral_zone_players += 1
            
            # Detect trap formation (3+ players in neutral zone)
            if neutral_zone_players >= 3:
                trap_instances.append({
                    'frame': frame_idx,
                    'timestamp': frame_data.get('timestamp', 0),
                    'neutral_players': neutral_zone_players,
                    'confidence': min(1.0, neutral_zone_players / 5.0)  # Normalize confidence
                })
        
        if not trap_instances:
            return {
                "trap_detected": False,
                "total_instances": 0,
                "percentage_of_game": 0.0,
                "avg_confidence": 0.0
            }
        
        # Calculate trap statistics
        trap_percentage = (len(trap_instances) / total_frames) * 100
        avg_confidence = np.mean([instance['confidence'] for instance in trap_instances])
        
        # Identify trap patterns
        trap_patterns = self._identify_trap_patterns(trap_instances)
        
        return {
            "trap_detected": True,
            "total_instances": len(trap_instances),
            "percentage_of_game": trap_percentage,
            "avg_confidence": avg_confidence,
            "patterns": trap_patterns,
            "instances": trap_instances
        }
    
    def _identify_trap_patterns(self, trap_instances: List[Dict]) -> Dict[str, Any]:
        """
        Identify patterns in trap formation usage.
        
        Args:
            trap_instances: List of trap detection instances
            
        Returns:
            Dictionary with identified patterns
        """
        if len(trap_instances) < 2:
            return {"duration_patterns": [], "frequency_patterns": []}
        
        # Analyze trap duration patterns
        durations = []
        for i in range(1, len(trap_instances)):
            duration = trap_instances[i]['frame'] - trap_instances[i-1]['frame']
            if duration == 1:  # Consecutive frames
                durations.append(duration)
        
        # Analyze trap frequency patterns
        frame_gaps = []
        for i in range(1, len(trap_instances)):
            gap = trap_instances[i]['frame'] - trap_instances[i-1]['frame']
            frame_gaps.append(gap)
        
        return {
            "duration_patterns": {
                "consecutive_frames": len([d for d in durations if d == 1]),
                "avg_duration": np.mean(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0
            },
            "frequency_patterns": {
                "avg_gap": np.mean(frame_gaps) if frame_gaps else 0,
                "min_gap": min(frame_gaps) if frame_gaps else 0,
                "max_gap": max(frame_gaps) if frame_gaps else 0
            }
        }
    
    def analyze_forechecking_patterns(
        self, 
        tracking_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze forechecking patterns and pressure in offensive zone.
        
        Args:
            tracking_data: List of frame data dictionaries
            
        Returns:
            Dictionary with forechecking analysis
        """
        forecheck_instances = []
        
        for frame_idx, frame_data in enumerate(tracking_data):
            if 'players' not in frame_data:
                continue
            
            # Count players in offensive zone
            offensive_zone_players = 0
            for player in frame_data['players']:
                if 'rink_position' in player and 'x' in player['rink_position']:
                    x = player['rink_position']['x']
                    y = player['rink_position']['y']
                    if self._classify_player_zone(x, y) == RinkZone.OFFENSIVE:
                        offensive_zone_players += 1
            
            # Detect aggressive forechecking (2+ players in offensive zone)
            if offensive_zone_players >= 2:
                forecheck_instances.append({
                    'frame': frame_idx,
                    'timestamp': frame_data.get('timestamp', 0),
                    'offensive_players': offensive_zone_players,
                    'pressure_level': min(1.0, offensive_zone_players / 3.0)
                })
        
        if not forecheck_instances:
            return {
                "forecheck_detected": False,
                "total_instances": 0,
                "avg_pressure": 0.0
            }
        
        # Calculate forechecking statistics
        avg_pressure = np.mean([instance['pressure_level'] for instance in forecheck_instances])
        
        # Analyze pressure patterns
        pressure_patterns = self._analyze_pressure_patterns(forecheck_instances)
        
        return {
            "forecheck_detected": True,
            "total_instances": len(forecheck_instances),
            "avg_pressure": avg_pressure,
            "pressure_patterns": pressure_patterns,
            "instances": forecheck_instances
        }
    
    def _analyze_pressure_patterns(self, forecheck_instances: List[Dict]) -> Dict[str, Any]:
        """
        Analyze patterns in forechecking pressure.
        
        Args:
            forecheck_instances: List of forechecking instances
            
        Returns:
            Dictionary with pressure pattern analysis
        """
        if len(forecheck_instances) < 2:
            return {"pressure_levels": [], "timing_patterns": []}
        
        # Analyze pressure levels
        pressure_levels = [instance['pressure_level'] for instance in forecheck_instances]
        
        # Analyze timing patterns
        timing_gaps = []
        for i in range(1, len(forecheck_instances)):
            gap = forecheck_instances[i]['frame'] - forecheck_instances[i-1]['frame']
            timing_gaps.append(gap)
        
        return {
            "pressure_levels": {
                "low_pressure": len([p for p in pressure_levels if p < 0.5]),
                "medium_pressure": len([p for p in pressure_levels if 0.5 <= p < 0.8]),
                "high_pressure": len([p for p in pressure_levels if p >= 0.8]),
                "avg_pressure": np.mean(pressure_levels)
            },
            "timing_patterns": {
                "avg_gap": np.mean(timing_gaps) if timing_gaps else 0,
                "sustained_pressure": len([g for g in timing_gaps if g <= 5])  # 5 frames or less
            }
        }
    
    def analyze_defensive_coverage(
        self, 
        tracking_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze defensive zone coverage patterns.
        
        Args:
            tracking_data: List of frame data dictionaries
            
        Returns:
            Dictionary with defensive coverage analysis
        """
        defensive_instances = []
        
        for frame_idx, frame_data in enumerate(tracking_data):
            if 'players' not in frame_data:
                continue
            
            # Count players in defensive zone
            defensive_zone_players = 0
            for player in frame_data['players']:
                if 'rink_position' in player and 'x' in player['rink_position']:
                    x = player['rink_position']['x']
                    y = player['rink_position']['y']
                    if self._classify_player_zone(x, y) == RinkZone.DEFENSIVE:
                        defensive_zone_players += 1
            
            # Detect defensive coverage (3+ players in defensive zone)
            if defensive_zone_players >= 3:
                defensive_instances.append({
                    'frame': frame_idx,
                    'timestamp': frame_data.get('timestamp', 0),
                    'defensive_players': defensive_zone_players,
                    'coverage_density': min(1.0, defensive_zone_players / 5.0)
                })
        
        if not defensive_instances:
            return {
                "defensive_coverage": False,
                "total_instances": 0,
                "avg_coverage": 0.0
            }
        
        # Calculate defensive coverage statistics
        avg_coverage = np.mean([instance['coverage_density'] for instance in defensive_instances])
        
        # Analyze coverage patterns
        coverage_patterns = self._analyze_coverage_patterns(defensive_instances)
        
        return {
            "defensive_coverage": True,
            "total_instances": len(defensive_instances),
            "avg_coverage": avg_coverage,
            "coverage_patterns": coverage_patterns,
            "instances": defensive_instances
        }
    
    def _analyze_coverage_patterns(self, defensive_instances: List[Dict]) -> Dict[str, Any]:
        """
        Analyze patterns in defensive zone coverage.
        
        Args:
            defensive_instances: List of defensive coverage instances
            
        Returns:
            Dictionary with coverage pattern analysis
        """
        if len(defensive_instances) < 2:
            return {"coverage_levels": [], "formation_patterns": []}
        
        # Analyze coverage levels
        coverage_levels = [instance['coverage_density'] for instance in defensive_instances]
        
        # Analyze formation patterns
        formation_patterns = []
        for instance in defensive_instances:
            if instance['defensive_players'] == 3:
                formation_patterns.append("1-2")
            elif instance['defensive_players'] == 4:
                formation_patterns.append("1-3")
            elif instance['defensive_players'] == 5:
                formation_patterns.append("1-4")
            else:
                formation_patterns.append("other")
        
        # Count formation frequencies
        formation_counts = {}
        for pattern in formation_patterns:
            formation_counts[pattern] = formation_counts.get(pattern, 0) + 1
        
        return {
            "coverage_levels": {
                "light_coverage": len([c for c in coverage_levels if c < 0.6]),
                "medium_coverage": len([c for c in coverage_levels if 0.6 <= c < 0.8]),
                "heavy_coverage": len([c for c in coverage_levels if c >= 0.8]),
                "avg_coverage": np.mean(coverage_levels)
            },
            "formation_patterns": formation_counts
        }
    
    def generate_zone_report(
        self, 
        tracking_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive zone analysis report.
        
        Args:
            tracking_data: List of frame data dictionaries
            
        Returns:
            Dictionary with comprehensive zone analysis
        """
        # Perform all zone analyses
        zone_distribution = self.analyze_zone_distribution(tracking_data)
        trap_analysis = self.analyze_trap_formation(tracking_data)
        forecheck_analysis = self.analyze_forechecking_patterns(tracking_data)
        defensive_analysis = self.analyze_defensive_coverage(tracking_data)
        
        # Compile comprehensive report
        report = {
            "zone_distribution": {
                zone.value: {
                    "avg_players": metrics.avg_players,
                    "max_players": metrics.max_players,
                    "min_players": metrics.min_players,
                    "formation_consistency": metrics.formation_consistency,
                    "transition_frequency": metrics.transition_frequency
                }
                for zone, metrics in zone_distribution.items()
            },
            "trap_analysis": trap_analysis,
            "forecheck_analysis": forecheck_analysis,
            "defensive_analysis": defensive_analysis,
            "summary": self._generate_zone_summary(
                zone_distribution, trap_analysis, forecheck_analysis, defensive_analysis
            )
        }
        
        return report
    
    def _generate_zone_summary(
        self, 
        zone_distribution: Dict[RinkZone, ZoneMetrics],
        trap_analysis: Dict[str, Any],
        forecheck_analysis: Dict[str, Any],
        defensive_analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate a text summary of zone analysis findings.
        
        Args:
            zone_distribution: Zone distribution analysis results
            trap_analysis: Trap formation analysis results
            forecheck_analysis: Forechecking analysis results
            defensive_analysis: Defensive coverage analysis results
            
        Returns:
            Dictionary with text summaries
        """
        summary = {}
        
        # Zone distribution summary
        offensive_zone = zone_distribution[RinkZone.OFFENSIVE]
        neutral_zone = zone_distribution[RinkZone.NEUTRAL]
        defensive_zone = zone_distribution[RinkZone.DEFENSIVE]
        
        summary["zone_distribution"] = (
            f"Team shows balanced zone distribution: "
            f"Offensive zone: {offensive_zone.avg_players:.1f} avg players, "
            f"Neutral zone: {neutral_zone.avg_players:.1f} avg players, "
            f"Defensive zone: {defensive_zone.avg_players:.1f} avg players. "
            f"Most stable formation in {max([offensive_zone, neutral_zone, defensive_zone], key=lambda x: x.formation_consistency).zone.value} zone."
        )
        
        # Trap formation summary
        if trap_analysis["trap_detected"]:
            summary["trap_formation"] = (
                f"Neutral zone trap detected in {trap_analysis['percentage_of_game']:.1f}% of game time. "
                f"Average confidence: {trap_analysis['avg_confidence']:.2f}. "
                f"Most common pattern: {trap_analysis['patterns']['duration_patterns']['consecutive_frames']} consecutive frame instances."
            )
        else:
            summary["trap_formation"] = "No significant neutral zone trap formations detected."
        
        # Forechecking summary
        if forecheck_analysis["forecheck_detected"]:
            summary["forechecking"] = (
                f"Aggressive forechecking detected {forecheck_analysis['total_instances']} times. "
                f"Average pressure level: {forecheck_analysis['avg_pressure']:.2f}. "
                f"Pressure distribution: {forecheck_analysis['pressure_patterns']['pressure_levels']['high_pressure']} high pressure instances."
            )
        else:
            summary["forechecking"] = "Limited aggressive forechecking detected."
        
        # Defensive coverage summary
        if defensive_analysis["defensive_coverage"]:
            summary["defensive_coverage"] = (
                f"Strong defensive coverage in {defensive_analysis['total_instances']} instances. "
                f"Average coverage density: {defensive_analysis['avg_coverage']:.2f}. "
                f"Most common formation: {max(defensive_analysis['coverage_patterns']['formation_patterns'].items(), key=lambda x: x[1])[0]}."
            )
        else:
            summary["defensive_coverage"] = "Limited defensive zone coverage detected."
        
        return summary
