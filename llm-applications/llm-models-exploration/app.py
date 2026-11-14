# Import streamlit and requests
from src.utils import (get_output, show_output)
from src.constants import TASKS
import streamlit as st
import json


with st.sidebar:
    st.markdown(
        "## How to use\n"
        "1. Enter your [Huggingface API token](https://huggingface.co/settings/tokens) (Recommended, as some model won't work)\n"
        "2. Choose a task to perform \n"
        "3. Choose a LLM model correspong to task \n"
        "4. Enter a different LLM model id from Huggingface hub (Optional) \n"
    )

    st.write("##")

    # Create a text input for accepting the Huggingface API Token
    huggingface_api_token = st.text_input("Huggingface API Token (Optional)", 
                                          key="hf_api_token", 
                                          type="password",
                                          help="You can get your API token from https://huggingface.co/settings/tokens."
                                        )

    # Create a select box for choosing the ML task
    task = st.selectbox("Choose a task", list(TASKS.keys()))

    # Create a select box for choosing the model based on the task
    select_model = st.selectbox("Choose a model", TASKS[task])

    # Create a text box for putting the model id (from Huggingface hub) based on the selected task
    optional_model = st.text_input("Enter Huggingface model (Optional)")

    if (optional_model != ""):
        model = optional_model
    else:
        model = select_model


# Create a title for the app
st.header("Huggingface Hub Model Explorer")

# Create a header for displaying the input and output widgets
st.subheader(f"{task} with {model}")

# Create different input and output widgets based on the task
if task == "Text Generation":
    # Create a text input for entering the text to generate from
    text_input = st.text_input("Enter some text to generate from")

    # Create a button for generating the text
    generate_button = st.button("Generate")

    # If the button is clicked and the input is not empty
    if generate_button and text_input:
        # Create a payload with the input text
        data = json.dumps({"inputs": text_input})

        # Get the output from the API
        output = get_output(task, model, data, api_token=huggingface_api_token)

        # Display the output text on the output widget
        show_output(output)

elif task == "Text Summarization":
    # Create a text area for entering the text to summarize
    text_area = st.text_area("Enter some text to summarize")

    # Create a button for summarizing the text
    summarize_button = st.button("Summarize")

    # If the button is clicked and the input is not empty
    if summarize_button and text_area:
        # Create a payload with the input text
        data = json.dumps({"inputs": text_area})

        # Get the output from the API
        output = get_output(task, model, data, api_token=huggingface_api_token)

        # Display the output summary on the output widget
        show_output(output)

elif task == "Text Classification":
    # Create a text input for entering the text to classify
    text_input = st.text_input("Enter some text to classify")

    # Create a button for classifying the text
    classify_button = st.button("Classify")

    # If the button is clicked and the input is not empty
    if classify_button and text_input:
        # Create a payload with the input text
        data = json.dumps({"inputs": text_input})

        # Get the output from the API
        output = get_output(task, model, data, api_token=huggingface_api_token)

        # Display the output label and score on the output widget
        ref_output = output[0]
        for out in ref_output:
            st.text(f"{out['label']}: {round(out['score']*100, 1)}%")

elif task == "Text-to-Speech":
    # Create a text input for entering the text to synthesize
    text_input = st.text_input("Enter some text to synthesize")

    # Create a button for synthesizing the speech
    synthesize_button = st.button("Synthesize")

    # If the button is clicked and the input is not empty
    if synthesize_button and text_input:
        # Create a payload with the input text
        data = json.dumps({"inputs": text_input})

        # Get the output from the API
        output = get_output(task, model, data, api_token=huggingface_api_token, model_type="audio")

        # Display the output audio on the output widget
        with open("audio.wav", "wb") as f:
            f.write(output.content)
        st.audio("audio.wav")
        
elif task == "Image Classification":
    # Create a file uploader for uploading an image to classify
    image_file = st.file_uploader("Upload an image to classify")

    # Create a button for classifying the image
    classify_button = st.button("Classify")

    # Create an empty output widget
    output_widget = st.empty()

    # If the button is clicked and the file is not None
    if classify_button and image_file:
        # Read the image file as bytes
        image_bytes = image_file.read()

        # Get the output from the API
        output = get_output(task, model, data=image_bytes, api_token=huggingface_api_token)

        # Display the output label and score on the output widget
        for items in output:
            st.text(f"{items['label']}: {round(items['score']*100, 1)}%")