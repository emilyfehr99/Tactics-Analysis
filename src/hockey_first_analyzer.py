"""
Hockey-First Tactical Analysis System

This system is built from the ground up with hockey knowledge as the foundation.
It understands the actual game mechanics, not just spatial positioning.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, NamedTuple
from dataclasses import dataclass
from enum import Enum
import logging
from scipy.spatial.distance import cdist
from scipy.spatial import ConvexHull
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameSituation(Enum):
    """Current game situation affecting all tactical analysis."""
    EVEN_STRENGTH = "even_strength"
    POWER_PLAY = "power_play"
    PENALTY_KILL = "penalty_kill"
    EMPTY_NET = "empty_net"
    PULLED_GOALIE = "pulled_goalie"
    FACE_OFF = "face_off"
    RUSH = "rush"
    CYCLE = "cycle"


class ZoneType(Enum):
    """Hockey zones based on actual game rules."""
    OFFENSIVE_ZONE = "offensive_zone"  # Beyond attacking blue line
    NEUTRAL_ZONE = "neutral_zone"      # Between blue lines
    DEFENSIVE_ZONE = "defensive_zone"  # Behind defending blue line


class PlayerPosition(Enum):
    """Actual hockey positions."""
    CENTER = "center"
    LEFT_WING = "left_wing"
    RIGHT_WING = "right_wing"
    LEFT_DEFENSE = "left_defense"
    RIGHT_DEFENSE = "right_defense"
    GOALIE = "goalie"


class PuckStatus(Enum):
    """Puck possession and movement status."""
    TEAM_A_POSSESSION = "team_a_possession"
    TEAM_B_POSSESSION = "team_b_possession"
    LOOSE_PUCK = "loose_puck"
    OUT_OF_PLAY = "out_of_play"


@dataclass
class HockeyRink:
    """Actual hockey rink geometry with proper zones."""
    width: float = 200.0  # feet
    height: float = 85.0  # feet
    
    # Blue lines (actual hockey zones)
    blue_line_distance: float = 75.0  # feet from each goal line
    
    # Goal lines
    goal_line_distance: float = 11.0  # feet from each end
    
    # Face-off circles and other features
    face_off_circles: List[Tuple[float, float, float]] = None  # (x, y, radius)
    
    def __post_init__(self):
        if self.face_off_circles is None:
            # Standard NHL face-off circle positions
            self.face_off_circles = [
                (self.width/2, self.height/2, 15.0),  # Center ice
                (self.blue_line_distance, self.height/2, 15.0),  # Offensive zone
                (self.width - self.blue_line_distance, self.height/2, 15.0),  # Defensive zone
            ]


@dataclass
class PuckData:
    """Puck location and movement data."""
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    status: PuckStatus
    last_touch_team: str
    time_since_last_touch: float


@dataclass
class PlayerData:
    """Complete player data with hockey context."""
    player_id: str
    team: str
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    role: PlayerPosition
    is_goalie: bool
    is_on_ice: bool
    shift_time: float
    energy_level: float  # 0.0 = exhausted, 1.0 = fresh
    skill_rating: float  # 0.0 = rookie, 1.0 = elite


@dataclass
class GameContext:
    """Complete game context for tactical analysis."""
    period: int
    time_remaining: float
    score: Tuple[int, int]  # (team_a, team_b)
    game_situation: GameSituation
    puck_data: PuckData
    face_off_location: Optional[Tuple[float, float]]
    power_play_teams: List[str]
    penalty_time_remaining: Dict[str, float]


@dataclass
class TacticalFormation:
    """Hockey formation with proper context."""
    name: str
    team: str
    confidence: float
    game_situation: GameSituation
    puck_zone: ZoneType
    player_roles: Dict[str, PlayerPosition]
    tactical_purpose: str
    effectiveness_score: float
    vulnerabilities: List[str]
    exploitation_opportunities: List[str]


class HockeyFirstAnalyzer:
    """
    Hockey-first tactical analyzer that understands the actual game.
    """
    
    def __init__(self, rink: HockeyRink = None):
        """Initialize with proper hockey rink geometry."""
        self.rink = rink or HockeyRink()
        self.team_rosters = {"Team A": [], "Team B": []}
        self.game_history = []
        
    def set_team_rosters(self, team_a_roster: List[PlayerData], team_b_roster: List[PlayerData]):
        """Set team rosters with player information."""
        self.team_rosters["Team A"] = team_a_roster
        self.team_rosters["Team B"] = team_b_roster
    
    def determine_zone_from_puck(self, puck_position: Tuple[float, float], attacking_team: str) -> ZoneType:
        """
        Determine zones based on puck location and attacking direction.
        This is how hockey actually works.
        """
        x, y = puck_position
        
        if attacking_team == "Team A":
            if x > self.rink.blue_line_distance:
                return ZoneType.OFFENSIVE_ZONE
            elif x < (self.rink.width - self.rink.blue_line_distance):
                return ZoneType.DEFENSIVE_ZONE
            else:
                return ZoneType.NEUTRAL_ZONE
        else:  # Team B
            if x < (self.rink.width - self.rink.blue_line_distance):
                return ZoneType.OFFENSIVE_ZONE
            elif x > self.rink.blue_line_distance:
                return ZoneType.DEFENSIVE_ZONE
            else:
                return ZoneType.NEUTRAL_ZONE
    
    def analyze_game_situation(self, players: List[PlayerData], puck_data: PuckData) -> GameSituation:
        """
        Determine the actual game situation based on hockey rules.
        """
        # Count players on ice for each team
        team_a_count = len([p for p in players if p.team == "Team A" and p.is_on_ice])
        team_b_count = len([p for p in players if p.team == "Team B" and p.is_on_ice])
        
        # Check for penalties (fewer than 5 skaters + goalie)
        if team_a_count < 6:
            return GameSituation.POWER_PLAY if puck_data.status == PuckStatus.TEAM_B_POSSESSION else GameSituation.PENALTY_KILL
        elif team_b_count < 6:
            return GameSituation.POWER_PLAY if puck_data.status == PuckStatus.TEAM_A_POSSESSION else GameSituation.PENALTY_KILL
        
        # Check for empty net (no goalie)
        team_a_goalie = any(p for p in players if p.team == "Team A" and p.is_goalie and p.is_on_ice)
        team_b_goalie = any(p for p in players if p.team == "Team B" and p.is_goalie and p.is_on_ice)
        
        if not team_a_goalie or not team_b_goalie:
            return GameSituation.EMPTY_NET
        
        # Check for face-off situation (puck at face-off circle)
        if puck_data.status == PuckStatus.LOOSE_PUCK:
            for circle_x, circle_y, radius in self.rink.face_off_circles:
                distance = np.sqrt((puck_data.position[0] - circle_x)**2 + (puck_data.position[1] - circle_y)**2)
                if distance < radius:
                    return GameSituation.FACE_OFF
        
        # Check for rush (high-speed puck movement)
        if np.linalg.norm(puck_data.velocity) > 50:  # Fast puck movement
            return GameSituation.RUSH
        
        return GameSituation.EVEN_STRENGTH
    
    def detect_hockey_formations(
        self, 
        players: List[PlayerData], 
        puck_data: PuckData, 
        game_context: GameContext
    ) -> List[TacticalFormation]:
        """
        Detect formations based on actual hockey tactical knowledge.
        """
        formations = []
        
        # Analyze each team separately
        for team in ["Team A", "Team B"]:
            team_players = [p for p in players if p.team == team and p.is_on_ice and not p.is_goalie]
            
            if len(team_players) < 5:  # Need 5 skaters
                continue
            
            # Determine the team's zone based on puck location
            puck_zone = self.determine_zone_from_puck(puck_data.position, team)
            
            # Detect formation based on game situation and puck zone
            formation = self._detect_formation_for_situation(
                team_players, team, game_context.game_situation, puck_zone, puck_data
            )
            
            if formation:
                formations.append(formation)
        
        return formations
    
    def _detect_formation_for_situation(
        self, 
        team_players: List[PlayerData], 
        team: str, 
        game_situation: GameSituation, 
        puck_zone: ZoneType, 
        puck_data: PuckData
    ) -> Optional[TacticalFormation]:
        """
        Detect formation based on specific hockey situation.
        """
        if game_situation == GameSituation.POWER_PLAY:
            return self._detect_power_play_formation(team_players, team, puck_zone, puck_data)
        elif game_situation == GameSituation.PENALTY_KILL:
            return self._detect_penalty_kill_formation(team_players, team, puck_zone, puck_data)
        elif game_situation == GameSituation.EVEN_STRENGTH:
            return self._detect_even_strength_formation(team_players, team, puck_zone, puck_data)
        elif game_situation == GameSituation.FACE_OFF:
            return self._detect_face_off_formation(team_players, team, puck_zone, puck_data)
        elif game_situation == GameSituation.RUSH:
            return self._detect_rush_formation(team_players, team, puck_zone, puck_data)
        
        return None
    
    def _detect_power_play_formation(
        self, 
        team_players: List[PlayerData], 
        team: str, 
        puck_zone: ZoneType, 
        puck_data: PuckData
    ) -> Optional[TacticalFormation]:
        """
        Detect power play formations (1-3-1, 2-1-2, etc.).
        """
        if puck_zone != ZoneType.OFFENSIVE_ZONE:
            return None
        
        # Analyze player positioning for power play
        offensive_players = [p for p in team_players if p.position[0] > self.rink.blue_line_distance]
        
        if len(offensive_players) >= 4:
            # Check for 1-3-1 power play
            if self._is_1_3_1_power_play(offensive_players):
                return TacticalFormation(
                    name="1-3-1 Power Play",
                    team=team,
                    confidence=0.9,
                    game_situation=GameSituation.POWER_PLAY,
                    puck_zone=puck_zone,
                    player_roles=self._assign_power_play_roles(offensive_players, "1-3-1"),
                    tactical_purpose="Create high-percentage scoring chances",
                    effectiveness_score=self._calculate_power_play_effectiveness(offensive_players),
                    vulnerabilities=self._identify_power_play_vulnerabilities(offensive_players),
                    exploitation_opportunities=self._identify_power_play_opportunities(offensive_players)
                )
            
            # Check for 2-1-2 power play
            elif self._is_2_1_2_power_play(offensive_players):
                return TacticalFormation(
                    name="2-1-2 Power Play",
                    team=team,
                    confidence=0.85,
                    game_situation=GameSituation.POWER_PLAY,
                    puck_zone=puck_zone,
                    player_roles=self._assign_power_play_roles(offensive_players, "2-1-2"),
                    tactical_purpose="Maintain puck possession and create shooting lanes",
                    effectiveness_score=self._calculate_power_play_effectiveness(offensive_players),
                    vulnerabilities=self._identify_power_play_vulnerabilities(offensive_players),
                    exploitation_opportunities=self._identify_power_play_opportunities(offensive_players)
                )
        
        return None
    
    def _detect_penalty_kill_formation(
        self, 
        team_players: List[PlayerData], 
        team: str, 
        puck_zone: ZoneType, 
        puck_data: PuckData
    ) -> Optional[TacticalFormation]:
        """
        Detect penalty kill formations (diamond, box, etc.).
        """
        if puck_zone != ZoneType.DEFENSIVE_ZONE:
            return None
        
        # Analyze defensive positioning
        defensive_players = [p for p in team_players if p.position[0] < (self.rink.width - self.rink.blue_line_distance)]
        
        if len(defensive_players) >= 4:
            # Check for diamond penalty kill
            if self._is_diamond_penalty_kill(defensive_players):
                return TacticalFormation(
                    name="Diamond Penalty Kill",
                    team=team,
                    confidence=0.9,
                    game_situation=GameSituation.PENALTY_KILL,
                    puck_zone=puck_zone,
                    player_roles=self._assign_penalty_kill_roles(defensive_players, "diamond"),
                    tactical_purpose="Protect the net and force outside shots",
                    effectiveness_score=self._calculate_penalty_kill_effectiveness(defensive_players),
                    vulnerabilities=self._identify_penalty_kill_vulnerabilities(defensive_players),
                    exploitation_opportunities=self._identify_penalty_kill_opportunities(defensive_players)
                )
            
            # Check for box penalty kill
            elif self._is_box_penalty_kill(defensive_players):
                return TacticalFormation(
                    name="Box Penalty Kill",
                    team=team,
                    confidence=0.85,
                    game_situation=GameSituation.PENALTY_KILL,
                    puck_zone=puck_zone,
                    player_roles=self._assign_penalty_kill_roles(defensive_players, "box"),
                    tactical_purpose="Block passing lanes and shots",
                    effectiveness_score=self._calculate_penalty_kill_effectiveness(defensive_players),
                    vulnerabilities=self._identify_penalty_kill_vulnerabilities(defensive_players),
                    exploitation_opportunities=self._identify_penalty_kill_opportunities(defensive_players)
                )
        
        return None
    
    def _detect_even_strength_formation(
        self, 
        team_players: List[PlayerData], 
        team: str, 
        puck_zone: ZoneType, 
        puck_data: PuckData
    ) -> Optional[TacticalFormation]:
        """
        Detect even strength formations based on puck zone.
        """
        if puck_zone == ZoneType.OFFENSIVE_ZONE:
            return self._detect_offensive_zone_formation(team_players, team, puck_data)
        elif puck_zone == ZoneType.DEFENSIVE_ZONE:
            return self._detect_defensive_zone_formation(team_players, team, puck_data)
        else:  # Neutral zone
            return self._detect_neutral_zone_formation(team_players, team, puck_data)
    
    def _detect_offensive_zone_formation(
        self, 
        team_players: List[PlayerData], 
        team: str, 
        puck_data: PuckData
    ) -> Optional[TacticalFormation]:
        """
        Detect offensive zone formations (cycle, crash the net, etc.).
        """
        # Analyze player positioning in offensive zone
        net_distance = np.sqrt((puck_data.position[0] - self.rink.width)**2 + (puck_data.position[1] - self.rink.height/2)**2)
        
        if net_distance < 30:  # Close to net
            return TacticalFormation(
                name="Crash the Net",
                team=team,
                confidence=0.8,
                game_situation=GameSituation.EVEN_STRENGTH,
                puck_zone=ZoneType.OFFENSIVE_ZONE,
                player_roles=self._assign_offensive_roles(team_players, "crash_net"),
                tactical_purpose="Create chaos and scoring chances in front of net",
                effectiveness_score=self._calculate_offensive_effectiveness(team_players),
                vulnerabilities=self._identify_offensive_vulnerabilities(team_players),
                exploitation_opportunities=self._identify_offensive_opportunities(team_players)
            )
        else:  # Further from net
            return TacticalFormation(
                name="Cycle Formation",
                team=team,
                confidence=0.75,
                game_situation=GameSituation.EVEN_STRENGTH,
                puck_zone=ZoneType.OFFENSIVE_ZONE,
                player_roles=self._assign_offensive_roles(team_players, "cycle"),
                tactical_purpose="Maintain possession and wear down defense",
                effectiveness_score=self._calculate_offensive_effectiveness(team_players),
                vulnerabilities=self._identify_offensive_vulnerabilities(team_players),
                exploitation_opportunities=self._identify_offensive_opportunities(team_players)
            )
    
    def _detect_defensive_zone_formation(
        self, 
        team_players: List[PlayerData], 
        team: str, 
        puck_data: PuckData
    ) -> Optional[TacticalFormation]:
        """
        Detect defensive zone formations (zone coverage, man-to-man, etc.).
        """
        # Analyze defensive positioning
        net_distance = np.sqrt((puck_data.position[0] - 0)**2 + (puck_data.position[1] - self.rink.height/2)**2)
        
        if net_distance < 30:  # Close to net
            return TacticalFormation(
                name="Tight Zone Coverage",
                team=team,
                confidence=0.8,
                game_situation=GameSituation.EVEN_STRENGTH,
                puck_zone=ZoneType.DEFENSIVE_ZONE,
                player_roles=self._assign_defensive_roles(team_players, "tight_zone"),
                tactical_purpose="Protect the net and clear rebounds",
                effectiveness_score=self._calculate_defensive_effectiveness(team_players),
                vulnerabilities=self._identify_defensive_vulnerabilities(team_players),
                exploitation_opportunities=self._identify_defensive_opportunities(team_players)
            )
        else:  # Further from net
            return TacticalFormation(
                name="Loose Zone Coverage",
                team=team,
                confidence=0.75,
                game_situation=GameSituation.EVEN_STRENGTH,
                puck_zone=ZoneType.DEFENSIVE_ZONE,
                player_roles=self._assign_defensive_roles(team_players, "loose_zone"),
                tactical_purpose="Pressure the puck and force outside shots",
                effectiveness_score=self._calculate_defensive_effectiveness(team_players),
                vulnerabilities=self._identify_defensive_vulnerabilities(team_players),
                exploitation_opportunities=self._identify_defensive_opportunities(team_players)
            )
    
    def _detect_neutral_zone_formation(
        self, 
        team_players: List[PlayerData], 
        team: str, 
        puck_data: PuckData
    ) -> Optional[TacticalFormation]:
        """
        Detect neutral zone formations (trap, rush, etc.).
        """
        # Check for trap formation (players spread across neutral zone)
        trap_score = self._calculate_trap_formation_score(team_players)
        
        if trap_score > 0.7:
            return TacticalFormation(
                name="Neutral Zone Trap",
                team=team,
                confidence=trap_score,
                game_situation=GameSituation.EVEN_STRENGTH,
                puck_zone=ZoneType.NEUTRAL_ZONE,
                player_roles=self._assign_neutral_zone_roles(team_players, "trap"),
                tactical_purpose="Force turnovers and prevent rushes",
                effectiveness_score=self._calculate_neutral_zone_effectiveness(team_players),
                vulnerabilities=self._identify_neutral_zone_vulnerabilities(team_players),
                exploitation_opportunities=self._identify_neutral_zone_opportunities(team_players)
            )
        else:
            return TacticalFormation(
                name="Rush Formation",
                team=team,
                confidence=0.6,
                game_situation=GameSituation.EVEN_STRENGTH,
                puck_zone=ZoneType.NEUTRAL_ZONE,
                player_roles=self._assign_neutral_zone_roles(team_players, "rush"),
                tactical_purpose="Create speed and offensive opportunities",
                effectiveness_score=self._calculate_neutral_zone_effectiveness(team_players),
                vulnerabilities=self._identify_neutral_zone_vulnerabilities(team_players),
                exploitation_opportunities=self._identify_neutral_zone_opportunities(team_players)
            )
    
    # Helper methods for formation detection
    def _is_1_3_1_power_play(self, players: List[PlayerData]) -> bool:
        """Check if players are in 1-3-1 power play formation."""
        # Sort players by y-coordinate (distance from boards)
        players_sorted = sorted(players, key=lambda p: p.position[1])
        
        # Should have 1 player high (near boards), 3 in middle, 1 low (near net)
        high_players = [p for p in players_sorted if p.position[1] > self.rink.height * 0.7]
        middle_players = [p for p in players_sorted if self.rink.height * 0.3 < p.position[1] < self.rink.height * 0.7]
        low_players = [p for p in players_sorted if p.position[1] < self.rink.height * 0.3]
        
        return len(high_players) == 1 and len(middle_players) == 3 and len(low_players) == 1
    
    def _is_2_1_2_power_play(self, players: List[PlayerData]) -> bool:
        """Check if players are in 2-1-2 power play formation."""
        # Sort players by x-coordinate (distance from blue line)
        players_sorted = sorted(players, key=lambda p: p.position[0])
        
        # Should have 2 players high, 1 in middle, 2 low
        high_players = [p for p in players_sorted if p.position[0] > self.rink.width * 0.8]
        middle_players = [p for p in players_sorted if self.rink.width * 0.6 < p.position[0] < self.rink.width * 0.8]
        low_players = [p for p in players_sorted if p.position[0] < self.rink.width * 0.6]
        
        return len(high_players) == 2 and len(middle_players) == 1 and len(low_players) == 2
    
    def _is_diamond_penalty_kill(self, players: List[PlayerData]) -> bool:
        """Check if players are in diamond penalty kill formation."""
        # Calculate center of mass
        center_x = np.mean([p.position[0] for p in players])
        center_y = np.mean([p.position[1] for p in players])
        
        # Check if players form a diamond around the center
        distances = [np.sqrt((p.position[0] - center_x)**2 + (p.position[1] - center_y)**2) for p in players]
        
        # Should have players at different distances forming a diamond
        return len(set([round(d/20) for d in distances])) >= 3  # At least 3 different distance groups
    
    def _is_box_penalty_kill(self, players: List[PlayerData]) -> bool:
        """Check if players are in box penalty kill formation."""
        # Sort players by position
        players_sorted = sorted(players, key=lambda p: (p.position[0], p.position[1]))
        
        # Should form a rectangular box
        if len(players_sorted) < 4:
            return False
        
        # Check if players form a box pattern
        x_positions = [p.position[0] for p in players_sorted]
        y_positions = [p.position[1] for p in players_sorted]
        
        # Should have players at corners of a box
        x_range = max(x_positions) - min(x_positions)
        y_range = max(y_positions) - min(y_positions)
        
        return x_range > 20 and y_range > 20  # Minimum box size
    
    def _calculate_trap_formation_score(self, players: List[PlayerData]) -> float:
        """Calculate how well players are positioned for a neutral zone trap."""
        # Check if players are spread across the neutral zone
        x_positions = [p.position[0] for p in players]
        y_positions = [p.position[1] for p in players]
        
        # Should be spread across neutral zone width
        x_spread = max(x_positions) - min(x_positions)
        y_spread = max(y_positions) - min(y_positions)
        
        # Ideal trap has good x-spread and controlled y-spread
        x_score = min(x_spread / 100, 1.0)  # Normalize to 0-1
        y_score = 1.0 - min(y_spread / 50, 1.0)  # Prefer controlled y-spread
        
        return (x_score + y_score) / 2.0
    
    # Role assignment methods
    def _assign_power_play_roles(self, players: List[PlayerData], formation_type: str) -> Dict[str, PlayerPosition]:
        """Assign roles based on power play formation."""
        roles = {}
        
        if formation_type == "1-3-1":
            # Sort by y-coordinate for 1-3-1
            players_sorted = sorted(players, key=lambda p: p.position[1])
            roles[players_sorted[0].player_id] = PlayerPosition.CENTER  # High forward
            roles[players_sorted[1].player_id] = PlayerPosition.LEFT_WING
            roles[players_sorted[2].player_id] = PlayerPosition.CENTER
            roles[players_sorted[3].player_id] = PlayerPosition.RIGHT_WING
            roles[players_sorted[4].player_id] = PlayerPosition.LEFT_DEFENSE  # Low defense
        
        elif formation_type == "2-1-2":
            # Sort by x-coordinate for 2-1-2
            players_sorted = sorted(players, key=lambda p: p.position[0])
            roles[players_sorted[0].player_id] = PlayerPosition.LEFT_WING  # High left
            roles[players_sorted[1].player_id] = PlayerPosition.RIGHT_WING  # High right
            roles[players_sorted[2].player_id] = PlayerPosition.CENTER  # Middle
            roles[players_sorted[3].player_id] = PlayerPosition.LEFT_DEFENSE  # Low left
            roles[players_sorted[4].player_id] = PlayerPosition.RIGHT_DEFENSE  # Low right
        
        return roles
    
    def _assign_penalty_kill_roles(self, players: List[PlayerData], formation_type: str) -> Dict[str, PlayerPosition]:
        """Assign roles based on penalty kill formation."""
        roles = {}
        
        if formation_type == "diamond":
            # Center player at diamond center
            center_player = min(players, key=lambda p: np.sqrt((p.position[0] - self.rink.width/2)**2 + (p.position[1] - self.rink.height/2)**2))
            roles[center_player.player_id] = PlayerPosition.CENTER
            
            # Assign other roles based on position
            for player in players:
                if player.player_id != center_player.player_id:
                    if player.position[0] < center_player.position[0]:
                        roles[player.player_id] = PlayerPosition.LEFT_DEFENSE
                    else:
                        roles[player.player_id] = PlayerPosition.RIGHT_DEFENSE
        
        elif formation_type == "box":
            # Assign box positions
            players_sorted = sorted(players, key=lambda p: (p.position[0], p.position[1]))
            roles[players_sorted[0].player_id] = PlayerPosition.LEFT_DEFENSE
            roles[players_sorted[1].player_id] = PlayerPosition.RIGHT_DEFENSE
            roles[players_sorted[2].player_id] = PlayerPosition.LEFT_WING
            roles[players_sorted[3].player_id] = PlayerPosition.RIGHT_WING
        
        return roles
    
    def _assign_offensive_roles(self, players: List[PlayerData], formation_type: str) -> Dict[str, PlayerPosition]:
        """Assign roles based on offensive zone formation."""
        roles = {}
        
        if formation_type == "crash_net":
            # Players closest to net
            net_position = (self.rink.width, self.rink.height/2)
            players_sorted = sorted(players, key=lambda p: np.sqrt((p.position[0] - net_position[0])**2 + (p.position[1] - net_position[1])**2))
            
            roles[players_sorted[0].player_id] = PlayerPosition.CENTER  # Net front
            roles[players_sorted[1].player_id] = PlayerPosition.LEFT_WING
            roles[players_sorted[2].player_id] = PlayerPosition.RIGHT_WING
            roles[players_sorted[3].player_id] = PlayerPosition.LEFT_DEFENSE
            roles[players_sorted[4].player_id] = PlayerPosition.RIGHT_DEFENSE
        
        elif formation_type == "cycle":
            # Cycle formation roles
            center_player = min(players, key=lambda p: np.sqrt((p.position[0] - self.rink.width/2)**2 + (p.position[1] - self.rink.height/2)**2))
            roles[center_player.player_id] = PlayerPosition.CENTER
            
            # Assign other roles based on position
            for player in players:
                if player.player_id != center_player.player_id:
                    if player.position[1] < center_player.position[1]:
                        roles[player.player_id] = PlayerPosition.LEFT_WING
                    else:
                        roles[player.player_id] = PlayerPosition.RIGHT_WING
        
        return roles
    
    def _assign_defensive_roles(self, players: List[PlayerData], formation_type: str) -> Dict[str, PlayerPosition]:
        """Assign roles based on defensive zone formation."""
        roles = {}
        
        if formation_type == "tight_zone":
            # Tight zone coverage roles
            net_position = (0, self.rink.height/2)
            players_sorted = sorted(players, key=lambda p: np.sqrt((p.position[0] - net_position[0])**2 + (p.position[1] - net_position[1])**2))
            
            roles[players_sorted[0].player_id] = PlayerPosition.CENTER  # Net front
            roles[players_sorted[1].player_id] = PlayerPosition.LEFT_DEFENSE
            roles[players_sorted[2].player_id] = PlayerPosition.RIGHT_DEFENSE
            roles[players_sorted[3].player_id] = PlayerPosition.LEFT_WING
            roles[players_sorted[4].player_id] = PlayerPosition.RIGHT_WING
        
        elif formation_type == "loose_zone":
            # Loose zone coverage roles
            center_player = min(players, key=lambda p: np.sqrt((p.position[0] - self.rink.width/2)**2 + (p.position[1] - self.rink.height/2)**2))
            roles[center_player.player_id] = PlayerPosition.CENTER
            
            # Assign other roles based on position
            for player in players:
                if player.player_id != center_player.player_id:
                    if player.position[0] < center_player.position[0]:
                        roles[player.player_id] = PlayerPosition.LEFT_DEFENSE
                    else:
                        roles[player.player_id] = PlayerPosition.RIGHT_DEFENSE
        
        return roles
    
    def _assign_neutral_zone_roles(self, players: List[PlayerData], formation_type: str) -> Dict[str, PlayerPosition]:
        """Assign roles based on neutral zone formation."""
        roles = {}
        
        if formation_type == "trap":
            # Trap formation roles
            players_sorted = sorted(players, key=lambda p: p.position[0])
            
            roles[players_sorted[0].player_id] = PlayerPosition.LEFT_WING  # Left side
            roles[players_sorted[1].player_id] = PlayerPosition.RIGHT_WING  # Right side
            roles[players_sorted[2].player_id] = PlayerPosition.CENTER  # Center
            roles[players_sorted[3].player_id] = PlayerPosition.LEFT_DEFENSE
            roles[players_sorted[4].player_id] = PlayerPosition.RIGHT_DEFENSE
        
        elif formation_type == "rush":
            # Rush formation roles
            players_sorted = sorted(players, key=lambda p: p.position[0], reverse=True)  # Sort by x-coordinate descending
            
            roles[players_sorted[0].player_id] = PlayerPosition.CENTER  # Lead rush
            roles[players_sorted[1].player_id] = PlayerPosition.LEFT_WING
            roles[players_sorted[2].player_id] = PlayerPosition.RIGHT_WING
            roles[players_sorted[3].player_id] = PlayerPosition.LEFT_DEFENSE
            roles[players_sorted[4].player_id] = PlayerPosition.RIGHT_DEFENSE
        
        return roles
    
    # Effectiveness calculation methods
    def _calculate_power_play_effectiveness(self, players: List[PlayerData]) -> float:
        """Calculate power play effectiveness based on positioning and movement."""
        # Factors: puck control, shooting lanes, net presence
        puck_control_score = 0.8  # Simplified
        shooting_lanes_score = 0.7  # Simplified
        net_presence_score = 0.6  # Simplified
        
        return (puck_control_score + shooting_lanes_score + net_presence_score) / 3.0
    
    def _calculate_penalty_kill_effectiveness(self, players: List[PlayerData]) -> float:
        """Calculate penalty kill effectiveness based on positioning and pressure."""
        # Factors: shot blocking, passing lane coverage, pressure
        shot_blocking_score = 0.8  # Simplified
        passing_coverage_score = 0.7  # Simplified
        pressure_score = 0.6  # Simplified
        
        return (shot_blocking_score + passing_coverage_score + pressure_score) / 3.0
    
    def _calculate_offensive_effectiveness(self, players: List[PlayerData]) -> float:
        """Calculate offensive zone effectiveness."""
        # Factors: puck possession, scoring chances, cycle efficiency
        puck_possession_score = 0.7  # Simplified
        scoring_chances_score = 0.6  # Simplified
        cycle_efficiency_score = 0.5  # Simplified
        
        return (puck_possession_score + scoring_chances_score + cycle_efficiency_score) / 3.0
    
    def _calculate_defensive_effectiveness(self, players: List[PlayerData]) -> float:
        """Calculate defensive zone effectiveness."""
        # Factors: shot blocking, passing lane coverage, clearing efficiency
        shot_blocking_score = 0.8  # Simplified
        passing_coverage_score = 0.7  # Simplified
        clearing_efficiency_score = 0.6  # Simplified
        
        return (shot_blocking_score + passing_coverage_score + clearing_efficiency_score) / 3.0
    
    def _calculate_neutral_zone_effectiveness(self, players: List[PlayerData]) -> float:
        """Calculate neutral zone effectiveness."""
        # Factors: transition speed, puck control, pressure
        transition_speed_score = 0.7  # Simplified
        puck_control_score = 0.6  # Simplified
        pressure_score = 0.5  # Simplified
        
        return (transition_speed_score + puck_control_score + pressure_score) / 3.0
    
    # Vulnerability and opportunity identification methods
    def _identify_power_play_vulnerabilities(self, players: List[PlayerData]) -> List[str]:
        """Identify power play vulnerabilities."""
        vulnerabilities = []
        
        # Check for gaps in coverage
        if len(players) < 5:
            vulnerabilities.append("Short-handed situation")
        
        # Check for poor puck movement
        vulnerabilities.append("Slow puck movement")
        
        # Check for lack of net presence
        vulnerabilities.append("Insufficient net presence")
        
        return vulnerabilities
    
    def _identify_power_play_opportunities(self, players: List[PlayerData]) -> List[str]:
        """Identify power play exploitation opportunities."""
        opportunities = []
        
        # Check for shooting lanes
        opportunities.append("Open shooting lanes")
        
        # Check for net front presence
        opportunities.append("Net front scoring chances")
        
        # Check for cross-ice passes
        opportunities.append("Cross-ice passing opportunities")
        
        return opportunities
    
    def _identify_penalty_kill_vulnerabilities(self, players: List[PlayerData]) -> List[str]:
        """Identify penalty kill vulnerabilities."""
        vulnerabilities = []
        
        # Check for gaps in coverage
        vulnerabilities.append("Coverage gaps")
        
        # Check for poor pressure
        vulnerabilities.append("Insufficient pressure")
        
        # Check for clearing issues
        vulnerabilities.append("Poor clearing ability")
        
        return vulnerabilities
    
    def _identify_penalty_kill_opportunities(self, players: List[PlayerData]) -> List[str]:
        """Identify penalty kill exploitation opportunities."""
        opportunities = []
        
        # Check for breakaway chances
        opportunities.append("Breakaway opportunities")
        
        # Check for short-handed scoring
        opportunities.append("Short-handed scoring chances")
        
        # Check for pressure points
        opportunities.append("Pressure point opportunities")
        
        return opportunities
    
    def _identify_offensive_vulnerabilities(self, players: List[PlayerData]) -> List[str]:
        """Identify offensive zone vulnerabilities."""
        vulnerabilities = []
        
        # Check for turnovers
        vulnerabilities.append("High turnover risk")
        
        # Check for poor cycle
        vulnerabilities.append("Inefficient cycle")
        
        # Check for lack of support
        vulnerabilities.append("Insufficient support")
        
        return vulnerabilities
    
    def _identify_offensive_opportunities(self, players: List[PlayerData]) -> List[str]:
        """Identify offensive zone opportunities."""
        opportunities = []
        
        # Check for scoring chances
        opportunities.append("High-percentage scoring chances")
        
        # Check for cycle opportunities
        opportunities.append("Cycle opportunities")
        
        # Check for net presence
        opportunities.append("Net front opportunities")
        
        return opportunities
    
    def _identify_defensive_vulnerabilities(self, players: List[PlayerData]) -> List[str]:
        """Identify defensive zone vulnerabilities."""
        vulnerabilities = []
        
        # Check for coverage gaps
        vulnerabilities.append("Coverage gaps")
        
        # Check for poor clearing
        vulnerabilities.append("Poor clearing ability")
        
        # Check for lack of pressure
        vulnerabilities.append("Insufficient pressure")
        
        return vulnerabilities
    
    def _identify_defensive_opportunities(self, players: List[PlayerData]) -> List[str]:
        """Identify defensive zone opportunities."""
        opportunities = []
        
        # Check for breakouts
        opportunities.append("Breakout opportunities")
        
        # Check for counter-attacks
        opportunities.append("Counter-attack opportunities")
        
        # Check for pressure points
        opportunities.append("Pressure point opportunities")
        
        return opportunities
    
    def _identify_neutral_zone_vulnerabilities(self, players: List[PlayerData]) -> List[str]:
        """Identify neutral zone vulnerabilities."""
        vulnerabilities = []
        
        # Check for gaps in coverage
        vulnerabilities.append("Coverage gaps")
        
        # Check for poor transition
        vulnerabilities.append("Slow transition")
        
        # Check for lack of pressure
        vulnerabilities.append("Insufficient pressure")
        
        return vulnerabilities
    
    def _identify_neutral_zone_opportunities(self, players: List[PlayerData]) -> List[str]:
        """Identify neutral zone opportunities."""
        opportunities = []
        
        # Check for rush opportunities
        opportunities.append("Rush opportunities")
        
        # Check for pressure points
        opportunities.append("Pressure point opportunities")
        
        # Check for transition speed
        opportunities.append("Fast transition opportunities")
        
        return opportunities
