"""
AdvancedRAGEvaluator for multi-source RAG agents with routing logic.

This evaluator is designed for advanced RAG agents that intelligently route
queries to different retrieval sources (local vector store, web search, etc.)
based on the query type.
"""

from typing import Optional, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_ibm import WatsonxLLM
from langgraph.graph import START, END, StateGraph
from langgraph.config import RunnableConfig
from langchain_community.tools import TavilySearchResults

from ibm_watsonx_gov.evaluators.agentic_evaluator import AgenticEvaluator
from ibm_watsonx_gov.entities.state import EvaluationState
from ibm_watsonx_gov.config.agentic_ai_configuration import TracingConfiguration

from .base_evaluator import BaseAgentEvaluator
from .config import WatsonxConfig, EvaluationConfig, VectorStoreConfig, LLMConfig
from .utils.vector_store import create_vector_store


class AppState(EvaluationState):
    """State for Advanced RAG agent.

    Attributes:
        retrieval_source: Which source was used ('local' or 'web').
    """
    retrieval_source: Optional[str] = None


class AdvancedRAGEvaluator(BaseAgentEvaluator):
    """Evaluator for advanced RAG agents with multi-source retrieval and routing.

    This evaluator creates and evaluates an advanced RAG agent that:
    1. Routes queries to appropriate retrieval sources (local docs or web)
    2. Retrieves relevant context from the selected source
    3. Generates answers using the retrieved context

    Metrics evaluated:
    - Context relevance
    - Faithfulness
    - Answer similarity
    - Routing accuracy
    - Retrieval/generation latency
    - Token counts and cost

    Example:
        ```python
        from wx_gov_agent_eval import AdvancedRAGEvaluator

        evaluator = AdvancedRAGEvaluator()

        # Build agent with your documents and web search
        evaluator.build_agent(
            documents=my_docs,
            enable_web_search=True,
            tavily_api_key="your-key"
        )

        # Evaluate
        result = evaluator.evaluate_single(
            input_text="What is the latest news about AI?",
            ground_truth="Recent AI developments include..."
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
        """Initialize AdvancedRAGEvaluator.

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
        self.web_search = None
        self.enable_web_search = False

    def build_agent(
        self,
        documents: Any,
        vector_store_path: Optional[str] = None,
        enable_web_search: bool = True,
        tavily_api_key: Optional[str] = None,
        web_search_k: int = 3
    ) -> Any:
        """Build the advanced RAG agent with multi-source retrieval.

        Args:
            documents: Documents to index (list of dicts, path to PDF, or URL).
            vector_store_path: Optional existing vector store path.
            enable_web_search: Whether to enable web search as a retrieval source.
            tavily_api_key: API key for Tavily web search (required if enable_web_search=True).
            web_search_k: Number of web search results to retrieve.

        Returns:
            Compiled LangGraph agent.
        """
        # Create local vector store
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

        # Setup web search if enabled
        if enable_web_search:
            if tavily_api_key is None:
                import os
                tavily_api_key = os.getenv("TAVILY_API_KEY")
                if tavily_api_key is None:
                    raise ValueError(
                        "Tavily API key required for web search. "
                        "Provide tavily_api_key parameter or set TAVILY_API_KEY environment variable."
                    )

            self.web_search = TavilySearchResults(
                api_key=tavily_api_key,
                max_results=web_search_k
            )
            self.enable_web_search = True

        # Setup evaluator
        self.evaluator = self._setup_evaluator()

        # Build graph
        self.agent = self._build_graph()

        return self.agent

    def _setup_evaluator(self) -> AgenticEvaluator:
        """Setup the AgenticEvaluator with metrics for advanced RAG."""
        tracing_config = TracingConfiguration(project_id=self.config.project_id) if self.eval_config.enable_tracing else None

        return AgenticEvaluator(tracing_configuration=tracing_config)

    def _build_graph(self) -> Any:
        """Build the LangGraph for advanced RAG with routing."""
        evaluator = self.evaluator

        def routing_node(state: AppState, config: RunnableConfig) -> dict:
            """Route query to appropriate retrieval source."""
            routing_prompt = ChatPromptTemplate.from_template(
                "Analyze the following question and determine if it requires current/recent information "
                "that would be found on the web, or if it can be answered from stored documents.\n\n"
                "Question: {input_text}\n\n"
                "Respond with ONLY 'web' or 'local' (no explanation):"
            )

            llm = WatsonxLLM(
                model_id=self.llm_config.model_id,
                url=self.config.url,
                project_id=self.config.project_id,
                params={
                    "max_new_tokens": 10,
                    "decoding_method": "greedy",
                },
            )

            formatted_prompt = routing_prompt.invoke({"input_text": state.input_text})
            result = llm.invoke(formatted_prompt)
            decision = result.content.strip().lower() if hasattr(result, "content") else str(result).strip().lower()

            # Default to local if web search not enabled
            if not self.enable_web_search or "local" in decision:
                return {"retrieval_source": "local"}
            else:
                return {"retrieval_source": "web"}

        @evaluator.evaluate_context_relevance(compute_real_time=self.eval_config.compute_real_time)
        def local_retrieval_node(state: AppState, config: RunnableConfig) -> dict:
            """Retrieve from local vector store."""
            context = self.retriever.invoke(state.input_text)
            return {"context": [doc.page_content for doc in context]}

        @evaluator.evaluate_context_relevance(compute_real_time=self.eval_config.compute_real_time)
        def web_retrieval_node(state: AppState, config: RunnableConfig) -> dict:
            """Retrieve from web search."""
            if self.web_search is None:
                # Fallback to local if web search not available
                context = self.retriever.invoke(state.input_text)
                return {"context": [doc.page_content for doc in context]}

            results = self.web_search.invoke(state.input_text)
            context = []
            for result in results:
                if isinstance(result, dict):
                    content = result.get("content", "") or result.get("snippet", "")
                    if content:
                        context.append(content)
                else:
                    context.append(str(result))

            return {"context": context}

        @evaluator.evaluate_faithfulness(compute_real_time=self.eval_config.compute_real_time)
        @evaluator.evaluate_answer_similarity(compute_real_time=self.eval_config.compute_real_time)
        def generate_node(state: AppState, config: RunnableConfig) -> dict:
            """Generate answer using retrieved context."""
            generate_prompt = ChatPromptTemplate.from_template(
                "Answer the following question based on the given context:\n"
                "Context: {context}\n"
                "Question: {input_text}\n"
                "Answer:"
            )

            formatted_prompt = generate_prompt.invoke(
                {"input_text": state.input_text, "context": "\n\n".join(state.context)}
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

        def route_retrieval(state: AppState) -> str:
            """Determine which retrieval node to use."""
            if state.retrieval_source == "web":
                return "web_retrieval"
            return "local_retrieval"

        # Build graph
        graph = StateGraph(AppState)
        graph.add_node("Routing", routing_node)
        graph.add_node("Local Retrieval", local_retrieval_node)
        graph.add_node("Web Retrieval", web_retrieval_node)
        graph.add_node("Generation", generate_node)

        graph.add_edge(START, "Routing")
        graph.add_conditional_edges("Routing", route_retrieval, {
            "local_retrieval": "Local Retrieval",
            "web_retrieval": "Web Retrieval"
        })
        graph.add_edge("Local Retrieval", "Generation")
        graph.add_edge("Web Retrieval", "Generation")
        graph.add_edge("Generation", END)

        return graph.compile()
