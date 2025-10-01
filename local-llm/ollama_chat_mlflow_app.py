"""
Streamlit chat app backed by a local Ollama server (OpenAI-compatible API)
with MLflow GenAI tracing enabled via mlflow.openai.autolog().

Overview
--------
This app demonstrates how to:
- Collect chat messages in a conversational UI using Streamlit's chat components
- Send the full conversation to an Ollama model through the OpenAI Python SDK
- Enable MLflow autolog to capture traces and token usage for each LLM call
- Surface token usage (input, output, total) in the Streamlit sidebar
- Persist per-interaction token totals as MLflow metrics

Token usage semantics
---------------------
Each time you send a message, we submit the entire conversation history
(`st.session_state.messages`) to the model. Therefore, the "input tokens" for
the current interaction include tokens for the system prompt, all prior user
and assistant messages, plus the new user prompt. As the conversation grows,
the input token count generally increases accordingly.

If you need per-turn-only input tokens (excluding history), either:
- Truncate the context before calling the model, or
- Maintain your own token estimation for only the newly added prompt.

"""

import os
import mlflow
import streamlit as st
from openai import OpenAI

# Fixed configuration (set in code)
OLLAMA_BASE_URL = "http://localhost:11434/v1"
MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
MLFLOW_EXPERIMENT = "Ollama-chat"


def initialize_mlflow(tracking_uri: str | None, experiment_name: str | None) -> None:
    """
    Configure MLflow for tracing and enable OpenAI autologging.

    Parameters
    ----------
    tracking_uri : str | None
        MLflow tracking server URI. If None or empty, MLflow defaults are used.
    experiment_name : str | None
        Name of the MLflow experiment to log traces/metrics under.

    Notes
    -----
    - mlflow.openai.autolog() automatically instruments OpenAI SDK calls and
      records spans and token usage for chat completions against Ollama's
      OpenAI-compatible endpoint.
    """
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    if experiment_name:
        mlflow.set_experiment(experiment_name)
    mlflow.openai.autolog()


def get_openai_client(base_url: str) -> OpenAI:
    """
    Build an OpenAI client pointed at the local Ollama server.

    Ollama exposes an OpenAI-compatible REST API, so we can use the OpenAI
    Python SDK by specifying the base_url and any string for api_key.
    """
    return OpenAI(base_url=base_url, api_key="dummy")


def ensure_session_state() -> None:
    """
    Initialize persistent state for chat messages and token usage summaries.

    Keys added:
    - messages: list of role/content dicts forming the conversation. We seed
      this with a single system message to steer model behavior.
    - token_summaries: list of dicts; each entry corresponds to a single
      LLM call and contains input/output/total token counts and per-span usage.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    if "token_summaries" not in st.session_state:
        st.session_state.token_summaries = []


def render_sidebar() -> dict:
    """
    Render simple settings in the sidebar.

    We fix the base URL and MLflow configuration in code for simplicity.
    The only adjustable option here is the Ollama model name.
    """
    st.sidebar.header("Settings")
    model = st.sidebar.text_input(
        label="Model",
        value=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        help="Ollama model name, e.g., llama3.2:3b",
    )
    return {
        "base_url": OLLAMA_BASE_URL,
        "model": model,
        "tracking_uri": MLFLOW_TRACKING_URI or None,
        "experiment": MLFLOW_EXPERIMENT or None,
    }


def display_chat_messages() -> None:
    """
    Display the conversation so far (excluding the system message) in the
    Streamlit chat UI. Streamlit renders these with `st.chat_message`.
    """
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def log_and_display_token_usage() -> None:
    """
    Retrieve the most recent MLflow trace and append token usage info to state.

    Behavior
    --------
    - Uses mlflow.get_last_active_trace_id() to capture the trace from the
      latest OpenAI SDK call (made to Ollama)
    - Extracts total token usage for the call and logs it into
      `st.session_state.token_summaries`
    - Logs per-interaction totals as MLflow metrics for easier charting
      (tokens.input, tokens.output, tokens.total)
    - Also captures per-span usage from the trace to display granular details
    """
    try:
        last_trace_id = mlflow.get_last_active_trace_id()
        if not last_trace_id:
            return
        trace = mlflow.get_trace(trace_id=last_trace_id)
        total_usage = getattr(trace.info, "token_usage", None)
        if total_usage:
            st.session_state.token_summaries.append(
                {
                    "input_tokens": total_usage.get("input_tokens", 0),
                    "output_tokens": total_usage.get("output_tokens", 0),
                    "total_tokens": total_usage.get("total_tokens", 0),
                    "spans": [
                        {
                            "name": span.name,
                            "usage": span.get_attribute("mlflow.chat.tokenUsage"),
                        }
                        for span in (trace.data.spans or [])
                        if span.get_attribute("mlflow.chat.tokenUsage") is not None
                    ],
                }
            )
            # Persist per-interaction token counts to MLflow metrics. We use a
            # monotonically increasing `step` index aligned with the number of
            # recorded interactions so far.
            idx = len(st.session_state.token_summaries)
            mlflow.log_metrics(
                {
                    "tokens.input": total_usage.get("input_tokens", 0),
                    "tokens.output": total_usage.get("output_tokens", 0),
                    "tokens.total": total_usage.get("total_tokens", 0),
                },
                step=idx,
            )
    except Exception as e:  # noqa: BLE001
        st.warning(f"Could not retrieve MLflow token usage: {e}")


def main() -> None:
    """
    Entry point for the Streamlit application.

    Flow
    ----
    1. Initialize session state and read sidebar settings
    2. Configure MLflow and create an OpenAI client pointing to Ollama
    3. Render the current conversation and accept a new user message
    4. Call the model with the full conversation and append the assistant reply
    5. Retrieve token usage from MLflow and update the sidebar display
    """
    st.set_page_config(page_title="Ollama Chat with MLflow Tracing", page_icon="💬")
    st.title("Ollama Chat 💬 with MLflow Tracing")

    ensure_session_state()
    settings = render_sidebar()

    initialize_mlflow(settings["tracking_uri"], settings["experiment"])
    client = get_openai_client(settings["base_url"])

    display_chat_messages()

    # Streamlit chat input renders an input box at the bottom of the page. When
    # the user submits, it returns a non-empty string; otherwise returns None.
    prompt = st.chat_input("Type your message and press Enter…")
    if prompt:
        # Add the user's message to the conversation state and echo it in the UI.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call Ollama via the OpenAI SDK using the full conversation history.
        with st.chat_message("assistant"):
            try:
                response = client.chat.completions.create(
                    model=settings["model"],
                    messages=st.session_state.messages,
                )
                assistant_text = response.choices[0].message.content
                st.markdown(assistant_text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_text}
                )
                # After the API call completes, retrieve token usage from MLflow
                # and update sidebar totals/history.
                log_and_display_token_usage()
            except Exception as e:  # noqa: BLE001
                st.error(f"LLM request failed: {e}")

    # Sidebar token usage display. Shows the latest totals and an expandable
    # history of per-interaction counts. Span-level details are included for
    # additional transparency.
    with st.sidebar:
        st.subheader("Token Usage")
        if st.session_state.token_summaries:
            last_summary = st.session_state.token_summaries[-1]
            cols = st.columns(3)
            cols[0].metric("Input", last_summary["input_tokens"])
            cols[1].metric("Output", last_summary["output_tokens"])
            cols[2].metric("Total", last_summary["total_tokens"])

            with st.expander("History (per interaction)"):
                for i, summary in enumerate(st.session_state.token_summaries, start=1):
                    st.markdown(
                        f"**{i}.** input: {summary['input_tokens']}, output: {summary['output_tokens']}, total: {summary['total_tokens']}"
                    )
                    if summary.get("spans"):
                        for j, span in enumerate(summary["spans"], start=1):
                            usage = span["usage"] or {}
                            st.caption(
                                f"- {j}. {span['name']}: in {usage.get('input_tokens', 0)}, out {usage.get('output_tokens', 0)}, total {usage.get('total_tokens', 0)}"
                            )


if __name__ == "__main__":
    main()



