#!/usr/bin/env python3
"""
Full Video Analyzer: Complete CHI vs PIT Analysis

This tool processes the ENTIRE video for complete tactical analysis.
"""

import sys
import subprocess
import time
from pathlib import Path
import argparse
import os


def run_full_video_tracking(video_path: str, cv_hockey_path: str = "../Computer-Vision-for-Hockey") -> str:
    """Run tracking on the ENTIRE video."""
    print(f"🎬 FULL VIDEO TRACKING: {Path(video_path).name}")
    print(f"   Processing ENTIRE video (no frame limits)")
    
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
        
        print(f"🎬 Starting FULL VIDEO tracking...")
        print(f"   This will process the ENTIRE video - please be patient...")
        print(f"   Expected time: 5-15 minutes depending on video length")
        
        start_time = time.time()
        
        # Call process_clip.py for ENTIRE video (no frame limits)
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
            "--num-seconds", "0",  # Process ENTIRE video
            "--frame-step", "1",   # Process EVERY frame
            "--max-frames", "0"    # NO frame limit - process ALL frames
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        print(f"   ⏳ Processing ENTIRE video - this will take time...")
        
        # Run and wait for completion (no timeout - let it finish)
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ FULL VIDEO tracking completed in {processing_time:.1f} seconds!")
        print(f"   Total time: {processing_time/60:.1f} minutes")
        
        # Find the generated tracking data
        output_path = Path(output_dir)
        if not output_path.exists():
            raise RuntimeError(f"Output directory not found: {output_dir}")
        
        tracking_files = list(output_path.glob("player_detection_data_*.json"))
        
        if not tracking_files:
            raise RuntimeError("No tracking data files found")
        
        tracking_file = str(tracking_files[0])
        print(f"✅ Full video tracking data: {tracking_file}")
        
        return str(Path(cv_hockey_dir) / tracking_file)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Full video tracking failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise
    finally:
        # Return to original directory
        os.chdir(original_dir)


def run_full_tactical_analysis(tracking_data_path: str):
    """Run tactical analysis on the full video data."""
    print(f"🔍 Running FULL VIDEO tactical analysis...")
    
    from src.tactical_analyzer import TacticalAnalyzer
    
    analyzer = TacticalAnalyzer(tracking_data_path)
    results = analyzer.run_enhanced_analysis_with_weaknesses()
    
    return results


def display_full_results(results: dict, tracking_file: str):
    """Display full video analysis results."""
    print("\n📊 FULL VIDEO TACTICAL ANALYSIS RESULTS")
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
        print("⚠️  No formations detected in this video")
        print("   This is unusual for a full video - check the data")
    
    if 'overall_quality' in results:
        quality = results['overall_quality']
        print(f"\n📈 Overall Quality Score: {quality.get('average_quality_score', 'N/A')}")
        print(f"🔴 Total Weaknesses: {quality.get('total_weaknesses_count', 'N/A')}")
    
    print(f"\n📁 Results saved to: {Path(tracking_file).parent}")
    print("✅ Full video analysis completed!")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Full Video Analyzer: Complete CHI vs PIT Analysis"
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
    
    args = parser.parse_args()
    
    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        sys.exit(1)
    
    print("🎬 FULL VIDEO ANALYZER: COMPLETE HOCKEY ANALYSIS")
    print("=" * 60)
    print(f"🎬 Input Video: {video_path.name}")
    print(f"🔧 CV-Hockey Path: {args.cv_hockey_path}")
    print(f"📊 Processing: ENTIRE VIDEO (no frame limits)")
    print(f"⏳ Expected Time: 5-15 minutes for full video")
    print(f"🎯 Goal: Complete tactical analysis of entire game")
    print()
    
    try:
        start_time = time.time()
        
        # Step 1: Full video tracking (ENTIRE video)
        tracking_file = run_full_video_tracking(
            str(video_path), 
            args.cv_hockey_path
        )
        
        # Step 2: Full tactical analysis
        results = run_full_tactical_analysis(tracking_file)
        
        # Step 3: Display results
        display_full_results(results, tracking_file)
        
        total_time = time.time() - start_time
        
        print(f"\n🎉 SUCCESS! ENTIRE video '{video_path.name}' fully analyzed!")
        print(f"📁 Results saved in: {Path(tracking_file).parent}")
        print(f"⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        
    except Exception as e:
        print(f"❌ Full video analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
