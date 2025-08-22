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
