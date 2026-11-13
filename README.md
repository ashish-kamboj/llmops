
What is LLM?
---
- LLM stands for Large Language Model, which is a type of artificial intelligence that can process and generate natural language text in a seemingly human manner. LLMs are trained on a huge amount of text data, mostly collected from the internet, to learn the patterns and rules of language. LLMs can then use this knowledge to answer questions, write essays, create stories, code software, and more, depending on the task and the prompt given by the user.
- LLMs are transformer based models

Current LLM models
---
 - GPT-4
 - GPT-3.5
 - LLaMA
 - LaMDA
 - BLOOM
 - Dolly

What is LLMOps?
---
- LLMOps is for fine-tuning, versioning, deploying and monitoring LLM models
- LLMOps encompasses the experimentation, iteration, deployment and continuous improvement of the LLM development lifecycle.

How is LLMOps different from MLOps?
---

- <ins>**Computational resources:**</ins> Training and fine-tuning large language models typically involves performing orders of magnitude more calculations on large data sets. To speed this process up, specialized hardware like GPUs is used for much faster data-parallel operations. Having access to these specialized compute resources becomes essential for both training and deploying large language models. The cost of inference can also make model compression and distillation techniques important.
- <ins>**Transfer learning:**</ins>  Unlike many traditional ML models that are created or trained from scratch, many large language models start from a foundation model and are fine-tuned with new data to improve performance in a more specific domain. Fine-tuning allows state-of-the-art performance for specific applications using less data and fewer compute resources.
- <ins>**Human feedback:**</ins>  One of the major improvements in training large language models has come through reinforcement learning from human feedback (RLHF). More generally, since LLM tasks are often very open ended, human feedback from your application’s end users is often critical for evaluating LLM performance. Integrating this feedback loop within your LLMOps pipelines both simplifies evaluation and provides data for future fine-tuning of your LLM.
- <ins>**Hyperparameter tuning:**</ins>  In classical ML, hyperparameter tuning often centers on improving accuracy or other metrics. For LLMs, tuning also becomes important for reducing the cost and computational power requirements of training and inference. For example, tweaking batch sizes and learning rates can dramatically change the speed and cost of training. Thus, both classical ML models and LLMs benefit from tracking and optimizing the tuning process, but with different emphases.
- <ins>**Performance metrics:**</ins>  Traditional ML models have very clearly defined performance metrics, such as accuracy, AUC, F1 score, etc. These metrics are fairly straightforward to calculate. When it comes to evaluating LLMs, however, a whole different set of standard metrics and scoring apply — such as 
	- ***bilingual evaluation understudy (BLEU)***
	- ***Recall-Oriented Understudy for Gisting Evaluation (ROUGE)***
	- Compares the machine/system generated text with the reference text (summarized or translated)
- <ins>**Prompt engineering:**</ins>  Instruction-following models can take complex prompts, or sets of instructions. Engineering these prompt templates is critical for getting accurate, reliable responses from LLMs. Prompt engineering can reduce the risk of model hallucination and prompt hacking, including prompt injection, leaking of sensitive data and jailbreaking.
- <ins>**Building LLM chains or pipelines:**</ins>  LLM pipelines, built using tools like  [LangChain](https://python.langchain.com/en/latest/index.html)  or  [LlamaIndex](https://github.com/jerryjliu/llama_index), string together multiple LLM calls and/or calls to external systems such as vector databases or web search. These pipelines allow LLMs to be used for complex tasks such as knowledge base Q&A, or answering user questions based on a set of documents. LLM application development often focuses on building these pipelines, rather than building new LLMs.
 

Vector database
---
https://learn.microsoft.com/en-us/semantic-kernel/memories/vector-db

Vector databases benchmarking
---

References
---
- https://www.databricks.com/glossary/llmops
- https://www.databricks.com/product/machine-learning/large-language-models
- https://www.freecodecamp.org/news/what-is-rouge-and-how-it-works-for-evaluation-of-summaries-e059fb8ac840/
- https://www.databricks.com/resources/webinar/build-your-own-large-language-model-dolly/thank-you?itm_data=llm-resources-dollywebinar
- https://www.dbdemos.ai/demo.html?demoName=llm-dolly-chatbot
- https://valohai.com/blog/llmops/
