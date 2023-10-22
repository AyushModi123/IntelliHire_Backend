from langchain.chat_models import ChatOpenAI
from langchain.chains.openai_functions import create_openai_fn_chain, create_structured_output_chain
import openai
import os
import json
openai.api_key = os.getenv('OPENAI_API_KEY')


llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.0)

def exec_prompt(output_schema, parse_prompt, input_data):
    chain = create_structured_output_chain(output_schema=output_schema, llm=llm, prompt=parse_prompt, verbose=False)
    output_data = chain.run(input_data)
    return output_data
