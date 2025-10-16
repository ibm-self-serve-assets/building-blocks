document.addEventListener("DOMContentLoaded", () => {
  const modalOverlay = document.getElementById("modal-overlay");
  const modalBody = document.getElementById("modal-body");
  const closeBtn = document.querySelector(".close-btn");

  const modalData = {
    agents: {
      title: "🤖 Agents",
      content: `
        <p><strong>IBM watsonx Orchestrate</strong> and <strong>watsonx.ai</strong> enable intelligent automation and task orchestration 
        across business processes. This building block provides APIs, SDKs, and automation flows that integrate AI assistants into enterprise workflows.</p>
        <a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents" target="_blank">🔗 View Agents Code</a>
      `
    },
    data: {
      title: "🧠 Data-for-AI",
      content: `
        <p>Data ingestion, preparation, and governance patterns built on <strong>watsonx.data</strong> to support AI-ready data pipelines. 
        Includes vector search, RAG services, and fine-tuning data workflows.</p>
        <a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai" target="_blank">🔗 Explore Data for AI</a>
      `
    },
    trusted: {
      title: "🛡 Trusted-AI",
      content: `
        <p>Ensuring fairness, transparency, and governance with <strong>watsonx.governance</strong>. 
        Includes model validation, explainability, and bias detection workflows.</p>
        <a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/trusted-ai" target="_blank">🔗 Learn More</a>
      `
    },
    optimize: {
      title: "⚙ Optimize",
      content: `
        <p><strong>IBM Turbonomic</strong> continuously optimizes performance and cost across hybrid cloud environments. 
        This building block provides FinOps automation and smart resource orchestration examples.</p>
        <a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/optimize" target="_blank">🔗 Open Optimize Block</a>
      `
    },
    observe: {
      title: "👁 Observe",
      content: `
        <p>Empower real-time observability and monitoring with <strong>IBM Instana</strong>. 
        Detect, analyze, and resolve issues proactively through AI-assisted insights.</p>
        <a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/observe" target="_blank">🔗 View Observability</a>
      `
    }
  };

  document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("click", () => {
      const key = card.getAttribute("data-modal");
      modalBody.innerHTML = `<h2>${modalData[key].title}</h2>${modalData[key].content}`;
      modalOverlay.style.display = "flex";
    });
  });

  closeBtn.addEventListener("click", () => {
    modalOverlay.style.display = "none";
  });

  modalOverlay.addEventListener("click", e => {
    if (e.target === modalOverlay) modalOverlay.style.display = "none";
  });
});

