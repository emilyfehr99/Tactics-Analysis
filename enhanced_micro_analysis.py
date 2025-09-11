#!/usr/bin/env python3
"""
Enhanced Micro Tactical Analysis for Hockey

This script provides granular, player-level tactical analysis with specific insights
about individual player behaviors, vulnerabilities, and exploitation opportunities.
"""

import sys
import json
from pathlib import Path
import argparse
from datetime import datetime

# Add src to path
sys.path.append('src')

from tactical_analyzer import TacticalAnalyzer
from micro_tactical_analyzer import MicroTacticalAnalyzer, PlayerBehaviorType, VulnerabilityType

def main():
    """Run enhanced micro tactical analysis."""
    
    parser = argparse.ArgumentParser(description='Enhanced Micro Tactical Analysis')
    parser.add_argument('input_file', help='Path to tracking data JSON file')
    parser.add_argument('--output-dir', default='results', help='Output directory')
    parser.add_argument('--team', default='Team B', help='Team to analyze')
    parser.add_argument('--min-frames', type=int, default=3, help='Minimum frames for formation detection')
    parser.add_argument('--min-confidence', type=float, default=0.3, help='Minimum confidence threshold')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("🏒 Enhanced Micro Tactical Analysis System")
    print("=" * 60)
    print(f"📁 Analyzing: {args.input_file}")
    print(f"🎯 Target Team: {args.team}")
    print()
    
    try:
        # Initialize analyzers
        tactical_analyzer = TacticalAnalyzer(
            input_path=args.input_file,
            output_dir=args.output_dir
        )
        
        micro_analyzer = MicroTacticalAnalyzer()
        
        # Load tracking data
        print("📊 Loading tracking data...")
        with open(args.input_file, 'r') as f:
            tracking_data = json.load(f)
        
        # Run formation analysis
        print("🔍 Analyzing formations...")
        formation_results = tactical_analyzer.analyze_formations(
            min_frames=args.min_frames,
            min_confidence=args.min_confidence
        )
        
        if not formation_results["detected_formations"]:
            print("❌ No formations detected with current parameters")
            return
        
        print(f"✅ Detected {len(formation_results['detected_formations'])} formations")
        print()
        
        # Run micro analysis on each formation
        all_micro_results = []
        
        for formation in formation_results["detected_formations"]:
            print(f"🔬 Micro Analysis: {formation['formation']} Formation")
            print("-" * 40)
            
            # Get player data for this formation timeframe
            formation_frames = list(range(formation['start_frame'], formation['end_frame'] + 1))
            formation_players = []
            
            for frame_idx in formation_frames:
                if frame_idx < len(tracking_data['frames']):
                    frame_data = tracking_data['frames'][frame_idx]
                    formation_players.extend(frame_data.get('players', []))
            
            # Run micro analysis
            micro_result = micro_analyzer.analyze_formation_micro_details(
                formation, formation_players, args.team
            )
            
            if micro_result:
                all_micro_results.append(micro_result)
                print_micro_analysis(micro_result)
                print()
        
        # Generate comprehensive report
        print("📋 Generating comprehensive micro tactical report...")
        generate_micro_report(all_micro_results, args.output_dir, args.team)
        
        print("🎉 Enhanced micro tactical analysis complete!")
        print(f"📁 Detailed results saved to: {args.output_dir}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

def print_micro_analysis(micro_result):
    """Print detailed micro analysis results."""
    
    print(f"Formation: {micro_result.formation_name}")
    print(f"Cohesion Score: {micro_result.formation_cohesion:.2f}")
    print(f"Tactical Effectiveness: {micro_result.tactical_effectiveness:.2f}")
    print()
    
    # Player-by-player analysis
    print("👥 Individual Player Analysis:")
    for player_analysis in micro_result.player_analyses:
        print(f"  Player {player_analysis.player_id} ({player_analysis.position_in_formation})")
        print(f"    Behavior: {player_analysis.behavior_type.value}")
        print(f"    Movement: {player_analysis.movement_pattern}")
        print(f"    Vulnerability Score: {player_analysis.vulnerability_score:.2f}")
        
        if player_analysis.vulnerabilities:
            print(f"    Vulnerabilities: {', '.join([v.value for v in player_analysis.vulnerabilities])}")
        
        if player_analysis.tactical_notes:
            print(f"    Tactical Notes:")
            for note in player_analysis.tactical_notes:
                print(f"      • {note}")
        
        if player_analysis.exploitation_opportunities:
            print(f"    Exploitation Opportunities:")
            for opp in player_analysis.exploitation_opportunities:
                print(f"      • {opp}")
        print()
    
    # Formation-level insights
    if micro_result.key_vulnerabilities:
        print("⚠️  Key Vulnerabilities:")
        for vuln in micro_result.key_vulnerabilities:
            print(f"  • {vuln}")
        print()
    
    if micro_result.exploitation_strategies:
        print("🎯 Exploitation Strategies:")
        for strategy in micro_result.exploitation_strategies:
            print(f"  • {strategy}")
        print()
    
    if micro_result.specific_recommendations:
        print("💡 Specific Recommendations:")
        for rec in micro_result.specific_recommendations:
            print(f"  • {rec}")
        print()

def generate_micro_report(micro_results, output_dir, team_name):
    """Generate comprehensive micro tactical report."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate HTML report
    html_report = generate_html_micro_report(micro_results, team_name)
    html_file = output_path / f"micro_tactical_report_{timestamp}.html"
    with open(html_file, 'w') as f:
        f.write(html_report)
    
    # Generate JSON report
    json_data = {
        "analysis_timestamp": datetime.now().isoformat(),
        "team_analyzed": team_name,
        "formations_analyzed": len(micro_results),
        "micro_analyses": []
    }
    
    for result in micro_results:
        json_data["micro_analyses"].append({
            "formation_name": result.formation_name,
            "formation_cohesion": result.formation_cohesion,
            "tactical_effectiveness": result.tactical_effectiveness,
            "player_analyses": [
                {
                    "player_id": p.player_id,
                    "position_in_formation": p.position_in_formation,
                    "behavior_type": p.behavior_type.value,
                    "movement_pattern": p.movement_pattern,
                    "speed_consistency": p.speed_consistency,
                    "positioning_accuracy": p.positioning_accuracy,
                    "vulnerability_score": p.vulnerability_score,
                    "vulnerabilities": [v.value for v in p.vulnerabilities],
                    "tactical_notes": p.tactical_notes,
                    "exploitation_opportunities": p.exploitation_opportunities
                }
                for p in result.player_analyses
            ],
            "key_vulnerabilities": result.key_vulnerabilities,
            "exploitation_strategies": result.exploitation_strategies,
            "specific_recommendations": result.specific_recommendations
        })
    
    json_file = output_path / f"micro_tactical_analysis_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"📄 Reports generated:")
    print(f"  • {html_file}")
    print(f"  • {json_file}")

def generate_html_micro_report(micro_results, team_name):
    """Generate HTML report for micro analysis."""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏒 Micro Tactical Analysis Report - {team_name}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        h1 {{
            font-family: 'Russo One', cursive;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }}
        
        h2 {{
            font-family: 'Russo One', cursive;
            color: #FFD700;
            border-bottom: 2px solid #FFD700;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        
        h3 {{
            color: #87CEEB;
            margin-top: 25px;
        }}
        
        .player-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #FFD700;
        }}
        
        .vulnerability {{
            color: #FF6B6B;
            font-weight: bold;
        }}
        
        .opportunity {{
            color: #4ECDC4;
            font-weight: bold;
        }}
        
        .behavior {{
            color: #FFD93D;
            font-weight: bold;
        }}
        
        .metric {{
            background: rgba(255, 255, 255, 0.1);
            padding: 5px 10px;
            border-radius: 5px;
            margin: 5px;
            display: inline-block;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            opacity: 0.7;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏒 Micro Tactical Analysis Report</h1>
        <p style="text-align: center; font-size: 1.2em;">Team: {team_name} | {len(micro_results)} Formations Analyzed</p>
"""
    
    for result in micro_results:
        html += f"""
        <h2>📊 Formation: {result.formation_name}</h2>
        
        <div class="metric">Cohesion: {result.formation_cohesion:.2f}</div>
        <div class="metric">Effectiveness: {result.tactical_effectiveness:.2f}</div>
        
        <h3>👥 Player Analysis</h3>
"""
        
        for player in result.player_analyses:
            html += f"""
        <div class="player-card">
            <h4>Player {player.player_id} - {player.position_in_formation}</h4>
            <p><span class="behavior">Behavior:</span> {player.behavior_type.value}</p>
            <p><span class="behavior">Movement:</span> {player.movement_pattern}</p>
            <p><span class="vulnerability">Vulnerability Score:</span> {player.vulnerability_score:.2f}</p>
            
            {f'<p><span class="vulnerability">Vulnerabilities:</span> {", ".join([v.value for v in player.vulnerabilities])}</p>' if player.vulnerabilities else ''}
            
            {f'<h5>Tactical Notes:</h5><ul>{"".join([f"<li>{note}</li>" for note in player.tactical_notes])}</ul>' if player.tactical_notes else ''}
            
            {f'<h5>Exploitation Opportunities:</h5><ul class="opportunity">{"".join([f"<li>{opp}</li>" for opp in player.exploitation_opportunities])}</ul>' if player.exploitation_opportunities else ''}
        </div>
"""
        
        if result.key_vulnerabilities:
            html += f"""
        <h3>⚠️ Key Vulnerabilities</h3>
        <ul>
            {"".join([f"<li>{vuln}</li>" for vuln in result.key_vulnerabilities])}
        </ul>
"""
        
        if result.exploitation_strategies:
            html += f"""
        <h3>🎯 Exploitation Strategies</h3>
        <ul>
            {"".join([f"<li>{strategy}</li>" for strategy in result.exploitation_strategies])}
        </ul>
"""
        
        if result.specific_recommendations:
            html += f"""
        <h3>💡 Specific Recommendations</h3>
        <ul>
            {"".join([f"<li>{rec}</li>" for rec in result.specific_recommendations])}
        </ul>
"""
    
    html += """
        <div class="footer">
            <p><strong>Enhanced Micro Tactical Analysis System v1.0.0</strong></p>
            <p>Granular player-level tactical insights for advanced hockey analysis</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

if __name__ == "__main__":
    main()
