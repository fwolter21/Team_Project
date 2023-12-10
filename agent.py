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
   making the app function. The code on it was written by chatgbt as I do not fully undertaand how it is doing its function '''
    
    code_pattern = r"```python(.*?)```"
    match = re.search(code_pattern, response, re.DOTALL)
    
    if match:
        # Extract the matched code and strip any leading/trailing whitespaces
        return match.group(1).strip()
    return None



def main():
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









