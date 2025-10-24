document.addEventListener("DOMContentLoaded", () => {
  const showModal = (modal) => modal.classList.add("show");
  const hideModal = (modal) => modal.classList.remove("show");

  /* ---------- TILE MODAL ---------- */
  const tileModal = document.getElementById("tile-modal");
  const tileTitle = document.getElementById("tile-modal-title");
  const tileBody = document.getElementById("tile-modal-body");
  const tileClose = tileModal.querySelector(".modal-close");

  const tileData = {
    agents: {
      title: "Agents - Building Blocks",
      items: [
        { name: "Agent Builder", desc: "The Agent Builder, powered by IBM watsonx Agentic Development Kit (ADK), simplifies the creation and deployment of intelligent, context-aware agents. It offers a modular framework for building goal-driven agents that integrate seamlessly into enterprise workflows." },
        { name: "AI Gateway", desc: "Ability to provide a unified abstraction layer across multiple LLM providers, eliminating vendor lock-in. With its built-in extensibility and model integration capabilities, it allows seamless onboarding and orchestration of models from OpenAI, Anthropic, Google, AWS Bedrock, Azure OpenAI, Mistral, Ollama, and IBM watsonx.ai within a single interoperable framework." },
        { name: "Multi-Agent Orchestration", desc: "Seamless coordination and interaction among specialized autonomous agents to achieve complex, multi-step objectives. It manages task delegation, context sharing, and decision synchronization across agents." }
      ]
    },
    data: {
      title: "Data for AI - Building Blocks",
      items: [
        { name: "Vector Search", desc: "Delivers a high-performance, vector-based retrieval engine designed for GenAI pipelines. It enables semantic similarity matching to enhance retrieval-augmented generation (RAG) and is optimized for scalability, low-latency queries, and large-scale AI workloads." },
        { name: "Question & Answer", desc: "Enables natural language interaction with enterprise data through intelligent query translation. Powered by watsonx.data Text2SQL, it transforms user questions into optimized, executable SQL queries, enabling seamless conversational access to structured datasets." },
        { name: "Zero-Copy Lakehouse", desc: "Provides a unified query layer that enables direct access to data across databases, data warehouses, and cloud object stores — without replicating or moving it. This architecture minimizes data latency, optimizes storage utilization, and significantly reduces infrastructure costs." },
        { name: "Data Security & Encryption", desc: "Safeguards sensitive information using advanced encryption, data masking, and fine-grained access controls. It strengthens data governance frameworks and ensures adherence to regulatory and compliance standards." }

      ]
    },
    trusted: {
      title: "Trusted AI - Building Blocks",
      items: [
        { name: "Secure IA Lifecycle", desc: "IBM Guardium AI Security ensures safe, compliant, and auditable AI adoption through model access controls, security posture management, and policy-driven governance. Its modular, API-based design enables flexible and scalable protection across hybrid and multicloud environments." },
        { name: "Runtime Evaluation", desc: "Performs real-time assessment of Generative AI prompts and responses to ensure model reliability, compliance, and safety. Designed for enterprise and regulated environments, it enables continuous policy enforcement, bias detection, and risk monitoring for large language models (LLMs) during runtime." },
        { name: "Design-Time Evaluations", desc: "Implements AI safety and compliance guardrails using IBM watsonx.governance for both design-time validation and real-time monitoring. Evaluates AI-generated content against bias, toxicity, jailbreaks, and policy violations through configurable risk metrics." }
      ]
    },
    optimize: {
      title: "Optimize - Building Blocks",
      items: [
        { name: "FinOps", desc: "Provides deep visibility into IT spend across hybrid and multicloud environments. It enables organizations to optimize cloud costs, forecast budgets, and align technology investments with business outcomes through data-driven insights and automated cost governance."},
        { name: "Automated Resilience and Compliance", desc: "AI-powered observability and decision intelligence platform that unifies data across IT operations, applications, and infrastructure for real-time insight and proactive issue resolution. It leverages generative AI, causal reasoning, and predictive analytics to deliver context-aware recommendations and automated remediation, enhancing operational efficiency and reliability across hybrid environments." },
        { name: "Automated Resource Management", desc: "Autonomous resource optimization by continuously analyzing application demand and automatically allocating compute, storage, and network resources in real time. It ensures performance assurance and cost efficiency across hybrid and multicloud environments through AI-driven workload placement, scaling, and elasticity management." }
      ]
    },
    observe: {
      title: "Observe - Building Blocks",
      items: [
        { name: "Network Performance", desc: "Delivers AI-driven network observability and analytics to monitor, predict, and optimize performance across complex hybrid and multicloud infrastructures. It provides real-time telemetry ingestion, anomaly detection, and automated root-cause analysis, ensuring proactive network assurance and operational resilience." },
        { name: "Application Observabality", desc: "Real-time, end-to-end visibility into applications, microservices, and infrastructure across hybrid and multicloud environments. It leverages AI-powered automated discovery, dependency mapping, and root-cause analysis to deliver continuous performance optimization and accelerated incident resolution." }
      ]
    },
    build: {
      title: "Build & Deploy - Building Blocks",
      items: [
        { name: "Authentication Management", desc: "Adaptive, AI-driven identity and access management (IAM) that secures user authentication across cloud and on-premises applications. It delivers risk-based multifactor authentication, single sign-on (SSO), and identity governance to ensure zero-trust security compliance and seamless user experiences." },
        { name: "Infrastructure as Code", desc: "Automation tool that enables declarative provisioning, management, and versioning of cloud and on-premises resources. It provides idempotent, multi-cloud orchestration through reusable configuration files, ensuring consistent and scalable infrastructure deployment across hybrid environments." },
        { name: "Code Assistant", desc: "Leverages large language models (LLMs) to accelerate code generation, modernization, and automation across programming languages and platforms. It provides context-aware code recommendations, test generation, and documentation assistance, enabling developers to enhance productivity and reduce technical debt in enterprise software delivery." },
      ]
    }
  };

  document.querySelectorAll(".tile").forEach(tile => {
    tile.addEventListener("click", () => {
      const key = tile.getAttribute("data-category");
      const data = tileData[key];
      if (data) {
        tileTitle.textContent = data.title;
        tileBody.innerHTML = data.items
          .map(item => `<p><strong>${item.name}</strong>: ${item.desc}</p>`)
          .join("");
        showModal(tileModal);
      }
    });
  });

  tileClose.addEventListener("click", () => hideModal(tileModal));
  window.addEventListener("click", e => { if (e.target === tileModal) hideModal(tileModal); });

  /* ---------- CARD MODAL ---------- */
  const cardOverlay = document.getElementById("card-modal-overlay");
  const cardBody = document.getElementById("card-modal-body");
  const cardClose = cardOverlay.querySelector(".close-btn");

  const cardData = {
    agents: {
      title: `<img src="icons/agent.png" alt="Agents Icon" class="modal-icon"> Agents`,
      content: `
    <p><strong>IBM watsonx Orchestrate</strong> and <strong>watsonx.ai</strong> enable intelligent automation and orchestration across business processes.</p>
    <ul>
      <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/agent-builder/contextual-knowledge-hub" target="_blank">🔗 Agent Builder</a></li>
      <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/ai-gateway" target="_blank">🔗 AI Gateway</a></li>
      <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/multi-agent-orchestration" target="_blank">🔗 Multi-Agent Orchestration</a></li>
    </ul>
  `
    },

    data: {
      title: `<img src="icons/data.png" alt="Agents Icon" class="modal-icon"> Data-for-AI`,
      content: `
        <p>Provides a unified, high-performance data access and retrieval framework optimized for GenAI workloads. It enables semantic vector search, natural language-to-SQL query translation, and zero-copy data federation across databases and cloud stores—delivering low-latency, scalable, and cost-efficient AI data pipelines.</p>
      <ul>
        <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/q-and-a/RAG-Accelerator" target="_blank">🔗 Question & Answer - RAG Accelerator</a></li>
        <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/q-and-a/Text-To-SQL" target="_blank">🔗 Question & Answer - Text To SQL </a></li>
        <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/vector-search" target="_blank">🔗 Vector Search</a></li>
        <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/data-security-and-encryption" target="_blank">🔗 Data Security & Encryption</a></li>
        <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/zero-copy-lakehouse" target="_blank">🔗 Zero Copy Lakehouse</a></li>
    </ul>      
      `
    },
    trusted: {
      title: `<img src="icons/trusted.png" alt="Agents Icon" class="modal-icon"> Trusted-AI`,
      content: `
        <p>Ensures secure, compliant, and auditable AI adoption across hybrid and multicloud environments through Guardium AI Security and watsonx.governance. It provides design-time and runtime evaluations with advanced guardrails, bias detection, and policy enforcement to maintain trust, safety, and regulatory alignment for large language models (LLMs)</strong>.</p>
        <ul>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/trusted-ai/secure-ai-lifecycle" target="_blank">🔗 Secure AI Lifecycle</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/trusted-ai/runtime-evaluations/generative_ai" target="_blank">🔗 Runtime Evaluations</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/trusted-ai/design-time-evaluations/gen-ai-evaluations" target="_blank">🔗 Design Time Evaluations</a></li>
    </ul>  
      `
    },
    optimize: {
      title: `<img src="icons/optimize.png" alt="Agents Icon" class="modal-icon"> Optimize`,
      content: `
        <p><strong>IBM Turbonomic</strong> automates performance and cost optimization across hybrid cloud environments.</p>
        <a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/optimize" target="_blank">🔗 Open Optimize Block</a>
      `
    },
    observe: {
      title: `<img src="icons/observe.png" alt="Agents Icon" class="modal-icon"> Observe`,
      content: `
        <p>Gain full-stack observability with <strong>IBM Instana</strong> to detect, analyze, and resolve issues proactively.</p>
        <a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/observe" target="_blank">🔗 View Observability</a>
      `
    },
    builddeploy: {
      title: `<img src="icons/build.png" alt="Agents Icon" class="modal-icon"> Build & Deploy`,
      content: `
        <p>Deployable configurations that dynamically generate new code snippets using <strong>natural language prompts</strong>.</p>
        <a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/build-and-deploy" target="_blank">🔗 Open Build & Deploy Block</a>
      `
    },
  };



  document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("click", () => {
      const key = card.getAttribute("data-modal");
      const data = cardData[key];
      if (data) {
        cardBody.innerHTML = `<h2>${data.title}</h2>${data.content}`;
        showModal(cardOverlay);
      }
    });
  });

  cardClose.addEventListener("click", () => hideModal(cardOverlay));
  cardOverlay.addEventListener("click", e => {
    if (e.target === cardOverlay) hideModal(cardOverlay);
  });
});
