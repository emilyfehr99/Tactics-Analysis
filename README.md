# 🏒 Hockey Tactical Analysis System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/emilyfehr99/Tactics-Analysis)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](https://github.com/emilyfehr99/Tactics-Analysis)

> **Automatically analyze hockey formations, tactics, and strategic patterns from player tracking data**

A comprehensive Python system that takes player tracking data from your Computer-Vision-for-Hockey project and analyzes hockey systems like **1-3-1**, **2-1-2**, **1-2-2**, and more to provide tactical insights and strategic recommendations.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/emilyfehr99/Tactics-Analysis.git
cd Tactics-Analysis

# Install dependencies
pip install -r requirements.txt

# Analyze your tracking data (one command!)
python3 analyze_any_data.py your_tracking_data.json
```

## 📊 What It Analyzes

### **Hockey Formations Detected**
- **1-3-1** - Power play and offensive zone formations
- **2-1-2** - Neutral zone trap and defensive formations  
- **1-2-2** - Standard defensive zone coverage
- **2-2-1** - Aggressive forechecking formations
- **1-4** - Defensive zone collapse
- **0-5** - Full defensive collapse

### **Analysis Types**
- **Formation Recognition** - When each formation is used and for how long
- **Zone Analysis** - Player distribution across offensive/defensive/neutral zones
- **Tactical Transitions** - How teams switch between formations
- **Pressure Patterns** - Offensive and defensive pressure analysis
- **Strategic Insights** - Automated recommendations for improvement

## 🎯 Key Features

- **🔄 Automatic Detection** - No manual input required
- **⚡ Fast Analysis** - Processes data in seconds
- **📈 Comprehensive Insights** - Tactical, strategic, and performance analysis
- **📁 Multiple Outputs** - JSON, CSV, TXT for different use cases
- **🔧 Easy Customization** - Adjustable parameters and thresholds
- **📊 Real Data Tested** - Verified with actual hockey tracking data

## 📁 Project Structure

```
Tactics-Analysis/
├── src/                          # Core analysis modules
│   ├── formation_detector.py     # Formation recognition engine
│   ├── tactical_analyzer.py      # Main analysis orchestrator
│   ├── zone_analyzer.py          # Zone-based analysis
│   └── analyze_formations.py     # Command-line interface
├── examples/                      # Usage examples
├── analyze_any_data.py           # One-click analysis tool
├── quick_test.py                 # System test script
├── requirements.txt               # Dependencies
└── README.md                      # Full documentation
```

## 🏆 Real Results

**Tested with 100 frames of real hockey tracking data:**

```
TACTICAL ANALYSIS COMPLETE
============================================================

Detected 2 formations:
  • 1-3-1 (confidence: 0.75) - 87 frames
  • 2-1-2 (confidence: 0.75) - 7 frames

Tactical Summary:
  Team deployed 2 distinct formations, with 1-3-1 being most common.
  Neutral zone trap used 2.0% of the time, indicating occasional defensive strategy.

Key Recommendations:
  • Formation Strategy: Focus on 1-3-1 formation
  • Neutral Zone Strategy: Increase neutral zone trap usage
  • Offensive Strategy: Maintain high offensive pressure
```

## 🚀 Usage Options

### **Option 1: One-Click Analysis (Recommended)**
```bash
python3 analyze_any_data.py your_tracking_data.json
```

### **Option 2: Command Line Interface**
```bash
python3 src/analyze_formations.py your_data.json --complete
```

### **Option 3: Programmatic Use**
```python
from src.tactical_analyzer import TacticalAnalyzer

analyzer = TacticalAnalyzer('your_data.json')
results = analyzer.run_complete_analysis()
```

## 📋 Requirements

- **Python**: 3.8+
- **Dependencies**: pandas, numpy, scipy, matplotlib, plotly, scikit-learn
- **Input**: JSON tracking data from Computer-Vision-for-Hockey project
- **Output**: Tactical analysis reports and insights

## 🔧 Installation

```bash
# Clone repository
git clone https://github.com/emilyfehr99/Tactics-Analysis.git
cd Tactics-Analysis

# Install dependencies
pip install -r requirements.txt

# Test the system
python3 quick_test.py
```

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get up and running in 5 minutes
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Common commands and troubleshooting
- **[SYSTEM_STATUS.md](SYSTEM_STATUS.md)** - System status and testing results
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview

## 🎯 Use Cases

### **Coaching and Analysis**
- **Post-game Review** - Analyze tactical decisions and effectiveness
- **Opponent Scouting** - Study other teams' formations and patterns
- **Performance Tracking** - Monitor formation effectiveness over time
- **Strategy Development** - Test new tactical approaches

### **Research and Development**
- **Tactical Evolution** - Track how hockey strategies change
- **Formation Effectiveness** - Study which formations work best
- **Player Positioning** - Analyze individual and team positioning
- **Game Theory** - Study strategic decision-making in hockey

## 🧪 Testing

The system has been thoroughly tested with real hockey tracking data:

```bash
# Run system tests
python3 quick_test.py

# Test with your data
python3 analyze_any_data.py your_data.json
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

1. **New Formation Types** - Add support for additional hockey systems
2. **Advanced Analytics** - Implement more sophisticated analysis algorithms
3. **Visualization Enhancements** - Create more interactive charts
4. **Performance Optimization** - Improve analysis speed for large datasets

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of the Computer-Vision-for-Hockey player tracking system
- Inspired by hockey analytics and tactical analysis research
- Uses open-source libraries for data analysis and visualization

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/emilyfehr99/Tactics-Analysis/issues)
- **Documentation**: Check the docs folder for detailed guides
- **Examples**: See the examples/ directory for usage examples

---

## 🎉 Ready to Analyze!

**The Hockey Tactical Analysis System is production-ready and tested with real data.**

Start analyzing your hockey tactics today:

```bash
git clone https://github.com/emilyfehr99/Tactics-Analysis.git
cd Tactics-Analysis
python3 analyze_any_data.py your_tracking_data.json
```

**Happy analyzing! 🏒📊**

---

*⭐ Star this repository if you find it useful!*
*🔄 Fork it to customize for your needs!*
*💬 Open issues for questions or improvements!*
