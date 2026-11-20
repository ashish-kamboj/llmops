import os
from typing import Dict, Any

import streamlit as st
import mlflow

from utils.config_loader import load_configs
from utils.mlflow_utils import setup_mlflow, ensure_prompt_registered, load_latest_prompt, check_prompt_exists
from utils.groq_client import init_groq_client
from utils.evaluation_utils import build_default_dataset, concept_coverage, response_length_check, is_concise, is_professional, is_accurate, is_helpful


def apply_page_config(app_cfg: Dict[str, Any]) -> None:
    st.set_page_config(
        page_title=app_cfg.get("title", "LLM Prompt Versioning & Evaluation"),
        page_icon=app_cfg.get("page_icon", "🧪"),
        layout=app_cfg.get("layout", "wide"),
    )
    # Inject custom CSS for a beautiful UI
    st.markdown(
        """
        <style>
        .stApp {background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);} 
        .block-container {padding-top: 2rem;}
        .big-title {font-size: 2.2rem; font-weight: 700; color: #E5E7EB;}
        .subtitle {color: #A5B4FC;}
        .card {background: #111827; padding: 1rem 1.25rem; border-radius: 14px; border: 1px solid rgba(255,255,255,0.08);} 
        .pill {display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; background: #1F2937; color: #C7D2FE; font-size: 0.8rem;}
        .accent {color: #8B5CF6;}
        .chat-bubble-user {background:#1E293B; padding:0.75rem 1rem; border-radius:12px; color:#E5E7EB;}
        .chat-bubble-assistant {background:#111827; padding:0.75rem 1rem; border-radius:12px; border:1px solid #1F2937; color:#E5E7EB;}
        .btn-primary {background:#6C63FF; color:white; padding:0.5rem 0.9rem; border-radius:10px; border:none;}
        .btn-primary:hover {filter: brightness(1.1);}
        
        /* Enhanced text input styling */
        .stTextInput > div > div > input {
            background-color: #2D3748 !important;
            border: 2px solid #4A5568 !important;
            border-radius: 8px !important;
            color: #E2E8F0 !important;
            padding: 0.5rem 0.75rem !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #6C63FF !important;
            box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1) !important;
        }
        
        /* Text area styling */
        .stTextArea > div > div > textarea {
            background-color: #2D3748 !important;
            border: 2px solid #4A5568 !important;
            border-radius: 8px !important;
            color: #E2E8F0 !important;
            padding: 0.5rem 0.75rem !important;
        }
        .stTextArea > div > div > textarea:focus {
            border-color: #6C63FF !important;
            box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1) !important;
        }
        
        /* Number input styling */
        .stNumberInput > div > div > input {
            background-color: #2D3748 !important;
            border: 2px solid #4A5568 !important;
            border-radius: 8px !important;
            color: #E2E8F0 !important;
            padding: 0.5rem 0.75rem !important;
        }
        .stNumberInput > div > div > input:focus {
            border-color: #6C63FF !important;
            box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1) !important;
        }
        
        /* Selectbox styling */
        .stSelectbox > div > div {
            background-color: #2D3748 !important;
            border: 2px solid #4A5568 !important;
            border-radius: 8px !important;
        }
        .stSelectbox > div > div:focus-within {
            border-color: #6C63FF !important;
            box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1) !important;
        }
        

        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    cfg = load_configs(os.path.join(os.path.dirname(__file__), "configs.yaml"))

    apply_page_config(cfg.get("app", {}))

    # Header
    st.markdown('<div class="big-title">🧪 LLM Prompt Versioning & Evaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Powered by MLflow Prompt Registry and Groq</div>', unsafe_allow_html=True)

    # Sidebar: Configs and Controls
    with st.sidebar:
        # Get values from config
        tracking_uri = cfg["mlflow"]["tracking_uri"]
        experiment_name = cfg["mlflow"]["experiment_name"]
        prompt_name = cfg["mlflow"]["prompt_name"]

        model = st.text_input("Groq Model", value=cfg["llm"]["model"])
        temperature = st.slider("Temperature", 0.0, 1.0, float(min(max(cfg["llm"]["temperature"], 0.0), 1.0)))
        max_tokens = st.number_input("Max Tokens", min_value=32, max_value=4096, value=int(cfg["llm"]["max_tokens"]))

        st.divider()
        st.caption("Groq API")
        api_present = os.getenv("GROQ_API_KEY") is not None
        st.markdown(f"API Key set: {'✅' if api_present else '❌'} (from .env file)")

        st.divider()
        
        # Collapsible prompt registration section
        with st.expander("Register New Prompt Version", expanded=False):
            with st.form("register_prompt_form"):
                system_prompt = st.text_area("System Message", value="You are a knowledgeable AI assistant. Provide accurate, helpful, and detailed answers to user questions.", height=120)
                user_prompt = st.text_area("User Template", value="Question: {{question}}", height=80)
                commit_message = st.text_input("Commit Message", value="New prompt version from Streamlit app")
                submitted = st.form_submit_button("Register Prompt Version", use_container_width=True)

            if submitted:
                setup_mlflow(tracking_uri, experiment_name)
                try:
                    template = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ]
                    # ensure_prompt_registered returns True if new version created, False if duplicate
                    version_created = ensure_prompt_registered(prompt_name, template, commit_message)
                    
                    if version_created:
                        st.success("✅ Prompt registered successfully. New version created.")
                        st.rerun()  # Refresh to show the new prompt is available
                    else:
                        st.warning("⚠️ This prompt is identical to the latest version. No new version created.")
                except Exception as e:
                    st.error(f"Failed to register prompt: {e}")

    # Initialize MLflow and client
    try:
        setup_mlflow(tracking_uri, experiment_name)
        groq_client = init_groq_client()
        
        # Check if prompt exists, but don't create one automatically
        if not check_prompt_exists(prompt_name):
            st.info(f"ℹ️ No prompt '{prompt_name}' found. Please register a prompt using the sidebar to start chatting or running evaluations.")
    except Exception as e:
        st.error(f"Initialization error: {e}")
        st.stop()

    # Tabs: Chat | Evaluation
    tab_chat, tab_eval, tab_runs = st.tabs(["💬 Chat", "📊 Evaluation", "📁 MLflow Runs"])

    with tab_chat:
        st.subheader("Chat with Latest Prompt")
        st.caption("The chat always uses the latest registered prompt.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Clear chat button
        if st.button("🗑️ Clear Chat", help="Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()

        # Input row
        col1, col2 = st.columns([5,1])
        with col1:
            user_question = st.text_input("Ask a question", key="chat_input", placeholder="Type your question...", help="Press Enter to send")
        with col2:
            send = st.button("Send", use_container_width=True)

        if send and user_question.strip():
            # Append user message
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            # Show processing indicator
            with st.spinner("Generating response..."):
                # Build messages from latest prompt
                try:
                    prompt = load_latest_prompt(prompt_name)
                    rendered = prompt.format(question=user_question)
                    messages = [{"role": m["role"], "content": m["content"]} for m in rendered]
                    # Call Groq
                    response = groq_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=float(temperature),
                        max_tokens=int(max_tokens),
                        top_p=1.0,
                        stream=False,
                    )
                    answer = response.choices[0].message.content
                except Exception as e:
                    if "RESOURCE_DOES_NOT_EXIST" in str(e):
                        answer = f"Error: Prompt '{prompt_name}' not found. Please register a prompt first using the sidebar."
                    else:
                        answer = f"Error: {e}"
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            
            # Clear the input after sending
            st.rerun()

        # Render history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-bubble-user'>🙂 <strong>You:</strong> {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-assistant'>🤖 <strong>Assistant:</strong> {msg['content']}</div>", unsafe_allow_html=True)

    with tab_eval:
        st.subheader("Evaluation")
        st.caption("Run evaluation on a dataset against the latest prompt and log results to MLflow.")

        # Dataset builder
        st.markdown("#### Dataset")
        default_data = build_default_dataset(cfg["evaluation"])
        if "eval_data" not in st.session_state:
            st.session_state.eval_data = default_data.copy()

        with st.expander("Add new evaluation row"):
            q = st.text_input("Question")
            expected = st.text_input("Expected key concepts (comma-separated)")
            topic = st.text_input("Topic", value="general")
            difficulty = st.selectbox("Difficulty", ["basic", "intermediate", "advanced"], index=1)
            if st.button("Add to dataset"):
                row = {
                    "inputs": {"question": q},
                    "expectations": {"key_concepts": [s.strip() for s in expected.split(",") if s.strip()]},
                    "tags": {"topic": topic, "difficulty": difficulty},
                }
                st.session_state.eval_data.append(row)

        st.write({"rows": len(st.session_state.eval_data)})
        st.dataframe(
            [{"question": r["inputs"]["question"], "concepts": ", ".join(r["expectations"].get("key_concepts", [])), "topic": r["tags"].get("topic"), "difficulty": r["tags"].get("difficulty")} for r in st.session_state.eval_data],
            use_container_width=True,
            hide_index=True,
        )

        # Evaluation controls
        max_length = st.number_input("Max words (response length check)", min_value=20, max_value=400, value=int(cfg["evaluation"].get("response_length_max", 100)))
        run_eval = st.button("Run Evaluation", type="primary", use_container_width=True)

        if run_eval:
            # Check if prompt exists before running evaluation
            try:
                load_latest_prompt(prompt_name)
            except Exception as e:
                if "RESOURCE_DOES_NOT_EXIST" in str(e):
                    st.error(f"Prompt '{prompt_name}' not found. Please register a prompt first using the sidebar.")
                    st.stop()
                else:
                    st.error(f"Error loading prompt: {e}")
                    st.stop()
            
            # Define predict function inline to capture current params
            @mlflow.trace
            def predict_fn(question: str) -> str:
                try:
                    prompt = load_latest_prompt(prompt_name)
                    rendered = prompt.format(question=question)
                    messages = [{"role": m["role"], "content": m["content"]} for m in rendered]
                    resp = groq_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=float(temperature),
                        max_tokens=int(max_tokens),
                        top_p=1.0,
                        stream=False,
                    )
                    return resp.choices[0].message.content
                except Exception as e:
                    if "RESOURCE_DOES_NOT_EXIST" in str(e):
                        return f"Error: Prompt '{prompt_name}' not found. Please register a prompt first."
                    else:
                        return f"Error: {e}"

            # Scorers
            from mlflow.genai import evaluate

            st.info("Starting evaluation... this may take a while depending on dataset size.")
            all_scorers = [
                # LLM-based scorers using Groq API
                is_concise,           # Evaluates brevity and directness
                is_professional,      # Evaluates tone and professionalism  
                is_accurate,          # Evaluates factual correctness
                is_helpful,           # Evaluates usefulness and relevance
                # Heuristic scorers
                concept_coverage,     # Evaluates coverage of key concepts
                response_length_check # Evaluates appropriate response length
            ]
            # Enrich expectations with max_length for response_length_check
            data = []
            for item in st.session_state.eval_data:
                item_copy = {**item}
                exp = dict(item_copy.get("expectations", {}))
                exp["max_length"] = max_length
                item_copy["expectations"] = exp
                data.append(item_copy)

            try:
                results = evaluate(data=data, predict_fn=predict_fn, scorers=all_scorers)
                st.success(f"Evaluation complete. Run ID: {results.run_id}")
                st.session_state.last_run_id = results.run_id
            except Exception as e:
                st.error(f"Evaluation failed: {e}")

    with tab_runs:
        st.subheader("MLflow Runs")
        st.caption("Quick links to MLflow UI for the configured tracking server.")
        
        # Main MLflow UI link
        mlflow_url = f"{tracking_uri}"
        st.markdown(f"**MLflow UI:** <a class='pill' href='{mlflow_url}' target='_blank'>{mlflow_url}</a>", unsafe_allow_html=True)
        
        st.divider()
        
        # Experiment-specific links
        st.markdown("#### Experiment Links")
        # Get experiment ID from MLflow
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment:
                experiment_id = experiment.experiment_id
                experiment_url = f"{tracking_uri}/#/experiments/{experiment_id}/"
                st.markdown(f"**Experiment:** <a class='pill' href='{experiment_url}' target='_blank'>{experiment_name}</a>", unsafe_allow_html=True)
            else:
                st.caption(f"Experiment '{experiment_name}' not found")
        except Exception as e:
            st.caption(f"Could not get experiment ID: {e}")
            # Fallback to experiment name
            experiment_url = f"{tracking_uri}/#/experiments/{experiment_name}/"
            st.markdown(f"**Experiment:** <a class='pill' href='{experiment_url}' target='_blank'>{experiment_name}</a>", unsafe_allow_html=True)
        
        # Prompt Registry link
        st.markdown("#### Prompt Registry")
        prompt_registry_url = f"{tracking_uri}/#/prompts"
        st.markdown(f"**Prompt Registry:** <a class='pill' href='{prompt_registry_url}' target='_blank'>View All Prompts</a>", unsafe_allow_html=True)
        
        # Specific prompt link
        prompt_url = f"{tracking_uri}/#/prompts/{prompt_name}"
        st.markdown(f"**Current Prompt:** <a class='pill' href='{prompt_url}' target='_blank'>{prompt_name}</a>", unsafe_allow_html=True)
        
        st.divider()
        
        # Recent evaluation runs
        st.markdown("#### Recent Evaluation Runs")
        if "last_run_id" in st.session_state:
            # Get experiment ID for the evaluation runs link
            try:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                if experiment:
                    experiment_id = experiment.experiment_id
                    run_url = f"{tracking_uri}/#/experiments/{experiment_id}/evaluation-runs?selectedRunUuid={st.session_state.last_run_id}"
                else:
                    # Fallback to experiment name
                    run_url = f"{tracking_uri}/#/experiments/{experiment_name}/evaluation-runs?selectedRunUuid={st.session_state.last_run_id}"
            except Exception:
                # Fallback to experiment name
                run_url = f"{tracking_uri}/#/experiments/{experiment_name}/evaluation-runs?selectedRunUuid={st.session_state.last_run_id}"
            
            st.markdown(f"**Last Run:** <a class='pill' href='{run_url}' target='_blank'>{st.session_state.last_run_id}</a>", unsafe_allow_html=True)
        else:
            st.caption("No evaluation runs yet. Run an evaluation to see results here.")
        
        # Instructions
        st.divider()
        st.markdown("#### How to Use")
        st.markdown("""
        - **Experiment**: View all runs and metrics for this experiment
        - **Prompt Registry**: Manage and version your prompts
        - **Current Prompt**: View the specific prompt being used
        - **Last Run**: View the most recent evaluation results
        """)


if __name__ == "__main__":
    main()
