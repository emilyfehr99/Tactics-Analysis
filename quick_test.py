#!/usr/bin/env python3
"""
Quick test of the hockey tactical analysis system
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.append('src')

from formation_detector import FormationDetector
from tactical_analyzer import TacticalAnalyzer

def create_simple_test_data():
    """Create a simple test dataset with just a few frames."""
    test_data = {
        "frames": [
            {
                "frame_id": 0,
                "timestamp": 0.0,
                "players": [
                    {
                        "player_id": "player_0",
                        "rink_position": {"x": 200, "y": 300},
                        "orientation": 0.0
                    },
                    {
                        "player_id": "player_1", 
                        "rink_position": {"x": 400, "y": 300},
                        "orientation": 0.0
                    },
                    {
                        "player_id": "player_2",
                        "rink_position": {"x": 600, "y": 300},
                        "orientation": 0.0
                    }
                ]
            },
            {
                "frame_id": 1,
                "timestamp": 0.1,
                "players": [
                    {
                        "player_id": "player_0",
                        "rink_position": {"x": 200, "y": 300},
                        "orientation": 0.0
                    },
                    {
                        "player_id": "player_1",
                        "rink_position": {"x": 400, "y": 300},
                        "orientation": 0.0
                    },
                    {
                        "player_id": "player_2",
                        "rink_position": {"x": 600, "y": 300},
                        "orientation": 0.0
                    }
                ]
            }
        ]
    }
    return test_data

def main():
    print("🏒 Quick Test of Hockey Tactical Analysis System")
    print("=" * 50)
    
    # Test 1: Formation Detector
    print("\n1. Testing Formation Detector...")
    try:
        detector = FormationDetector()
        print("   ✅ Formation detector created successfully")
        
        # Test zone classification
        zone = detector.classify_player_zone(200, 300)
        print(f"   ✅ Zone classification working: {zone.value}")
        
    except Exception as e:
        print(f"   ❌ Formation detector failed: {e}")
        return
    
    # Test 2: Create test data
    print("\n2. Creating test data...")
    try:
        test_data = create_simple_test_data()
        print(f"   ✅ Created test data with {len(test_data['frames'])} frames")
        
        # Save test data
        test_file = Path("quick_test_data.json")
        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        print(f"   ✅ Saved test data to {test_file}")
        
    except Exception as e:
        print(f"   ❌ Test data creation failed: {e}")
        return
    
    # Test 3: Basic Analysis
    print("\n3. Testing basic analysis...")
    try:
        analyzer = TacticalAnalyzer(
            input_path="quick_test_data.json",
            output_dir="quick_test_results"
        )
        print("   ✅ Tactical analyzer created successfully")
        
        # Quick formation test
        formations = analyzer.analyze_formations(min_frames=1, min_confidence=0.3)
        print(f"   ✅ Formation analysis completed: {len(formations['detected_formations'])} formations detected")
        
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎉 All tests passed! System is working correctly.")
    print("\nNext steps:")
    print("1. Copy your tracking data to this directory")
    print("2. Run: python3 src/analyze_formations.py your_data.json --complete")
    print("3. Check the results directory for analysis output")

if __name__ == "__main__":
    main()
