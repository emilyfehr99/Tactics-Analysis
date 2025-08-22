# Quick Start Guide - Hockey Tactical Analysis

Get up and running with hockey tactical analysis in minutes!

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd hockey_tactical_analysis
pip install -r requirements.txt
```

### 2. Test the System

```bash
python test_system.py
```

This will create sample data and test all components. You should see "ALL TESTS PASSED!" if everything is working.

### 3. Analyze Your Data

#### Option A: Command Line (Recommended for beginners)

```bash
# Basic formation analysis
python src/analyze_formations.py path/to/your/tracking_data.json

# Complete tactical analysis
python src/analyze_formations.py path/to/your/tracking_data.json --complete

# Custom parameters
python src/analyze_formations.py path/to/your/tracking_data.json --min-frames 10 --min-confidence 0.7
```

#### Option B: Python Script

```python
from src.tactical_analyzer import TacticalAnalyzer

# Initialize analyzer
analyzer = TacticalAnalyzer('path/to/your/tracking_data.json')

# Run complete analysis
results = analyzer.run_complete_analysis()

# Or run specific analyses
formations = analyzer.analyze_formations()
zones = analyzer.analyze_zones()
insights = analyzer.generate_tactical_insights()
```

## 📊 What You'll Get

### Formation Analysis
- **1-3-1**: Power play formations
- **2-1-2**: Neutral zone trap
- **1-2-2**: Defensive coverage
- **2-2-1**: Aggressive forechecking
- **1-4**: Defensive collapse

### Zone Analysis
- Player distribution across rink zones
- Neutral zone trap detection
- Forechecking pressure analysis
- Defensive coverage patterns

### Tactical Insights
- Formation effectiveness ratings
- Strategic recommendations
- Transition pattern analysis
- Pressure consistency metrics

## 📁 Input Data Format

### JSON Format (from Computer-Vision-for-Hockey)
```json
{
  "frames": [
    {
      "frame_id": 0,
      "timestamp": 0.0,
      "players": [
        {
          "player_id": "player_0",
          "rink_position": {
            "x": 382.86,
            "y": 200.60
          },
          "orientation": 0.0
        }
      ]
    }
  ]
}
```

### CSV Format
```csv
frame_id,timestamp,player_id,x,y,orientation
0,0.0,player_0,382.86,200.60,0.0
```

## 🔧 Customization

### Adjust Formation Detection
```python
# More strict formation detection
formations = analyzer.analyze_formations(
    min_frames=10,        # Require 10+ frames
    min_confidence=0.8    # Require 80%+ confidence
)
```

### Custom Rink Dimensions
```python
analyzer = TacticalAnalyzer(
    input_path='data.json',
    rink_dimensions=(1200, 500)  # Custom rink size
)
```

## 📈 Example Output

```
TACTICAL ANALYSIS COMPLETE
============================================================

Detected 5 formations:
  • 1-3-1 (confidence: 0.85)
  • 2-1-2 (confidence: 0.78)
  • 1-2-2 (confidence: 0.82)

Tactical Summary:
  Team deployed 5 distinct formations, with 1-3-1 being most common. 
  Neutral zone trap used 15.2% of the time, indicating moderate defensive strategy.

Key Recommendations:
  • Formation Strategy: Focus on 1-3-1 formation (effectiveness: high). 
    Review 2-1-2 strategy for improvement.
  • Offensive Strategy: Maintain high offensive pressure - it's working effectively.
```

## 🎯 Common Use Cases

### 1. Post-Game Analysis
```bash
python src/analyze_formations.py game_data.json --complete
```

### 2. Formation Comparison
```bash
# Analyze specific formations
python src/analyze_formations.py data.json --formations "1-3-1,2-1-2"
```

### 3. Batch Analysis
```bash
# Analyze multiple games
for file in data/*.json; do
    python src/analyze_formations.py "$file" --complete --output "results/$(basename $file .json)"
done
```

## 🚨 Troubleshooting

### "No formations detected"
- Try reducing `--min-frames` (default: 5)
- Try reducing `--min-confidence` (default: 0.6)
- Check that your data has player positions in `rink_position.x` and `rink_position.y`

### "Import error"
- Make sure you're in the `hockey_tactical_analysis` directory
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### "File format error"
- JSON files should have `frames` array with player data
- CSV files should have columns: `frame_id`, `player_id`, `x`, `y`
- Use `--verbose` flag for detailed error messages

## 📚 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Check examples/** directory for more code examples
3. **Customize formations** in the source code for your specific needs
4. **Integrate with your existing** hockey analysis pipeline

## 🆘 Need Help?

- Check the test output for system status
- Run with `--verbose` flag for detailed logging
- Review the example scripts in `examples/` directory
- Check that your tracking data format matches the expected structure

---

**Happy analyzing! 🏒📊**
