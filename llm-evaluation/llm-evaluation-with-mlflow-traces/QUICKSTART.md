# Quick Start Guide

# Quick Start Guide

Get started with LLM evaluation in 5 minutes!

## Prerequisites
- Python 3.8+
- Groq API account (free tier available)

## Step-by-Step Setup

### 1. Install Dependencies (2 minutes)

```bash
cd llm-evaluation-from-mlflow-traces
pip install -r requirements.txt
```

### 2. Configure API Key (1 minute)

Edit the `.env` file and add your Groq API key:

```bash
# Open .env file
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

Add your key:
```
GROQ_API_KEY=gsk_your_actual_api_key_here
```

Get your free API key from: https://console.groq.com/

### 3. (Optional) Customize Configuration (2 minutes)

Edit `config.yaml` to customize:

```yaml
# Change which models to test
ab_testing:
  test_models:
    - "llama-3.1-8b"     # Fast model
    - "llama-3.1-70b"    # Accurate model

# Add your own test questions
sample_questions:
  - "What is machine learning?"
  - "Your custom question here"

# Adjust model parameters
groq:
  default_temperature: 0.7  # 0.0 = deterministic, 1.0 = creative
  max_tokens: 500           # Response length limit
```

### 4. Run the Notebook (< 1 minute)

Open in VS Code or Jupyter and run all cells:

```bash
# Open in VS Code
code llm_evaluation_with_traces.ipynb

# Or use Jupyter
jupyter notebook llm_evaluation_with_traces.ipynb
```

Click "Run All" or press `Ctrl+Shift+Enter` repeatedly.

## What You'll Get

After running:

✅ **6 conversations** with LLM responses  
✅ **MLflow traces** captured automatically  
✅ **Evaluation metrics** calculated (ROUGE, BLEU, METEOR)  
✅ **A/B test results** comparing models  
✅ **5 visualization charts** (PNG files)  
✅ **Statistical analysis** of model performance  

## View Results

### In the Notebook
Scroll through cells to see:
- Conversation examples
- Metric scores per conversation
- Overall performance statistics
- Model comparison tables

### In MLflow UI

```bash
mlflow ui --port 5000
```

Open browser: http://localhost:5000

Navigate to:
- **Experiments** → `llm-chat-evaluation-groq`
- **Traces** tab for detailed interactions
- **Datasets** tab for evaluation data

### Visualization Files

Check these generated PNG files:
1. `evaluation_metrics_comparison.png` - Bar charts
2. `model_performance_radar.png` - Radar chart
3. `metrics_correlation_heatmap.png` - Correlation matrix
4. `token_efficiency_vs_performance.png` - Cost analysis
5. `metrics_distribution_boxplot.png` - Statistical distribution

## Common Customizations

### Test Different Models

Edit `config.yaml`:
```yaml
ab_testing:
  test_models:
    - "mixtral-8x7b"
    - "gemma-7b"
```

### Add More Questions

Edit `config.yaml`:
```yaml
sample_questions:
  - "Explain blockchain technology"
  - "What is DevOps?"
  - "How does neural network work?"
```

### Change Temperature for Creativity

Edit `config.yaml`:
```yaml
groq:
  default_temperature: 1.0  # More creative
  # or
  default_temperature: 0.3  # More focused
```

### Enable/Disable Metrics

Edit `config.yaml`:
```yaml
evaluation:
  metrics:
    rouge:
      enabled: true
    bleu:
      enabled: false  # Disable BLEU
```

## Troubleshooting

### "GROQ_API_KEY not found"
- Check `.env` file exists
- Ensure no spaces around the `=` sign
- Restart notebook kernel after editing

### "Module not found"
```bash
pip install -r requirements.txt
```

### "NLTK data not found"
The notebook auto-downloads. If issues persist:
```python
import nltk
nltk.download('punkt')
nltk.download('wordnet')
```

### "Port 5000 already in use"
```bash
mlflow ui --port 5001
```

## Next Steps

1. **Add your own questions** to `config.yaml`
2. **Test more models** by editing the model list
3. **Adjust quality thresholds** for your use case
4. **Integrate with your application** for production evaluation
5. **Schedule periodic evaluations** for monitoring

## Key Files

- `config.yaml` - **All configuration** (edit this!)
- `.env` - **API keys only**
- `llm_evaluation_with_traces.ipynb` - Main notebook (don't edit unless adding features)
- `requirements.txt` - Dependencies

## Need Help?

- Check `README.md` for detailed documentation
- Review `config.yaml` comments for parameter descriptions
- See notebook markdown cells for explanations

## That's It!

You're ready to evaluate LLMs systematically. Happy testing! 🚀

## Prerequisites

- Python 3.8+
- Groq API account (free tier available)

## Step-by-Step Setup

### 1. Clone/Navigate to Directory

```bash
cd llm-evaluation-from-mlflow-traces
```

### 2. Create Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Your Groq API Key

1. Go to https://console.groq.com/
2. Sign up (free)
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `gsk_...`)

### 5. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env and paste your API key
# On Windows: notepad .env
# On Linux/Mac: nano .env
```

Your `.env` should look like:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

### 6. Run the Notebook

**Option A: VS Code**
```bash
code llm_evaluation_with_traces.ipynb
```
- Select Python kernel
- Run all cells (Ctrl+Shift+P → "Run All")

**Option B: Jupyter**
```bash
jupyter notebook llm_evaluation_with_traces.ipynb
```
- Click "Run All" in the Cell menu

### 7. View Results

The notebook will:
- ✅ Generate 6 conversations with 2 different models
- ✅ Evaluate using 6 different metrics
- ✅ Create 5 visualizations (PNG files)
- ✅ Display A/B testing comparison
- ✅ Save traces to MLflow

### 8. Explore MLflow UI (Optional)

```bash
mlflow ui --port 5000
```

Open browser: http://localhost:5000

Navigate to:
- **Experiments** → `llm-chat-evaluation-groq`
- View traces, metrics, and comparisons

## What You'll Get

### Console Output
```
✓ Groq client initialized
✓ Generated 6 conversations with traces
✓ Added expectations to 6 traces
✓ Evaluated 6 conversations

📊 Overall Performance Metrics:
ROUGE-1  | Mean: 0.452 | Std: 0.123 ...
BLEU     | Mean: 0.384 | Std: 0.098 ...

🏆 A/B Test Winners:
ROUGE-1 | Winner: llama-3.1-70b | Score: 0.512
```

### Generated Files
```
evaluation_metrics_comparison.png    # Bar charts
model_performance_radar.png          # Radar chart
metrics_correlation_heatmap.png      # Correlation matrix
token_efficiency_vs_performance.png  # Scatter plot
metrics_distribution_boxplot.png     # Box plots
```

### MLflow Tracking
- All traces stored in `mlruns/`
- Datasets created for reuse
- Metrics logged for comparison

## Troubleshooting

### Error: "GROQ_API_KEY not found"
- Check `.env` file exists
- Ensure no spaces around `=`
- Key should start with `gsk_`

### Error: "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Error: "NLTK data not found"
```python
import nltk
nltk.download('punkt')
nltk.download('wordnet')
```

### Rate Limiting
- Free tier: ~30 requests/minute
- Add `time.sleep(2)` between calls if needed

## Next Steps

After running successfully:

1. **Modify Questions**: Edit `sample_questions` list
2. **Add More Models**: Include `mixtral-8x7b` or `gemma-7b`
3. **Custom Metrics**: Implement domain-specific evaluation
4. **Scale Up**: Test with 50+ conversations
5. **Production**: Integrate with your application

## Need Help?

- Check `README.md` for detailed documentation
- Review notebook markdown cells for explanations
- Open an issue if you find bugs

## Success Checklist

- [ ] Groq API key configured
- [ ] All dependencies installed
- [ ] Notebook runs without errors
- [ ] 5 PNG files generated
- [ ] MLflow UI accessible
- [ ] A/B test results displayed

**Estimated Time**: 5-10 minutes

Happy evaluating! 🚀
