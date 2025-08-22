#!/usr/bin/env python3
"""
Wait and Analyze: Complete Hockey Analysis

This tool waits for Computer-Vision-for-Hockey to complete tracking,
then runs tactical analysis on the results.
"""

import sys
import subprocess
import time
from pathlib import Path
import argparse
import os


def run_tracking_and_wait(video_path: str, cv_hockey_path: str = "../Computer-Vision-for-Hockey", max_frames: int = 200) -> str:
    """Run tracking and wait for completion."""
    print(f"🎬 TRACKING: {Path(video_path).name}")
    print(f"   Processing {max_frames} frames (every single frame)")
    
    # Change to Computer-Vision-for-Hockey directory
    original_dir = Path.cwd()
    cv_hockey_dir = Path(cv_hockey_path)
    
    if not cv_hockey_dir.exists():
        raise FileNotFoundError(f"Computer-Vision-for-Hockey directory not found: {cv_hockey_dir}")
    
    # Check if video exists
    video_file = cv_hockey_dir / "data" / "videos" / Path(video_path).name
    if not video_file.exists():
        print(f"📁 Copying video to {cv_hockey_dir}/data/videos/")
        import shutil
        shutil.copy2(video_path, video_file)
    
    try:
        # Change to CV-Hockey directory and run tracking
        os.chdir(cv_hockey_dir)
        
        # Create output directory with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = f"output/tracking_results_{timestamp}"
        
        print(f"🎬 Starting tracking...")
        print(f"   This will process {max_frames} frames - please wait...")
        
        start_time = time.time()
        
        # Call process_clip.py and wait for completion
        cmd = [
            "python3", "src/process_clip.py",
            "--video", f"data/videos/{Path(video_path).name}",
            "--segmentation-model", "models/segmentation.pt",
            "--detection-model", "models/detection.pt",
            "--orientation-model", "models/orient.pth",
            "--rink-coordinates", "data/rink_coordinates.json",
            "--rink-image", "data/rink_resized.png",
            "--output-dir", output_dir,
            "--start-second", "0",
            "--num-seconds", "0",  # Process entire video
            "--frame-step", "1",   # Process EVERY frame
            "--max-frames", str(max_frames)  # Limit for speed
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        print(f"   ⏳ Please wait for tracking to complete...")
        
        # Run and wait for completion (no timeout)
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ Tracking completed in {processing_time:.1f} seconds!")
        
        # Find the generated tracking data
        output_path = Path(output_dir)
        if not output_path.exists():
            raise RuntimeError(f"Output directory not found: {output_dir}")
        
        tracking_files = list(output_path.glob("player_detection_data_*.json"))
        
        if not tracking_files:
            raise RuntimeError("No tracking data files found")
        
        tracking_file = str(tracking_files[0])
        print(f"✅ Tracking data: {tracking_file}")
        
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
    """Run tactical analysis."""
    print(f"🔍 Running tactical analysis...")
    
    from src.tactical_analyzer import TacticalAnalyzer
    
    analyzer = TacticalAnalyzer(tracking_data_path)
    results = analyzer.run_enhanced_analysis_with_weaknesses()
    
    return results


def display_results(results: dict, tracking_file: str):
    """Display analysis results."""
    print("\n📊 TACTICAL ANALYSIS RESULTS")
    print("=" * 50)
    
    if 'formation_analysis' in results and results['formation_analysis']:
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
                    for w in weaknesses[:3]:  # Show first 3
                        print(f"     - {w.get('type', 'Unknown')}: {w.get('description', 'No description')}")
    else:
        print("⚠️  No formations detected in this clip")
        print("   This is normal for short clips - try longer video segments")
    
    if 'overall_quality' in results:
        quality = results['overall_quality']
        print(f"\n📈 Overall Quality Score: {quality.get('average_quality_score', 'N/A')}")
        print(f"🔴 Total Weaknesses: {quality.get('total_weaknesses_count', 'N/A')}")
    
    print(f"\n📁 Results saved to: {Path(tracking_file).parent}")
    print("✅ Analysis completed!")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Wait and Analyze: Complete Hockey Analysis"
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
        default=200,
        help="Maximum frames to process (default: 200 - processes every frame)"
    )
    
    args = parser.parse_args()
    
    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        sys.exit(1)
    
    print("🎬 WAIT AND ANALYZE: COMPLETE HOCKEY ANALYSIS")
    print("=" * 60)
    print(f"🎬 Input Video: {video_path.name}")
    print(f"🔧 CV-Hockey Path: {args.cv_hockey_path}")
    print(f"📊 Max Frames: {args.max_frames} (EVERY single frame)")
    print(f"⏳ Strategy: Wait for tracking to complete, then analyze")
    print()
    
    try:
        start_time = time.time()
        
        # Step 1: Run tracking and wait for completion
        tracking_file = run_tracking_and_wait(
            str(video_path), 
            args.cv_hockey_path,
            args.max_frames
        )
        
        # Step 2: Run tactical analysis
        results = run_tactical_analysis(tracking_file)
        
        # Step 3: Display results
        display_results(results, tracking_file)
        
        total_time = time.time() - start_time
        
        print(f"\n🎉 SUCCESS! Video '{video_path.name}' fully analyzed!")
        print(f"📁 Results saved in: {Path(tracking_file).parent}")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
