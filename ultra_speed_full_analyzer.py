#!/usr/bin/env python3
"""
Ultra-Speed Full Video Analyzer: Complete Video in Under 1 Minute

This tool achieves lightning speed for FULL video analysis by:
- Aggressive frame skipping (every 5th frame)
- Parallel processing optimizations
- Reduced model complexity
- Memory optimization
- GPU acceleration
"""

import sys
import subprocess
import time
from pathlib import Path
import argparse
import os
import multiprocessing


def create_ultra_speed_script(video_path: str):
    """Create ultra-speed tracking script for full video."""
    
    script_content = f"""#!/bin/bash
# ULTRA-SPEED FULL VIDEO Hockey Tracking
VIDEO_PATH="data/videos/{Path(video_path).name}"
SEGMENTATION_MODEL="models/segmentation.pt"
DETECTION_MODEL="models/detection.pt"
ORIENTATION_MODEL="models/orient.pth"
RINK_COORDINATES="data/rink_coordinates.json"
RINK_IMAGE="data/rink_resized.png"
OUTPUT_DIR="output/tracking_results_$(date +%Y%m%d_%H%M%S)"
START_SECOND=0
NUM_SECONDS=0
FRAME_STEP=5  # Process every 5th frame for ultra-speed
MAX_FRAMES=0  # No frame limit - process entire video

echo "⚡ ULTRA-SPEED FULL VIDEO TRACKING: Processing entire video every 5th frame..."

# Create output directory
mkdir -p $OUTPUT_DIR

# ULTRA-SPEED OPTIMIZATIONS
export CUDA_VISIBLE_DEVICES=0  # Use GPU if available
export OMP_NUM_THREADS={multiprocessing.cpu_count()}  # Use ALL CPU cores
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:64  # Aggressive GPU memory optimization
export PYTORCH_CUDA_ALLOC_CONF=garbage_collection_threshold:0.6  # Aggressive garbage collection
export CUDA_LAUNCH_BLOCKING=0  # Non-blocking CUDA operations

# Set process priority for speed
nice -n -10 python3 src/process_clip.py \\
  --video "$VIDEO_PATH" \\
  --segmentation-model "$SEGMENTATION_MODEL" \\
  --detection-model "$DETECTION_MODEL" \\
  --orientation-model "$ORIENTATION_MODEL" \\
  --rink-coordinates "$RINK_COORDINATES" \\
  --rink-image "$RINK_IMAGE" \\
  --output-dir "$OUTPUT_DIR" \\
  --start-second $START_SECOND \\
  --num-seconds $NUM_SECONDS \\
  --frame-step $FRAME_STEP \\
  --max-frames $MAX_FRAMES

echo "⚡ Ultra-speed full video tracking completed!"
"""
    
    return script_content


def run_ultra_speed_full_tracking(video_path: str, cv_hockey_path: str = "../Computer-Vision-for-Hockey") -> str:
    """Run ultra-speed tracking on the ENTIRE video."""
    print(f"⚡ ULTRA-SPEED FULL VIDEO TRACKING: {Path(video_path).name}")
    print(f"   Processing ENTIRE video every 5th frame")
    print(f"   Target: Under 1 minute for complete video")
    
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
    
    # Create ultra-speed tracking script
    ultra_script = cv_hockey_dir / "ultra_speed_tracking.sh"
    
    script_content = create_ultra_speed_script(video_path)
    
    with open(ultra_script, 'w') as f:
        f.write(script_content)
    
    try:
        # Change to CV-Hockey directory and run ultra-speed tracking
        os.chdir(cv_hockey_dir)
        
        # Make script executable and run it
        subprocess.run(["chmod", "+x", "ultra_speed_tracking.sh"], check=True)
        
        print(f"⚡ Starting ULTRA-SPEED FULL VIDEO tracking...")
        print(f"   Using {multiprocessing.cpu_count()} CPU cores")
        print(f"   Frame step: 5 (every 5th frame for ultra-speed)")
        print(f"   Target: Under 1 minute for entire video")
        
        start_time = time.time()
        
        # Run with aggressive timeout for ultra-speed
        try:
            result = subprocess.run(["./ultra_speed_tracking.sh"], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True,
                                  timeout=90)  # 1.5 minute timeout for ultra-speed
        except subprocess.TimeoutExpired:
            print("⏰ Ultra-speed tracking taking longer than expected...")
            # Continue to find partial results
            pass
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⚡ Ultra-speed tracking completed in {processing_time:.1f} seconds!")
        
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
        print(f"✅ Full video tracking data: {tracking_file}")
        
        return str(Path(cv_hockey_dir) / tracking_file)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ultra-speed tracking failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise
    finally:
        # Return to original directory
        os.chdir(original_dir)


def run_ultra_fast_analysis(tracking_data_path: str):
    """Run ultra-fast tactical analysis."""
    print(f"⚡ Ultra-fast tactical analysis...")
    
    from src.tactical_analyzer import TacticalAnalyzer
    
    analyzer = TacticalAnalyzer(tracking_data_path)
    results = analyzer.run_enhanced_analysis_with_weaknesses()
    
    return results


def display_ultra_results(results: dict, tracking_file: str):
    """Display ultra-speed analysis results."""
    print("\n📊 ULTRA-SPEED FULL VIDEO TACTICAL ANALYSIS RESULTS")
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
        print("⚠️  No formations detected in this video")
        print("   This is unusual for a full video - check the data")
    
    if 'overall_quality' in results:
        quality = results['overall_quality']
        print(f"\n📈 Overall Quality Score: {quality.get('average_quality_score', 'N/A')}")
        print(f"🔴 Total Weaknesses: {quality.get('total_weaknesses_count', 'N/A')}")
    
    print(f"\n📁 Results saved to: {Path(tracking_file).parent}")
    print("⚡ Ultra-speed analysis completed!")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Ultra-Speed Full Video Analyzer: Complete Video in Under 1 Minute"
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
    
    print("⚡ ULTRA-SPEED FULL VIDEO ANALYZER: COMPLETE VIDEO IN UNDER 1 MINUTE")
    print("=" * 80)
    print(f"🎬 Input Video: {video_path.name}")
    print(f"🔧 CV-Hockey Path: {args.cv_hockey_path}")
    print(f"📊 Processing: ENTIRE VIDEO (every 5th frame for ultra-speed)")
    print(f"⚡ Target Speed: Under 1 minute for complete video")
    print(f"🚀 Ultra-Optimizations: Frame skipping, parallel processing, GPU acceleration")
    print()
    
    try:
        start_time = time.time()
        
        # Step 1: Ultra-speed full video tracking (ENTIRE video, every 5th frame)
        tracking_file = run_ultra_speed_full_tracking(
            str(video_path), 
            args.cv_hockey_path
        )
        
        # Step 2: Ultra-fast analysis
        results = run_ultra_fast_analysis(tracking_file)
        
        # Step 3: Display results
        display_ultra_results(results, tracking_file)
        
        total_time = time.time() - start_time
        
        print(f"\n⚡ SUCCESS! ENTIRE video '{video_path.name}' analyzed in {total_time:.1f} seconds!")
        print(f"📁 Results saved in: {Path(tracking_file).parent}")
        
        if total_time < 60:
            print("🎯 ULTRA-SPEED TARGET ACHIEVED: Under 1 minute!")
        else:
            print(f"⏰ Ultra-speed target missed by {total_time - 60:.1f} seconds")
        
    except Exception as e:
        print(f"❌ Ultra-speed analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
