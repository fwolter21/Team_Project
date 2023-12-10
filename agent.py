from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.llms import openai
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from key import OPENAI_API_KEY
openai_api_key = OPENAI_API_KEY
import streamlit as st
import  matplotlib.pyplot as plt
import tempfile
import streamlit as st
import pandas as pd
import os
import re
import seaborn as sns
import plotly.express as px 







def agent_function(file_path, user_input):
    '''
    Interacts with an agent to process user input and return a response.

    This function creates an agent instance with ChatOpenAI. It formats the user's input, sends it to the agent, and returns
    the agent's response.

    Parameters:
    - file_path (str): The file path of the CSV file being analyzed.
    - user_input (str): The user's input or query to be processed by the agent.

    Returns:
    - dict: The response from the agent, or None if an exception occurs.
    '''
    # Create an agent instance
    agent = create_csv_agent(
        ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY),
        file_path,  # Pass the file_path as the path argument
        agent_type=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )
    try:
        # Properly format the user's input and wrap it with the required "input" key
        tool_input = {
            "input": {
                "name": "python",
                "arguments": user_input
            }
        }
        
        response = agent.run(tool_input)
        return response
    except Exception as e:
        st.write(f"Error: {e}")
        return None
    


def answers_from_content(response): 
    '''Processes the response from the agent and displays the results in the Streamlit app.

    This function handles different types of responses such as textual answers, bar charts,
    tables, line plots, and scatter plots. Depending on the response type, it displays
    the appropriate content or visualization in the Streamlit app.

    Parameters:
    - response (dict): The response dictionary from the agent_function.

    Returns:
    - None: This function does not return a value but displays results in the Streamlit app.
    '''
    if 'answer' in response: 
        st.write(response['answer'])
    if 'bar' in response: 
        data = response['bar']
        df = pd.DataFrame(data)
        df.set_index('columns', inplace=True)
        st.bokeh_chart(df)
    if 'table' in response:
        data = response['table']
        df = pd.DataFrame['data'], columns = data['columns']
        st.table(df)
    if 'line' in response:
        data = response['line']
        df = pd.DataFrame(data)
        fig = px.line(df, x='x_column', y='y_column')  
        st.plotly_chart(fig)  
    if 'scatter' in response:
        data = response['scatter']
        df = pd.DataFrame(data)
        fig = px.scatter(df, x='x_column', y='y_column')  
        st.plotly_chart(fig) 




def extract_code_from_response(response):
    '''This function takes pyhton code from a string of repsosne. It was developed as I was ecountering issues 
   making the app function. The code on it was written by chatgbt below as I was struggling to properly account for the variations in user input as well as properly execuitng the code for visualizations'''
    
    code_pattern = r"```python(.*?)```"
    match = re.search(code_pattern, response, re.DOTALL)
    
    if match:
        # Extract the matched code and strip any leading/trailing whitespaces
        return match.group(1).strip()
    return None



def main():
    """
    Main function for the Streamlit app to analyze CSV files.

    This function sets up the Streamlit app layout and handles user interactions.
    It allows users to upload a CSV file, input a query, and then processes this query
    using the agent_function. It also handles the visualization of responses, including
    executing any Python code returned by the agent.

    Steps:
    - Sets up the Streamlit page configuration and header.
    - Provides instructions on how to use the app in the sidebar.
    - Handles CSV file upload and reads the file into a Pandas DataFrame.
    - Takes user input as a query and processes it using the agent_function.
    - Executes any returned Python code for visualization and displays it.
    - Handles and displays errors if they occur during code execution.
    """
    st.set_page_config(page_title='Ask your CSV')
    st.header('Ask your CSV')
    with st.sidebar:
        st.write("## How to Use")
        st.markdown("""
            - Upload your CSV file.
            - Enter your query or select options for analysis.
            - Example query: "Show the age distribution."
        """)
   
    user_csv = st.file_uploader("Upload your CSV file", type='csv')

    if user_csv is not None:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, user_csv.name)
        os.makedirs(temp_dir, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(user_csv.getbuffer())
       
        df = pd.read_csv(file_path)
        st.dataframe(df)
        
        user_input = st.text_input('Your Question')
        if st.button('Run'):
            response = agent_function(file_path, user_input)
            
            # Extracting and executing code from the response
            code_to_execute = extract_code_from_response(response)
            if code_to_execute:
                try:
                    exec(code_to_execute, globals(), {"df": df, "plt": plt})
                    fig = plt.gcf()
                    st.pyplot(fig)
                except Exception as e:
                    st.write(f"Error executing code: {e}")
            else:
                st.write(response)

    st.divider()

if __name__ == "__main__":
    main()









