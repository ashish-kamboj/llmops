# AI Speech Analyzer - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### 1. Get Your Groq API Key
1. Visit: https://console.groq.com/keys
2. Sign up for a free account
3. Generate an API key
4. Copy it to your clipboard

### 2. Configure the Application
1. Open the `.env` file in this folder
2. Replace `your_groq_api_key_here` with your actual API key
3. Save the file

**Note:** The app always reads the Groq API key from `.env`. There is no sidebar input for the key.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
streamlit run app.py
```

### 5. Start Analyzing!
1. Upload an audio file (MP3, WAV, etc.) **or record audio directly in the app** using the native audio recorder
2. **Optional:** Toggle "Parallel Processing" in the sidebar (ON = faster, OFF = sequential)
3. Click "Analyze Speech" or "Analyze Recorded Speech"
4. View your results with processing time comparison!

## 📖 Need More Help?
Read the full README.md file for detailed documentation.

## 🎯 Test the App
Try with a sample audio file:
- Record yourself saying: "I love this new technology! It's amazing how AI can understand speech."
- Save as MP3 or WAV
- Upload and analyze!

Expected Results:
- **Transcription**: Your spoken words converted to text
- **Sentiment**: Positive 😊
- **Translation**: Hindi version of your speech

---

**Having Issues?** 
Check the Troubleshooting section in README.md
