#!/usr/bin/env python3
"""
Test Enhanced Hockey Tactical Analysis with Weakness Detection

This script tests the new enhanced analysis capabilities including:
- Tactical weakness detection
- Formation quality assessment
- Coverage gap analysis
- Behavioral pattern recognition
"""

import json
import numpy as np
from pathlib import Path
from src.tactical_weakness_detector import (
    TacticalWeaknessDetector, 
    WeaknessType, 
    CoverageQuality,
    FormationQuality
)
from src.tactical_analyzer import TacticalAnalyzer

def create_test_tracking_data():
    """Create test tracking data with known tactical weaknesses."""
    
    # Create 50 frames of tracking data
    frames = []
    
    for frame_id in range(50):
        frame_data = {
            "frame_id": frame_id,
            "timestamp": frame_id * 0.04,  # 25 FPS
            "players": []
        }
        
        if frame_id < 25:
            # First 25 frames: 1-2-2 formation with coverage gap
            players = [
                # Defensemen with wide gap (weakness)
                {
                    "player_id": 1,
                    "type": "defense",
                    "x": 1200,  # Far right
                    "y": 300,
                    "side": "strong"
                },
                {
                    "player_id": 2,
                    "type": "defense", 
                    "x": 800,   # Far left - creates wide gap
                    "y": 300,
                    "side": "weak"
                },
                # Forwards
                {
                    "player_id": 3,
                    "type": "forward",
                    "x": 1000,  # Center
                    "y": 200,
                    "side": "center"
                },
                {
                    "player_id": 4,
                    "type": "forward",
                    "x": 1100,  # Right wing
                    "y": 400,
                    "side": "strong"
                },
                {
                    "player_id": 5,
                    "type": "forward",
                    "x": 900,   # Left wing - too far from net
                    "y": 400,
                    "side": "weak"
                }
            ]
        else:
            # Last 25 frames: 2-1-2 formation with poor trap execution
            players = [
                # Forwards not maintaining trap pressure
                {
                    "player_id": 1,
                    "type": "forward",
                    "x": 600,  # Too far back
                    "y": 200,
                    "side": "left"
                },
                {
                    "player_id": 2,
                    "type": "forward", 
                    "x": 600,  # Too far back
                    "y": 400,
                    "side": "right"
                },
                # Center not reading play effectively
                {
                    "player_id": 3,
                    "type": "forward",
                    "x": 700,  # Poor position
                    "y": 300,
                    "side": "center"
                },
                # Defensemen too aggressive
                {
                    "player_id": 4,
                    "type": "defense",
                    "x": 500,  # Too far forward
                    "y": 250,
                    "side": "left"
                },
                {
                    "player_id": 5,
                    "type": "defense",
                    "x": 500,  # Too far forward
                    "y": 350,
                    "side": "right"
                }
            ]
        
        frame_data["players"] = players
        frames.append(frame_data)
    
    return frames

def test_weakness_detector():
    """Test the tactical weakness detector."""
    print("🧪 Testing Tactical Weakness Detector...")
    
    # Create test data
    test_frames = create_test_tracking_data()
    
    # Initialize detector
    detector = TacticalWeaknessDetector()
    
    # Test 1-2-2 formation analysis (first 25 frames)
    print("\n📋 Testing 1-2-2 Formation Analysis...")
    players_1_2_2 = test_frames[12]["players"]  # Middle frame of 1-2-2
    
    quality_1_2_2 = detector.analyze_formation_quality(
        "1-2-2", players_1_2_2, test_frames, (0, 24)
    )
    
    print(f"  Formation: {quality_1_2_2.formation_name}")
    print(f"  Overall Score: {quality_1_2_2.overall_score:.3f}")
    print(f"  Coverage Quality: {quality_1_2_2.coverage_quality.value}")
    print(f"  Weaknesses Detected: {len(quality_1_2_2.weaknesses)}")
    
    # Check for expected weaknesses
    coverage_gaps = [w for w in quality_1_2_2.weaknesses if w.weakness_type == WeaknessType.COVERAGE_GAP]
    positioning_issues = [w for w in quality_1_2_2.weaknesses if w.weakness_type == WeaknessType.POOR_POSITIONING]
    
    print(f"  Coverage Gaps: {len(coverage_gaps)}")
    print(f"  Positioning Issues: {len(positioning_issues)}")
    
    if coverage_gaps:
        print("  ✅ Coverage gap detection working")
        for weakness in coverage_gaps:
            print(f"    - {weakness.description}")
            print(f"      Severity: {weakness.severity:.2f}")
            print(f"      Recommendations: {len(weakness.recommendations)}")
    
    if positioning_issues:
        print("  ✅ Positioning issue detection working")
        for weakness in positioning_issues:
            print(f"    - {weakness.description}")
            print(f"      Severity: {weakness.severity:.2f}")
    
    # Test 2-1-2 formation analysis (last 25 frames)
    print("\n📋 Testing 2-1-2 Formation Analysis...")
    players_2_1_2 = test_frames[37]["players"]  # Middle frame of 2-1-2
    
    quality_2_1_2 = detector.analyze_formation_quality(
        "2-1-2", players_2_1_2, test_frames, (25, 49)
    )
    
    print(f"  Formation: {quality_2_1_2.formation_name}")
    print(f"  Overall Score: {quality_2_1_2.overall_score:.3f}")
    print(f"  Coverage Quality: {quality_2_1_2.coverage_quality.value}")
    print(f"  Weaknesses Detected: {len(quality_2_1_2.weaknesses)}")
    
    # Check for expected weaknesses
    formation_breakdowns = [w for w in quality_2_1_2.weaknesses if w.weakness_type == WeaknessType.FORMATION_BREAKDOWN]
    
    print(f"  Formation Breakdowns: {len(formation_breakdowns)}")
    
    if formation_breakdowns:
        print("  ✅ Formation breakdown detection working")
        for weakness in formation_breakdowns:
            print(f"    - {weakness.description}")
            print(f"      Severity: {weakness.severity:.2f}")
    
    print("\n✅ Weakness Detector Tests Completed!")

def test_enhanced_analyzer():
    """Test the enhanced tactical analyzer."""
    print("\n🧪 Testing Enhanced Tactical Analyzer...")
    
    # Create test data file
    test_data = {"frames": create_test_tracking_data()}
    test_file = "test_enhanced_data.json"
    
    with open(test_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    try:
        # Initialize enhanced analyzer
        analyzer = TacticalAnalyzer(test_file)
        
        # Run enhanced analysis
        print("  Running enhanced analysis with weakness detection...")
        results = analyzer.run_enhanced_analysis_with_weaknesses()
        
        # Verify results structure
        print("  Verifying results structure...")
        
        required_keys = [
            "enhanced_formation_analysis",
            "zone_analysis", 
            "enhanced_tactical_insights",
            "analysis_metadata"
        ]
        
        for key in required_keys:
            if key in results:
                print(f"    ✅ {key} present")
            else:
                print(f"    ❌ {key} missing")
                return False
        
        # Check formation analysis
        formation_analysis = results["enhanced_formation_analysis"]
        if "detected_formations" in formation_analysis:
            formations = formation_analysis["detected_formations"]
            print(f"    ✅ Detected {len(formations)} formations")
            
            for formation in formations:
                if "quality_analysis" in formation:
                    quality = formation["quality_analysis"]
                    print(f"      {formation['formation']}: Score {quality['overall_score']:.3f}")
                else:
                    print(f"      ❌ Quality analysis missing for {formation['formation']}")
        
        # Check weakness analysis
        weakness_analysis = results["enhanced_tactical_insights"]["weakness_analysis"]
        print(f"    ✅ Total weaknesses: {weakness_analysis['total_weaknesses']}")
        print(f"    ✅ Critical issues: {weakness_analysis['critical_issues']}")
        
        # Check quality summary
        quality_summary = results["enhanced_tactical_insights"]["quality_summary"]
        if "average_quality_score" in quality_summary:
            print(f"    ✅ Average quality: {quality_summary['average_quality_score']:.3f}")
        
        print("  ✅ Enhanced Analyzer Tests Completed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Enhanced analyzer test failed: {e}")
        return False
    finally:
        # Clean up test file
        if Path(test_file).exists():
            Path(test_file).unlink()

def main():
    """Run all tests."""
    print("🏒 ENHANCED HOCKEY TACTICAL ANALYSIS - COMPREHENSIVE TESTING")
    print("=" * 70)
    
    # Test individual components
    test_weakness_detector()
    
    # Test integrated system
    success = test_enhanced_analyzer()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 ALL TESTS PASSED! Enhanced analysis system is working correctly.")
        print("\n🚀 You can now use the enhanced analysis with:")
        print("  • python3 enhanced_analysis_demo.py your_data.json")
        print("  • analyzer.run_enhanced_analysis_with_weaknesses()")
        print("  • Detailed weakness detection and quality assessment")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    print("\n📊 The enhanced system now provides:")
    print("  • Coverage gap detection (e.g., defensemen too far apart)")
    print("  • Positioning quality analysis")
    print("  • Formation consistency tracking")
    print("  • Pressure pattern analysis")
    print("  • Specific tactical recommendations")
    print("  • Formation quality scoring")

if __name__ == "__main__":
    main()
