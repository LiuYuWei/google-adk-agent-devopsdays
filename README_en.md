# Google ADK Agent DevOpsDays

This is a project based on the Google ADK (Agent Development Kit), providing a standardized architecture for developers to quickly build, test, and deploy AI Agents. It also ships a DevOpsDays k8s/docker simulated fault dataset for diagnosis practice.

## Features

- **Native Gemini Engine**: Built-in `gemini_agent` powered by native Google Gemini (Vertex AI).
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
   Edit `gemini_agent/.env` with your Vertex AI settings (or API keys).

3. **Run Agent**:
   ```bash
   make run
   ```
   Once started, open the URL (default: http://localhost:8000) to chat with your AI assistant.

## Directory Structure

- `gemini_agent/`: Agent implementation driven by native Google Gemini.
  - `tools/sample_tool.py`: Utility functions (e.g., timezone lookup).
  - `models/gemini_model.py`: Model initialization logic.
  - `instruction/system.md`: System instructions.
  - `data/`: DevOpsDays k8s/docker simulated fault dataset for diagnosis practice.
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
