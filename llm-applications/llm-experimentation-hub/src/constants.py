# Define the Huggingface Inference API base URL
HF_API_URL = "https://api-inference.huggingface.co"

# Define a dictionary of ML tasks and their corresponding models
TASKS = {
    "Text Generation": ["gpt2", "gpt2-medium", "gpt2-large", "gpt2-xl"],
    "Text Summarization": ["facebook/bart-large-cnn", "philschmid/bart-large-cnn-samsum", "t5-small", "t5-base", "t5-large", "t5-3b", "t5-11b"],
    "Text Classification": ["distilbert-base-uncased-finetuned-sst-2-english", "ProsusAI/finbert", "cardiffnlp/twitter-roberta-base-sentiment-latest", "bert-base-uncased", "bert-large-uncased", "distilbert-base-uncased"],
    "Text-to-Speech": ["microsoft/speecht5_tts", "facebook/wav2vec2-base-960h", "facebook/wav2vec2-large-960h-lv60", "facebook/wav2vec2-large-xlsr-53"],
    "Image Classification": ["google/vit-base-patch16-224", "google/vit-large-patch16-224", "google/vit-large-patch32-224"]
}