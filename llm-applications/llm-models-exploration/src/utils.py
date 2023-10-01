from src.constants import HF_API_URL
import streamlit as st
import requests

# Define a function to get the output from the Huggingface Inference API
def get_output(task, model, data, api_token, model_type=None):
    # Construct the request URL
    url = f"{HF_API_URL}/models/{model}?task={task}"
    print(f"api_token:: {api_token}")
    # Send a POST request with the payload as JSON data
    if(api_token !=""):
        headers = {"Authorization": f"Bearer {api_token}"}
        response = requests.post(url, headers=headers, data=data)
    else:
        response = requests.post(url, data=data)

    # Check if the request was successful
    if model_type is None:
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": f"Request failed with status code {response.status_code}",
                    "description": "Please check whether Model id is correct or Inference API is available for this model."}
        else:
            return {"error": f"Request failed with status code {response.status_code}",
                    "description": None}
    else:
        return response
    

## Function for displaying the output of a epecified task choosen
def show_output(output):
    if isinstance(output, list):
        st.text_area(label="Generated Text Output", value=output[0][list(output[0].keys())[0]])
    else:
        st.error(output['error'])
        st.error(output['description'])