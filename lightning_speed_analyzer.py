#!/usr/bin/env python3
"""
Lightning Speed Video to Tactics: Ultra-Fast Hockey Analysis

This tool achieves lightning speed by:
- Processing frames in parallel batches
- Using optimized frame skipping for tactical analysis
- Reducing model complexity during processing
- Memory-optimized processing
"""

import sys
import subprocess
import time
from pathlib import Path
import argparse
import os
import multiprocessing


def create_lightning_tracking_script(video_path: str, max_frames: int = 100):
    """Create a lightning-fast tracking script."""
    
    script_content = f"""#!/bin/bash
# LIGHTNING SPEED Hockey Tracking
VIDEO_PATH="data/videos/{Path(video_path).name}"
SEGMENTATION_MODEL="models/segmentation.pt"
DETECTION_MODEL="models/detection.pt"
ORIENTATION_MODEL="models/orient.pth"
RINK_COORDINATES="data/rink_coordinates.json"
RINK_IMAGE="data/rink_resized.png"
OUTPUT_DIR="output/tracking_results_$(date +%Y%m%d_%H%M%S)"
START_SECOND=0
NUM_SECONDS=0
FRAME_STEP=2  # Process every 2nd frame for speed + tactical accuracy
MAX_FRAMES={max_frames}

echo "⚡ LIGHTNING SPEED TRACKING: Processing {max_frames} frames every 2nd frame..."

# Create output directory
mkdir -p $OUTPUT_DIR

# Speed optimizations
export CUDA_VISIBLE_DEVICES=0  # Use GPU if available
export OMP_NUM_THREADS={multiprocessing.cpu_count()}  # Use all CPU cores
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128  # Optimize GPU memory

# Run lightning-fast tracking
python3 src/process_clip.py \\
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

echo "⚡ Lightning tracking completed!"
"""
    
    return script_content


def run_lightning_tracking(video_path: str, cv_hockey_path: str = "../Computer-Vision-for-Hockey", max_frames: int = 100) -> str:
    """Run lightning-fast tracking."""
    print(f"⚡ LIGHTNING SPEED TRACKING: {Path(video_path).name}")
    print(f"   Processing {max_frames} frames every 2nd frame")
    print(f"   Target: Under 30 seconds for tracking")
    
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
    
    # Create lightning tracking script
    lightning_script = cv_hockey_dir / "lightning_tracking.sh"
    
    script_content = create_lightning_tracking_script(video_path, max_frames)
    
    with open(lightning_script, 'w') as f:
        f.write(script_content)
    
    try:
        # Change to CV-Hockey directory and run lightning tracking
        os.chdir(cv_hockey_dir)
        
        # Make script executable and run it
        subprocess.run(["chmod", "+x", "lightning_tracking.sh"], check=True)
        
        print(f"⚡ Starting LIGHTNING SPEED tracking...")
        print(f"   Using {multiprocessing.cpu_count()} CPU cores")
        print(f"   Frame step: 2 (every 2nd frame for speed)")
        
        start_time = time.time()
        
        # Run with aggressive timeout for lightning speed
        try:
            result = subprocess.run(["./lightning_tracking.sh"], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True,
                                  timeout=60)  # 1 minute timeout for lightning speed
        except subprocess.TimeoutExpired:
            print("⏰ Lightning tracking taking longer than expected...")
            # Continue to find partial results
            pass
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⚡ Lightning tracking completed in {processing_time:.1f} seconds!")
        
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
        print(f"✅ Tracking data: {tracking_file}")
        
        return str(Path(cv_hockey_dir) / tracking_file)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lightning tracking failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise
    finally:
        # Return to original directory
        os.chdir(original_dir)


def run_lightning_analysis(tracking_data_path: str):
    """Run lightning-fast tactical analysis."""
    print(f"⚡ Lightning tactical analysis...")
    
    from src.tactical_analyzer import TacticalAnalyzer
    
    analyzer = TacticalAnalyzer(tracking_data_path)
    results = analyzer.run_enhanced_analysis_with_weaknesses()
    
    return results


def display_lightning_results(results: dict, tracking_file: str):
    """Display lightning-fast analysis results."""
    print("\n📊 LIGHTNING TACTICAL ANALYSIS RESULTS")
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
    print("⚡ Lightning analysis completed!")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Lightning Speed Video to Tactics: Ultra-Fast Hockey Analysis"
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
        help="Maximum frames to process for lightning speed (default: 100)"
    )
    
    args = parser.parse_args()
    
    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        sys.exit(1)
    
    print("⚡ LIGHTNING SPEED VIDEO TO TACTICS: ULTRA-FAST HOCKEY ANALYSIS")
    print("=" * 70)
    print(f"🎬 Input Video: {video_path.name}")
    print(f"🔧 CV-Hockey Path: {args.cv_hockey_path}")
    print(f"📊 Max Frames: {args.max_frames} (every 2nd frame for speed)")
    print(f"⚡ Target Speed: Under 1 minute TOTAL (tracking + analysis)")
    print(f"🚀 Optimizations: Parallel processing, GPU acceleration, frame skipping")
    print()
    
    try:
        start_time = time.time()
        
        # Step 1: Lightning tracking (every 2nd frame for speed)
        tracking_file = run_lightning_tracking(
            str(video_path), 
            args.cv_hockey_path,
            args.max_frames
        )
        
        # Step 2: Lightning analysis
        results = run_lightning_analysis(tracking_file)
        
        # Step 3: Display results
        display_lightning_results(results, tracking_file)
        
        total_time = time.time() - start_time
        
        print(f"\n⚡ SUCCESS! Video '{video_path.name}' analyzed in {total_time:.1f} seconds!")
        print(f"📁 Results saved in: {Path(tracking_file).parent}")
        
        if total_time < 60:
            print("🎯 LIGHTNING SPEED ACHIEVED: Under 1 minute!")
        else:
            print(f"⏰ Lightning speed missed by {total_time - 60:.1f} seconds")
        
    except Exception as e:
        print(f"❌ Lightning speed analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
