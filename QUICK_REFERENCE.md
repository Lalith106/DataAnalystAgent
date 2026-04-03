# 📋 Quick Reference Card

## 🚀 Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Open browser to
http://localhost:8501
```

---

## 💬 Usage Examples

### Visualization Requests (Will Generate Graphs)
```
"Show me a bar chart of sales by region"
"Plot the sales trend over months"
"Create a scatter plot of price vs quantity"
"Make a histogram of customer ages"
"Generate a correlation heatmap"
"Display a box plot by category"
```

### Analysis Requests (Will Return Text)
```
"What is the average price?"
"Find the top 5 selling products"
"How many records per category?"
"Calculate the total revenue"
"Show me the missing values"
"What is the sales distribution?"
```

---

## 🎨 Available Visualizations

| Type | Code | Use Case |
|------|------|----------|
| Bar Chart | `plt.bar()` | Compare categories |
| Line Plot | `plt.plot()` | Show trends |
| Scatter Plot | `plt.scatter()` | Show relationships |
| Histogram | `plt.hist()` | Show distribution |
| Box Plot | `sns.boxplot()` | Show quartiles |
| Heatmap | `sns.heatmap()` | Show correlation |
| Pie Chart | `plt.pie()` | Show proportions |

---

## 🔧 Files You Might Need

```
📁 DataAnalystAgent/
├── app.py                    ← Main Streamlit app
├── requirements.txt          ← Python dependencies
├── agent/
│   └── graph.py             ← Agent logic (MODIFIED)
├── executor/
│   └── python_exec.py       ← Code executor (MODIFIED)
├── data/
│   └── dataset_store.py     ← Data storage
└── 📖 Documentation/
    ├── QUICK_START.md       ← Start here
    ├── TECHNICAL_DOCS.md    ← Deep dive
    └── ENHANCEMENT_SUMMARY.md ← Overview
```

---

## 🧠 How It Works

```
Your Question
    ↓
AI: "Do they want a graph?" ← ⭐ NEW
    ↓
    ├─ Yes → Generate matplotlib code ✨
    │
    └─ No → Generate pandas code ✨
    ↓
Execute Code
    ↓
    ├─ Graph → Capture image, encode as PNG
    │
    └─ Analysis → Extract text result
    ↓
Display in Chat ✨
```

---

## ✨ Key Features

```
✅ Automatic Intent Detection
   - No need to say "create visualization"
   - AI understands your intent

✅ Professional Charts
   - Properly labeled
   - Optimized for display
   - Publication quality

✅ Error Handling
   - Retries up to 3 times
   - Graceful degradation
   - Clear error messages

✅ Fast Execution
   - Quick code generation
   - Quick visualization creation
   - Instant display
```

---

## 🐛 Troubleshooting

### Image Not Displaying?
```
Solution: Refresh the page (F5)
Alternative: Ask the same question again
```

### Wrong Chart Type?
```
Solution: Be more specific
Example: "Create a BAR chart of sales"
Instead of: "Plot this data"
```

### Error "Column not found"?
```
Solution: Check your column names
Use: "List all columns" first
Then reference exact names
```

### Code Execution Error?
```
Solution: Automatic - agent retries up to 3 times
Fallback: Try rephrasing your question
```

---

## 📊 Example Workflow

### Step 1: Upload Data
```
Click "Upload your dataset"
Choose CSV, Excel, or Parquet file
See preview and data quality report
```

### Step 2: Ask Question
```
Type: "Show me a bar chart of region"
```

### Step 3: See Result
```
AI detects: Visualization request
AI generates: matplotlib code
Executes: Captures figure
Displays: Chart in chat + explanation
```

### Step 4: Ask Another
```
Type: "What's the average?"
AI detects: Analysis request
Returns: Calculated value + explanation
```

---

## 💡 Pro Tips

```
1️⃣ Be specific about chart type
   ✅ "Create a bar chart"
   ❌ "Show this"

2️⃣ Use actual column names
   ✅ "Sales by region"
   ❌ "Plot data"

3️⃣ Clear chat to start fresh
   Click "Clear Chat" button

4️⃣ Check console for generated code
   Helps understand what agent created

5️⃣ Multiple visualizations work too
   "Show me 2-3 charts of different aspects"
```

---

## 🎯 Common Prompts

### Quick Charts
```
"Bar chart of [column]"
"Line plot of [column] over time"
"Histogram of [column]"
"Scatter plot of [col1] vs [col2]"
```

### Quick Analysis
```
"Average of [column]"
"Total of [column]"
"Count by [category]"
"Top 10 [items]"
```

### Comparisons
```
"Compare [col1] and [col2]"
"Relationship between [x] and [y]"
"Correlation matrix"
"Distribution of [column]"
```

---

## 📈 Understanding Results

### Visualization Output
```
[Chart Image Display]
└─ Brief explanation of what it shows
```

### Analysis Output
```
Calculated Result
└─ Explanation in simple terms
```

---

## 🔐 Security Notes

```
✅ Your data stays local
✅ Code runs in isolated sandbox
✅ No file system access
✅ No external API calls
✅ Only pandas/matplotlib libraries
```

---

## 📞 Getting Help

### For Usage Questions
→ Read QUICK_START.md

### For Technical Details
→ Read TECHNICAL_DOCS.md

### For Changes Made
→ Read CHANGES_CHECKLIST.md

### For Complete Overview
→ Read ENHANCEMENT_SUMMARY.md

---

## ✅ Checklist Before Using

- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Run app: `streamlit run app.py`
- [ ] Upload test CSV file
- [ ] Test visualization: "Show me a bar chart"
- [ ] Test analysis: "What is the average?"
- [ ] Check console for generated code
- [ ] Verify images display correctly

---

## 🎉 You're Ready!

Your Data Analyst Agent now has:
- ✅ Full graph generation capability
- ✅ Automatic intent detection
- ✅ Professional visualization support
- ✅ Smart error handling
- ✅ Natural language understanding

**Start using it right away! 🚀📊**

---

## 📝 Quick Reference

```
Feature              Before    After
──────────────────────────────────────
Data Analysis        ✅        ✅
Visualizations       ❌        ✅ ⭐
Auto Detection       ❌        ✅ ⭐
Chart Types          0         8+
Error Handling       Basic     Enhanced
Documentation        Basic     Comprehensive
```

---

## 🚀 Next Steps

1. **Install:** `pip install -r requirements.txt`
2. **Run:** `streamlit run app.py`
3. **Test:** Upload data and ask questions
4. **Enjoy:** Get instant graphs and analysis! 🎉

---

**Questions? Check the documentation files!**

**Ready? Start the app now! 🚀**

