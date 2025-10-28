"""
AI Speech Analyzer - Streamlit Application

A production-grade speech analysis application that provides:
1. Speech-to-Text conversion using Groq's Whisper model
2. Sentiment Analysis using advanced LLM
3. English to Hindi Translation

Features:
- Beautiful, modern UI with custom styling
- Async parallel processing for optimal performance
- Configurable models and parameters
- Support for file upload and audio recording
- Real-time processing feedback

Author: AI Speech Analyzer Team
"""

import asyncio
import logging

import streamlit as st

# Import custom modules
from services import SpeechAnalysisService, AnalysisResults
from utils import (
    load_environment,
    load_config,
    validate_audio_file,
    save_uploaded_file,
    cleanup_temp_files,
    setup_logging,
    format_processing_time,
    get_sentiment_emoji,
    get_sentiment_color
)

# Configure page settings
st.set_page_config(
    page_title="AI Speech Analyzer 🎤",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_custom_css():
    """Load custom CSS for beautiful UI styling."""
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main container */
        .main {
            padding: 2rem;
        }
        
        /* Header styling */
        .app-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .app-title {
            color: white;
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .app-subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            font-weight: 300;
            margin-top: 0.5rem;
        }
        
        /* Card styling */
        .result-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .result-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .result-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #2c3e50;
        }
        
        .result-content {
            font-size: 1.1rem;
            line-height: 1.6;
            color: #34495e;
        }
        
        /* Sentiment badge */
        .sentiment-badge {
            display: inline-block;
            padding: 0.5rem 1.5rem;
            border-radius: 25px;
            font-weight: 600;
            font-size: 1.2rem;
            margin: 1rem 0;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }
        
        /* Hindi text styling */
        .hindi-text {
            font-size: 1.3rem;
            line-height: 1.8;
            color: #2c3e50;
            padding: 1rem;
            background: rgba(255,255,255,0.5);
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        /* Info boxes */
        .info-box {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            border-left: 4px solid #ff6b6b;
        }
        
        /* Success message */
        .success-box {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            border-left: 4px solid #4CAF50;
        }
        
        /* Processing animation */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .processing {
            animation: pulse 2s ease-in-out infinite;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* Button styling */
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        /* File uploader styling */
        .uploadedFile {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 1rem;
        }
        
        /* Metric styling */
        .metric-container {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem 0;
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-top: 3rem;
            border-top: 1px solid #ecf0f1;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the application header."""
    st.markdown("""
        <div class="app-header">
            <h1 class="app-title">🎤 AI Speech Analyzer</h1>
            <p class="app-subtitle">Transcribe • Analyze • Translate | Powered by Groq AI</p>
        </div>
    """, unsafe_allow_html=True)


def render_results(results: AnalysisResults):
    """
    Render analysis results in a beautiful format.
    
    Args:
        results: AnalysisResults object containing all analysis data
    """
    # Create three columns for layout
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Column 1: Transcription
    with col1:
        st.markdown("""
            <div class="result-card">
                <div class="result-title">📝 Transcription</div>
                <div class="result-content">{}</div>
            </div>
        """.format(results.transcription), unsafe_allow_html=True)
    
    # Column 2: Sentiment Analysis
    with col2:
        sentiment = results.sentiment.sentiment
        emoji = get_sentiment_emoji(sentiment)
        color = get_sentiment_color(sentiment)
        
        st.markdown(f"""
            <div class="result-card">
                <div class="result-title">💭 Sentiment Analysis</div>
                <div style="text-align: center;">
                    <span class="sentiment-badge" style="background-color: {color}; color: white;">
                        {emoji} {sentiment}
                    </span>
                </div>
                <div class="result-content" style="margin-top: 1rem;">
                    <strong>Analysis:</strong><br/>
                    {results.sentiment.confidence or "N/A"}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Show key phrases if available
        if results.sentiment.key_phrases:
            st.markdown("**🔑 Key Phrases:**")
            for phrase in results.sentiment.key_phrases:
                st.markdown(f"- {phrase}")
    
    # Column 3: Hindi Translation
    with col3:
        st.markdown(f"""
            <div class="result-card">
                <div class="result-title">🌐 Hindi Translation</div>
                <div class="hindi-text">
                    {results.translation.translated_text}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Processing time
    st.markdown(f"""
        <div class="success-box">
            ✅ <strong>Analysis Complete!</strong> 
            Processing time: <strong>{format_processing_time(results.processing_time)}</strong>
        </div>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'service' not in st.session_state:
        st.session_state.service = None
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


async def process_audio_async(service: SpeechAnalysisService, audio_path: str):
    """
    Process audio file asynchronously.
    
    Args:
        service: SpeechAnalysisService instance
        audio_path: Path to the audio file
    """
    try:
        results = await service.process_audio_file(audio_path)
        st.session_state.results = results
        st.session_state.processing = False
        return results
    except Exception as e:
        st.session_state.processing = False
        raise e


def main():
    """Main application entry point."""
    # Load custom CSS
    load_custom_css()
    
    # Render header
    render_header()
    
    # Initialize session state
    initialize_session_state()
    
    try:
        # Load configuration and environment
        config = load_config("config.yaml")
        setup_logging(config)

        # Always read Groq API key from .env
        try:
            api_key = load_environment()
        except ValueError:
            st.sidebar.error("❌ Groq API key not found in .env file. Please add GROQ_API_KEY to .env.")
            return

        # Sidebar configuration
        with st.sidebar:
            st.markdown("## ⚙️ Configuration")

            # Model selection
            st.markdown("### 🤖 Model Selection")

            stt_model = st.selectbox(
                "Speech-to-Text Model",
                ["whisper-large-v3", "whisper-large-v3-turbo"],
                index=0,
                help="Whisper model for audio transcription"
            )

            llm_model = st.selectbox(
                "Language Model",
                [
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768"
                ],
                index=0,
                help="LLM for sentiment analysis and translation"
            )

            # Update config with selected models
            config['models']['speech_to_text'] = stt_model
            config['models']['language_model'] = llm_model

            st.markdown("---")

            # Processing options
            st.markdown("### 🚀 Processing Options")
            parallel_processing = st.checkbox(
                "Parallel Processing",
                value=config['api']['parallel_processing'],
                help="⚡ When enabled: Sentiment analysis and translation run simultaneously (faster). When disabled: They run one after another (slower, but easier to debug)."
            )
            config['api']['parallel_processing'] = parallel_processing
            
            # Show current mode
            if parallel_processing:
                st.info("⚡ **Mode:** Parallel - Faster processing (~40% time reduction)")
            else:
                st.warning("🐢 **Mode:** Sequential - Slower but sequential execution")

            st.markdown("---")

            # About section
            with st.expander("ℹ️ About"):
                st.markdown("""
                **AI Speech Analyzer** uses cutting-edge AI models from Groq:

                - **Whisper**: State-of-the-art speech recognition
                - **Llama 3**: Advanced language understanding

                **Architecture**:
                - REST API approach for reliability
                - Async parallel processing for speed
                - Production-grade error handling

                **Tech Stack**:
                - Streamlit for UI
                - Groq API for AI models
                - Python asyncio for concurrency
                """)

            # Help section
            with st.expander("❓ Help"):
                st.markdown("""
                **How to use:**

                1. Add your Groq API key to the .env file
                2. Upload an audio file or record audio
                3. Click "Analyze Speech"
                4. View transcription, sentiment, and translation

                **Supported formats:**
                - MP3, MP4, WAV, WebM, M4A
                - Max file size: 25MB
                """)

        # Main content area
        st.markdown("## 🎵 Upload or Record Audio")

        # Create tabs for upload and record
        tab1, tab2 = st.tabs(["📁 Upload File", "🎙️ Record Audio"])

        with tab1:
            uploaded_file = st.file_uploader(
                "Choose an audio file",
                type=config['audio']['supported_formats'],
                help=f"Supported formats: {', '.join(config['audio']['supported_formats'])}. Max size: {config['audio']['max_file_size_mb']}MB"
            )

            if uploaded_file is not None:
                # Display file info
                file_size_mb = uploaded_file.size / (1024 * 1024)
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("File Name", uploaded_file.name)
                with col2:
                    st.metric("File Size", f"{file_size_mb:.2f} MB")
                with col3:
                    st.metric("Format", uploaded_file.name.split('.')[-1].upper())

                # Audio player
                st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")

                # Analyze button
                if st.button("🚀 Analyze Speech", type="primary", use_container_width=True):
                    with st.spinner("🔄 Processing your audio..."):
                        try:
                            # Save uploaded file
                            audio_path = save_uploaded_file(uploaded_file)

                            # Validate audio file
                            is_valid, error_msg = validate_audio_file(audio_path, config)
                            if not is_valid:
                                st.error(f"❌ {error_msg}")
                            else:
                                # Initialize service
                                service = SpeechAnalysisService(api_key, config)

                                # Process audio (async)
                                st.session_state.processing = True

                                # Create progress indicator
                                progress_text = st.empty()
                                progress_bar = st.progress(0)

                                progress_text.markdown("**Step 1/3:** 🎤 Converting speech to text...")
                                progress_bar.progress(33)

                                # Run async processing
                                results = asyncio.run(service.process_audio_file(audio_path))

                                # Update progress based on mode
                                if config['api']['parallel_processing']:
                                    progress_text.markdown("**Steps 2-3/3:** 💭🌐 Analyzing sentiment & translating (parallel)...")
                                else:
                                    progress_text.markdown("**Step 2/3:** 💭 Analyzing sentiment...")
                                    progress_bar.progress(66)
                                    progress_text.markdown("**Step 3/3:** 🌐 Translating to Hindi (sequential)...")
                                progress_bar.progress(100)

                                # Clear progress indicators
                                progress_text.empty()
                                progress_bar.empty()

                                # Store results
                                st.session_state.results = results

                                # Cleanup
                                cleanup_temp_files()

                                # Success message
                                st.success("✅ Analysis complete!")

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            logging.error(f"Processing error: {str(e)}")

        with tab2:
            st.markdown("### 🎙️ Record Audio")
            st.info("Click the microphone button below to record your voice, then analyze it!")
            
            # Use st.audio_input for recording (Streamlit 1.50.0+)
            audio_value = st.audio_input(
                "Record a voice message",
                sample_rate=16000,  # Optimal for speech recognition
                key="audio_input"
            )
            
            if audio_value:
                st.audio(audio_value)
                
                if st.button("🚀 Analyze Recorded Speech", type="primary", use_container_width=True):
                    with st.spinner("🔄 Processing your recorded audio..."):
                        try:
                            # Save recorded audio to temp file
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                                tmp_audio.write(audio_value.getvalue())
                                audio_path = tmp_audio.name

                            # Validate audio file
                            is_valid, error_msg = validate_audio_file(audio_path, config)
                            if not is_valid:
                                st.error(f"❌ {error_msg}")
                            else:
                                # Initialize service
                                service = SpeechAnalysisService(api_key, config)

                                # Process audio (async)
                                st.session_state.processing = True

                                # Create progress indicator
                                progress_text = st.empty()
                                progress_bar = st.progress(0)

                                progress_text.markdown("**Step 1/3:** 🎤 Converting speech to text...")
                                progress_bar.progress(33)

                                # Run async processing
                                results = asyncio.run(service.process_audio_file(audio_path))

                                # Update progress based on mode
                                if config['api']['parallel_processing']:
                                    progress_text.markdown("**Steps 2-3/3:** 💭🌐 Analyzing sentiment & translating (parallel)...")
                                else:
                                    progress_text.markdown("**Step 2/3:** 💭 Analyzing sentiment...")
                                    progress_bar.progress(66)
                                    progress_text.markdown("**Step 3/3:** 🌐 Translating to Hindi (sequential)...")
                                progress_bar.progress(100)

                                # Clear progress indicators
                                progress_text.empty()
                                progress_bar.empty()

                                # Store results
                                st.session_state.results = results

                                # Cleanup
                                cleanup_temp_files()

                                # Success message
                                st.success("✅ Analysis complete!")

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            logging.error(f"Processing error: {str(e)}")

        # Display results if available
        if st.session_state.results:
            st.markdown("---")
            st.markdown("## 📊 Analysis Results")
            render_results(st.session_state.results)

            # Download results option
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                import json
                results_json = json.dumps({
                    "transcription": st.session_state.results.transcription,
                    "sentiment": st.session_state.results.sentiment.model_dump(),
                    "translation": st.session_state.results.translation.model_dump(),
                    "processing_time": st.session_state.results.processing_time
                }, indent=2, ensure_ascii=False)

                st.download_button(
                    label="📥 Download Results (JSON)",
                    data=results_json,
                    file_name="speech_analysis_results.json",
                    mime="application/json",
                    use_container_width=True
                )

    except FileNotFoundError as e:
        st.error(f"❌ Configuration Error: {str(e)}")
        st.info("💡 Make sure config.yaml exists in the application directory")
    except ValueError as e:
        st.error(f"❌ Configuration Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")
        logging.error(f"Application error: {str(e)}")


if __name__ == "__main__":
    main()
