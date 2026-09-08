# Bobserver Skills Directory

Place your desired IBM Bob skills in this directory to make them available to Bobserver during headless executions.

## 🚀 How to Add Skills

1. Browse the centralized skill catalog at [`building-blocks/ibm-bob/skills/`](../../../../ibm-bob/skills/).
2. Copy the skill folders you want your Bobserver instance to access into this directory:
   ```text
   assets/bob-server/skills/
   ├── agent/                 # watsonx Orchestrate agent lifecycle
   ├── code-modernization-expert/  # Code refactoring and modernization
   ├── infrastructure-as-code-terraform/ # Terraform IaC automation
   └── ...
   ```
3. When Bobserver provisions workspaces for runs or jobs, it will automatically seed and load the skills located here into Bob's execution context.

For more details on authoring and using skills, see the [IBM Bob Skills & Modes Guide](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/bob-skills-and-modes/).
