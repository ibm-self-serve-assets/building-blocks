document.addEventListener("DOMContentLoaded", () => {
  function stopVideoPlayback() {
    const video = document.getElementById("demoVideo");
    if (video) {
      video.pause();
      video.currentTime = 0;
      video.src = "";
      video.load();
    }
  }

  const showModal = (modal) => modal.classList.add("show");
  const hideModal = (modal) => modal.classList.remove("show");

  const tileModal = document.getElementById("tile-modal");
  const tileTitle = document.getElementById("tile-modal-title");
  const tileBody = document.getElementById("tile-modal-body");
  const tileClose = tileModal.querySelector(".modal-close");

  const cardOverlay = document.getElementById("card-modal-overlay");
  const cardBody = document.getElementById("card-modal-body");
  const cardClose = cardOverlay.querySelector(".close-btn");

  tileModal.style.transition = "background 0.25s ease";

  /* ---------- STATIC TITLES FOR VIDEO MODAL ---------- */
  const demoTitles = {
    agents: "Multi Agent Orchestration Demo",
    data: "Text2SQL Demo",
    data_rag: "Retrieval-Augmented Generation Demo",
    trusted: "Design Time Evaluations Guardrail Demo"
  };

  /* ---------- STATIC LABELS FOR DEMO LINK TEXT ---------- */
  const demoLabels = {
    agents: "Multi Agent Orchestration",
    data: "Text2SQL",
    data_rag: "Retrieval-Augmented Generation",
    trusted: "Design Time Evaluations Guardrail",
    optimize: "Application Observability"
  };

  const createLink = (key, label) =>
    `<p style="margin-top:1rem;">
      <a href="#" class="open-modal-link" data-target="${key}" style="color:#00b4ff;text-decoration:none;font-weight:500;">
        🔗 Access ${label} Repository
      </a>
    </p>`;

  const overviewLinks = {
    agents: "https://ibm.sharepoint.com/:p:/r/sites/BuildEngineering_DEPT/Shared%20Documents/IBM%20Build/IBM%20Build_Building%20Blocks/AI/Agents/BB_Agents_EntryPoints.pptx?d=wbbed7561714c4490ab9aada13c749db9&csf=1&web=1&e=HJRmXc",
    data: "https://ibm.sharepoint.com/:p:/r/sites/BuildEngineering_DEPT/Shared%20Documents/IBM%20Build/IBM%20Build_Building%20Blocks/AI/Data%20for%20AI/BB_DataforAI_EntryPoints.pptx?d=we335fabd3bb14a089f51d8dea6e30204&csf=1&web=1&e=XwS4ZJ",
    trusted: "https://ibm.sharepoint.com/:p:/r/sites/BuildEngineering_DEPT/Shared%20Documents/IBM%20Build/IBM%20Build_Building%20Blocks/AI/Trusted%20AI/BB_TrustedAI_EntryPoints.pptx?d=w67201531f05f40859f7648f41fd47a69&csf=1&web=1&e=ljt6Tu",
    optimize: "https://ibm.sharepoint.com/:p:/r/sites/BuildEngineering_DEPT/Shared%20Documents/IBM%20Build/IBM%20Build_Building%20Blocks/Automation/Optimize/BB_Optimize_EntryPoints.pptx?d=w3215882eb8b2488a844ca73422ea46af&csf=1&web=1&e=nZYgb5",
    observe: "https://ibm.sharepoint.com/:p:/r/sites/BuildEngineering_DEPT/Shared%20Documents/IBM%20Build/IBM%20Build_Building%20Blocks/Automation/Observe/BB_Observe_EntryPoints.pptx?d=w8792b7275f854b1bb261156bc8f47a6d&csf=1&web=1&e=3cazpo",
    build: "https://ibm.sharepoint.com/:p:/r/sites/BuildEngineering_DEPT/Shared%20Documents/IBM%20Build/IBM%20Build_Building%20Blocks/Automation/Build%26Deploy/BB_Build%26Deploy_EntryPoints.pptx?d=wc9be1050d7d44f4683ff30dee22e2e1e&csf=1&web=1&e=aAlhJ6"
  };

  /* ---------- DEMO VIDEO FILE LINKS ---------- */
  const demoLinks = {
    agents:
      "https://github.com/ibm-self-serve-assets/building-blocks/raw/refs/heads/main/agents/multi-agent-orchestration/Smart-Choice-Supplier/demo/Smart_Choice_Supplier_Agent.mp4",

    data:
      "https://github.com/ibm-self-serve-assets/building-blocks/raw/refs/heads/main/data-for-ai/q-and-a/Text-To-SQL/demo/text_to_sql_demo.mp4",

    data_rag:
      "https://github.com/ibm-self-serve-assets/building-blocks/raw/refs/heads/main/data-for-ai/q-and-a/RAG-Accelerator/demo/QnA_RAG_BB.mp4",

    trusted:
      "https://github.com/ibm-self-serve-assets/building-blocks/raw/refs/heads/main/trusted-ai/design-time-evaluations/gen-ai-evaluations/demo/Customer_Care_Guardrail_Demo.mp4",

    optimize:
      "https://github.com/ibm-self-serve-assets/building-blocks/raw/refs/heads/main/observe/application-observability/Application_Observability_Instana.mp4"
  };

  /* ---------- NEW STATIC DEMO LINK GENERATOR ---------- */
  const createOverviewLink = (key, label) =>
    overviewLinks[key]
      ? `<p><a href="${overviewLinks[key]}" target="_blank" style="color:#00b4ff;">🔗 Overview of ${label} (Presentation)</a></p>`
      : "";

  const createDemoLink = (key) =>
    demoLinks[key]
      ? `<p><a href="#" class="play-demo-link" data-demo="${demoLinks[key]}" data-category="${key}" style="color:#ff6f00;font-weight:500;">🎬 Watch ${demoLabels[key]} Demo</a></p>`
      : "";

  /* ---------------------- TILE DATA ---------------------- */
  const tileData = {
    agents: {
      title: "Agents - Building Blocks",
      items: [
        { name: "Agent Builder", desc: "Build modular, goal-driven enterprise agents." },
        { name: "AI Gateway", desc: "Unified abstraction layer for LLMs." },
        { name: "Multi-Agent Orchestration", desc: "Coordinate agents for complex workflows." }
      ],
      link:
        createLink("agents", "Agents") +
        createOverviewLink("agents", "Agents") +
        createDemoLink("agents")
    },

    data: {
      title: "Data for AI - Building Blocks",
      items: [
        { name: "Vector Search", desc: "High-performance semantic retrieval." },
        { name: "Question & Answer", desc: "Natural language → SQL." },
        { name: "Zero-Copy Lakehouse", desc: "Query without replication." },
        { name: "Data Security", desc: "Governed, secure access." }
      ],
      link:
        createLink("data", "Data for AI") +
        createOverviewLink("data", "Data for AI") +
        createDemoLink("data") +
        createDemoLink("data_rag")
    },

    trusted: {
      title: "Trusted AI - Building Blocks",
      items: [
        { name: "Design-Time Evaluations", desc: "Safety & bias checks." },
        { name: "Runtime Evaluation", desc: "Live guardrails for AI." },
        { name: "Secure AI Lifecycle", desc: "End-to-end governance." }
      ],
      link:
        createLink("trusted", "Trusted AI") +
        createOverviewLink("trusted", "Trusted AI") +
        createDemoLink("trusted")
    },

    optimize: {
      title: "Optimize - Building Blocks",
      items: [
        { name: "Automated Resilience & Compliance", desc: "Observe, Automate, Govern, Accelerate." },
        { name: "FinOps", desc: "Visibility, Automation, Governance, Value" },
        { name: "Automated Resource Management", desc: "Automate, Assess, Remediate, Scale." }
      ],
      link: 
        createOverviewLink("optimize", "Optimize") +
        createDemoLink("optimize")
    },

    observe: {
      title: "Observe - Building Blocks",
      items: [
        { name: "Application Observability", desc: "Observing, Tracing, and Analyzing Application." },
        { name: "Network Performance", desc: "Speed, Latency, Bandwidth, Jitter, Loss" }
      ],
      link: createOverviewLink("observe", "Observe")
    },

    build: {
      title: "Build & Deploy - Building Blocks",
      items: [
        { name: "iPaaS", desc: "Integrating and connecting diverse applications." },
        { name: "Authentication Management", desc: "Visibility, Automation, Governance, Value" },
        { name: "Infrastructure as Code", desc: "Stateful creation and management of cloud resources." },
        { name: "Code Assistant", desc: "Accelerate development, improve code quality." }
      ],
      link: createOverviewLink("build", "Build & Deploy")
    }
  };

  /* ---------------------- CARD DATA ---------------------- */
  const cardData = {
    agents: {
      title: `<img src="icons/agent.png" class="modal-icon"> Agents`,
      content: `
        <p>Intelligent workflow orchestration powered by Watsonx.</p>
        <ul>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/agent-builder/contextual-knowledge-hub" target="_blank">🔗 Agent Builder</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/ai-gateway" target="_blank">🔗 AI Gateway</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/multi-agent-orchestration" target="_blank">🔗 Multi-Agent Orchestration</a></li>
        </ul>`
    },

    data: {
      title: `<img src="icons/data.png" class="modal-icon"> Data-for-AI`,
      content: `<p>Unified data retrieval for GenAI pipelines.</p>
       <ul>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/zero-copy-lakehouse" target="_blank">🔗 Zero Copy Lakehouse</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/vector-search" target="_blank">🔗 Vector Search</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/q-and-a" target="_blank">🔗 Q&A</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/data-for-ai/data-security-and-encryption" target="_blank">🔗 Data Security & Encryption</a></li>
        </ul>`
    },

    trusted: {
      title: `<img src="icons/trusted.png" class="modal-icon"> Trusted-AI`,
      content: `<p>Safe & governed AI across lifecycle.</p>
       <ul>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/trusted-ai/design-time-evaluations/gen-ai-evaluations" target="_blank">🔗 Design time Evaluations</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/trusted-ai/runtime-evaluations" target="_blank">🔗 Agent & AI Observability</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/trusted-ai/compliance-accelerators" target="_blank">🔗 Compliance Accelerators</a></li>
          <li><a href="https://github.com/ibm-self-serve-assets/building-blocks/tree/main/trusted-ai/secure-ai-lifecycle" target="_blank">🔗 Secure AI Lifecycle</a></li>
        </ul>`
    },

    observe: {
      title: `<img src="icons/observe.png" class="modal-icon"> Observe`,
      content: `<p>Holistic Application and Network Monitoring.</p>
       <ul>
          <li><a href="#">🔗 Application Observability</a></li>
          <li><a href="#">🔗 Network Performance</a></li>
        </ul>`
    },

    optimize: {
      title: `<img src="icons/optimize.png" class="modal-icon"> Optimize`,
      content: `<p>Integrated Resilience, FinOps Resource Automation.</p>
       <ul>
          <li><a href="#">🔗 Automated Resilience & Compliance</a></li>
          <li><a href="#">🔗 FinOps</a></li>
          <li><a href="#">🔗 Automated Resource Management</a></li>
        </ul>`
    },

    builddeploy: {
      title: `<img src="icons/build.png" class="modal-icon"> Build & Deploy`,
      content: `<p>Authentication-Driven Infrastructure Automation With Assistance.</p>
       <ul>
          <li><a href="#">🔗 iPaaS</a></li>
          <li><a href="#">🔗 Authentication Management</a></li>
          <li><a href="#">🔗 Infrastructure as Code</a></li>
          <li><a href="#">🔗 Code Assistant</a></li>
        </ul>`
    }
  };

  /* ---------------------- TILE CLICK ---------------------- */
  document.querySelectorAll(".tile").forEach((tile) => {
    tile.addEventListener("click", () => {
      stopVideoPlayback();
      const key = tile.dataset.category;
      const data = tileData[key];

      tileTitle.textContent = data.title;
      tileBody.innerHTML =
        data.items.map((i) => `<p><strong>${i.name}</strong>: ${i.desc}</p>`).join("") +
        data.link;

      tileModal.style.background = "rgba(0,0,0,0.15)";
      showModal(tileModal);
    });
  });

  /* ---------------------- CLOSE TILE MODAL ---------------------- */
  tileClose.addEventListener("click", () => {
    stopVideoPlayback();
    hideModal(tileModal);
  });

  window.addEventListener("click", (e) => {
    if (e.target === tileModal) {
      stopVideoPlayback();
      hideModal(tileModal);
    }
  });

  /* ---------------------- CARD MODAL ---------------------- */
  document.querySelectorAll(".card").forEach((card) => {
    card.addEventListener("click", () => {
      stopVideoPlayback();
      const key = card.dataset.modal;
      const data = cardData[key];

      cardBody.innerHTML = `<h2>${data.title}</h2>${data.content}`;
      showModal(cardOverlay);
    });
  });

  cardClose.addEventListener("click", () => hideModal(cardOverlay));

  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("open-modal-link")) {
      e.preventDefault();
      stopVideoPlayback();
      hideModal(tileModal);

      const key = e.target.dataset.target;
      const data = cardData[key];

      cardBody.innerHTML = `<h2>${data.title}</h2>${data.content}`;
      showModal(cardOverlay);
    }
  });

  /* ---------------------- PLAY DEMO VIDEO ---------------------- */
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("play-demo-link")) {
      e.preventDefault();

      const videoUrl = e.target.dataset.demo;
      const category = e.target.dataset.category;

      stopVideoPlayback();

      tileTitle.textContent = demoTitles[category];
      tileModal.style.background = "rgba(0,0,0,0.75)";

      tileBody.innerHTML = `
        <div id="video-loading-spinner" style="
          width:80px;height:80px;
          border:8px solid #888;
          border-top-color:#00b4ff;
          border-radius:50%;
          animation:spin 1s linear infinite;
          margin:120px auto;
        "></div>

        <style>
          @keyframes spin { from { transform: rotate(0); } to { transform: rotate(360deg); } }
        </style>
      `;

      showModal(tileModal);

      setTimeout(() => {
        tileBody.innerHTML = `
          <button id="back-btn" style="
            background:none;
            border:1px solid #00b4ff;
            padding:6px 14px;
            border-radius:6px;
            color:#00b4ff;
            cursor:pointer;
            font-size:15px;
            margin-bottom:20px;
          ">⟵ Return</button>

          <video 
            id="demoVideo"
            controls 
            autoplay 
            preload="auto"
            style="
              width:100%;
              max-width:1600px;
              height:auto;
              max-height: calc(100vh - 260px);
              object-fit:contain;
              background:#000;
              border-radius:14px;
              display:block;
              margin:0 auto;
            "
          >
            <source src="${videoUrl}" type="video/mp4">
          </video>
        `;

        const video = document.getElementById("demoVideo");

        video.addEventListener("canplay", () => {
          const spinner = document.getElementById("video-loading-spinner");
          spinner && spinner.remove();
        });

        document.getElementById("back-btn").addEventListener("click", () => {
          stopVideoPlayback();

          // FIX: RAG maps back to the "data" tile
          const resolvedCategory = category === "data_rag" ? "data" : category;
          const data = tileData[resolvedCategory];

          tileTitle.textContent = data.title;
          tileBody.innerHTML =
            data.items.map((i) => `<p><strong>${i.name}</strong>: ${i.desc}</p>`).join("") +
            data.link;

          tileModal.style.background = "rgba(0,0,0,0.15)";
        });
      }, 300);
    }
  });

});
