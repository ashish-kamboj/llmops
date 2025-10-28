"""
Service module for AI-powered speech analysis.

This module provides core services for:
1. Speech-to-Text conversion using Groq's Whisper API
2. Sentiment Analysis using Groq's LLM API
3. English to Hindi Translation using Groq's LLM API

All API calls are implemented asynchronously for optimal performance.
Sentiment analysis and translation are executed in parallel to minimize latency.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from groq import Groq, AsyncGroq
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class SpeechToTextResult(BaseModel):
    """Result model for speech-to-text conversion."""
    text: str = Field(..., description="Transcribed text from audio")
    language: Optional[str] = Field(None, description="Detected language")
    duration: Optional[float] = Field(None, description="Processing duration in seconds")


class SentimentResult(BaseModel):
    """Result model for sentiment analysis."""
    sentiment: str = Field(..., description="Detected sentiment (Positive/Negative/Neutral)")
    confidence: Optional[str] = Field(None, description="Confidence explanation")
    key_phrases: Optional[list[str]] = Field(None, description="Key phrases that indicate sentiment")


class TranslationResult(BaseModel):
    """Result model for translation."""
    translated_text: str = Field(..., description="Translated text in Hindi")
    original_text: str = Field(..., description="Original English text")


class AnalysisResults(BaseModel):
    """Combined results from all analysis operations."""
    transcription: str
    sentiment: SentimentResult
    translation: TranslationResult
    processing_time: float


class SpeechAnalysisService:
    """
    Main service class for speech analysis operations.
    
    This class handles all interactions with the Groq API for:
    - Speech-to-text transcription
    - Sentiment analysis
    - Language translation
    
    It uses async operations and parallel processing for optimal performance.
    """
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        """
        Initialize the Speech Analysis Service.
        
        Args:
            api_key: Groq API key for authentication
            config: Configuration dictionary containing model names and settings
        """
        self.api_key = api_key
        self.config = config
        
        # Initialize synchronous client for speech-to-text (Groq SDK requirement)
        self.client = Groq(api_key=api_key)
        
        # Initialize async client for text operations
        self.async_client = AsyncGroq(api_key=api_key)
        
        # Extract model configurations
        self.stt_model = config.get('models', {}).get('speech_to_text', 'whisper-large-v3')
        self.llm_model = config.get('models', {}).get('language_model', 'llama-3.3-70b-versatile')
        
        # Extract API configurations
        self.timeout = config.get('api', {}).get('timeout', 30)
        self.parallel_processing = config.get('api', {}).get('parallel_processing', True)
        
        logger.info(f"SpeechAnalysisService initialized with STT model: {self.stt_model}, LLM model: {self.llm_model}")
    
    def speech_to_text(self, audio_file_path: str) -> SpeechToTextResult:
        """
        Convert speech audio to text using Groq's Whisper API.
        
        This is a synchronous operation as required by the Groq SDK.
        
        Args:
            audio_file_path: Path to the audio file to transcribe
            
        Returns:
            SpeechToTextResult containing the transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        try:
            logger.info(f"Starting speech-to-text transcription for: {audio_file_path}")
            
            # Open and transcribe the audio file
            with open(audio_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=(Path(audio_file_path).name, audio_file.read()),
                    model=self.stt_model,
                    response_format="verbose_json",  # Get additional metadata
                    temperature=0.0  # Deterministic output for transcription
                )
            
            # Extract results
            text = transcription.text
            language = getattr(transcription, 'language', None)
            
            logger.info(f"Transcription successful. Text length: {len(text)} characters")
            
            return SpeechToTextResult(
                text=text,
                language=language,
                duration=None
            )
            
        except Exception as e:
            logger.error(f"Speech-to-text conversion failed: {str(e)}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of the given text using Groq's LLM API.
        
        This is an async operation that can run in parallel with other tasks.
        
        Args:
            text: Text to analyze for sentiment
            
        Returns:
            SentimentResult containing sentiment classification and details
            
        Raises:
            Exception: If sentiment analysis fails
        """
        import time
        start = time.time()
        try:
            logger.info("Starting sentiment analysis")
            
            # Construct sentiment analysis prompt
            prompt = f"""Analyze the sentiment of the following text and classify it as either "Positive", "Negative", or "Neutral".

Text: "{text}"

Provide your analysis in the following JSON format:
{{
    "sentiment": "Positive/Negative/Neutral",
    "confidence": "Brief explanation of why you classified it this way",
    "key_phrases": ["phrase1", "phrase2", "phrase3"]
}}

Respond ONLY with the JSON object, no additional text."""

            # Get sentiment configuration
            temperature = self.config.get('sentiment', {}).get('temperature', 0.3)
            max_tokens = self.config.get('sentiment', {}).get('max_tokens', 150)
            
            # Call Groq API asynchronously
            response = await self.async_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. Analyze text and provide accurate sentiment classifications with explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Parse response
            import json
            result = json.loads(response.choices[0].message.content)
            
            elapsed = time.time() - start
            logger.info(f"Sentiment analysis complete: {result.get('sentiment')} (took {elapsed:.2f}s)")
            
            return SentimentResult(
                sentiment=result.get('sentiment', 'Neutral'),
                confidence=result.get('confidence'),
                key_phrases=result.get('key_phrases', [])
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            raise Exception(f"Failed to analyze sentiment: {str(e)}")
    
    async def translate_to_hindi(self, text: str) -> TranslationResult:
        """
        Translate English text to Hindi using Groq's LLM API.
        
        This is an async operation that can run in parallel with other tasks.
        
        Args:
            text: English text to translate
            
        Returns:
            TranslationResult containing translated Hindi text
            
        Raises:
            Exception: If translation fails
        """
        import time
        start = time.time()
        try:
            logger.info("Starting English to Hindi translation")
            
            # Construct translation prompt
            prompt = f"""Translate the following English text to Hindi (Devanagari script). 
Maintain the original meaning, tone, and context. Provide a natural, fluent translation.

English Text: "{text}"

Provide your translation in the following JSON format:
{{
    "translated_text": "Your Hindi translation here",
    "original_text": "The original English text"
}}

Respond ONLY with the JSON object, no additional text."""

            # Get translation configuration
            temperature = self.config.get('translation', {}).get('temperature', 0.5)
            max_tokens = self.config.get('translation', {}).get('max_tokens', 1000)
            
            # Call Groq API asynchronously
            response = await self.async_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert English to Hindi translator. Provide accurate, natural translations that preserve meaning and tone."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Parse response
            import json
            result = json.loads(response.choices[0].message.content)
            
            elapsed = time.time() - start
            logger.info(f"Translation complete (took {elapsed:.2f}s)")
            
            return TranslationResult(
                translated_text=result.get('translated_text', ''),
                original_text=text
            )
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise Exception(f"Failed to translate text: {str(e)}")
    
    async def analyze_speech_parallel(self, transcribed_text: str) -> Tuple[SentimentResult, TranslationResult]:
        """
        Execute sentiment analysis and translation in parallel.
        
        This method runs both operations concurrently to minimize total processing time.
        This is the recommended approach for production systems where latency matters.
        
        Args:
            transcribed_text: Text to analyze and translate
            
        Returns:
            Tuple of (SentimentResult, TranslationResult)
        """
        import time
        logger.info("Starting parallel analysis (sentiment + translation)")
        start = time.time()
        
        # Execute both tasks concurrently
        sentiment_task = self.analyze_sentiment(transcribed_text)
        translation_task = self.translate_to_hindi(transcribed_text)
        
        # Wait for both to complete
        sentiment_result, translation_result = await asyncio.gather(
            sentiment_task,
            translation_task
        )
        
        elapsed = time.time() - start
        logger.info(f"Parallel analysis complete in {elapsed:.2f}s")
        return sentiment_result, translation_result
    
    async def process_audio_file(self, audio_file_path: str) -> AnalysisResults:
        """
        Complete pipeline: Convert audio to text, then analyze sentiment and translate.
        
        This is the main entry point for processing an audio file.
        
        Args:
            audio_file_path: Path to the audio file to process
            
        Returns:
            AnalysisResults containing all results
        """
        import time
        start_time = time.time()
        
        try:
            # Step 1: Speech to Text (synchronous, must complete first)
            logger.info("Pipeline step 1/3: Speech-to-Text")
            stt_result = self.speech_to_text(audio_file_path)
            transcribed_text = stt_result.text
            
            if not transcribed_text or len(transcribed_text.strip()) == 0:
                raise Exception("No speech detected in the audio file")
            
            # Step 2 & 3: Sentiment Analysis and Translation
            logger.info(f"Pipeline steps 2-3/3: {'Parallel' if self.parallel_processing else 'Sequential'} mode")
            
            import time as time_module
            step2_start = time_module.time()
            
            if self.parallel_processing:
                # Run in parallel for better performance
                sentiment_result, translation_result = await self.analyze_speech_parallel(transcribed_text)
            else:
                # Run sequentially (if configured)
                sentiment_result = await self.analyze_sentiment(transcribed_text)
                translation_result = await self.translate_to_hindi(transcribed_text)
            
            step2_time = time_module.time() - step2_start
            logger.info(f"Sentiment + Translation took {step2_time:.2f}s in {'parallel' if self.parallel_processing else 'sequential'} mode")
            
            # Calculate total processing time
            processing_time = time.time() - start_time
            
            logger.info(f"Complete pipeline finished in {processing_time:.2f} seconds")
            
            return AnalysisResults(
                transcription=transcribed_text,
                sentiment=sentiment_result,
                translation=translation_result,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Audio processing pipeline failed: {str(e)}")
            raise
