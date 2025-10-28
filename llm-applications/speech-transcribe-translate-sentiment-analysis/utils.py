"""
Utility functions for the Speech Analysis App.

This module provides helper functions for:
1. Configuration loading and validation
2. Audio file validation and processing
3. File operations and cleanup
4. Environment setup
"""

import os
import logging
from typing import Dict, Any, List
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class AudioConfig(BaseModel):
    """Configuration model for audio settings."""
    max_file_size_mb: int = Field(default=25, ge=1, le=100)
    supported_formats: List[str] = Field(default_factory=lambda: ["mp3", "mp4", "wav", "webm"])
    sample_rate: int = Field(default=44100, ge=8000, le=48000)
    channels: int = Field(default=1, ge=1, le=2)
    max_recording_duration: int = Field(default=300, ge=10, le=600)


class AppConfig(BaseModel):
    """Main application configuration model."""
    models: Dict[str, str]
    api: Dict[str, Any]
    audio: AudioConfig
    ui: Dict[str, Any]
    sentiment: Dict[str, Any]
    translation: Dict[str, Any]
    logging: Dict[str, Any]


def load_environment() -> str:
    """
    Load environment variables from .env file.
    
    Returns:
        Groq API key from environment
        
    Raises:
        ValueError: If API key is not found
    """
    # Load .env file
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key or api_key == 'your_groq_api_key_here':
        raise ValueError(
            "GROQ_API_KEY not found in environment. "
            "Please copy .env.example to .env and add your API key."
        )
    
    logger.info("Environment variables loaded successfully")
    return api_key


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load application configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid
    """
    try:
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate audio config
        audio_config = AudioConfig(**config.get('audio', {}))
        config['audio'] = audio_config.model_dump()
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {str(e)}")


def validate_audio_file(file_path: str, config: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate an audio file against configuration constraints.
    
    Args:
        file_path: Path to the audio file
        config: Application configuration dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        file_obj = Path(file_path)
        
        # Check if file exists
        if not file_obj.exists():
            return False, "File does not exist"
        
        # Check file extension
        file_extension = file_obj.suffix.lower().lstrip('.')
        supported_formats = config.get('audio', {}).get('supported_formats', [])
        
        if file_extension not in supported_formats:
            return False, f"Unsupported format. Supported: {', '.join(supported_formats)}"
        
        # Check file size
        file_size_mb = file_obj.stat().st_size / (1024 * 1024)
        max_size_mb = config.get('audio', {}).get('max_file_size_mb', 25)
        
        if file_size_mb > max_size_mb:
            return False, f"File too large ({file_size_mb:.2f}MB). Maximum: {max_size_mb}MB"
        
        logger.info(f"Audio file validation passed: {file_path}")
        return True, ""
        
    except Exception as e:
        logger.error(f"Error validating audio file: {str(e)}")
        return False, f"Validation error: {str(e)}"


def save_uploaded_file(uploaded_file, temp_dir: str = "temp") -> str:
    """
    Save an uploaded Streamlit file to temporary directory.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        temp_dir: Directory to save temporary files
        
    Returns:
        Path to the saved file
    """
    try:
        # Create temp directory if it doesn't exist
        temp_path = Path(temp_dir)
        temp_path.mkdir(exist_ok=True)
        
        # Generate file path
        file_path = temp_path / uploaded_file.name
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"File saved to: {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {str(e)}")
        raise Exception(f"Failed to save file: {str(e)}")


def cleanup_temp_files(temp_dir: str = "temp"):
    """
    Clean up temporary audio files.
    
    Args:
        temp_dir: Directory containing temporary files
    """
    try:
        temp_path = Path(temp_dir)
        
        if temp_path.exists():
            for file in temp_path.glob("*"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {file}: {str(e)}")
            
            logger.info("Temporary files cleaned up")
            
    except Exception as e:
        logger.warning(f"Failed to cleanup temp files: {str(e)}")


def setup_logging(config: Dict[str, Any]):
    """
    Setup application logging based on configuration.
    
    Args:
        config: Application configuration dictionary
    """
    log_config = config.get('logging', {})
    log_level = log_config.get('level', 'INFO')
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File logging (if enabled)
    if log_config.get('enable_file_logging', False):
        log_file = log_config.get('log_file', 'logs/app.log')
        log_path = Path(log_file).parent
        log_path.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        logging.getLogger().addHandler(file_handler)
    
    logger.info("Logging configured successfully")


def format_processing_time(seconds: float) -> str:
    """
    Format processing time in a human-readable format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"


def get_sentiment_emoji(sentiment: str) -> str:
    """
    Get an emoji representation for a sentiment.
    
    Args:
        sentiment: Sentiment classification
        
    Returns:
        Emoji string
    """
    sentiment_lower = sentiment.lower()
    
    if 'positive' in sentiment_lower:
        return "😊"
    elif 'negative' in sentiment_lower:
        return "😔"
    else:
        return "😐"


def get_sentiment_color(sentiment: str) -> str:
    """
    Get a color code for a sentiment.
    
    Args:
        sentiment: Sentiment classification
        
    Returns:
        Color hex code
    """
    sentiment_lower = sentiment.lower()
    
    if 'positive' in sentiment_lower:
        return "#4CAF50"  # Green
    elif 'negative' in sentiment_lower:
        return "#F44336"  # Red
    else:
        return "#FFC107"  # Amber
