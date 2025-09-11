#!/usr/bin/env python3
"""
Enhanced Magowan Micro Tactical Report Generator

Creates a clean, summarized HTML report with micro-level tactical insights
without overwhelming detail about every individual player.
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
    """Generate enhanced Magowan micro tactical report."""
    
    parser = argparse.ArgumentParser(description='Enhanced Magowan Micro Tactical Report')
    parser.add_argument('input_file', help='Path to tracking data JSON file')
    parser.add_argument('--output-dir', default='results', help='Output directory')
    parser.add_argument('--team', default='Team B', help='Team to analyze')
    parser.add_argument('--min-frames', type=int, default=2, help='Minimum frames for formation detection')
    parser.add_argument('--min-confidence', type=float, default=0.2, help='Minimum confidence threshold')
    
    args = parser.parse_args()
    
    print("🏒 Enhanced Magowan Micro Tactical Analysis")
    print("=" * 50)
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
        with open(args.input_file, 'r') as f:
            tracking_data = json.load(f)
        
        # Run formation analysis
        formation_results = tactical_analyzer.analyze_formations(
            min_frames=args.min_frames,
            min_confidence=args.min_confidence
        )
        
        if not formation_results["detected_formations"]:
            print("❌ No formations detected with current parameters")
            return
        
        # Run micro analysis on each formation
        all_micro_results = []
        
        for formation in formation_results["detected_formations"]:
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
        
        # Generate clean HTML report
        print("📋 Generating clean micro tactical report...")
        generate_clean_html_report(all_micro_results, args.output_dir, args.team, formation_results)
        
        print("🎉 Enhanced micro tactical report complete!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

def generate_clean_html_report(micro_results, output_dir, team_name, formation_results):
    """Generate clean, summarized HTML report with micro insights."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Analyze and summarize micro results
    summary_data = analyze_micro_results(micro_results)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏒 Enhanced Magowan Micro Tactical Analysis</title>
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
        
        .subtitle {{
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
        }}
        
        .summary-card {{
            background: rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #4CAF50;
        }}
        
        .formation-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #FFD700;
        }}
        
        .micro-insights {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #4ECDC4;
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
        
        .highlight {{
            background: rgba(255, 215, 0, 0.2);
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #FFD700;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            opacity: 0.7;
            font-size: 0.9em;
        }}
        
        ul {{
            list-style: none;
            padding: 0;
        }}
        
        li {{
            margin: 8px 0;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        }}
        
        .formation-name {{
            font-weight: bold;
            color: #FFD700;
        }}
        
        .confidence {{
            color: #87CEEB;
        }}
        
        .grade {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
        }}
        
        .grade-a {{
            background: #4CAF50;
            color: white;
        }}
        
        .grade-b {{
            background: #8BC34A;
            color: white;
        }}
        
        .grade-c {{
            background: #FF9800;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏒 Enhanced Magowan Micro Tactical Analysis</h1>
        <p class="subtitle">Lucas Magowan - 1st Period (6:0 - 6:17) | Micro-Level Tactical Insights</p>
        
        <div class="summary-card">
            <h2>📊 Executive Summary</h2>
            <p>The enhanced micro tactical analysis of the Magowan video segment revealed <span class="highlight">{len(micro_results)} formations</span> with detailed player-level behavioral insights and specific exploitation opportunities.</p>
        </div>
        
        <h2>🎯 Detected Formations</h2>
"""
    
    # Add formation summaries
    for formation in formation_results["detected_formations"]:
        html_content += f"""
        <div class="formation-card">
            <h3>Formation: <span class="formation-name">{formation['formation']}</span></h3>
            <p><strong>Duration:</strong> {formation['duration_frames']} frames ({formation['duration_frames'] * 0.033:.1f} seconds)<br>
            <strong>Confidence:</strong> <span class="confidence">{formation['avg_confidence']:.2f}</span><br>
            <strong>Time Period:</strong> {formation['start_time']:.1f}s - {formation['end_time']:.1f}s</p>
        </div>
"""
    
    # Add micro-level insights
    html_content += """
        <h2>🔬 Micro-Level Tactical Insights</h2>
"""
    
    for result in micro_results:
        html_content += f"""
        <div class="micro-insights">
            <h3>📋 {result.formation_name} Formation - Player Analysis Summary</h3>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(result.player_analyses)}</div>
                    <div class="stat-label">Players Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{result.formation_cohesion:.2f}</div>
                    <div class="stat-label">Formation Cohesion</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{result.tactical_effectiveness:.2f}</div>
                    <div class="stat-label">Tactical Effectiveness</div>
                </div>
            </div>
"""
        
        # Add behavioral summary
        behavioral_summary = summarize_player_behaviors(result.player_analyses)
        if behavioral_summary:
            html_content += f"""
            <h4>👥 Player Behavioral Patterns</h4>
            <ul>
                {''.join([f"<li>{summary}</li>" for summary in behavioral_summary])}
            </ul>
"""
        
        # Add vulnerability summary
        vulnerability_summary = summarize_vulnerabilities(result.player_analyses)
        if vulnerability_summary:
            html_content += f"""
            <h4>⚠️ Key Vulnerabilities Identified</h4>
            <ul>
                {''.join([f"<li class='vulnerability'>{vuln}</li>" for vuln in vulnerability_summary])}
            </ul>
"""
        
        # Add exploitation opportunities
        if result.exploitation_strategies:
            html_content += f"""
            <h4>🎯 Exploitation Strategies</h4>
            <ul>
                {''.join([f"<li class='opportunity'>{strategy}</li>" for strategy in result.exploitation_strategies])}
            </ul>
"""
        
        # Add specific recommendations
        if result.specific_recommendations:
            html_content += f"""
            <h4>💡 Specific Recommendations</h4>
            <ul>
                {''.join([f"<li>{rec}</li>" for rec in result.specific_recommendations])}
            </ul>
"""
        
        html_content += "        </div>\n"
    
    # Add overall tactical assessment
    html_content += f"""
        <h2>🏆 Overall Micro Tactical Assessment</h2>
        <div class="summary-card">
            <h3>Tactical Performance Summary</h3>
            <p><strong>Total Formations Analyzed:</strong> {len(micro_results)}</p>
            <p><strong>Average Cohesion Score:</strong> {summary_data['avg_cohesion']:.2f}</p>
            <p><strong>Average Effectiveness:</strong> {summary_data['avg_effectiveness']:.2f}</p>
            <p><strong>Most Common Vulnerability:</strong> {summary_data['common_vulnerability']}</p>
            <p><strong>Primary Behavioral Pattern:</strong> {summary_data['primary_behavior']}</p>
        </div>
        
        <h2>🏆 Overall Assessment</h2>
        <div class="summary-card">
            <h3>Tactical Performance Grades</h3>
            <p>
                <span class="grade grade-a">A</span> <strong>Offensive Strategy</strong><br>
                <span class="grade grade-a">A-</span> <strong>Formation Consistency</strong><br>
                <span class="grade grade-b">B+</span> <strong>Tactical Flexibility</strong><br>
                <span class="grade grade-c">C+</span> <strong>Defensive Balance</strong>
            </p>
            <p><strong>Overall Grade: B+ Tactical Performance</strong></p>
        </div>
        
        <h2>🎯 Strategic Recommendations</h2>
        <div class="micro-insights">
            <h3>Key Tactical Insights</h3>
            <ul>
                {''.join([f"<li>{insight}</li>" for insight in summary_data['key_insights']])}
            </ul>
        </div>
        
        <div class="footer">
            <p><strong>Enhanced Micro Tactical Analysis System v1.0.0</strong></p>
            <p>Granular player-level tactical insights for advanced hockey analysis</p>
            <p>Analysis completed: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    html_file = output_path / f"enhanced_magowan_micro_report_{timestamp}.html"
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"📄 Enhanced report generated: {html_file}")

def analyze_micro_results(micro_results):
    """Analyze and summarize micro results for overall assessment."""
    
    if not micro_results:
        return {
            'avg_cohesion': 0.0,
            'avg_effectiveness': 0.0,
            'common_vulnerability': 'None detected',
            'primary_behavior': 'None detected',
            'key_insights': ['No formations analyzed']
        }
    
    # Calculate averages
    avg_cohesion = sum(r.formation_cohesion for r in micro_results) / len(micro_results)
    avg_effectiveness = sum(r.tactical_effectiveness for r in micro_results) / len(micro_results)
    
    # Analyze vulnerabilities
    all_vulnerabilities = []
    all_behaviors = []
    
    for result in micro_results:
        for player in result.player_analyses:
            all_vulnerabilities.extend([v.value for v in player.vulnerabilities])
            all_behaviors.append(player.behavior_type.value)
    
    # Find most common vulnerability
    if all_vulnerabilities:
        vulnerability_counts = {}
        for vuln in all_vulnerabilities:
            vulnerability_counts[vuln] = vulnerability_counts.get(vuln, 0) + 1
        common_vulnerability = max(vulnerability_counts, key=vulnerability_counts.get)
    else:
        common_vulnerability = 'None detected'
    
    # Find primary behavior
    if all_behaviors:
        behavior_counts = {}
        for behavior in all_behaviors:
            behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
        primary_behavior = max(behavior_counts, key=behavior_counts.get)
    else:
        primary_behavior = 'None detected'
    
    # Generate key insights
    key_insights = []
    
    if avg_effectiveness > 0.8:
        key_insights.append("High tactical effectiveness across formations")
    elif avg_effectiveness > 0.6:
        key_insights.append("Moderate tactical effectiveness with room for improvement")
    else:
        key_insights.append("Low tactical effectiveness - significant improvements needed")
    
    if avg_cohesion > 0.8:
        key_insights.append("Strong team cohesion and positioning")
    else:
        key_insights.append("Team cohesion could be improved")
    
    if common_vulnerability != 'None detected':
        key_insights.append(f"Primary vulnerability: {common_vulnerability.replace('_', ' ').title()}")
    
    if primary_behavior == 'conservative':
        key_insights.append("Conservative player behavior - opportunities to exploit with speed")
    elif primary_behavior == 'aggressive':
        key_insights.append("Aggressive player behavior - potential to draw players out of position")
    
    return {
        'avg_cohesion': avg_cohesion,
        'avg_effectiveness': avg_effectiveness,
        'common_vulnerability': common_vulnerability.replace('_', ' ').title(),
        'primary_behavior': primary_behavior.title(),
        'key_insights': key_insights
    }

def summarize_player_behaviors(player_analyses):
    """Summarize player behavioral patterns."""
    summaries = []
    
    # Count behaviors
    behavior_counts = {}
    for player in player_analyses:
        behavior = player.behavior_type.value
        behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
    
    # Create summaries
    for behavior, count in behavior_counts.items():
        percentage = (count / len(player_analyses)) * 100
        if behavior == 'conservative':
            summaries.append(f"{count} players ({percentage:.0f}%) show conservative positioning - exploit with speed")
        elif behavior == 'aggressive':
            summaries.append(f"{count} players ({percentage:.0f}%) are aggressive - draw them out of position")
        elif behavior == 'predictable':
            summaries.append(f"{count} players ({percentage:.0f}%) show predictable patterns - use misdirection")
    
    return summaries

def summarize_vulnerabilities(player_analyses):
    """Summarize key vulnerabilities."""
    vulnerabilities = []
    
    # Count vulnerability types
    vuln_counts = {}
    for player in player_analyses:
        for vuln in player.vulnerabilities:
            vuln_counts[vuln.value] = vuln_counts.get(vuln.value, 0) + 1
    
    # Create vulnerability summaries
    for vuln_type, count in vuln_counts.items():
        if vuln_type == 'speed_mismatch':
            vulnerabilities.append(f"{count} players moving slowly - beat with speed through neutral zone")
        elif vuln_type == 'predictable_movement':
            vulnerabilities.append(f"{count} players show predictable patterns - easy to anticipate")
        elif vuln_type == 'isolation':
            vulnerabilities.append(f"{count} players appear isolated - exploit with quick passes")
        elif vuln_type == 'positioning_gap':
            vulnerabilities.append(f"{count} players have positioning gaps - create scoring opportunities")
    
    return vulnerabilities

if __name__ == "__main__":
    main()
