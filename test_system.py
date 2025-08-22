#!/usr/bin/env python3
"""
Test Script for Hockey Tactical Analysis System

This script creates sample tracking data and tests the analysis system
to ensure all components are working correctly.
"""

import sys
import json
import numpy as np
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent / "src"))

from tactical_analyzer import TacticalAnalyzer

def create_sample_tracking_data():
    """Create sample player tracking data for testing."""
    
    # Sample rink dimensions
    rink_width, rink_height = 1400, 600
    
    # Define sample formations over time
    sample_formations = [
        # 1-3-1 formation (offensive zone)
        {
            'name': '1-3-1',
            'duration': 30,  # frames
            'zone_distribution': {
                'offensive': [(0.1, 0.3), (0.15, 0.5), (0.2, 0.4), (0.25, 0.6), (0.1, 0.7)],
                'neutral': [],
                'defensive': []
            }
        },
        # 2-1-2 formation (neutral zone trap)
        {
            'name': '2-1-2',
            'duration': 25,
            'zone_distribution': {
                'offensive': [],
                'neutral': [(0.4, 0.3), (0.45, 0.5), (0.5, 0.4), (0.55, 0.6), (0.6, 0.7)],
                'defensive': []
            }
        },
        # 1-2-2 formation (defensive zone)
        {
            'name': '1-2-2',
            'duration': 20,
            'zone_distribution': {
                'offensive': [],
                'neutral': [],
                'defensive': [(0.7, 0.3), (0.75, 0.5), (0.8, 0.4), (0.85, 0.6), (0.9, 0.7)]
            }
        }
    ]
    
    frames = []
    frame_id = 0
    
    for formation in sample_formations:
        for frame in range(formation['duration']):
            frame_data = {
                'frame_id': frame_id,
                'timestamp': frame_id * 0.1,  # 0.1 seconds per frame
                'players': []
            }
            
            # Add players based on formation
            zone_dist = formation['zone_distribution']
            
            # Offensive zone players
            for i, (x_ratio, y_ratio) in enumerate(zone_dist['offensive']):
                frame_data['players'].append({
                    'player_id': f'offensive_{i}',
                    'rink_position': {
                        'x': x_ratio * rink_width,
                        'y': y_ratio * rink_height
                    },
                    'orientation': np.random.uniform(0, 2 * np.pi),
                    'team': 'Team A'
                })
            
            # Neutral zone players
            for i, (x_ratio, y_ratio) in enumerate(zone_dist['neutral']):
                frame_data['players'].append({
                    'player_id': f'neutral_{i}',
                    'rink_position': {
                        'x': x_ratio * rink_width,
                        'y': y_ratio * rink_height
                    },
                    'orientation': np.random.uniform(0, 2 * np.pi),
                    'team': 'Team A'
                })
            
            # Defensive zone players
            for i, (x_ratio, y_ratio) in enumerate(zone_dist['defensive']):
                frame_data['players'].append({
                    'player_id': f'defensive_{i}',
                    'rink_position': {
                        'x': x_ratio * rink_width,
                        'y': y_ratio * rink_height
                    },
                    'orientation': np.random.uniform(0, 2 * np.pi),
                    'team': 'Team A'
                })
            
            frames.append(frame_data)
            frame_id += 1
    
    return frames

def test_formation_detection():
    """Test formation detection functionality."""
    print("Testing formation detection...")
    
    # Create sample data
    sample_data = create_sample_tracking_data()
    
    # Save sample data
    data_dir = Path("test_data")
    data_dir.mkdir(exist_ok=True)
    
    sample_file = data_dir / "sample_tracking.json"
    with open(sample_file, 'w') as f:
        json.dump({'frames': sample_data}, f, indent=2)
    
    print(f"Created sample data with {len(sample_data)} frames")
    
    # Test analyzer
    try:
        analyzer = TacticalAnalyzer(
            input_path=sample_file,
            output_dir="test_results"
        )
        
        # Test formation analysis
        formation_results = analyzer.analyze_formations(min_frames=5)
        
        print(f"\nFormation Detection Results:")
        print(f"  Detected formations: {len(formation_results['detected_formations'])}")
        
        for formation in formation_results['detected_formations']:
            print(f"    • {formation['formation']} (confidence: {formation['avg_confidence']:.2f})")
        
        # Test zone analysis
        zone_results = analyzer.analyze_zones()
        print(f"\nZone Analysis Results:")
        print(f"  Zones analyzed: {len(zone_results['zone_distribution'])}")
        
        # Test tactical insights
        tactical_insights = analyzer.generate_tactical_insights()
        print(f"\nTactical Insights Generated:")
        print(f"  Summary: {tactical_insights['summary'][:100]}...")
        
        print("\n✅ All tests passed! System is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_loading():
    """Test CSV data loading functionality."""
    print("\nTesting CSV data loading...")
    
    # Create sample CSV data
    import pandas as pd
    
    csv_data = []
    sample_data = create_sample_tracking_data()
    
    for frame in sample_data:
        for player in frame['players']:
            csv_data.append({
                'frame_id': frame['frame_id'],
                'timestamp': frame['timestamp'],
                'player_id': player['player_id'],
                'x': player['rink_position']['x'],
                'y': player['rink_position']['y'],
                'orientation': player['orientation'],
                'team': player['team']
            })
    
    # Save as CSV
    data_dir = Path("test_data")
    csv_file = data_dir / "sample_tracking.csv"
    
    df = pd.DataFrame(csv_data)
    df.to_csv(csv_file, index=False)
    
    print(f"Created sample CSV with {len(csv_data)} player records")
    
    # Test CSV loading
    try:
        analyzer = TacticalAnalyzer(
            input_path=csv_file,
            output_dir="test_results_csv"
        )
        
        print(f"CSV loaded successfully: {len(analyzer.tracking_data)} frames")
        
        # Quick formation test
        formation_results = analyzer.analyze_formations(min_frames=3)
        print(f"  Detected formations from CSV: {len(formation_results['detected_formations'])}")
        
        print("✅ CSV loading test passed!")
        return True
        
    except Exception as e:
        print(f"❌ CSV loading test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("HOCKEY TACTICAL ANALYSIS SYSTEM - TEST SUITE")
    print("=" * 60)
    
    # Test 1: Formation detection with JSON
    test1_passed = test_formation_detection()
    
    # Test 2: CSV loading
    test2_passed = test_csv_loading()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! The system is ready to use.")
        print("\nNext steps:")
        print("1. Copy your tracking data to the data/ directory")
        print("2. Run: python src/analyze_formations.py data/your_file.json --complete")
        print("3. Check the results/ directory for analysis output")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    
    print("\nSample data created in test_data/ directory")
    print("Test results saved in test_results/ directory")

if __name__ == "__main__":
    main()
