#!/usr/bin/env python3
"""Debug script to isolate the improvement_priority issue."""

import json
from src.tactical_analyzer import TacticalAnalyzer

def main():
    # Create simple test data
    test_data = {
        "frames": [
            {
                "frame_id": 0,
                "timestamp": 0.0,
                "players": [
                    {"player_id": 1, "type": "defense", "x": 1200, "y": 300, "zone": "defensive"},
                    {"player_id": 2, "type": "defense", "x": 800, "y": 300, "zone": "defensive"},
                    {"player_id": 3, "type": "forward", "x": 1000, "y": 200, "zone": "defensive"}
                ]
            }
        ]
    }
    
    # Save test data
    with open("debug_test.json", "w") as f:
        json.dump(test_data, f)
    
    try:
        analyzer = TacticalAnalyzer("debug_test.json")
        results = analyzer.run_enhanced_analysis_with_weaknesses()
        
        print("✅ Enhanced analysis completed successfully!")
        print(f"Results keys: {list(results.keys())}")
        
        if "enhanced_formation_analysis" in results:
            formations = results["enhanced_formation_analysis"]["detected_formations"]
            print(f"Formations detected: {len(formations)}")
            
            for formation in formations:
                print(f"Formation: {formation['formation']}")
                if "quality_analysis" in formation:
                    quality = formation["quality_analysis"]
                    print(f"  Quality keys: {list(quality.keys())}")
                    if "weaknesses" in quality:
                        print(f"  Weaknesses: {len(quality['weaknesses'])}")
                        for w in quality['weaknesses']:
                            print(f"    - {w['description']} (severity: {w['severity']})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
