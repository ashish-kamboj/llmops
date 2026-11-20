# LLM Evaluation with MLflow Traces and Groq API

## Overview

This notebook demonstrates **end-to-end LLM evaluation** using:
- **MLflow** for trace capture and dataset management
- **Groq API** for fast LLM inference
- **Advanced metrics**: ROUGE, BLEU, METEOR, Semantic Similarity
- **A/B Testing** between different models
- **Comprehensive visualizations** of evaluation results

## Features

✅ Real-world chat simulation with Groq-powered LLMs  
✅ Automatic trace capture with MLflow  
✅ Ground truth annotation (expectations)  
✅ Dataset building from traces  
✅ Industry-standard evaluation metrics (ROUGE, BLEU, METEOR)  
✅ A/B testing framework for model comparison  
✅ Beautiful visualizations (radar charts, heatmaps, box plots)  
✅ Token efficiency analysis  

## Setup Instructions

### 1. Install Dependencies

```bash
pip install mlflow groq pandas numpy matplotlib seaborn rouge-score nltk python-dotenv scikit-learn
```

### 2. Get Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Generate an API key

### 3. Configure Environment and Settings

**A. Set up API key in `.env`:**

Edit `.env` file (already exists):
```
GROQ_API_KEY=your_actual_api_key_here
```

**B. Configure parameters in `config.yaml`:**

The `config.yaml` file contains ALL configurable parameters:
- Groq models and settings
- A/B testing configuration
- Evaluation metrics
- Sample questions and expected answers
- Visualization settings
- MLflow configuration

**No need to modify the notebook code - just edit config.yaml!**

### 4. Run the Notebook

Open `llm_evaluation_with_traces.ipynb` in Jupyter or VS Code and run all cells.

## What Gets Evaluated?

### Evaluation Metrics Explained

| Metric | Description | Range | Best Use Case |
|--------|-------------|-------|---------------|
| **ROUGE-1** | Unigram (single word) overlap | 0-1 | Content recall |
| **ROUGE-2** | Bigram (two-word phrase) overlap | 0-1 | Phrase accuracy |
| **ROUGE-L** | Longest common subsequence | 0-1 | Sentence structure |
| **BLEU** | N-gram precision with brevity penalty | 0-1 | Translation quality |
| **METEOR** | Advanced metric with synonyms | 0-1 | Semantic similarity |
| **Semantic Similarity** | Jaccard word overlap | 0-1 | Lexical similarity |

## A/B Testing with Groq

The notebook supports A/B testing between different Groq models:

- **llama-3.1-8b-instant**: Fast, efficient, good for high-volume
- **llama-3.1-70b-versatile**: Slower but more accurate
- **mixtral-8x7b-32768**: Good reasoning, large context
- **gemma-7b-it**: Efficient instruction-following

### A/B Testing Strategies

1. **Model Comparison** (✅ Implemented)
   - Compare different model architectures
   - Analyze performance vs cost tradeoffs

2. **Temperature Testing** (Example provided)
   - Test creativity vs determinism
   - Range: 0.0 (focused) to 2.0 (creative)

3. **Prompt Engineering**
   - Test different system prompts
   - Compare instruction formats

4. **Context Window Testing**
   - Vary context lengths
   - Measure performance degradation

## Visualization Outputs

The notebook generates 5 comprehensive visualizations:

1. **evaluation_metrics_comparison.png**: Bar charts comparing all metrics across models
2. **model_performance_radar.png**: Radar chart for holistic comparison
3. **metrics_correlation_heatmap.png**: Understand metric relationships
4. **token_efficiency_vs_performance.png**: Cost-benefit analysis
5. **metrics_distribution_boxplot.png**: Statistical distribution of scores

## MLflow UI

View all results in the MLflow UI:

```bash
mlflow ui --port 5000
```

Then open: http://localhost:5000

Navigate to:
- **Experiments** → `llm-chat-evaluation-groq`
- **Traces** tab for interaction details
- **Datasets** tab for evaluation datasets
- **Compare runs** for model comparison

## Configuration File (config.yaml)

**🎯 All parameters are now centralized in `config.yaml`!**

No need to modify the notebook code. Just edit the config file to:

### Groq Settings
- Change models for A/B testing
- Adjust temperature, max_tokens, top_p
- Modify system prompt

### Sample Questions
- Add/remove test questions
- Customize expected answers
- Set quality metrics

### Evaluation Metrics
- Enable/disable metrics (ROUGE, BLEU, METEOR)
- Set quality thresholds
- Configure scoring parameters

### Visualization
- Adjust figure sizes
- Change colors
- Modify output filenames

### MLflow
- Set tracking URI
- Configure experiment name
- Control auto-logging

**Example config.yaml structure:**
```yaml
groq:
  default_model: "llama-3.1-8b"
  default_temperature: 0.7
  max_tokens: 500

ab_testing:
  enabled: true
  test_models:
    - "llama-3.1-8b"
    - "llama-3.1-70b"

sample_questions:
  - "Your question here"
  
expected_answers:
  - question: "Your question"
    answer: "Expected answer"
    quality_metrics:
      relevance: 1.0
```

## Project Structure

```
llm-evaluation-from-mlflow-traces/
├── llm_evaluation_with_traces.ipynb  # Main notebook
├── config.yaml                        # 🌟 Central configuration file
├── .env                               # API keys
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── mlruns/                            # MLflow tracking data
├── evaluation_metrics_comparison.png  # Generated visualizations
├── model_performance_radar.png
├── metrics_correlation_heatmap.png
├── token_efficiency_vs_performance.png
└── metrics_distribution_boxplot.png
```

## Key Concepts

### The Evaluation Loop

```
User Question → LLM Response → Capture Trace → Add Expectations → 
Build Dataset → Run Evaluation → Analyze Results → Iterate
```

### Expectations (Ground Truth)

Expectations are reference answers or quality metrics that define "good" responses:
- **Reference answers**: Expert-written ideal responses
- **Quality metrics**: Relevance, accuracy, completeness scores
- **Boolean flags**: is_helpful, is_factual, has_citations

### Why Build Datasets from Traces?

- ✅ Capture **real user interactions**
- ✅ **Evolve** your test suite over time
- ✅ **Systematic evaluation** across model versions
- ✅ **Compare** different models consistently
- ✅ **Track improvements** over iterations

## Advanced Usage

### Custom Evaluation Metrics

Add your own metrics in the evaluation section:

```python
def custom_metric(prediction: str, reference: str) -> float:
    # Your evaluation logic
    return score

# Add to evaluation
result = evaluate_response(prediction, reference)
result['custom_metric'] = custom_metric(prediction, reference)
```

### Production Integration

For production use:
1. Capture traces automatically from live traffic
2. Queue for human annotation (expectations)
3. Periodically build datasets
4. Run scheduled evaluations
5. Alert on metric degradation

## Troubleshooting

### Common Issues

**1. GROQ_API_KEY not found**
- Ensure `.env` file exists in the same directory
- Check the API key is correctly formatted

**2. NLTK data not found**
- Run: `nltk.download('punkt')` and `nltk.download('wordnet')`

**3. MLflow UI not loading**
- Ensure mlflow is running: `mlflow ui --port 5000`
- Check port 5000 is not in use

**4. Rate limiting from Groq**
- Add delays between API calls
- Use a paid plan for higher limits

## Resources

- [MLflow GenAI Documentation](https://mlflow.org/docs/latest/genai/)
- [Groq API Documentation](https://console.groq.com/docs)
- [ROUGE Metric Paper](https://aclanthology.org/W04-1013/)
- [BLEU Metric Paper](https://aclanthology.org/P02-1040/)

## License

MIT License - feel free to use and modify for your projects!

## Contributing

Suggestions and improvements welcome! Open an issue or submit a PR.
