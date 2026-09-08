"""
BasicRAGEvaluator for simple RAG agents using local documents.

This evaluator is designed for RAG agents that retrieve context from a local
vector store and generate answers using an LLM.
"""

from typing import Optional, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_ibm import WatsonxLLM, WatsonxEmbeddings
from langgraph.graph import START, END, StateGraph
from langgraph.config import RunnableConfig

from ibm_watsonx_gov.evaluators.agentic_evaluator import AgenticEvaluator
from ibm_watsonx_gov.entities.state import EvaluationState
from ibm_watsonx_gov.config.agentic_ai_configuration import TracingConfiguration

from .base_evaluator import BaseAgentEvaluator
from .config import WatsonxConfig, EvaluationConfig, VectorStoreConfig, LLMConfig
from .utils.vector_store import create_vector_store


class AppState(EvaluationState):
    """State for Basic RAG agent."""
    pass


class BasicRAGEvaluator(BaseAgentEvaluator):
    """Evaluator for basic RAG agents with local document retrieval.

    This evaluator creates and evaluates a simple RAG agent that:
    1. Retrieves relevant context from a local vector store
    2. Generates answers using an LLM

    Metrics evaluated:
    - Context relevance
    - Faithfulness
    - Answer similarity
    - Retrieval/generation latency
    - Token counts and cost

    Example:
        ```python
        from wx_gov_agent_eval import BasicRAGEvaluator

        evaluator = BasicRAGEvaluator()

        # Build agent with your documents
        evaluator.build_agent(documents=my_docs)

        # Evaluate
        result = evaluator.evaluate_single(
            input_text="What is AI?",
            ground_truth="AI is..."
        )

        # Get metrics
        evaluator.display_results()
        ```
    """

    def __init__(
        self,
        watsonx_config: Optional[WatsonxConfig] = None,
        eval_config: Optional[EvaluationConfig] = None,
        vector_store_config: Optional[VectorStoreConfig] = None,
        llm_config: Optional[LLMConfig] = None,
        **kwargs
    ):
        """Initialize BasicRAGEvaluator.

        Args:
            watsonx_config: Watsonx configuration.
            eval_config: Evaluation configuration.
            vector_store_config: Vector store configuration.
            llm_config: LLM configuration.
            **kwargs: Additional arguments passed to BaseAgentEvaluator.
        """
        super().__init__(watsonx_config, eval_config, **kwargs)

        self.vector_store_config = vector_store_config or VectorStoreConfig()
        self.llm_config = llm_config or LLMConfig()
        self.vector_store = None
        self.retriever = None

    def build_agent(
        self,
        documents: Any,
        vector_store_path: Optional[str] = None
    ) -> Any:
        """Build the basic RAG agent.

        Args:
            documents: Documents to index (list of dicts, path to PDF, or URL).
            vector_store_path: Optional existing vector store path.

        Returns:
            Compiled LangGraph agent.
        """
        # Create vector store
        if vector_store_path is None:
            self.vector_store = create_vector_store(
                documents=documents,
                embedding_model_id=self.vector_store_config.embedding_model_id,
                apikey=self.config.apikey,
                project_id=self.config.project_id,
                chunk_size=self.vector_store_config.chunk_size,
                chunk_overlap=self.vector_store_config.chunk_overlap,
                persist_directory=self.vector_store_config.persist_directory
            )
        else:
            from langchain_community.vectorstores import Chroma
            from langchain_ibm import WatsonxEmbeddings

            embedding_model = WatsonxEmbeddings(
                model_id=self.vector_store_config.embedding_model_id,
                url=self.config.url,
                apikey=self.config.apikey,
                project_id=self.config.project_id,
            )
            self.vector_store = Chroma(
                persist_directory=vector_store_path,
                embedding_function=embedding_model
            )

        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": self.vector_store_config.top_k,
                "score_threshold": self.vector_store_config.similarity_threshold
            }
        )

        # Setup evaluator
        self.evaluator = self._setup_evaluator()

        # Build graph
        self.agent = self._build_graph()

        return self.agent

    def _setup_evaluator(self) -> AgenticEvaluator:
        """Setup the AgenticEvaluator with metrics for basic RAG."""
        tracing_config = TracingConfiguration(project_id=self.config.project_id) if self.eval_config.enable_tracing else None

        return AgenticEvaluator(tracing_configuration=tracing_config)

    def _build_graph(self) -> Any:
        """Build the LangGraph for basic RAG."""
        evaluator = self.evaluator

        @evaluator.evaluate_context_relevance(compute_real_time=self.eval_config.compute_real_time)
        def retrieval_node(state: AppState, config: RunnableConfig) -> dict:
            context = self.retriever.invoke(state.input_text)
            return {"context": [doc.page_content for doc in context]}

        @evaluator.evaluate_faithfulness(compute_real_time=self.eval_config.compute_real_time)
        @evaluator.evaluate_answer_similarity(compute_real_time=self.eval_config.compute_real_time)
        def generate_node(state: AppState, config: RunnableConfig) -> dict:
            generate_prompt = ChatPromptTemplate.from_template(
                "Answer the following question based on the given context:\n"
                "Context: {context}\n"
                "Question: {input_text}\n"
                "Answer:"
            )

            formatted_prompt = generate_prompt.invoke(
                {"input_text": state.input_text, "context": "\n".join(state.context)}
            )

            llm = WatsonxLLM(
                model_id=self.llm_config.model_id,
                url=self.config.url,
                project_id=self.config.project_id,
                params={
                    "max_new_tokens": self.llm_config.max_new_tokens,
                    "decoding_method": self.llm_config.decoding_method,
                    "repetition_penalty": self.llm_config.repetition_penalty,
                    "stop_sequences": self.llm_config.stop_sequences,
                },
            )

            result = llm.invoke(formatted_prompt)
            output_text = result.content if hasattr(result, "content") else result

            return {"generated_text": output_text}

        graph = StateGraph(AppState)
        graph.add_node("Retrieval Node", retrieval_node)
        graph.add_node("Generation Node", generate_node)
        graph.add_edge(START, "Retrieval Node")
        graph.add_edge("Retrieval Node", "Generation Node")
        graph.add_edge("Generation Node", END)

        return graph.compile()
