#!/usr/bin/env python3
"""
Video to Tactics: Integrated Hockey Analysis Tool

This tool takes a hockey video and:
1. Generates tracking data using Computer-Vision-for-Hockey
2. Runs tactical analysis on the generated data
3. Provides complete insights from video to tactics
"""

import sys
import subprocess
import time
from pathlib import Path
import argparse
import os


def run_tracking_on_video(video_path: str, cv_hockey_path: str = "../Computer-Vision-for-Hockey") -> str:
    """Run the Computer-Vision-for-Hockey tracking system on a video."""
    print(f"🎬 Running tracking on: {Path(video_path).name}")
    
    # Change to Computer-Vision-for-Hockey directory
    original_dir = Path.cwd()
    cv_hockey_dir = Path(cv_hockey_path)
    
    if not cv_hockey_dir.exists():
        raise FileNotFoundError(f"Computer-Vision-for-Hockey directory not found: {cv_hockey_dir}")
    
    # Check if video exists
    video_file = cv_hockey_dir / "data" / "videos" / Path(video_path).name
    if not video_file.exists():
        # Try to copy video to the right location
        print(f"📁 Copying video to {cv_hockey_dir}/data/videos/")
        import shutil
        shutil.copy2(video_path, video_file)
    
    # Update the tracking script to use our video
    tracking_script = cv_hockey_dir / "run_tracking.sh"
    if tracking_script.exists():
        # Read and modify the script to use our video
        with open(tracking_script, 'r') as f:
            script_content = f.read()
        
        # Replace the video path
        script_content = script_content.replace(
            'VIDEO_PATH="data/videos/CAN-SWE.mp4"',
            f'VIDEO_PATH="data/videos/{Path(video_path).name}"'
        )
        
        # Write the modified script
        with open(tracking_script, 'w') as f:
            f.write(script_content)
    
    try:
        # Change to CV-Hockey directory and run tracking
        os.chdir(cv_hockey_dir)
        
        # Make script executable and run it
        subprocess.run(["chmod", "+x", "run_tracking.sh"], check=True)
        
        print("🚀 Starting tracking process...")
        print("   This may take several minutes depending on video length...")
        
        result = subprocess.run(["./run_tracking.sh"], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        # Find the generated tracking data
        output_dirs = list(Path("output").glob("tracking_results_*"))
        if not output_dirs:
            raise RuntimeError("No tracking results directory found")
        
        # Get the most recent one
        latest_output = max(output_dirs, key=lambda x: x.stat().st_mtime)
        tracking_files = list(latest_output.glob("player_detection_data_*.json"))
        
        if not tracking_files:
            raise RuntimeError("No tracking data files found")
        
        tracking_file = str(tracking_files[0])
        print(f"✅ Tracking completed: {tracking_file}")
        
        return str(Path(cv_hockey_dir) / tracking_file)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tracking failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise
    finally:
        # Return to original directory
        os.chdir(original_dir)


def run_tactical_analysis(tracking_data_path: str):
    """Run our tactical analysis on the tracking data."""
    print(f"🔍 Running tactical analysis...")
    
    # Import and run our analyzer
    from src.tactical_analyzer import TacticalAnalyzer
    
    analyzer = TacticalAnalyzer(tracking_data_path)
    results = analyzer.run_enhanced_analysis_with_weaknesses()
    
    return results


def display_results(results: dict, tracking_file: str):
    """Display the analysis results."""
    print("\n📊 TACTICAL ANALYSIS RESULTS")
    print("=" * 50)
    
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
                    for w in weaknesses[:2]:
                        print(f"     - {w.get('type', 'Unknown')}: {w.get('description', 'No description')}")
    
    if 'overall_quality' in results:
        quality = results['overall_quality']
        print(f"\n📈 Overall Quality Score: {quality.get('average_quality_score', 'N/A')}")
        print(f"🔴 Total Weaknesses: {quality.get('total_weaknesses_count', 'N/A')}")
    
    print(f"\n📁 Results saved to: {Path(tracking_file).parent}")
    print("✅ Complete analysis finished!")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Video to Tactics: Complete Hockey Analysis"
    )
    parser.add_argument(
        "video_path",
        help="Path to hockey video file (.mp4, .avi, etc.)"
    )
    parser.add_argument(
        "--cv-hockey-path",
        default="../Computer-Vision-for-Hockey",
        help="Path to Computer-Vision-for-Hockey project"
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=100,
        help="Maximum frames to process (default: 100)"
    )
    
    args = parser.parse_args()
    
    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        sys.exit(1)
    
    print("🚀 VIDEO TO TACTICS: INTEGRATED HOCKEY ANALYSIS")
    print("=" * 60)
    print(f"🎬 Input Video: {video_path.name}")
    print(f"🔧 CV-Hockey Path: {args.cv_hockey_path}")
    print(f"📊 Max Frames: {args.max_frames}")
    print()
    
    try:
        # Step 1: Generate tracking data
        tracking_file = run_tracking_on_video(
            str(video_path), 
            args.cv_hockey_path
        )
        
        # Step 2: Run tactical analysis
        results = run_tactical_analysis(tracking_file)
        
        # Step 3: Display results
        display_results(results, tracking_file)
        
        print(f"\n🎉 SUCCESS! Video '{video_path.name}' has been fully analyzed!")
        print(f"📁 All results saved in: {Path(tracking_file).parent}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
