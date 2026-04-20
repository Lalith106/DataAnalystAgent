from typing import TypedDict
from langgraph.graph import END, StateGraph
#from app import is_visualization
from data.dataset_store import  get_df
from executor.python_exec import execute_python
from openai import OpenAI
import os
import json


DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

client = OpenAI(
    api_key= DATABRICKS_TOKEN,
    base_url="https://2435710707330314.ai-gateway.cloud.databricks.com/mlflow/v1"
)  # Initialize the OpenAI client


def _format_dataset_profile(summary: dict) -> str:
    lines = [
        f"Rows: {summary.get('rows', 0):,}",
        f"Columns: {summary.get('columns', 0):,}",
        f"Total cells: {summary.get('total_cells', 0):,}",
        f"Missing cells: {summary.get('missing_cells', 0):,} ({summary.get('missing_pct', 0)}%)",
        f"Duplicate rows: {summary.get('duplicate_rows', 0):,}",
        f"Numeric columns: {', '.join(summary.get('numeric_cols', [])) or 'None'}",
        f"Categorical columns: {', '.join(summary.get('categorical_cols', [])) or 'None'}",
        f"Datetime columns: {', '.join(summary.get('datetime_cols', [])) or 'None'}",
    ]

    numeric_stats = summary.get('numeric_stats', [])[:8]
    if numeric_stats:
        lines.append("Numeric highlights:")
        for item in numeric_stats:
            lines.append(
                f"- {item.get('column')}: min={item.get('min')}, max={item.get('max')}, "
                f"mean={item.get('mean')}, median={item.get('median')}, nulls={item.get('nulls')}"
            )

    cat_stats = summary.get('cat_stats', [])[:8]
    if cat_stats:
        lines.append("Categorical highlights:")
        for item in cat_stats:
            lines.append(
                f"- {item.get('column')}: unique={item.get('unique')}, top='{item.get('top')}', "
                f"top_freq={item.get('top_freq')}, nulls={item.get('nulls')}"
            )

    date_ranges = summary.get('date_ranges', [])
    if date_ranges:
        lines.append("Date ranges:")
        for item in date_ranges:
            lines.append(f"- {item.get('column')}: {item.get('min')} to {item.get('max')}")

    return "\n".join(lines)


def generate_dataset_summary(summary: dict) -> str:
    """
    Generate a concise natural-language summary from a compact dataset profile.
    """
    profile_text = _format_dataset_profile(summary)

    prompt = f"""
    You are an expert data analyst.

    Write an overall dataset summary from the dataset profile below.
    Focus on the structure, likely use case, data quality, and any broad patterns.

    Rules:
    - Keep it concise: 3 to 5 sentences maximum.
    - Write a generic overview of the whole dataset, not row-level commentary.
    - Mention the dominant data types, missingness, duplicates, and whether the dataset looks tidy or needs cleanup.
    - If the business context is unclear, say it appears to be a dataset related to a general business/operational process.
    - Do not invent facts beyond the profile.
    - Do not mention that you are an AI model.
    - Do not use markdown headings or bullet points.

    Dataset profile:
    {profile_text}
    """

    response = client.chat.completions.create(
        model="databricks-llama-4-maverick",
        messages=[
            {"role": "system", "content": "You are a concise data analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()
    return content


class AgentState(TypedDict):
    question: str
    code : str
    result: str
    retries: int
    original_language: str
    is_visualization: bool
    visualization_data: str
    visualization_summary: str

#NODE -1
def normalize_query(state: AgentState) -> AgentState:
    question = state["question"]

    prompt = f"""
    You are a multilingual data analyst assistant.

    Your job:
    1. Detect the language of the user query
    2. Convert it into a clear English data analysis question
    3. Keep the meaning EXACT

    Return JSON ONLY:
    {{
        "language": "<detected language>",
        "english_query": "<clean English version>"
    }}

    User Query: 
    {question}
    """

    response = client.chat.completions.create(
        model="databricks-llama-4-maverick",
        messages=[
            {"role": "system", "content": "You are a multilingual assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
        state["question"] = data["english_query"]   # overwrite question
        state["original_language"] = data["language"]
    except:
        state["original_language"] = "English"

    return state

#NODE -1.5: Detect if visualization is needed
def detect_visualization(state: AgentState) -> AgentState:
    question = state["question"]
    prompt = f"""You are a data analysis assistant.
    
    Determine if the user is asking for a visualization/graph/chart or just data analysis.
    
    Return JSON ONLY:
    {{
        "needs_visualization": true/false,
        "reason": "<brief explanation>"
    }}

    Examples:
    - "plot sales by month" -> needs_visualization: true
    - "show me a bar chart of countries" -> needs_visualization: true
    - "what is the total sales?" -> needs_visualization: false
    - "summarize the data" -> needs_visualization: false
    - "do an eda data analysis on the dataset" -> needs_visualization: false
    - "create a scatter plot" -> needs_visualization: true

    User Query: {question}
    """

    response = client.chat.completions.create(
        model="databricks-llama-4-maverick",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    if content.startswith("```"):
        content = content.split("\n", 1)[1]  # remove first line (```json)
        content = content.rsplit("```", 1)[0]  # remove closing ```
        content = content.strip()
    try:
        data = json.loads(content)
        state["is_visualization"] = data.get("needs_visualization", False)
    except:
        state["is_visualization"] = False

    return state

#Node-2: Generate Code
def generate_code(state: AgentState) -> AgentState:
    question = state['question']
    df = get_df()
    is_visualization = state.get("is_visualization", False)
    previous_error = state.get("result", "")

    if is_visualization:
        prompt = f"""You are an AI data analyst. You are given a question and a dataset.
    Your task is to write Python code using matplotlib and seaborn to create a visualization.
    
    Dataset Information
    -------------------
    Total rows: {len(df)}
    Columns: {list(df.columns)}

    Column Types:
    {df.dtypes}

    Sample Data:
    {df.sample(5).to_string()}

    Question/Visualization Request:
    {question}

    Previous error (if any):
    {previous_error}

    Rules:
    - Output ONLY executable Python code
    - Do NOT include markdown
    - Do NOT include explanation
    - Do NOT include emojis
    - Start directly with Python code
    - Do NOT import any libraries (matplotlib, seaborn, pandas are available)
    - Do NOT create API clients
    - Do NOT use Anthropic or OpenAI
    - Do NOT load files
    - The dataframe `df` is already available
    - Use plt (matplotlib.pyplot) and sns (seaborn) for visualizations
    - Use plt.show() or just create the figure (it will be captured)
    - Set figure size if needed: plt.figure(figsize=(12, 6))
    - Add proper labels, titles, and legends
    - Make the chart presentation-ready and readable
    - Prefer a clean, modern style such as `sns.set_theme(style="whitegrid", context="talk")`
    - Use high-contrast axis labels, tick labels, and titles so they are clearly visible
    - Avoid low-contrast text colors like light gray on dark backgrounds unless they remain readable
    - Use a colorblind-friendly palette and tasteful spacing
    - Increase label font sizes when needed for clarity
    - Call plt.tight_layout() before showing
"""
    else:
        prompt = f"""You are an AI data analyst. You are given a question and a dataset. 
    Your task is to write Python code using pandas to answer the question based on the dataset.

    Dataset Information
    -------------------
    Total rows: {len(df)}
    Columns: {list(df.columns)}

    Column Types:
    {df.dtypes}

    Sample Data:
    {df.sample(5).to_string()}

    Question:
    {question}

    Previous error (if any):
    {previous_error}

    Do NOT import any libraries.
    Use only pandas operations.
    Write ONLY executable Python code using pandas.
    Rules:
    - Output ONLY executable Python code
    - Do NOT include markdown
    - Do NOT include explanation
    - Do NOT include emojis
    - Start directly with Python code
    - Do NOT import any libraries

    - Do NOT create API clients
    - Do NOT use Anthropic or OpenAI
    - Do NOT load files
    - The dataframe `df` is already available

    - Store the final answer in variable `result`
"""
    
    response = client.chat.completions.create(
    model="databricks-llama-4-maverick",
    messages=[
            {"role": "system", "content": "You are a helpful data analyst that writes code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    state['code'] = response.choices[0].message.content
    return state

#Node-3: Execute Code
def execute_code(state: AgentState) -> AgentState:
    code = state['code']
    is_visualization = state.get("is_visualization", False)
    execution_result = execute_python(code, is_visualization)
    
    # Store the execution result
    state['result'] = execution_result['content']
    
    # Store visualization data if it's a visualization
    if execution_result['type'] == 'visualization':
        state['visualization_data'] = execution_result.get('content', '')
        state['visualization_summary'] = execution_result.get('summary', '')
    else:
        state['visualization_data'] = ''
        state['visualization_summary'] = ''
    
    print(f"[EXECUTION] Type: {execution_result['type']}")
    print(f"[EXECUTION] Result length: {len(state['result'])}")
    return state


#Node-4 Explain Result
def explain_result(state: AgentState) -> AgentState:
    question = state['question']
    code = state['code']
    result = state['result']
    is_visualization = state.get("is_visualization", False)
    
    if is_visualization:
        viz_summary = state.get("visualization_summary", "")
        state['result'] = viz_summary or f"Generated a visualization for: {question}."
        return state
    else:
        # For text results, provide detailed explanation
        prompt = f"""You are an AI data analyst. You have executed the following code to answer the question: {question}
        Code: {code}
        Result: {result}
        Explain the result in simple terms."""

    response = client.chat.completions.create(
    model="databricks-llama-4-maverick",
    messages=[
            {"role": "system", "content": "You are a helpful data analyst that explains results."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    
    state['result'] = response.choices[0].message.content
    return state

#Node -5: check for errors and decide next step
def check_error(state: AgentState):
    result = state["result"]
    retries = state.get("retries", 0)
    if "Error executing code" in result:
        if retries <= 3:
            state["retries"] = retries + 1
            return "generate_code"

    return "explain_result"


builder = StateGraph(AgentState)

builder.add_node("normalize_query", normalize_query)
builder.add_node("detect_visualization", detect_visualization)
builder.add_node("generate_code", generate_code)
builder.add_node("execute_code", execute_code)
builder.add_node("explain_result", explain_result)

builder.set_entry_point("normalize_query")

builder.add_edge("normalize_query", "detect_visualization")
builder.add_edge("detect_visualization", "generate_code")
builder.add_edge("generate_code", "execute_code")
builder.add_conditional_edges(
    "execute_code",
    check_error
)
builder.add_edge("explain_result", END)

graph = builder.compile()