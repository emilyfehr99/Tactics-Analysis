"""
Real Hockey Analysis System

This system is built from the ground up with actual hockey knowledge.
It understands the game as hockey players and coaches do.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, NamedTuple
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict, deque
import json
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameState(Enum):
    """Real hockey game states."""
    EVEN_STRENGTH = "even_strength"
    POWER_PLAY = "power_play"
    PENALTY_KILL = "penalty_kill"
    EMPTY_NET = "empty_net"
    PULLED_GOALIE = "pulled_goalie"
    FACE_OFF = "face_off"
    ICING = "icing"
    OFFSIDE = "offside"


class ZoneEntry(Enum):
    """How teams enter zones."""
    CARRY = "carry"
    DUMP = "dump"
    PASS = "pass"
    RUSH = "rush"
    RECOVERY = "recovery"


class ShotType(Enum):
    """Types of shots in hockey."""
    WRIST = "wrist"
    SLAP = "slap"
    SNAP = "snap"
    BACKHAND = "backhand"
    TIP = "tip"
    DEFLECTION = "deflection"
    WRAPAROUND = "wraparound"


class PlayerRole(Enum):
    """Real hockey player roles and responsibilities."""
    # Forwards
    CENTER = "center"
    LEFT_WING = "left_wing"
    RIGHT_WING = "right_wing"
    
    # Defense
    LEFT_DEFENSE = "left_defense"
    RIGHT_DEFENSE = "right_defense"
    
    # Specialized roles
    POWER_PLAY_QB = "power_play_qb"  # Quarterback on power play
    PENALTY_KILL_FORWARD = "penalty_kill_forward"
    PENALTY_KILL_DEFENSE = "penalty_kill_defense"
    NET_FRONT_PRESENCE = "net_front_presence"
    POINT_MAN = "point_man"
    HALF_WALL = "half_wall"
    
    # Goalie
    GOALIE = "goalie"


@dataclass
class PuckEvent:
    """Real hockey puck events."""
    timestamp: float
    event_type: str  # "shot", "pass", "carry", "dump", "recovery", "turnover"
    player_id: str
    team: str
    location: Tuple[float, float]
    target_location: Optional[Tuple[float, float]] = None
    success: bool = True
    details: Dict[str, Any] = None


@dataclass
class PlayerSkills:
    """Individual player skills and tendencies."""
    player_id: str
    skating_speed: float  # 0.0 to 1.0
    shot_accuracy: float
    passing_accuracy: float
    defensive_awareness: float
    physical_presence: float
    hockey_iq: float
    power_play_specialist: bool = False
    penalty_kill_specialist: bool = False
    face_off_percentage: float = 0.5
    shooting_percentage: float = 0.1
    plus_minus: int = 0
    time_on_ice_per_game: float = 0.0


@dataclass
class TeamSystem:
    """Team-specific coaching systems and tendencies."""
    team_id: str
    offensive_system: str  # "crash_net", "cycle", "rush", "possession"
    defensive_system: str  # "zone", "man_to_man", "hybrid"
    power_play_formation: str  # "1-3-1", "2-1-2", "umbrella"
    penalty_kill_formation: str  # "diamond", "box", "wedge"
    neutral_zone_strategy: str  # "trap", "pressure", "hybrid"
    face_off_strategy: str  # "aggressive", "conservative", "situational"
    line_change_frequency: float  # Changes per minute
    shot_selection: str  # "high_volume", "high_percentage", "balanced"


@dataclass
class GameSequence:
    """A sequence of play in hockey."""
    start_time: float
    end_time: float
    team_with_puck: str
    zone: str  # "offensive", "neutral", "defensive"
    sequence_type: str  # "rush", "cycle", "dump_and_chase", "power_play", "penalty_kill"
    events: List[PuckEvent]
    outcome: str  # "goal", "shot", "turnover", "clear", "icing", "offside"
    effectiveness_score: float  # Based on actual outcomes


@dataclass
class HockeyFormation:
    """Real hockey formation with context."""
    name: str
    team: str
    confidence: float
    game_state: GameState
    zone: str
    player_roles: Dict[str, PlayerRole]
    tactical_purpose: str
    effectiveness_score: float  # Based on actual outcomes
    vulnerabilities: List[str]
    opportunities: List[str]
    time_active: float
    success_rate: float  # Actual success rate
    shots_generated: int
    goals_allowed: int


class RealHockeyAnalyzer:
    """
    Real hockey analysis system that understands the game.
    """
    
    def __init__(self):
        """Initialize with real hockey knowledge."""
        self.game_sequences = deque(maxlen=1000)  # Last 1000 sequences
        self.puck_events = deque(maxlen=10000)  # Last 10,000 events
        self.player_skills = {}
        self.team_systems = {}
        self.formation_history = deque(maxlen=1000)
        
        # Real hockey rink dimensions (NHL standard)
        self.rink_length = 200.0  # feet
        self.rink_width = 85.0   # feet
        self.blue_line_distance = 75.0  # feet from each goal line
        self.goal_line_distance = 11.0  # feet from each end
        
        # Face-off circles
        self.face_off_circles = [
            (self.rink_length/2, self.rink_width/2, 15.0),  # Center ice
            (self.blue_line_distance, self.rink_width/2, 15.0),  # Offensive zone
            (self.rink_length - self.blue_line_distance, self.rink_width/2, 15.0),  # Defensive zone
        ]
        
        # Initialize with default team systems
        self._initialize_default_systems()
    
    def _initialize_default_systems(self):
        """Initialize with realistic team systems."""
        # Default systems for analysis
        self.team_systems["Team A"] = TeamSystem(
            team_id="Team A",
            offensive_system="cycle",
            defensive_system="zone",
            power_play_formation="1-3-1",
            penalty_kill_formation="diamond",
            neutral_zone_strategy="trap",
            face_off_strategy="situational",
            line_change_frequency=0.8,  # Changes per minute
            shot_selection="balanced"
        )
        
        self.team_systems["Team B"] = TeamSystem(
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
    
    def set_player_skills(self, player_skills: Dict[str, PlayerSkills]):
        """Set individual player skills and tendencies."""
        self.player_skills = player_skills
    
    def set_team_systems(self, team_systems: Dict[str, TeamSystem]):
        """Set team-specific coaching systems."""
        self.team_systems = team_systems
    
    def add_puck_event(self, event: PuckEvent):
        """Add a puck event to the analysis."""
        self.puck_events.append(event)
        
        # Update game sequences based on events
        self._update_game_sequences(event)
    
    def _update_game_sequences(self, event: PuckEvent):
        """Update game sequences based on puck events."""
        # This is where we'd analyze sequences of play
        # For now, we'll create a simple sequence
        if event.event_type == "shot":
            sequence = GameSequence(
                start_time=event.timestamp - 5.0,  # 5 seconds before shot
                end_time=event.timestamp,
                team_with_puck=event.team,
                zone=self._determine_zone(event.location, event.team),
                sequence_type="shot_sequence",
                events=[event],
                outcome="shot",
                effectiveness_score=self._calculate_shot_effectiveness(event)
            )
            self.game_sequences.append(sequence)
    
    def _determine_zone(self, location: Tuple[float, float], team: str) -> str:
        """Determine zone based on location and team."""
        x, y = location
        
        if team == "Team A":
            if x > self.blue_line_distance:
                return "offensive"
            elif x < (self.rink_length - self.blue_line_distance):
                return "defensive"
            else:
                return "neutral"
        else:  # Team B
            if x < (self.rink_length - self.blue_line_distance):
                return "offensive"
            elif x > self.blue_line_distance:
                return "defensive"
            else:
                return "neutral"
    
    def _calculate_shot_effectiveness(self, event: PuckEvent) -> float:
        """Calculate shot effectiveness based on location and context."""
        x, y = event.location
        
        # Distance from net
        if event.team == "Team A":
            net_distance = np.sqrt((x - self.rink_length)**2 + (y - self.rink_width/2)**2)
        else:
            net_distance = np.sqrt((x - 0)**2 + (y - self.rink_width/2)**2)
        
        # Shot effectiveness based on distance and angle
        distance_score = max(0, 1.0 - net_distance / 100.0)  # Closer is better
        
        # Angle score (shots from center are more effective)
        center_distance = abs(y - self.rink_width/2)
        angle_score = max(0, 1.0 - center_distance / (self.rink_width/2))
        
        # Combine scores
        effectiveness = (distance_score * 0.6 + angle_score * 0.4)
        
        return min(1.0, effectiveness)
    
    def analyze_game_flow(self, time_window: float = 60.0) -> Dict[str, Any]:
        """
        Analyze the flow of the game over a time window.
        This is what real hockey analysis looks like.
        """
        current_time = max([event.timestamp for event in self.puck_events]) if self.puck_events else 0
        start_time = current_time - time_window
        
        # Get events in time window
        recent_events = [event for event in self.puck_events if start_time <= event.timestamp <= current_time]
        
        if not recent_events:
            return {"error": "No events in time window"}
        
        # Analyze sequences
        sequences = [seq for seq in self.game_sequences if start_time <= seq.start_time <= current_time]
        
        # Calculate real hockey metrics
        analysis = {
            "time_window": time_window,
            "total_events": len(recent_events),
            "sequences": len(sequences),
            "team_metrics": self._calculate_team_metrics(recent_events, sequences),
            "formation_analysis": self._analyze_formations_in_window(sequences),
            "puck_possession": self._calculate_possession_time(recent_events),
            "zone_entries": self._analyze_zone_entries(recent_events),
            "shot_quality": self._analyze_shot_quality(recent_events),
            "turnover_analysis": self._analyze_turnovers(recent_events),
            "game_flow": self._analyze_game_flow_patterns(sequences)
        }
        
        return analysis
    
    def _calculate_team_metrics(self, events: List[PuckEvent], sequences: List[GameSequence]) -> Dict[str, Any]:
        """Calculate real team metrics."""
        team_metrics = {"Team A": {}, "Team B": {}}
        
        for team in ["Team A", "Team B"]:
            team_events = [e for e in events if e.team == team]
            team_sequences = [s for s in sequences if s.team_with_puck == team]
            
            # Shots
            shots = [e for e in team_events if e.event_type == "shot"]
            
            # Goals (simplified - would need actual goal detection)
            goals = [e for e in team_events if e.event_type == "shot" and e.success and self._is_goal(e)]
            
            # Possession time
            possession_time = sum([s.end_time - s.start_time for s in team_sequences])
            
            # Zone entries
            zone_entries = [e for e in team_events if e.event_type == "carry" and self._is_zone_entry(e)]
            
            # Turnovers
            turnovers = [e for e in team_events if e.event_type == "turnover"]
            
            team_metrics[team] = {
                "shots": len(shots),
                "goals": len(goals),
                "possession_time": possession_time,
                "zone_entries": len(zone_entries),
                "turnovers": len(turnovers),
                "shot_percentage": len(goals) / len(shots) if shots else 0,
                "possession_percentage": possession_time / (possession_time + sum([s.end_time - s.start_time for s in sequences if s.team_with_puck != team])) if sequences else 0
            }
        
        return team_metrics
    
    def _analyze_formations_in_window(self, sequences: List[GameSequence]) -> Dict[str, Any]:
        """Analyze formations based on actual game sequences."""
        if not sequences:
            return {"error": "No sequences to analyze"}
        
        # Group sequences by team and zone
        team_sequences = defaultdict(list)
        for seq in sequences:
            team_sequences[seq.team_with_puck].append(seq)
        
        formation_analysis = {}
        
        for team, team_seqs in team_sequences.items():
            # Analyze offensive sequences
            offensive_seqs = [s for s in team_seqs if s.zone == "offensive"]
            
            if offensive_seqs:
                # Calculate effectiveness
                total_shots = sum([len([e for e in s.events if e.event_type == "shot"]) for s in offensive_seqs])
                total_goals = sum([len([e for e in s.events if e.event_type == "shot" and self._is_goal(e)]) for s in offensive_seqs])
                
                formation_analysis[team] = {
                    "offensive_sequences": len(offensive_seqs),
                    "shots_generated": total_shots,
                    "goals_scored": total_goals,
                    "effectiveness": total_goals / total_shots if total_shots > 0 else 0,
                    "average_sequence_length": np.mean([s.end_time - s.start_time for s in offensive_seqs]),
                    "formation_type": self._detect_formation_type(offensive_seqs)
                }
        
        return formation_analysis
    
    def _detect_formation_type(self, sequences: List[GameSequence]) -> str:
        """Detect formation type based on sequence patterns."""
        if not sequences:
            return "unknown"
        
        # Analyze sequence types
        sequence_types = [s.sequence_type for s in sequences]
        
        if "power_play" in sequence_types:
            return "power_play"
        elif "rush" in sequence_types:
            return "rush"
        elif "cycle" in sequence_types:
            return "cycle"
        else:
            return "mixed"
    
    def _calculate_possession_time(self, events: List[PuckEvent]) -> Dict[str, float]:
        """Calculate actual puck possession time."""
        possession_time = {"Team A": 0.0, "Team B": 0.0}
        
        if not events:
            return possession_time
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        current_team = None
        last_timestamp = sorted_events[0].timestamp
        
        for event in sorted_events:
            if current_team and event.timestamp > last_timestamp:
                possession_time[current_team] += event.timestamp - last_timestamp
            
            current_team = event.team
            last_timestamp = event.timestamp
        
        return possession_time
    
    def _analyze_zone_entries(self, events: List[PuckEvent]) -> Dict[str, Any]:
        """Analyze zone entries and their success."""
        zone_entries = [e for e in events if e.event_type == "carry" and self._is_zone_entry(e)]
        
        if not zone_entries:
            return {"total": 0, "successful": 0, "success_rate": 0}
        
        successful_entries = [e for e in zone_entries if e.success]
        
        return {
            "total": len(zone_entries),
            "successful": len(successful_entries),
            "success_rate": len(successful_entries) / len(zone_entries),
            "by_team": {
                team: len([e for e in zone_entries if e.team == team])
                for team in ["Team A", "Team B"]
            }
        }
    
    def _analyze_shot_quality(self, events: List[PuckEvent]) -> Dict[str, Any]:
        """Analyze shot quality and effectiveness."""
        shots = [e for e in events if e.event_type == "shot"]
        
        if not shots:
            return {"total": 0, "high_quality": 0, "average_quality": 0}
        
        shot_qualities = [self._calculate_shot_effectiveness(shot) for shot in shots]
        high_quality_shots = [q for q in shot_qualities if q > 0.7]
        
        return {
            "total": len(shots),
            "high_quality": len(high_quality_shots),
            "average_quality": np.mean(shot_qualities),
            "by_team": {
                team: {
                    "total": len([s for s in shots if s.team == team]),
                    "average_quality": np.mean([self._calculate_shot_effectiveness(s) for s in shots if s.team == team])
                }
                for team in ["Team A", "Team B"]
            }
        }
    
    def _analyze_turnovers(self, events: List[PuckEvent]) -> Dict[str, Any]:
        """Analyze turnovers and their impact."""
        turnovers = [e for e in events if e.event_type == "turnover"]
        
        if not turnovers:
            return {"total": 0, "by_zone": {}, "by_team": {}}
        
        # Analyze by zone
        zone_turnovers = defaultdict(int)
        for turnover in turnovers:
            zone = self._determine_zone(turnover.location, turnover.team)
            zone_turnovers[zone] += 1
        
        # Analyze by team
        team_turnovers = {
            team: len([t for t in turnovers if t.team == team])
            for team in ["Team A", "Team B"]
        }
        
        return {
            "total": len(turnovers),
            "by_zone": dict(zone_turnovers),
            "by_team": team_turnovers
        }
    
    def _analyze_game_flow_patterns(self, sequences: List[GameSequence]) -> Dict[str, Any]:
        """Analyze patterns in game flow."""
        if not sequences:
            return {"error": "No sequences to analyze"}
        
        # Calculate momentum shifts
        momentum_shifts = []
        for i in range(1, len(sequences)):
            prev_seq = sequences[i-1]
            curr_seq = sequences[i]
            
            if prev_seq.team_with_puck != curr_seq.team_with_puck:
                momentum_shifts.append({
                    "time": curr_seq.start_time,
                    "from_team": prev_seq.team_with_puck,
                    "to_team": curr_seq.team_with_puck
                })
        
        # Calculate sequence effectiveness
        sequence_effectiveness = [s.effectiveness_score for s in sequences]
        
        return {
            "momentum_shifts": len(momentum_shifts),
            "average_sequence_effectiveness": np.mean(sequence_effectiveness),
            "sequence_variability": np.std(sequence_effectiveness),
            "dominant_team": max(["Team A", "Team B"], key=lambda t: len([s for s in sequences if s.team_with_puck == t]))
        }
    
    def _is_goal(self, event: PuckEvent) -> bool:
        """Determine if a shot resulted in a goal."""
        # This would need actual goal detection logic
        # For now, we'll use a simplified approach
        return event.success and self._calculate_shot_effectiveness(event) > 0.8
    
    def _is_zone_entry(self, event: PuckEvent) -> bool:
        """Determine if an event represents a zone entry."""
        # This would need more sophisticated logic
        # For now, we'll use a simplified approach
        return event.event_type == "carry" and event.success
    
    def get_actionable_insights(self, time_window: float = 60.0) -> Dict[str, Any]:
        """
        Get actionable insights for coaches and players.
        This is what real hockey analysis provides.
        """
        analysis = self.analyze_game_flow(time_window)
        
        insights = {
            "coaching_recommendations": self._generate_coaching_recommendations(analysis),
            "player_adjustments": self._generate_player_adjustments(analysis),
            "tactical_opportunities": self._identify_tactical_opportunities(analysis),
            "vulnerability_assessment": self._assess_vulnerabilities(analysis),
            "momentum_analysis": self._analyze_momentum(analysis)
        }
        
        return insights
    
    def _generate_coaching_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific coaching recommendations."""
        recommendations = []
        
        # Analyze team metrics
        team_metrics = analysis.get("team_metrics", {})
        
        for team, metrics in team_metrics.items():
            # Shot percentage analysis
            if metrics.get("shot_percentage", 0) < 0.1:
                recommendations.append(f"{team}: Improve shot selection - current percentage too low")
            
            # Possession analysis
            if metrics.get("possession_percentage", 0) < 0.4:
                recommendations.append(f"{team}: Increase puck possession time")
            
            # Turnover analysis
            if metrics.get("turnovers", 0) > 10:
                recommendations.append(f"{team}: Reduce turnovers - too many giveaways")
        
        return recommendations
    
    def _generate_player_adjustments(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific player adjustment recommendations."""
        adjustments = []
        
        # Analyze shot quality
        shot_quality = analysis.get("shot_quality", {})
        
        for team, quality_data in shot_quality.get("by_team", {}).items():
            if quality_data.get("average_quality", 0) < 0.5:
                adjustments.append(f"{team}: Players need to get closer to net for higher quality shots")
        
        # Analyze zone entries
        zone_entries = analysis.get("zone_entries", {})
        if zone_entries.get("success_rate", 0) < 0.6:
            adjustments.append("Improve zone entry success rate - practice puck protection")
        
        return adjustments
    
    def _identify_tactical_opportunities(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify specific tactical opportunities."""
        opportunities = []
        
        # Analyze formation effectiveness
        formation_analysis = analysis.get("formation_analysis", {})
        
        for team, formation_data in formation_analysis.items():
            if formation_data.get("effectiveness", 0) > 0.7:
                opportunities.append(f"{team}: Current formation is highly effective - maintain this approach")
            elif formation_data.get("effectiveness", 0) < 0.3:
                opportunities.append(f"{team}: Current formation is ineffective - consider tactical changes")
        
        # Analyze momentum
        game_flow = analysis.get("game_flow", {})
        if game_flow.get("momentum_shifts", 0) > 5:
            opportunities.append("High momentum shifts - focus on maintaining possession during transitions")
        
        return opportunities
    
    def _assess_vulnerabilities(self, analysis: Dict[str, Any]) -> List[str]:
        """Assess team vulnerabilities."""
        vulnerabilities = []
        
        # Analyze turnovers by zone
        turnovers = analysis.get("turnover_analysis", {})
        zone_turnovers = turnovers.get("by_zone", {})
        
        for zone, count in zone_turnovers.items():
            if count > 5:
                vulnerabilities.append(f"High turnover rate in {zone} zone - improve puck protection")
        
        # Analyze shot quality against
        shot_quality = analysis.get("shot_quality", {})
        for team, quality_data in shot_quality.get("by_team", {}).items():
            if quality_data.get("average_quality", 0) > 0.7:
                vulnerabilities.append(f"{team}: Allowing high-quality shots - tighten defensive coverage")
        
        return vulnerabilities
    
    def _analyze_momentum(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze game momentum."""
        game_flow = analysis.get("game_flow", {})
        
        momentum_analysis = {
            "current_momentum": game_flow.get("dominant_team", "even"),
            "momentum_shifts": game_flow.get("momentum_shifts", 0),
            "sequence_effectiveness": game_flow.get("average_sequence_effectiveness", 0),
            "momentum_stability": 1.0 - game_flow.get("sequence_variability", 0)
        }
        
        return momentum_analysis
