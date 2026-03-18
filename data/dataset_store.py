df_store = None

def set_df(df):
    global df_store
    df_store = df

def get_df():
    return df_store

def clear_df():
    global df_store
    df_store = None