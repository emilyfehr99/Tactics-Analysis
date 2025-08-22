#!/usr/bin/env python3
"""
Focused Segment Analyzer: Quick 3-Second Tactical Analysis

This tool processes a focused 3-second segment (~50 frames) from the CHI vs PIT video
for quick tactical insights without the full video processing time.
"""

import sys
import subprocess
import time
from pathlib import Path
import argparse
import os


def run_focused_tracking(video_path: str, start_second: int = 3, num_seconds: int = 3, cv_hockey_path: str = "../Computer-Vision-for-Hockey") -> str:
    """Run focused tracking on a 3-second segment."""
    print(f"🎯 FOCUSED TRACKING: {Path(video_path).name}")
    print(f"   Segment: {start_second}s to {start_second + num_seconds}s")
    print(f"   Expected frames: ~{num_seconds * 30} frames")
    print(f"   Target: Under 2 minutes for focused analysis")
    
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
        # Change to CV-Hockey directory and run focused tracking
        os.chdir(cv_hockey_dir)
        
        # Create output directory with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = f"output/tracking_results_{timestamp}"
        
        print(f"🎯 Starting focused segment tracking...")
        print(f"   Processing {start_second}s to {start_second + num_seconds}s")
        print(f"   This should be much faster than full video...")
        
        start_time = time.time()
        
        # Call process_clip.py for focused segment
        cmd = [
            "python3", "src/process_clip.py",
            "--video", f"data/videos/{Path(video_path).name}",
            "--segmentation-model", "models/segmentation.pt",
            "--detection-model", "models/detection.pt",
            "--orientation-model", "models/orient.pth",
            "--rink-coordinates", "data/rink_coordinates.json",
            "--rink-image", "data/rink_resized.png",
            "--output-dir", output_dir,
            "--start-second", str(start_second),
            "--num-seconds", str(num_seconds),  # Process only 3 seconds
            "--frame-step", "1",   # Process every frame in the segment
            "--max-frames", "0"    # No frame limit within the segment
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        print(f"   ⏳ Processing focused segment...")
        
        # Run with reasonable timeout for focused segment
        try:
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  check=True,
                                  timeout=180)  # 3 minute timeout for focused segment
        except subprocess.TimeoutExpired:
            print("⏰ Focused tracking taking longer than expected...")
            # Continue to find partial results
            pass
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ Focused tracking completed in {processing_time:.1f} seconds!")
        
        # Find the generated tracking data
        output_path = Path(output_dir)
        if not output_path.exists():
            raise RuntimeError(f"Output directory not found: {output_dir}")
        
        tracking_files = list(output_path.glob("player_detection_data_*.json"))
        
        if not tracking_files:
            raise RuntimeError("No tracking data files found")
        
        tracking_file = str(tracking_files[0])
        print(f"✅ Focused segment tracking data: {tracking_file}")
        
        return str(Path(cv_hockey_dir) / tracking_file)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Focused tracking failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise
    finally:
        # Return to original directory
        os.chdir(original_dir)


def run_focused_analysis(tracking_data_path: str):
    """Run tactical analysis on the focused segment."""
    print(f"🔍 Running focused tactical analysis...")
    
    from src.tactical_analyzer import TacticalAnalyzer
    
    analyzer = TacticalAnalyzer(tracking_data_path)
    results = analyzer.run_enhanced_analysis_with_weaknesses()
    
    return results


def display_focused_results(results: dict, tracking_file: str, start_second: int, num_seconds: int):
    """Display focused analysis results."""
    print("\n📊 FOCUSED SEGMENT TACTICAL ANALYSIS RESULTS")
    print("=" * 60)
    print(f"🎯 Segment: {start_second}s to {start_second + num_seconds}s")
    print(f"⏱️  Duration: {num_seconds} seconds")
    print("=" * 60)
    
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
        print("⚠️  No formations detected in this segment")
        print("   This is normal for short segments - try longer segments")
    
    if 'overall_quality' in results:
        quality = results['overall_quality']
        print(f"\n📈 Overall Quality Score: {quality.get('average_quality_score', 'N/A')}")
        print(f"🔴 Total Weaknesses: {quality.get('total_weaknesses_count', 'N/A')}")
    
    print(f"\n📁 Results saved to: {Path(tracking_file).parent}")
    print("✅ Focused analysis completed!")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Focused Segment Analyzer: Quick 3-Second Tactical Analysis"
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
        "--start-second",
        type=int,
        default=3,
        help="Start time in seconds (default: 3)"
    )
    parser.add_argument(
        "--num-seconds",
        type=int,
        default=3,
        help="Number of seconds to process (default: 3)"
    )
    
    args = parser.parse_args()
    
    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        sys.exit(1)
    
    print("🎯 FOCUSED SEGMENT ANALYZER: QUICK TACTICAL ANALYSIS")
    print("=" * 70)
    print(f"🎬 Input Video: {video_path.name}")
    print(f"🔧 CV-Hockey Path: {args.cv_hockey_path}")
    print(f"⏱️  Segment: {args.start_second}s to {args.start_second + args.num_seconds}s")
    print(f"📊 Expected Frames: ~{args.num_seconds * 30} frames")
    print(f"⚡ Target Speed: Under 2 minutes for focused segment")
    print(f"🎯 Goal: Quick tactical insights from focused game segment")
    print()
    
    try:
        start_time = time.time()
        
        # Step 1: Focused segment tracking
        tracking_file = run_focused_tracking(
            str(video_path), 
            args.start_second,
            args.num_seconds,
            args.cv_hockey_path
        )
        
        # Step 2: Focused tactical analysis
        results = run_focused_analysis(tracking_file)
        
        # Step 3: Display results
        display_focused_results(results, tracking_file, args.start_second, args.num_seconds)
        
        total_time = time.time() - start_time
        
        print(f"\n🎯 SUCCESS! Focused segment analyzed in {total_time:.1f} seconds!")
        print(f"📁 Results saved in: {Path(tracking_file).parent}")
        
        if total_time < 120:
            print("🎯 TARGET ACHIEVED: Under 2 minutes for focused segment!")
        else:
            print(f"⏰ Target missed by {total_time - 120:.1f} seconds")
        
    except Exception as e:
        print(f"❌ Focused analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
