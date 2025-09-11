"""
Main Tactical Analyzer for Hockey Analysis

This module integrates formation detection, zone analysis, and movement tracking
to provide comprehensive tactical insights from player tracking data.
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import logging
from datetime import datetime

from formation_detector import FormationDetector, RinkZone
from zone_analyzer import ZoneAnalyzer
from tactical_weakness_detector import TacticalWeaknessDetector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TacticalAnalyzer:
    """
    Main tactical analysis engine that integrates all analysis components.
    
    Provides comprehensive analysis of hockey tactics, formations, and
    strategic patterns from player tracking data.
    """
    
    def __init__(
        self, 
        input_path: Union[str, Path],
        rink_dimensions: Tuple[int, int] = (1400, 600),
        output_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize the tactical analyzer.
        
        Args:
            input_path: Path to tracking data (JSON or CSV)
            rink_dimensions: Tuple of (width, height) for the rink image
            output_dir: Directory to save analysis results
        """
        self.input_path = Path(input_path)
        self.rink_dimensions = rink_dimensions
        self.output_dir = Path(output_dir) if output_dir else Path("results")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analysis components
        self.formation_detector = FormationDetector(rink_dimensions)
        self.zone_analyzer = ZoneAnalyzer(rink_dimensions)
        self.weakness_detector = TacticalWeaknessDetector(rink_dimensions)
        
        # Load and process tracking data
        self.tracking_data = self._load_tracking_data()
        
        # Analysis results cache
        self._formation_analysis = None
        self._zone_analysis = None
        self._tactical_insights = None
        
        logger.info(f"Tactical analyzer initialized with {len(self.tracking_data)} frames")
    
    def _load_tracking_data(self) -> List[Dict]:
        """
        Load tracking data from JSON or CSV file.
        
        Returns:
            List of frame data dictionaries
        """
        if self.input_path.suffix.lower() == '.json':
            return self._load_json_data()
        elif self.input_path.suffix.lower() == '.csv':
            return self._load_csv_data()
        else:
            raise ValueError(f"Unsupported file format: {self.input_path.suffix}")
    
    def _load_json_data(self) -> List[Dict]:
        """Load tracking data from JSON file."""
        try:
            with open(self.input_path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if 'frames' in data:
                return data['frames']
            elif isinstance(data, list):
                return data
            else:
                logger.warning("Unexpected JSON structure, attempting to parse as frames list")
                return [data]
                
        except Exception as e:
            logger.error(f"Error loading JSON data: {e}")
            raise
    
    def _load_csv_data(self) -> List[Dict]:
        """Load tracking data from CSV file."""
        try:
            df = pd.read_csv(self.input_path)
            
            # Group by frame and reconstruct frame data
            frames = []
            for frame_id in df['frame_id'].unique():
                frame_data = df[df['frame_id'] == frame_id]
                
                # Extract frame metadata
                frame_info = {
                    'frame_id': int(frame_id),
                    'timestamp': frame_data['timestamp'].iloc[0] if 'timestamp' in frame_data.columns else 0.0,
                    'players': []
                }
                
                # Extract player data
                for _, row in frame_data.iterrows():
                    player = {
                        'player_id': row.get('player_id', f'player_{len(frame_info["players"])}'),
                        'rink_position': {
                            'x': row.get('x', 0.0),
                            'y': row.get('y', 0.0)
                        },
                        'orientation': row.get('orientation', 0.0)
                    }
                    
                    # Add bounding box if available
                    if 'bbox_x1' in row.columns:
                        player['bbox'] = [
                            row.get('bbox_x1', 0.0),
                            row.get('bbox_y1', 0.0),
                            row.get('bbox_x2', 0.0),
                            row.get('bbox_y2', 0.0)
                        ]
                    
                    frame_info['players'].append(player)
                
                frames.append(frame_info)
            
            # Sort frames by frame_id
            frames.sort(key=lambda x: x['frame_id'])
            return frames
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            raise
    
    def analyze_formations(
        self, 
        min_frames: int = 5,
        min_confidence: float = 0.6
    ) -> Dict[str, Any]:
        """
        Analyze hockey formations throughout the game.
        
        Args:
            min_frames: Minimum consecutive frames to confirm formation
            min_confidence: Minimum confidence threshold for formation detection
            
        Returns:
            Dictionary with formation analysis results
        """
        if self._formation_analysis is None:
            logger.info("Analyzing formations...")
            
            # Detect formations over time
            detected_formations = self.formation_detector.detect_formations_over_time(
                self.tracking_data, min_frames
            )
            
            # Analyze formation transitions
            transition_analysis = self.formation_detector.analyze_formation_transitions(
                detected_formations
            )
            
            # Calculate formation statistics
            formation_stats = self.formation_detector.get_formation_statistics(
                detected_formations
            )
            
            self._formation_analysis = {
                "detected_formations": detected_formations,
                "transition_analysis": transition_analysis,
                "formation_statistics": formation_stats,
                "analysis_parameters": {
                    "min_frames": min_frames,
                    "min_confidence": min_confidence,
                    "total_frames": len(self.tracking_data)
                }
            }
            
            logger.info(f"Formation analysis complete: {len(detected_formations)} formations detected")
        
        return self._formation_analysis
    
    def analyze_zones(self) -> Dict[str, Any]:
        """
        Analyze player positioning and distribution across rink zones.
        
        Returns:
            Dictionary with zone analysis results
        """
        if self._zone_analysis is None:
            logger.info("Analyzing zone distribution...")
            
            # Generate comprehensive zone report
            self._zone_analysis = self.zone_analyzer.generate_zone_report(self.tracking_data)
            
            logger.info("Zone analysis complete")
        
        return self._zone_analysis
    
    def generate_tactical_insights(self) -> Dict[str, Any]:
        """
        Generate comprehensive tactical insights from all analyses.
        
        Returns:
            Dictionary with tactical insights and recommendations
        """
        if self._tactical_insights is None:
            logger.info("Generating tactical insights...")
            
            # Ensure all analyses are complete
            formation_analysis = self.analyze_formations()
            zone_analysis = self.analyze_zones()
            
            # Generate tactical insights
            insights = self._analyze_tactical_patterns(formation_analysis, zone_analysis)
            
            # Generate strategic recommendations
            recommendations = self._generate_strategic_recommendations(
                formation_analysis, zone_analysis
            )
            
            # Compile comprehensive insights
            self._tactical_insights = {
                "tactical_patterns": insights,
                "strategic_recommendations": recommendations,
                "summary": self._generate_tactical_summary(formation_analysis, zone_analysis),
                "analysis_timestamp": datetime.now().isoformat(),
                "data_source": str(self.input_path)
            }
            
            logger.info("Tactical insights generated")
        
        return self._tactical_insights
    
    def _analyze_tactical_patterns(
        self, 
        formation_analysis: Dict[str, Any], 
        zone_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze tactical patterns from formation and zone analysis.
        
        Args:
            formation_analysis: Results from formation analysis
            zone_analysis: Results from zone analysis
            
        Returns:
            Dictionary with tactical pattern analysis
        """
        patterns = {}
        
        # Analyze formation effectiveness
        if formation_analysis["detected_formations"]:
            patterns["formation_effectiveness"] = self._analyze_formation_effectiveness(
                formation_analysis
            )
        
        # Analyze tactical transitions
        if formation_analysis["transition_analysis"]["transitions"]:
            patterns["tactical_transitions"] = self._analyze_tactical_transitions(
                formation_analysis
            )
        
        # Analyze zone-based tactics
        patterns["zone_tactics"] = self._analyze_zone_tactics(zone_analysis)
        
        # Analyze pressure patterns
        patterns["pressure_analysis"] = self._analyze_pressure_patterns(zone_analysis)
        
        return patterns
    
    def _analyze_formation_effectiveness(
        self, 
        formation_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze the effectiveness of different formations.
        
        Args:
            formation_analysis: Results from formation analysis
            
        Returns:
            Dictionary with formation effectiveness analysis
        """
        formations = formation_analysis["detected_formations"]
        stats = formation_analysis["formation_statistics"]
        
        effectiveness = {}
        
        for formation_name, formation_stats in stats["formation_counts"].items():
            # Calculate effectiveness metrics
            avg_duration = formation_stats["total_duration"] / formation_stats["count"]
            consistency = formation_stats["avg_confidence"]
            
            # Classify formation effectiveness
            if consistency >= 0.8 and avg_duration >= 15:
                effectiveness_level = "high"
            elif consistency >= 0.6 and avg_duration >= 10:
                effectiveness_level = "medium"
            else:
                effectiveness_level = "low"
            
            effectiveness[formation_name] = {
                "effectiveness_level": effectiveness_level,
                "avg_duration": avg_duration,
                "consistency": consistency,
                "usage_percentage": formation_stats["percentage_of_game"],
                "recommendation": self._get_formation_recommendation(
                    formation_name, effectiveness_level, formation_stats
                )
            }
        
        return effectiveness
    
    def _analyze_tactical_transitions(
        self, 
        formation_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze tactical transitions between formations.
        
        Args:
            formation_analysis: Results from formation analysis
            
        Returns:
            Dictionary with transition analysis
        """
        transitions = formation_analysis["transition_analysis"]
        
        # Analyze transition patterns
        transition_analysis = {
            "total_transitions": transitions["total_transitions"],
            "most_common_transition": transitions["most_common"],
            "transition_frequency": self._calculate_transition_frequency(transitions),
            "transition_patterns": self._identify_transition_patterns(transitions)
        }
        
        return transition_analysis
    
    def _analyze_zone_tactics(self, zone_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze zone-based tactical patterns.
        
        Args:
            zone_analysis: Results from zone analysis
            
        Returns:
            Dictionary with zone tactical analysis
        """
        zone_tactics = {}
        
        # Analyze offensive tactics
        if zone_analysis["forecheck_analysis"]["forecheck_detected"]:
            zone_tactics["offensive_tactics"] = {
                "forechecking_style": self._classify_forechecking_style(
                    zone_analysis["forecheck_analysis"]
                ),
                "pressure_consistency": self._analyze_pressure_consistency(
                    zone_analysis["forecheck_analysis"]
                )
            }
        
        # Analyze defensive tactics
        if zone_analysis["defensive_analysis"]["defensive_coverage"]:
            zone_tactics["defensive_tactics"] = {
                "coverage_style": self._classify_defensive_style(
                    zone_analysis["defensive_analysis"]
                ),
                "collapse_patterns": self._analyze_collapse_patterns(
                    zone_analysis["defensive_analysis"]
                )
            }
        
        # Analyze neutral zone tactics
        if zone_analysis["trap_analysis"]["trap_detected"]:
            zone_tactics["neutral_zone_tactics"] = {
                "trap_effectiveness": self._analyze_trap_effectiveness(
                    zone_analysis["trap_analysis"]
                ),
                "trap_timing": self._analyze_trap_timing(
                    zone_analysis["trap_analysis"]
                )
            }
        
        return zone_tactics
    
    def _analyze_pressure_patterns(self, zone_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze pressure patterns across all zones.
        
        Args:
            zone_analysis: Results from zone analysis
            
        Returns:
            Dictionary with pressure pattern analysis
        """
        pressure_patterns = {}
        
        # Analyze offensive pressure
        if zone_analysis["forecheck_analysis"]["forecheck_detected"]:
            forecheck = zone_analysis["forecheck_analysis"]
            pressure_patterns["offensive_pressure"] = {
                "pressure_level": forecheck["avg_pressure"],
                "pressure_consistency": forecheck["pressure_patterns"]["pressure_levels"]["high_pressure"] / max(forecheck["total_instances"], 1),
                "sustained_pressure": forecheck["pressure_patterns"]["timing_patterns"]["sustained_pressure"]
            }
        
        # Analyze defensive pressure
        if zone_analysis["defensive_analysis"]["defensive_coverage"]:
            defensive = zone_analysis["defensive_analysis"]
            pressure_patterns["defensive_pressure"] = {
                "coverage_density": defensive["avg_coverage"],
                "coverage_consistency": defensive["coverage_patterns"]["coverage_levels"]["heavy_coverage"] / max(defensive["total_instances"], 1)
            }
        
        return pressure_patterns
    
    def _get_formation_recommendation(
        self, 
        formation_name: str, 
        effectiveness_level: str, 
        formation_stats: Dict[str, Any]
    ) -> str:
        """
        Generate recommendations for formation usage.
        
        Args:
            formation_name: Name of the formation
            effectiveness_level: Effectiveness level (high/medium/low)
            formation_stats: Statistics for the formation
            
        Returns:
            Recommendation string
        """
        if effectiveness_level == "high":
            return f"Continue using {formation_name} - it's working well with {formation_stats['avg_confidence']:.2f} confidence"
        elif effectiveness_level == "medium":
            return f"Consider refining {formation_name} - moderate effectiveness with room for improvement"
        else:
            return f"Review {formation_name} strategy - low effectiveness suggests need for tactical adjustment"
    
    def _calculate_transition_frequency(self, transitions: Dict[str, Any]) -> float:
        """Calculate the frequency of formation transitions."""
        if not transitions["transitions"]:
            return 0.0
        
        # Calculate average frames between transitions
        total_frames = max(transitions["transitions"][-1]["transition_frame"], 1)
        return len(transitions["transitions"]) / total_frames
    
    def _identify_transition_patterns(self, transitions: Dict[str, Any]) -> Dict[str, Any]:
        """Identify patterns in formation transitions."""
        if not transitions["transitions"]:
            return {}
        
        # Analyze transition timing
        transition_times = [t["transition_time"] for t in transitions["transitions"]]
        
        # Group transitions by time periods
        early_transitions = len([t for t in transition_times if t < 300])  # First 5 minutes
        mid_transitions = len([t for t in transition_times if 300 <= t < 900])  # 5-15 minutes
        late_transitions = len([t for t in transition_times if t >= 900])  # After 15 minutes
        
        return {
            "early_game_transitions": early_transitions,
            "mid_game_transitions": mid_transitions,
            "late_game_transitions": late_transitions,
            "transition_timing_pattern": "early" if early_transitions > mid_transitions else "consistent"
        }
    
    def _classify_forechecking_style(self, forecheck_analysis: Dict[str, Any]) -> str:
        """Classify the team's forechecking style."""
        avg_pressure = forecheck_analysis["avg_pressure"]
        
        if avg_pressure >= 0.8:
            return "aggressive"
        elif avg_pressure >= 0.5:
            return "moderate"
        else:
            return "conservative"
    
    def _analyze_pressure_consistency(self, forecheck_analysis: Dict[str, Any]) -> float:
        """Analyze the consistency of offensive pressure."""
        pressure_levels = forecheck_analysis["pressure_patterns"]["pressure_levels"]
        total_instances = forecheck_analysis["total_instances"]
        
        if total_instances == 0:
            return 0.0
        
        # Calculate consistency based on pressure level distribution
        high_pressure_ratio = pressure_levels["high_pressure"] / total_instances
        return high_pressure_ratio
    
    def _classify_defensive_style(self, defensive_analysis: Dict[str, Any]) -> str:
        """Classify the team's defensive style."""
        avg_coverage = defensive_analysis["avg_coverage"]
        
        if avg_coverage >= 0.8:
            return "collapsing"
        elif avg_coverage >= 0.6:
            return "balanced"
        else:
            return "aggressive"
    
    def _analyze_collapse_patterns(self, defensive_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze defensive collapse patterns."""
        coverage_patterns = defensive_analysis["coverage_patterns"]
        
        return {
            "formation_preference": max(coverage_patterns["formation_patterns"].items(), key=lambda x: x[1])[0],
            "coverage_intensity": "heavy" if coverage_patterns["coverage_levels"]["heavy_coverage"] > coverage_patterns["coverage_levels"]["light_coverage"] else "light"
        }
    
    def _analyze_trap_effectiveness(self, trap_analysis: Dict[str, Any]) -> str:
        """Analyze the effectiveness of neutral zone trap."""
        if trap_analysis["percentage_of_game"] >= 20:
            return "frequent"
        elif trap_analysis["percentage_of_game"] >= 10:
            return "moderate"
        else:
            return "occasional"
    
    def _analyze_trap_timing(self, trap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the timing of trap formations."""
        patterns = trap_analysis["patterns"]
        
        return {
            "sustained_traps": patterns["duration_patterns"]["consecutive_frames"],
            "avg_trap_duration": patterns["duration_patterns"]["avg_duration"],
            "trap_frequency": patterns["frequency_patterns"]["avg_gap"]
        }
    
    def _generate_strategic_recommendations(
        self, 
        formation_analysis: Dict[str, Any], 
        zone_analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate strategic recommendations based on analysis.
        
        Args:
            formation_analysis: Results from formation analysis
            zone_analysis: Results from zone analysis
            
        Returns:
            Dictionary with strategic recommendations
        """
        recommendations = {}
        
        # Formation-based recommendations
        if formation_analysis["detected_formations"]:
            effectiveness = self._analyze_formation_effectiveness(formation_analysis)
            
            # Identify best and worst formations
            best_formation = max(effectiveness.items(), key=lambda x: x[1]["effectiveness_level"] == "high")
            worst_formation = min(effectiveness.items(), key=lambda x: x[1]["effectiveness_level"] == "low")
            
            recommendations["formation_strategy"] = (
                f"Focus on {best_formation[0]} formation (effectiveness: {best_formation[1]['effectiveness_level']}). "
                f"Review {worst_formation[0]} strategy for improvement."
            )
        
        # Zone-based recommendations
        if zone_analysis["trap_analysis"]["trap_detected"]:
            trap_percentage = zone_analysis["trap_analysis"]["percentage_of_game"]
            if trap_percentage > 25:
                recommendations["neutral_zone_strategy"] = "Consider reducing neutral zone trap usage - may be too predictable."
            elif trap_percentage < 10:
                recommendations["neutral_zone_strategy"] = "Increase neutral zone trap usage for better defensive control."
        
        if zone_analysis["forecheck_analysis"]["forecheck_detected"]:
            pressure_level = zone_analysis["forecheck_analysis"]["avg_pressure"]
            if pressure_level < 0.5:
                recommendations["offensive_strategy"] = "Increase offensive zone pressure for better puck control."
            elif pressure_level > 0.8:
                recommendations["offensive_strategy"] = "Maintain high offensive pressure - it's working effectively."
        
        if zone_analysis["defensive_analysis"]["defensive_coverage"]:
            coverage_density = zone_analysis["defensive_analysis"]["avg_coverage"]
            if coverage_density < 0.6:
                recommendations["defensive_strategy"] = "Strengthen defensive zone coverage to prevent scoring chances."
            elif coverage_density > 0.8:
                recommendations["defensive_strategy"] = "Strong defensive coverage - consider counter-attack opportunities."
        
        return recommendations
    
    def _generate_tactical_summary(
        self, 
        formation_analysis: Dict[str, Any], 
        zone_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive tactical summary.
        
        Args:
            formation_analysis: Results from formation analysis
            zone_analysis: Results from zone analysis
            
        Returns:
            Comprehensive tactical summary string
        """
        summary_parts = []
        
        # Formation summary
        if formation_analysis["detected_formations"]:
            total_formations = len(formation_analysis["detected_formations"])
            most_common = formation_analysis["formation_statistics"]["most_common"]
            summary_parts.append(
                f"Team deployed {total_formations} distinct formations, with {most_common} being most common."
            )
        
        # Zone tactics summary
        if zone_analysis["trap_analysis"]["trap_detected"]:
            trap_percentage = zone_analysis["trap_analysis"]["percentage_of_game"]
            summary_parts.append(
                f"Neutral zone trap used {trap_percentage:.1f}% of the time, indicating {self._analyze_trap_effectiveness(zone_analysis['trap_analysis'])} defensive strategy."
            )
        
        if zone_analysis["forecheck_analysis"]["forecheck_detected"]:
            pressure_level = zone_analysis["forecheck_analysis"]["avg_pressure"]
            summary_parts.append(
                f"Offensive pressure maintained at {pressure_level:.2f} level, showing {self._classify_forechecking_style(zone_analysis['forecheck_analysis'])} forechecking approach."
            )
        
        if zone_analysis["defensive_analysis"]["defensive_coverage"]:
            coverage_density = zone_analysis["defensive_analysis"]["avg_coverage"]
            summary_parts.append(
                f"Defensive coverage density at {coverage_density:.2f}, reflecting {self._classify_defensive_style(zone_analysis['defensive_analysis'])} defensive style."
            )
        
        # Overall tactical assessment
        if summary_parts:
            summary_parts.append(
                "Overall, the team shows a balanced tactical approach with room for strategic refinement."
            )
        else:
            summary_parts.append(
                "Limited tactical patterns detected - may indicate transitional or experimental play."
            )
        
        return " ".join(summary_parts)
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """
        Run complete tactical analysis and save results.
        
        Returns:
            Dictionary with complete analysis results
        """
        logger.info("Starting complete tactical analysis...")
        
        # Run all analyses
        formation_analysis = self.analyze_formations()
        zone_analysis = self.analyze_zones()
        tactical_insights = self.generate_tactical_insights()
        
        # Compile complete results
        complete_analysis = {
            "formation_analysis": formation_analysis,
            "zone_analysis": zone_analysis,
            "tactical_insights": tactical_insights,
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_source": str(self.input_path),
                "total_frames": len(self.tracking_data),
                "analysis_version": "1.0.0"
            }
        }
        
        # Save results
        self._save_analysis_results(complete_analysis)
        
        logger.info("Complete tactical analysis finished and saved")
        return complete_analysis
    
    def run_enhanced_analysis_with_weaknesses(
        self, 
        min_frames: int = 5, 
        min_confidence: float = 0.6
    ) -> Dict[str, Any]:
        """
        Run enhanced tactical analysis with detailed weakness detection.
        
        This method provides in-depth analysis of formation quality, including:
        - Coverage gaps and positioning issues
        - Formation breakdowns and consistency problems
        - Behavioral patterns that create vulnerabilities
        - Specific tactical recommendations for improvement
        
        Args:
            min_frames: Minimum consecutive frames to confirm formation
            min_confidence: Minimum confidence threshold for formation detection
            
        Returns:
            Enhanced analysis results with weakness detection
        """
        logger.info("Starting enhanced tactical analysis with weakness detection...")
        
        # Run basic formation detection
        formation_analysis = self.formation_detector.detect_formations_over_time(
            self.tracking_data, min_frames
        )
        
        logger.info(f"Detected {len(formation_analysis)} formations for enhanced analysis")
        
        if not formation_analysis:
            logger.warning("No formations detected for enhanced analysis")
            # Return basic structure with no formations
            return {
                "enhanced_formation_analysis": {
                    "detected_formations": [],
                    "total_weaknesses": 0,
                    "weakness_summary": {"message": "No formations detected"},
                    "quality_distribution": {"message": "No formations for quality analysis"}
                },
                "zone_analysis": self._convert_zone_analysis_for_json(
                    self.zone_analyzer.analyze_zone_distribution(self.tracking_data)
                ),
                "enhanced_tactical_insights": {
                    "weakness_analysis": {
                        "total_weaknesses": 0,
                        "weakness_distribution": {},
                        "critical_issues": 0,
                        "formation_breakdowns": 0
                    },
                    "formation_insights": {},
                    "strategic_recommendations": {"overall_strategy": "No formations detected for analysis"},
                    "quality_summary": {"message": "No formations detected"},
                    "tactical_priorities": ["No formations detected for tactical analysis"]
                },
                "analysis_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "data_source": str(self.input_path),
                    "total_frames": len(self.tracking_data),
                    "analysis_version": "1.1.0",
                    "analysis_type": "enhanced_with_weakness_detection"
                }
            }
        
        # Analyze each detected formation for quality and weaknesses
        enhanced_formations = []
        total_weaknesses = []
        
        for formation in formation_analysis:
            formation_name = formation["formation"]
            start_frame = formation["start_frame"]
            end_frame = formation["end_frame"]
            
            # Get players from the middle frame of the formation for analysis
            mid_frame = (start_frame + end_frame) // 2
            if mid_frame < len(self.tracking_data) and 'players' in self.tracking_data[mid_frame]:
                players = self.tracking_data[mid_frame]['players']
                
                # Analyze formation quality and detect weaknesses
                formation_quality = self.weakness_detector.analyze_formation_quality(
                    formation_name, players, self.tracking_data, (start_frame, end_frame)
                )
                
                # Update formation data with quality analysis
                enhanced_formation = {
                    **formation,
                    "quality_analysis": {
                        "overall_score": formation_quality.overall_score,
                        "coverage_quality": formation_quality.coverage_quality.value,
                        "weaknesses": [
                            {
                                "type": w.weakness_type.value,
                                "severity": w.severity,
                                "description": w.description,
                                "affected_players": w.affected_players,
                                "zone": w.zone,
                                "recommendations": w.recommendations,
                                "metrics": w.metrics
                            }
                            for w in formation_quality.weaknesses
                        ],
                        "strengths": formation_quality.strengths,
                        "improvement_areas": formation_quality.improvement_areas,
                        "tactical_insights": formation_quality.tactical_insights,
                        "improvement_priority": self._calculate_improvement_priority(formation_quality.weaknesses)
                    }
                }
                
                enhanced_formations.append(enhanced_formation)
                # Convert weaknesses to dictionaries for consistency
                total_weaknesses.extend([
                    {
                        "type": w.weakness_type.value,
                        "severity": w.severity,
                        "description": w.description,
                        "affected_players": w.affected_players,
                        "zone": w.zone,
                        "recommendations": w.recommendations,
                        "metrics": w.metrics
                    }
                    for w in formation_quality.weaknesses
                ])
        
        # Run zone analysis
        zone_analysis = self.zone_analyzer.analyze_zone_distribution(self.tracking_data)
        
        # Convert RinkZone enums to strings for JSON serialization
        zone_analysis = self._convert_zone_analysis_for_json(zone_analysis)
        
        # Generate enhanced tactical insights
        try:
            enhanced_insights = self._generate_enhanced_tactical_insights(
                enhanced_formations, zone_analysis, total_weaknesses
            )
        except Exception as e:
            logger.error(f"Error generating enhanced tactical insights: {e}")
            import traceback
            traceback.print_exc()
            # Return basic structure on error
            enhanced_insights = {
                "weakness_analysis": {
                    "total_weaknesses": len(total_weaknesses),
                    "weakness_distribution": {},
                    "critical_issues": 0,
                    "formation_breakdowns": 0
                },
                "formation_insights": {},
                "strategic_recommendations": {"overall_strategy": "Error in analysis"},
                "quality_summary": {"message": "Error in analysis"},
                "tactical_priorities": ["Error in analysis"]
            }
        
        # Compile enhanced results
        enhanced_analysis = {
            "enhanced_formation_analysis": {
                "detected_formations": enhanced_formations,
                "total_weaknesses": len(total_weaknesses),
                "weakness_summary": self._summarize_weaknesses(total_weaknesses),
                "quality_distribution": self._analyze_quality_distribution(enhanced_formations)
            },
            "zone_analysis": zone_analysis,
            "enhanced_tactical_insights": enhanced_insights,
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_source": str(self.input_path),
                "total_frames": len(self.tracking_data),
                "analysis_version": "1.1.0",
                "analysis_type": "enhanced_with_weakness_detection"
            }
        }
        
        # Save enhanced results
        self._save_enhanced_analysis_results(enhanced_analysis)
        
        logger.info("Enhanced tactical analysis with weakness detection completed")
        return enhanced_analysis
    
    def _generate_enhanced_tactical_insights(
        self, 
        enhanced_formations: List[Dict], 
        zone_analysis: Dict, 
        total_weaknesses: List
    ) -> Dict[str, Any]:
        """Generate enhanced tactical insights with weakness analysis."""
        
        # Analyze weakness patterns
        weakness_patterns = self._analyze_weakness_patterns(total_weaknesses)
        
        # Generate formation-specific insights
        formation_insights = {}
        for formation in enhanced_formations:
            formation_name = formation["formation"]
            quality = formation["quality_analysis"]
            
            # Debug logging
            logger.debug(f"Processing formation {formation_name} with {len(quality['weaknesses'])} weaknesses")
            logger.debug(f"Quality keys: {list(quality.keys())}")
            logger.debug(f"Formation keys: {list(formation.keys())}")
            
            try:
                improvement_priority = self._calculate_improvement_priority(quality["weaknesses"])
            except Exception as e:
                logger.warning(f"Error calculating improvement priority for {formation_name}: {e}")
                improvement_priority = "unknown"
            
            formation_insights[formation_name] = {
                "quality_score": quality["overall_score"],
                "coverage_quality": quality["coverage_quality"],
                "key_weaknesses": [w["description"] for w in quality["weaknesses"][:3]],  # Top 3
                "key_strengths": quality["strengths"][:3],  # Top 3
                "critical_issues": [w for w in quality["weaknesses"] if w["severity"] > 0.7],
                "improvement_priority": improvement_priority
            }
        
        # Generate strategic recommendations
        strategic_recommendations = self._generate_strategic_recommendations(
            enhanced_formations, weakness_patterns
        )
        
        return {
            "weakness_analysis": {
                "total_weaknesses": len(total_weaknesses),
                "weakness_distribution": weakness_patterns,
                "critical_issues": len([w for w in total_weaknesses if w["severity"] > 0.7]),
                "formation_breakdowns": len([w for w in total_weaknesses if w["type"] == "formation_breakdown"])
            },
            "formation_insights": formation_insights,
            "strategic_recommendations": strategic_recommendations,
            "quality_summary": self._generate_quality_summary(enhanced_formations),
            "tactical_priorities": self._identify_tactical_priorities(total_weaknesses)
        }
    
    def _analyze_weakness_patterns(self, weaknesses: List) -> Dict[str, Any]:
        """Analyze patterns in detected weaknesses."""
        patterns = {
            "by_type": {},
            "by_severity": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "by_zone": {},
            "most_common": []
        }
        
        for weakness in weaknesses:
            # Count by type
            w_type = weakness["type"]
            patterns["by_type"][w_type] = patterns["by_type"].get(w_type, 0) + 1
            
            # Count by severity
            if weakness["severity"] <= 0.3:
                patterns["by_severity"]["low"] += 1
            elif weakness["severity"] <= 0.6:
                patterns["by_severity"]["medium"] += 1
            elif weakness["severity"] <= 0.8:
                patterns["by_severity"]["high"] += 1
            else:
                patterns["by_severity"]["critical"] += 1
            
            # Count by zone
            zone = weakness["zone"]
            patterns["by_zone"][zone] = patterns["by_zone"].get(zone, 0) + 1
        
        # Find most common weaknesses
        weakness_counts = {}
        for weakness in weaknesses:
            desc = weakness["description"]
            weakness_counts[desc] = weakness_counts.get(desc, 0) + 1
        
        patterns["most_common"] = sorted(
            weakness_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]
        
        return patterns
    
    def _calculate_improvement_priority(self, weaknesses: List) -> str:
        """Calculate improvement priority based on weaknesses."""
        if not weaknesses:
            return "maintain"
        
        try:
            # Handle both TacticalWeakness objects and dictionaries
            if hasattr(weaknesses[0], 'severity'):
                # TacticalWeakness objects
                critical_count = len([w for w in weaknesses if w.severity > 0.7])
                high_count = len([w for w in weaknesses if w.severity > 0.5])
            else:
                # Dictionaries
                critical_count = len([w for w in weaknesses if w["severity"] > 0.7])
                high_count = len([w for w in weaknesses if w["severity"] > 0.5])
            
            if critical_count > 0:
                return "critical"
            elif high_count > 2:
                return "high"
            elif high_count > 0:
                return "medium"
            else:
                return "low"
        except Exception as e:
            logger.warning(f"Error calculating improvement priority: {e}")
            return "unknown"
    
    def _generate_strategic_recommendations(
        self, 
        enhanced_formations: List[Dict], 
        weakness_patterns: Dict
    ) -> Dict[str, str]:
        """Generate strategic recommendations based on weakness analysis."""
        recommendations = {}
        
        # Formation-specific recommendations
        for formation in enhanced_formations:
            formation_name = formation["formation"]
            quality = formation["quality_analysis"]
            
            if quality["overall_score"] < 0.6:
                recommendations[f"{formation_name}_priority"] = "Immediate attention required"
            elif quality["overall_score"] < 0.8:
                recommendations[f"{formation_name}_focus"] = "Focus on key weaknesses"
            else:
                recommendations[f"{formation_name}_maintenance"] = "Maintain current standards"
        
        # Overall strategic recommendations
        if weakness_patterns["by_severity"]["critical"] > 0:
            recommendations["overall_strategy"] = "Critical issues require immediate tactical adjustments"
        elif weakness_patterns["by_severity"]["high"] > 3:
            recommendations["overall_strategy"] = "Multiple high-priority issues suggest need for systematic improvement"
        elif weakness_patterns["by_severity"]["high"] > 0:
            recommendations["overall_strategy"] = "Address high-priority weaknesses to improve overall performance"
        else:
            recommendations["overall_strategy"] = "Focus on fine-tuning and maintaining current tactical standards"
        
        return recommendations
    
    def _generate_quality_summary(self, enhanced_formations: List[Dict]) -> Dict[str, Any]:
        """Generate summary of formation quality across all formations."""
        if not enhanced_formations:
            return {"message": "No formations detected for quality analysis"}
        
        quality_scores = [f["quality_analysis"]["overall_score"] for f in enhanced_formations]
        coverage_qualities = [f["quality_analysis"]["coverage_quality"] for f in enhanced_formations]
        
        return {
            "average_quality_score": np.mean(quality_scores),
            "quality_range": (min(quality_scores), max(quality_scores)),
            "excellent_formations": len([q for q in quality_scores if q >= 0.9]),
            "good_formations": len([q for q in quality_scores if q >= 0.8]),
            "fair_formations": len([q for q in quality_scores if q >= 0.6]),
            "poor_formations": len([q for q in quality_scores if q < 0.6]),
            "coverage_quality_distribution": {
                quality: coverage_qualities.count(quality) 
                for quality in set(coverage_qualities)
            }
        }
    
    def _identify_tactical_priorities(self, weaknesses: List) -> List[str]:
        """Identify tactical priorities based on weakness analysis."""
        priorities = []
        
        # Critical weaknesses
        critical_weaknesses = [w for w in weaknesses if w["severity"] > 0.8]
        if critical_weaknesses:
            priorities.append("Address critical tactical vulnerabilities immediately")
        
        # Coverage gaps
        coverage_gaps = [w for w in weaknesses if w["type"] == "coverage_gap"]
        if coverage_gaps:
            priorities.append("Improve gap control and defensive coverage")
        
        # Formation breakdowns
        breakdowns = [w for w in weaknesses if w["type"] == "formation_breakdown"]
        if breakdowns:
            priorities.append("Increase formation discipline and consistency")
        
        # Positioning issues
        positioning = [w for w in weaknesses if w["type"] == "poor_positioning"]
        if positioning:
            priorities.append("Work on fundamental positioning skills")
        
        return priorities
    
    def _summarize_weaknesses(self, weaknesses: List) -> Dict[str, Any]:
        """Summarize detected weaknesses."""
        if not weaknesses:
            return {"message": "No tactical weaknesses detected"}
        
        return {
            "total_count": len(weaknesses),
            "by_severity": {
                "critical": len([w for w in weaknesses if w["severity"] > 0.8]),
                "high": len([w for w in weaknesses if w["severity"] > 0.6]),
                "medium": len([w for w in weaknesses if w["severity"] > 0.3]),
                "low": len([w for w in weaknesses if w["severity"] <= 0.3])
            },
            "by_type": {
                w["type"]: len([w2 for w2 in weaknesses if w2["type"] == w["type"]])
                for w in weaknesses
            }
        }
    
    def _analyze_quality_distribution(self, enhanced_formations: List[Dict]) -> Dict[str, Any]:
        """Analyze distribution of formation quality scores."""
        if not enhanced_formations:
            return {"message": "No formations for quality analysis"}
        
        quality_scores = [f["quality_analysis"]["overall_score"] for f in enhanced_formations]
        
        return {
            "mean": np.mean(quality_scores),
            "median": np.median(quality_scores),
            "std": np.std(quality_scores),
            "quartiles": np.percentile(quality_scores, [25, 50, 75]).tolist(),
            "distribution": {
                "excellent": len([q for q in quality_scores if q >= 0.9]),
                "good": len([q for q in quality_scores if q >= 0.8]),
                "fair": len([q for q in quality_scores if q >= 0.6]),
                "poor": len([q for q in quality_scores if q < 0.6])
            }
        }
    
    def _save_enhanced_analysis_results(self, results: Dict[str, Any]) -> None:
        """Save enhanced analysis results to output directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save enhanced JSON results
        json_path = self.output_dir / f"enhanced_tactical_analysis_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save enhanced CSV summary
        csv_path = self.output_dir / f"enhanced_tactical_summary_{timestamp}.csv"
        self._save_enhanced_csv_summary(results, csv_path)
        
        # Save enhanced text report
        report_path = self.output_dir / f"enhanced_tactical_report_{timestamp}.txt"
        self._save_enhanced_text_report(results, report_path)
        
        logger.info(f"Enhanced analysis results saved to {self.output_dir}")
    
    def _convert_zone_analysis_for_json(self, zone_analysis: Dict) -> Dict:
        """Convert RinkZone enums to strings for JSON serialization."""
        converted = {}
        
        for zone, metrics in zone_analysis.items():
            if hasattr(zone, 'value'):
                zone_key = zone.value
            else:
                zone_key = str(zone)
            
            converted[zone_key] = {
                'avg_players': metrics.avg_players,
                'max_players': metrics.max_players,
                'min_players': metrics.min_players,
                'player_density': metrics.player_density,
                'formation_consistency': metrics.formation_consistency,
                'transition_frequency': metrics.transition_frequency
            }
        
        return converted
    
    def _save_enhanced_csv_summary(self, results: Dict[str, Any], csv_path: Path) -> None:
        """Save enhanced analysis summary as CSV."""
        summary_data = []
        
        # Enhanced formation summary with quality metrics
        if results["enhanced_formation_analysis"]["detected_formations"]:
            for formation in results["enhanced_formation_analysis"]["detected_formations"]:
                quality = formation["quality_analysis"]
                summary_data.append({
                    "formation_name": formation["formation"],
                    "start_time": formation["start_time"],
                    "end_time": formation["end_time"],
                    "duration_frames": formation["duration_frames"],
                    "confidence": formation["avg_confidence"],
                    "quality_score": quality["overall_score"],
                    "coverage_quality": quality["coverage_quality"],
                    "weakness_count": len(quality["weaknesses"]),
                    "critical_weaknesses": len([w for w in quality["weaknesses"] if w["severity"] > 0.7]),
                    "improvement_priority": quality["improvement_priority"]
                })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            df.to_csv(csv_path, index=False)
    
    def _save_enhanced_text_report(self, results: Dict[str, Any], report_path: Path) -> None:
        """Save enhanced analysis as text report."""
        with open(report_path, 'w') as f:
            f.write("ENHANCED HOCKEY TACTICAL ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Analysis Date: {results['analysis_metadata']['timestamp']}\n")
            f.write(f"Data Source: {results['analysis_metadata']['data_source']}\n")
            f.write(f"Total Frames Analyzed: {results['analysis_metadata']['total_frames']}\n")
            f.write(f"Analysis Type: {results['analysis_metadata']['analysis_type']}\n\n")
            
            # Write weakness analysis summary
            weakness_summary = results["enhanced_tactical_insights"]["weakness_analysis"]
            f.write("TACTICAL WEAKNESS ANALYSIS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Weaknesses Detected: {weakness_summary['total_weaknesses']}\n")
            f.write(f"Critical Issues: {weakness_summary['critical_issues']}\n")
            f.write(f"Formation Breakdowns: {weakness_summary['formation_breakdowns']}\n\n")
            
            # Write quality summary
            quality_summary = results["enhanced_tactical_insights"]["quality_summary"]
            f.write("FORMATION QUALITY SUMMARY\n")
            f.write("-" * 30 + "\n")
            
            if "message" in quality_summary:
                f.write(f"{quality_summary['message']}\n\n")
            else:
                f.write(f"Average Quality Score: {quality_summary['average_quality_score']:.3f}\n")
                f.write(f"Excellent Formations: {quality_summary['excellent_formations']}\n")
                f.write(f"Good Formations: {quality_summary['good_formations']}\n")
                f.write(f"Fair Formations: {quality_summary['fair_formations']}\n")
                f.write(f"Poor Formations: {quality_summary['poor_formations']}\n\n")
            
            # Write tactical priorities
            f.write("TACTICAL PRIORITIES\n")
            f.write("-" * 25 + "\n")
            for priority in results["enhanced_tactical_insights"]["tactical_priorities"]:
                f.write(f"• {priority}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("End of Enhanced Report\n")
    
    def _save_analysis_results(self, results: Dict[str, Any]) -> None:
        """
        Save analysis results to output directory.
        
        Args:
            results: Complete analysis results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_path = self.output_dir / f"tactical_analysis_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save CSV summary
        csv_path = self.output_dir / f"tactical_summary_{timestamp}.csv"
        self._save_csv_summary(results, csv_path)
        
        # Save text report
        report_path = self.output_dir / f"tactical_report_{timestamp}.txt"
        self._save_text_report(results, report_path)
        
        logger.info(f"Analysis results saved to {self.output_dir}")
    
    def _save_csv_summary(self, results: Dict[str, Any], csv_path: Path) -> None:
        """Save analysis summary as CSV."""
        # Extract key metrics for CSV
        summary_data = []
        
        # Formation summary
        if results["formation_analysis"]["detected_formations"]:
            for formation in results["formation_analysis"]["detected_formations"]:
                summary_data.append({
                    "analysis_type": "formation",
                    "formation_name": formation["formation"],
                    "start_time": formation["start_time"],
                    "end_time": formation["end_time"],
                    "duration_frames": formation["duration_frames"],
                    "confidence": formation["avg_confidence"]
                })
        
        # Zone summary
        zone_analysis = results["zone_analysis"]
        if zone_analysis["trap_analysis"]["trap_detected"]:
            summary_data.append({
                "analysis_type": "zone_tactic",
                "formation_name": "neutral_zone_trap",
                "start_time": 0,
                "end_time": 0,
                "duration_frames": zone_analysis["trap_analysis"]["total_instances"],
                "confidence": zone_analysis["trap_analysis"]["avg_confidence"]
            })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            df.to_csv(csv_path, index=False)
    
    def _save_text_report(self, results: Dict[str, Any], report_path: Path) -> None:
        """Save analysis as text report."""
        with open(report_path, 'w') as f:
            f.write("HOCKEY TACTICAL ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Analysis Date: {results['analysis_metadata']['timestamp']}\n")
            f.write(f"Data Source: {results['analysis_metadata']['data_source']}\n")
            f.write(f"Total Frames Analyzed: {results['analysis_metadata']['total_frames']}\n\n")
            
            # Write tactical insights summary
            f.write("TACTICAL INSIGHTS SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(results['tactical_insights']['summary'] + "\n\n")
            
            # Write strategic recommendations
            f.write("STRATEGIC RECOMMENDATIONS\n")
            f.write("-" * 30 + "\n")
            for category, recommendation in results['tactical_insights']['strategic_recommendations'].items():
                f.write(f"{category.replace('_', ' ').title()}: {recommendation}\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("End of Report\n")
