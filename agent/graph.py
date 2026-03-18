from typing import TypedDict
from langgraph.graph import END, StateGraph
from databricks_langchain import ChatDatabricks
from data.dataset_store import  get_df
from executor.python_exec import execute_python
from openai import OpenAI
import os

DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

client = OpenAI(
    api_key= DATABRICKS_TOKEN,
    base_url="https://adb-4224005571705028.8.azuredatabricks.net/serving-endpoints"
)  # Initialize the OpenAI client

class AgentState(TypedDict):
    question: str
    code : str
    result: str
    retries: int

#Node-1 : Generate Code
def generate_code(state: AgentState) -> AgentState:
    question = state['question']
    df = get_df()
    previous_error = state.get("result", "")

    prompt = f"""You are an AI data analyst. You are given a question and a dataset. 
    Your task is to write Python code using pandas to answer the question based on the dataset.
    You are an AI data analyst.

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
    - Do NOT include markdown.
    - Do NOT import any libraries

    - Do NOT create API clients
    - Do NOT use Anthropic or OpenAI
    - Do NOT load files
    - The dataframe `df` is already available

    - Store the final answer in variable `result`
"""
    
    response = client.chat.completions.create(
    model="databricks-claude-sonnet-4-6",
    messages=[
            {"role": "system", "content": "You are a helpful data analyst that writes pandas code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    state['code'] = response.choices[0].message.content
    print(state['code'])
    return state

#Node-2 : Execute Code
def execute_code(state: AgentState) -> AgentState:
    code = state['code']
    result = execute_python(code)
    state['result'] = result
    print(state['result'])
    return state


#Node-3: Explain Result
def explain_result(state: AgentState) -> AgentState:
    question = state['question']
    code = state['code']
    result = state['result']
    
    prompt = f"""You are an AI data analyst. You have executed the following code to answer the question: {question}
    Code: {code}
    Result: {result}
    Explain the result in simple terms."""

    response = client.chat.completions.create(
    model="databricks-claude-sonnet-4-6",
    messages=[
            {"role": "system", "content": "You are a helpful data analyst that explains results."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    
    # response = llm.invoke(prompt)
    state['result'] = response.choices[0].message.content
    return state

#Node -4 : check for errors and decide next step
def check_error(state: AgentState):
    previous_error=""
    result = state["result"]
    retries = state.get("retries", 0)
    if "Error executing code" in result:
        previous_error = state["result"]
        if retries <=3:
            state["retries"] = retries + 1
            return "generate_code"

    return "explain_result"


builder = StateGraph(AgentState)

builder.add_node("generate_code", generate_code)
builder.add_node("execute_code", execute_code)
builder.add_node("explain_result", explain_result)

builder.set_entry_point("generate_code")


builder.add_edge("generate_code", "execute_code")
builder.add_conditional_edges(
    "execute_code",
    check_error
)
builder.add_edge("explain_result", END)

graph = builder.compile()