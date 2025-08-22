# Hockey Tactical Analysis - Quick Usage Guide

## 🚀 **Quick Start (5 seconds)**

```bash
# Analyze your tracking data
python3 src/analyze_formations.py your_data.json --complete
```

---

## 📋 **What You Need**

- **Input**: JSON file from Computer-Vision-for-Hockey project
- **Command**: `python3 src/analyze_formations.py [filename] --complete`
- **Output**: Results saved to `results/` directory

---

## 🎯 **Common Commands**

### **Basic Analysis**
```bash
python3 src/analyze_formations.py data.json
```

### **Complete Analysis (Recommended)**
```bash
python3 src/analyze_formations.py data.json --complete
```

### **Custom Parameters**
```bash
python3 src/analyze_formations.py data.json --min-frames 10 --min-confidence 0.7
```

### **Custom Output Directory**
```bash
python3 src/analyze_formations.py data.json --complete --output my_results/
```

---

## 📊 **What You'll Get**

### **Formations Detected**
- 1-3-1 (Power play)
- 2-1-2 (Neutral zone trap)
- 1-2-2 (Defensive coverage)
- 2-2-1 (Aggressive forechecking)
- 1-4 (Defensive collapse)

### **Analysis Output**
- **JSON**: Complete analysis data
- **CSV**: Formation summary
- **TXT**: Human-readable report
- **Console**: Quick summary

---

## 🔧 **Troubleshooting**

### **"No formations detected"**
```bash
# Try lower thresholds
python3 src/analyze_formations.py data.json --min-frames 3 --min-confidence 0.4
```

### **"Import error"**
```bash
# Make sure you're in the right directory
cd hockey_tactical_analysis
```

### **"File not found"**
```bash
# Check file path and copy data to project directory
cp /path/to/your/tracking_data.json ./
```

---

## 📁 **File Structure**

```
hockey_tactical_analysis/
├── src/analyze_formations.py    # Main command-line tool
├── your_tracking_data.json      # Your data goes here
├── results/                     # Analysis output
└── README.md                    # Full documentation
```

---

## 🎯 **Workflow**

1. **Copy data**: `cp your_data.json ./`
2. **Run analysis**: `python3 src/analyze_formations.py your_data.json --complete`
3. **Check results**: Look in `results/` directory
4. **Review insights**: Read the tactical report

---

## 🏒 **Example Output**

```
TACTICAL ANALYSIS COMPLETE
============================================================

Detected 2 formations:
  • 1-3-1 (confidence: 0.75)
  • 2-1-2 (confidence: 0.75)

Tactical Summary:
  Team deployed 2 distinct formations, with 1-3-1 being most common.

Key Recommendations:
  • Formation Strategy: Focus on 1-3-1 formation
  • Neutral Zone Strategy: Increase neutral zone trap usage
  • Offensive Strategy: Maintain high offensive pressure
```

---

## 💡 **Pro Tips**

- **Use `--complete`** for full analysis
- **Start with default parameters** then adjust
- **Check the results directory** for detailed output
- **Use `--verbose`** for debugging if needed

---

## 🆘 **Need Help?**

- **Check README.md** for full documentation
- **Run `python3 quick_test.py`** to test system
- **Use `--verbose` flag** for detailed error messages
- **Check file format** matches expected structure

---

**Happy analyzing! 🏒📊**
