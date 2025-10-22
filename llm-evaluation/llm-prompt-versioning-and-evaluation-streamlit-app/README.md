# LLM Prompt Versioning & Evaluation (Streamlit)

A beautiful Streamlit app to manage prompt versions with MLflow Prompt Registry, chat using the latest prompt, and run evaluations with Groq.

## Features
- Register new prompt versions; MLflow handles versioning
- Chat tab always uses the latest prompt
- Build and edit evaluation dataset in the UI
- Run evaluation with heuristic scorers (concept coverage, response length)
- Links to MLflow UI for viewing runs and results

## Not Included (per requirements)
- Alternative Guidelines with Custom Model section
- Iterative prompt improvement code (Step 7)
- Advanced features and tips (Step 8)

## Setup
1. Create and activate a virtual environment (optional)
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up your .env file:
   - Edit the `.env` file in this directory (`llm-evaluation-streamlit-code/.env`)
   - Set your `GROQ_API_KEY` in the .env file
   - Optionally override other settings (MLflow URI, experiment name, etc.)
4. Start MLflow UI in another terminal (if not already running):
```bash
mlflow ui
```

## Run
```bash
streamlit run app.py
```

## Configs
- Edit `configs.yaml` to change default dataset, prompt name, and parameters.
- In the sidebar, you can override MLflow and model parameters at runtime.

## Notes
- The chat and evaluation both load `prompts:/<prompt_name>@latest` from MLflow.
- Prompt versions are created via the sidebar form.
- Evaluation scorers are simple and fast; you can add LLM-based scorers later if desired.
