document.addEventListener("DOMContentLoaded", () => {
  /* ---------------------- Stop Video Helper ---------------------- */
  function stopVideoPlayback() {
    const video = document.getElementById("demoVideo");
    if (video) {
      video.pause();
      video.currentTime = 0;
      video.src = "";
      video.load();
    }
  }

  /* ---------------------- Modal Helpers ---------------------- */
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

  /* ---------------------- Config / Links ---------------------- */

  const createLink = (key, label) =>
    `<p style="margin-top:1rem;">
      <a href="#" class="open-modal-link" data-target="${key}" style="color:#00b4ff;text-decoration:none;font-weight:500;">
        🔗 Access ${label} Repository
      </a>
    </p>`;

  const overviewLinks = {
    agents: "https://ibm.sharepoint.com/:p:/r/.../BB_Agents_EntryPoints.pptx",
    data: "https://ibm.sharepoint.com/:p:/r/.../BB_DataforAI_EntryPoints.pptx",
    trusted: "https://ibm.sharepoint.com/:p:/r/.../BB_TrustedAI_EntryPoints.pptx"
  };

  const demoLinks = {
    agents:
      "https://github.com/ibm-self-serve-assets/building-blocks/raw/refs/heads/main/agents/multi-agent-orchestration/Smart-Choice-Supplier/demo/Smart_Choice_Supplier_Agent.mp4",
    data: "https://example.com/data-demo.mp4",
    trusted: "https://example.com/trusted-demo.mp4"
  };

  const createOverviewLink = (key, label) =>
    overviewLinks[key]
      ? `<p><a href="${overviewLinks[key]}" target="_blank" style="color:#00b4ff;">🔗 Overview of ${label} (Presentation)</a></p>`
      : "";

  const createDemoLink = (key, label) =>
    demoLinks[key]
      ? `<p><a href="#" class="play-demo-link" data-demo="${demoLinks[key]}" data-category="${key}" style="color:#ff6f00;font-weight:500;">🎬 Watch ${label} Demo</a></p>`
      : "";

  /* ---------------------- Tile Data ---------------------- */
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
        createDemoLink("agents", "Agents")
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
        createDemoLink("data", "Data for AI")
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
        createDemoLink("trusted", "Trusted AI")
    }
  };

  /* ---------------------- Card Data ---------------------- */

  const cardData = {
    agents: {
      title: `<img src="icons/agent.png" class="modal-icon"> Agents`,
      content: `
        <p>Intelligent workflow orchestration powered by Watsonx.</p>
        <ul>
          <li><a href="#">🔗 Agent Builder</a></li>
          <li><a href="#">🔗 AI Gateway</a></li>
          <li><a href="#">🔗 Multi-Agent Orchestration</a></li>
        </ul>`
    },

    data: {
      title: `<img src="icons/data.png" class="modal-icon"> Data-for-AI`,
      content: `<p>Unified data retrieval for GenAI pipelines.</p>`
    },

    trusted: {
      title: `<img src="icons/trusted.png" class="modal-icon"> Trusted-AI`,
      content: `<p>Safe & governed AI across lifecycle.</p>`
    }
  };

  /* ---------------------- Tile Click ---------------------- */
  document.querySelectorAll(".tile").forEach((tile) => {
    tile.addEventListener("click", () => {
      stopVideoPlayback();
      const key = tile.dataset.category;
      const data = tileData[key];

      tileTitle.textContent = data.title;
      tileBody.innerHTML =
        data.items.map((i) => `<p><strong>${i.name}</strong>: ${i.desc}</p>`).join("") + data.link;

      tileModal.style.background = "rgba(0,0,0,0.15)";
      showModal(tileModal);
    });
  });

  /* ---------------------- Close Button ---------------------- */
  tileClose.addEventListener("click", () => {
    stopVideoPlayback();
    hideModal(tileModal);
    tileModal.style.background = "rgba(0,0,0,0.15)";
  });

  /* ---------------------- Close on Background Click ---------------------- */
  window.addEventListener("click", (e) => {
    if (e.target === tileModal) {
      stopVideoPlayback();
      hideModal(tileModal);
      tileModal.style.background = "rgba(0,0,0,0.15)";
    }
  });

  /* ---------------------- Card Modal ---------------------- */
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

  /* ---------------------- Tile → Card Navigation ---------------------- */
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

  /* ---------------------- PLAY DEMO VIDEO INSIDE MODAL ---------------------- */
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("play-demo-link")) {
      e.preventDefault();

      const videoUrl = e.target.dataset.demo;
      const category = e.target.dataset.category;

      stopVideoPlayback();

      tileTitle.textContent = "Smart Choice Supplier";
      tileModal.style.background = "rgba(0,0,0,0.75)";

      // Loading Spinner
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
            @keyframes spin {from {transform: rotate(0);} to {transform: rotate(360deg);} }
        </style>
      `;

      showModal(tileModal);

      /* ---------- Load Video After Small Delay ---------- */
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
          ">⟵ Return to Agents Info</button>

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
              border-radius: 14px;
              display:block;
              margin:0 auto;
            "
          >
            <source src="${videoUrl}" type="video/mp4">
          </video>
        `;

        const video = document.getElementById("demoVideo");

        /* Hide spinner when video loads */
        video.addEventListener("canplay", () => {
          const spinner = document.getElementById("video-loading-spinner");
          spinner && spinner.remove();
        });

        /* ---------- Back Button ---------- */
        document.getElementById("back-btn").addEventListener("click", () => {
          stopVideoPlayback();
          const data = tileData[category];

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
