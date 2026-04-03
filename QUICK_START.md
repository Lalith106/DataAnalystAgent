# 🚀 Quick Start Guide - Graph Generation

## What's New? 📊

Your Data Analyst Agent now generates **graphs and visualizations** using matplotlib & seaborn!

---

## Installation

1. **Install new dependency:**
   ```bash
   pip install seaborn==0.13.0
   ```
   
   Or update all:
   ```bash
   pip install -r requirements.txt
   ```

2. **No code changes needed** - everything is pre-configured!

---

## Usage Examples

### 🎨 Example 1: Create a Bar Chart
**You ask:**
```
"Show me a bar chart of sales by region"
```

**Agent will:**
1. ✅ Detect this is a visualization request
2. ✅ Generate matplotlib code with plt.bar()
3. ✅ Execute the code
4. ✅ Display the chart in the chat
5. ✅ Provide an explanation

**Expected Output:**
A professional bar chart with labels, title, and legend

---

### 📈 Example 2: Line Plot Over Time
**You ask:**
```
"Plot the sales trend over months"
```

**Agent will:**
- Generate plt.plot() code
- Display a line chart showing trends
- Explain the pattern

---

### 📊 Example 3: Distribution Analysis
**You ask:**
```
"Show me a histogram of customer ages"
```

**Agent will:**
- Generate sns.histplot() code
- Display distribution visualization
- Explain the distribution

---

### 📉 Example 4: Text Analysis (Still Works!)
**You ask:**
```
"What is the total revenue?"
```

**Agent will:**
- Generate pandas code (not visualization)
- Return calculated result as text
- Explain the finding

---

## How It Works

```
Your Question
    ↓
AI detects: "Is this a graph request?"
    ↓
YES → Generate matplotlib/seaborn code
NO  → Generate pandas code
    ↓
Execute code
    ↓
YES → Capture image as PNG → Display with st.image()
NO  → Return text result
    ↓
Explain result
```

---

## Supported Chart Types

The agent can create:

| Type | Code | Usage |
|------|------|-------|
| Bar Chart | `plt.bar()`, `sns.barplot()` | Compare categories |
| Line Plot | `plt.plot()`, `sns.lineplot()` | Show trends |
| Scatter Plot | `plt.scatter()`, `sns.scatterplot()` | Show relationships |
| Histogram | `plt.hist()`, `sns.histplot()` | Show distributions |
| Box Plot | `sns.boxplot()` | Show quartiles |
| Heatmap | `sns.heatmap()` | Show correlations |
| Pie Chart | `plt.pie()` | Show proportions |
| Violin Plot | `sns.violinplot()` | Show distributions |

---

## Prompt Examples

### ✅ VISUALIZATION PROMPTS (Try These!)
```
"Create a bar chart of product sales"
"Plot the trend over time"
"Show me a scatter plot of price vs quantity"
"Make a histogram of customer ages"
"Generate a correlation heatmap"
"Display a box plot by category"
"Show pie chart of market share"
```

### ✅ ANALYSIS PROMPTS (Still Work!)
```
"What's the average price?"
"Find the top 5 products"
"How many records per category?"
"Calculate total revenue"
"Show me missing values"
```

---

## Key Points

### ✨ Automatic Detection
- You DON'T need to say "create a visualization"
- The AI automatically detects if you want a graph
- Natural language understood

### 🎨 High Quality
- Professional matplotlib styling
- Proper labels, titles, legends
- Optimized for web display (100 DPI PNG)

### ⚡ Fast & Efficient
- Figures automatically closed (no memory leaks)
- Base64 encoding for efficient transfer
- Cached in chat history

### 🛡️ Safe
- Code runs in isolated namespace
- Limited to data analysis libraries only
- No file system or network access

---

## Troubleshooting

### Issue: Image not displaying
- **Solution:** Try refreshing the page (F5)
- **Alternative:** Ask the same question again

### Issue: "Error executing code"
- **Cause:** Invalid column name or unsupported operation
- **Solution:** The agent will retry up to 3 times automatically
- **Fallback:** Ask differently or ask for text analysis instead

### Issue: Wrong chart type generated
- **Solution:** Be more specific: "Use a bar chart" instead of "Plot this"
- **Example:** "Create a bar chart showing top 10 items"

---

## File Changes Summary

| File | Change | Details |
|------|--------|---------|
| `executor/python_exec.py` | Rewritten | Now handles matplotlib execution |
| `agent/graph.py` | Enhanced | Added detect_visualization node |
| `app.py` | Updated | Display images in chat |
| `requirements.txt` | Added | seaborn==0.13.0 |

---

## Architecture Changes

### Old Flow:
```
Question → Generate Pandas Code → Execute → Return Text
```

### New Flow:
```
Question → Detect Type → Generate Code (pandas or matplotlib)
         → Execute → Capture Result/Image → Return Text/Base64 PNG
```

---

## Testing

Try this workflow:

1. **Start app:**
   ```bash
   streamlit run app.py
   ```

2. **Upload sample data** (CSV with 3+ columns)

3. **Test visualization:**
   ```
   "Show me a bar chart of [column_name]"
   ```

4. **Test analysis:**
   ```
   "What is the average [numeric_column]?"
   ```

5. **Test error recovery:**
   ```
   "Plot [invalid_column]"  → Should retry and ask for clarification
   ```

---

## Next Steps

Your agent now supports:
- ✅ Data analysis with pandas
- ✅ Visualizations with matplotlib/seaborn
- ✅ Intelligent detection of user intent
- ✅ Professional chart generation
- ✅ Error handling & recovery

**Start using it right away!** No additional configuration needed.

---

## Support

If you encounter issues:
1. Check the console output for error messages
2. Review the code being generated (printed to console)
3. Try rephrasing your question
4. Verify your data has the columns you're referencing

Enjoy your enhanced AI Data Analyst! 🎉📊

