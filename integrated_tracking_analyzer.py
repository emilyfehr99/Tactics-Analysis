#!/usr/bin/env python3
"""
Integrated Hockey Tracking and Tactical Analysis Tool

This tool combines the video tracking capabilities from Computer-Vision-for-Hockey
with the tactical analysis system to provide a complete workflow from video to insights.
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

# Add the Computer-Vision-for-Hockey src to path
CV_HOCKEY_SRC = Path("../Computer-Vision-for-Hockey/src")
if CV_HOCKEY_SRC.exists():
    sys.path.insert(0, str(CV_HOCKEY_SRC))

try:
    from player_tracker import PlayerTracker
    from process_clip import process_video_clip
    TRACKING_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: Computer-Vision-for-Hockey tracking modules not available")
    print("   This tool will only work with existing tracking data files")
    TRACKING_AVAILABLE = False

# Import our tactical analysis modules
from src.tactical_analyzer import TacticalAnalyzer


class IntegratedTrackingAnalyzer:
    """Combines video tracking and tactical analysis in one workflow."""
    
    def __init__(self, cv_hockey_path: str = "../Computer-Vision-for-Hockey"):
        self.cv_hockey_path = Path(cv_hockey_path)
        self.tracking_available = TRACKING_AVAILABLE
        
        if not self.tracking_available:
            print("⚠️  Tracking capabilities disabled - only analysis available")
        
        # Default paths for Computer-Vision-for-Hockey
        self.models_dir = self.cv_hockey_path / "models"
        self.data_dir = self.cv_hockey_path / "data"
        self.output_dir = self.cv_hockey_path / "output"
        
    def check_tracking_requirements(self) -> bool:
        """Check if all required tracking files exist."""
        if not self.tracking_available:
            return False
            
        required_files = [
            self.models_dir / "segmentation.pt",
            self.models_dir / "detection.pt", 
            self.models_dir / "orient.pth",
            self.data_dir / "rink_resized.png"
        ]
        
        missing_files = [f for f in required_files if not f.exists()]
        if missing_files:
            print("❌ Missing required tracking files:")
            for f in missing_files:
                print(f"   - {f}")
            return False
            
        return True
    
    def generate_tracking_data(self, video_path: str, max_frames: int = 100) -> Optional[str]:
        """Generate tracking data from a video file."""
        if not self.tracking_available:
            print("❌ Tracking not available - cannot generate data")
            return None
            
        if not self.check_tracking_requirements():
            print("❌ Tracking requirements not met")
            return None
            
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"❌ Video file not found: {video_path}")
            return None
            
        print(f"🎬 Generating tracking data from: {video_path.name}")
        print("   This may take several minutes...")
        
        # Create output directory with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = self.output_dir / f"tracking_results_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Run the tracking process
            tracking_file = process_video_clip(
                video_path=str(video_path),
                segmentation_model=str(self.models_dir / "segmentation.pt"),
                detection_model=str(self.models_dir / "detection.pt"),
                orientation_model=str(self.models_dir / "orient.pth"),
                rink_coordinates=str(self.data_dir / "rink_coordinates.json"),
                rink_image=str(self.data_dir / "rink_resized.png"),
                output_dir=str(output_dir),
                start_second=0,
                num_seconds=0,  # Process entire video
                frame_step=1,
                max_frames=max_frames
            )
            
            if tracking_file and Path(tracking_file).exists():
                print(f"✅ Tracking data generated: {tracking_file}")
                return tracking_file
            else:
                print("❌ Failed to generate tracking data")
                return None
                
        except Exception as e:
            print(f"❌ Error during tracking: {e}")
            return None
    
    def run_tactical_analysis(self, tracking_data_path: str) -> Dict[str, Any]:
        """Run tactical analysis on tracking data."""
        print(f"🔍 Running tactical analysis on: {Path(tracking_data_path).name}")
        
        analyzer = TacticalAnalyzer(tracking_data_path)
        results = analyzer.run_enhanced_analysis_with_weaknesses()
        
        return results
    
    def process_video_to_insights(self, video_path: str, max_frames: int = 100) -> Dict[str, Any]:
        """Complete workflow: video → tracking → analysis → insights."""
        print("🚀 INTEGRATED HOCKEY TRACKING & TACTICAL ANALYSIS")
        print("=" * 60)
        
        # Step 1: Generate tracking data
        tracking_file = self.generate_tracking_data(video_path, max_frames)
        if not tracking_file:
            print("❌ Failed to generate tracking data - workflow stopped")
            return {}
        
        # Step 2: Run tactical analysis
        analysis_results = self.run_tactical_analysis(tracking_file)
        
        # Step 3: Display results
        self.display_integrated_results(analysis_results, tracking_file)
        
        return analysis_results
    
    def display_integrated_results(self, results: Dict[str, Any], tracking_file: str):
        """Display the complete analysis results."""
        print("\n📊 INTEGRATED ANALYSIS RESULTS")
        print("=" * 60)
        
        # Basic stats
        if 'formation_analysis' in results:
            formations = results['formation_analysis']
            print(f"🏗️  Formations Detected: {len(formations)}")
            
            for i, formation in enumerate(formations, 1):
                print(f"\n{i}. {formation['formation_name']}")
                print(f"   Duration: {formation['duration_frames']} frames")
                print(f"   Confidence: {formation['confidence']:.2f}")
                
                if 'quality_analysis' in formation:
                    quality = formation['quality_analysis']
                    print(f"   Quality Score: {quality.get('quality_score', 'N/A')}")
                    print(f"   Coverage Quality: {quality.get('coverage_quality', 'N/A')}")
                    
                    weaknesses = quality.get('weaknesses', [])
                    if weaknesses:
                        print(f"   Weaknesses: {len(weaknesses)}")
                        for w in weaknesses[:2]:  # Show first 2
                            print(f"     - {w.get('type', 'Unknown')}: {w.get('description', 'No description')}")
        
        # Overall quality
        if 'overall_quality' in results:
            quality = results['overall_quality']
            print(f"\n📈 Overall Quality Score: {quality.get('average_quality_score', 'N/A')}")
            print(f"🔴 Total Weaknesses: {quality.get('total_weaknesses_count', 'N/A')}")
        
        # Tactical insights
        if 'tactical_insights' in results:
            insights = results['tactical_insights']
            print(f"\n💡 Key Tactical Insights:")
            for insight in insights.get('key_insights', [])[:3]:  # Show first 3
                print(f"   • {insight}")
        
        print(f"\n📁 Results saved to: {Path(tracking_file).parent}")
        print("✅ Complete workflow finished successfully!")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Integrated Hockey Tracking and Tactical Analysis Tool"
    )
    parser.add_argument(
        "input", 
        help="Video file path or existing tracking data JSON file"
    )
    parser.add_argument(
        "--max-frames", 
        type=int, 
        default=100,
        help="Maximum frames to process (default: 100)"
    )
    parser.add_argument(
        "--cv-hockey-path",
        default="../Computer-Vision-for-Hockey",
        help="Path to Computer-Vision-for-Hockey project"
    )
    
    args = parser.parse_args()
    
    # Initialize the integrated analyzer
    analyzer = IntegratedTrackingAnalyzer(args.cv_hockey_path)
    
    input_path = Path(args.input)
    
    if input_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
        # Input is a video file - run complete workflow
        print(f"🎬 Processing video file: {input_path.name}")
        analyzer.process_video_to_insights(str(input_path), args.max_frames)
        
    elif input_path.suffix.lower() == '.json':
        # Input is tracking data - just run analysis
        print(f"📊 Analyzing existing tracking data: {input_path.name}")
        results = analyzer.run_tactical_analysis(str(input_path))
        analyzer.display_integrated_results(results, str(input_path))
        
    else:
        print("❌ Unsupported input format. Use video file (.mp4, .avi, etc.) or tracking data (.json)")
        sys.exit(1)


if __name__ == "__main__":
    main()
