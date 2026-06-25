# Google ADK Agent Template

This is a project template based on the Google ADK (Agent Development Kit), designed to provide a standardized architecture for developers to quickly build, test, and deploy AI Agents.

## Features

- **Dual Engine Support**: Built-in `gemini_agent` (Native Google Gemini) and `litellm_agent` (Universal support via LiteLLM for OpenAI, Anthropic, etc.).
- **Structured Development**: Manage `tools`, `models`, and `instructions` through a clean directory layout.
- **Timezone Tool Example**: Includes a `get_current_time` tool with multi-timezone support, demonstrating how to build tools with parameters.
- **Makefile Automation**: `make setup` for one-click environment initialization, handling venv and `.env` files automatically.

## Quick Start

1. **One-click Initialization**:
   This command creates a virtual environment, copies `.env.template` to `.env`, and installs all dependencies.
   ```bash
   make setup
   ```

2. **Configure Environment**:
   Edit the `.env` file in each agent directory with your API keys or Vertex AI settings.

3. **Run Agent**:
   ```bash
   make run
   ```
   Once started, open the URL (default: http://localhost:8000) to chat with your AI assistant.

## Directory Structure

- `gemini_agent/`: Agent implementation driven by native Google Gemini.
- `litellm_agent/`: Universal Agent driven by LiteLLM (supports OpenAI, Claude, etc.).
  - `tools/sample_tool.py`: Utility functions (e.g., timezone lookup).
  - `models/default.py`: Model initialization logic.
  - `instruction/system.md`: System instructions.
  - `.env.template`: Local environment variable template.

## Development Guide

- **Add Tools**: Add a function in `tools/sample_tool.py` and register it in the `tools` list in `agent.py`.
- **Update Instructions**: Edit `instruction/system.md`.
- **Vertex AI Support**:
  Set `GOOGLE_GENAI_USE_VERTEXAI=1` in your `.env` to switch to Vertex AI mode.

## Useful Makefile Commands

- `make setup`: Complete environment initialization.
- `make init-env`: Initialize `.env` files only.
- `make clean`: Clean cache and temporary files.
