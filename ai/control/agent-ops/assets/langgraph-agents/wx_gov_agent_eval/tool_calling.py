"""
ToolCallingEvaluator for agents that use custom tools.

This evaluator is designed for agents that incorporate function/tool calling
capabilities, with comprehensive evaluation of tool usage accuracy and safety.
"""

from typing import Optional, Any, List, Callable, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_ibm import WatsonxLLM
from langgraph.graph import START, END, StateGraph
from langgraph.config import RunnableConfig
from langgraph.prebuilt import ToolNode

from ibm_watsonx_gov.evaluators.agentic_evaluator import AgenticEvaluator
from ibm_watsonx_gov.entities.state import EvaluationState
from ibm_watsonx_gov.config.agentic_ai_configuration import TracingConfiguration

from .base_evaluator import BaseAgentEvaluator
from .config import WatsonxConfig, EvaluationConfig, LLMConfig


class AppState(EvaluationState):
    """State for Tool Calling agent."""
    pass


class ToolCallingEvaluator(BaseAgentEvaluator):
    """Evaluator for agents with custom tool calling capabilities.

    This evaluator creates and evaluates agents that:
    1. Analyze user queries to determine if tools are needed
    2. Call appropriate tools with correct parameters
    3. Generate final answers using tool results

    Metrics evaluated:
    - Tool call accuracy (correct tool selection and parameters)
    - Answer similarity
    - Content safety (PII, HAP, HARM) if enabled
    - Tool usage latency
    - Token counts and cost

    Example:
        ```python
        from wx_gov_agent_eval import ToolCallingEvaluator
        from langchain_core.tools import tool

        @tool
        def get_weather(location: str) -> str:
            '''Get weather for a location.'''
            return f"Weather in {location}: Sunny, 72°F"

        evaluator = ToolCallingEvaluator()

        # Build agent with your tools
        evaluator.build_agent(tools=[get_weather])

        # Evaluate
        result = evaluator.evaluate_single(
            input_text="What's the weather in Boston?",
            ground_truth="Sunny and 72 degrees"
        )

        # Get metrics
        evaluator.display_results()
        ```
    """

    def __init__(
        self,
        watsonx_config: Optional[WatsonxConfig] = None,
        eval_config: Optional[EvaluationConfig] = None,
        llm_config: Optional[LLMConfig] = None,
        **kwargs
    ):
        """Initialize ToolCallingEvaluator.

        Args:
            watsonx_config: Watsonx configuration.
            eval_config: Evaluation configuration.
            llm_config: LLM configuration.
            **kwargs: Additional arguments passed to BaseAgentEvaluator.
        """
        super().__init__(watsonx_config, eval_config, **kwargs)

        self.llm_config = llm_config or LLMConfig()
        self.tools = []

    def build_agent(
        self,
        tools: List[Callable],
        system_message: Optional[str] = None
    ) -> Any:
        """Build the tool calling agent.

        Args:
            tools: List of LangChain tools (decorated with @tool).
            system_message: Optional custom system message for the agent.

        Returns:
            Compiled LangGraph agent.
        """
        self.tools = tools

        # Default system message if not provided
        if system_message is None:
            system_message = (
                "You are a helpful assistant with access to tools. "
                "Use the tools when necessary to answer user questions accurately. "
                "If you don't need to use any tools, respond directly."
            )

        self.system_message = system_message

        # Setup evaluator
        self.evaluator = self._setup_evaluator()

        # Build graph
        self.agent = self._build_graph()

        return self.agent

    def _setup_evaluator(self) -> AgenticEvaluator:
        """Setup the AgenticEvaluator with metrics for tool calling."""
        tracing_config = TracingConfiguration(project_id=self.config.project_id) if self.eval_config.enable_tracing else None

        return AgenticEvaluator(tracing_configuration=tracing_config)

    def _build_graph(self) -> Any:
        """Build the LangGraph for tool calling agent."""
        evaluator = self.evaluator

        # Create LLM with tool binding
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

        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(self.tools)

        @evaluator.evaluate_tool_call_accuracy(compute_real_time=self.eval_config.compute_real_time)
        def agent_node(state: AppState, config: RunnableConfig) -> dict:
            """Agent reasoning node that decides whether to use tools."""
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_message),
                ("human", "{input_text}")
            ])

            formatted_prompt = prompt.invoke({"input_text": state.input_text})
            result = llm_with_tools.invoke(formatted_prompt)

            # Check if tools were called
            if hasattr(result, 'tool_calls') and result.tool_calls:
                return {
                    "messages": [result],
                    "tool_calls": result.tool_calls
                }
            else:
                # No tools needed, generate direct answer
                output_text = result.content if hasattr(result, "content") else str(result)
                return {"generated_text": output_text}

        # Content safety evaluation if enabled
        if self.eval_config.enable_content_safety:
            @evaluator.evaluate_pii(compute_real_time=self.eval_config.compute_real_time)
            @evaluator.evaluate_hap(compute_real_time=self.eval_config.compute_real_time)
            @evaluator.evaluate_answer_similarity(compute_real_time=self.eval_config.compute_real_time)
            def synthesis_node(state: AppState, config: RunnableConfig) -> dict:
                """Synthesize final answer from tool results."""
                return self._synthesize_answer(state)
        else:
            @evaluator.evaluate_answer_similarity(compute_real_time=self.eval_config.compute_real_time)
            def synthesis_node(state: AppState, config: RunnableConfig) -> dict:
                """Synthesize final answer from tool results."""
                return self._synthesize_answer(state)

        def should_continue(state: AppState) -> str:
            """Determine whether to call tools or end."""
            if "tool_calls" in state and state.tool_calls:
                return "tools"
            return "synthesize"

        # Create tool node
        tool_node = ToolNode(self.tools)

        # Build graph
        graph = StateGraph(AppState)
        graph.add_node("Agent", agent_node)
        graph.add_node("Tools", tool_node)
        graph.add_node("Synthesize", synthesis_node)

        graph.add_edge(START, "Agent")
        graph.add_conditional_edges("Agent", should_continue, {
            "tools": "Tools",
            "synthesize": "Synthesize"
        })
        graph.add_edge("Tools", "Synthesize")
        graph.add_edge("Synthesize", END)

        return graph.compile()

    def _synthesize_answer(self, state: AppState) -> dict:
        """Synthesize final answer from tool results or direct response."""
        # If we have tool results, synthesize answer
        if "messages" in state and len(state.messages) > 1:
            synthesis_prompt = ChatPromptTemplate.from_template(
                "Based on the following tool results, provide a clear and concise answer to the user's question.\n\n"
                "User question: {input_text}\n"
                "Tool results: {tool_results}\n\n"
                "Answer:"
            )

            # Extract tool results from messages
            tool_results = []
            for msg in state.messages[1:]:  # Skip the agent's initial message
                if hasattr(msg, 'content'):
                    tool_results.append(msg.content)

            llm = WatsonxLLM(
                model_id=self.llm_config.model_id,
                url=self.config.url,
                project_id=self.config.project_id,
                params={
                    "max_new_tokens": self.llm_config.max_new_tokens,
                    "decoding_method": self.llm_config.decoding_method,
                    "repetition_penalty": self.llm_config.repetition_penalty,
                },
            )

            formatted_prompt = synthesis_prompt.invoke({
                "input_text": state.input_text,
                "tool_results": "\n".join(tool_results)
            })

            result = llm.invoke(formatted_prompt)
            output_text = result.content if hasattr(result, "content") else str(result)

            return {"generated_text": output_text}
        else:
            # Direct answer already in state
            return {}
