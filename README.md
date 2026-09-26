# 🤖 JEV — Multimodel AI Assistant

> A local multimodel AI assistant that intelligently routes user queries to specialized AI models for general tasks, coding, and image generation.

<p align="center">

<img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python" />
<img src="https://img.shields.io/badge/Ollama-Local%20AI-black?style=for-the-badge" />
<img src="https://img.shields.io/badge/ComfyUI-Image%20Generation-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/Qwen-Multimodel-purple?style=for-the-badge" />

</p>

---

## 🧠 What is JEV?

**JEV** is a local multimodel AI assistant designed around one simple idea:

> **Don't use one model for everything. Use the right model for the right task.**

Instead of sending every request to a single AI model, JEV first analyzes the user's query and determines what type of task it is.

Currently, JEV supports three routes:

| Route | Backend | Purpose |
|---|---|---|
| 🧠 **GENERAL** | Qwen3 8B | General questions, explanations, reasoning and conversation |
| 💻 **CODING** | Qwen2.5 Coder 7B | Programming, debugging, APIs, algorithms and software development |
| 🎨 **IMAGE** | ComfyUI + Qwen Image | Image generation |

The routing decision is handled by **Noul through OpenRouter**, while the actual task execution happens locally.

---

# 🏗️ Architecture

```text
                         ┌─────────────────┐
                         │      USER       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │       JEV       │
                         │     ROUTER      │
                         └────────┬────────┘
                                  │
                         Noul / OpenRouter
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ▼                ▼                ▼
          ┌────────────┐  ┌────────────┐  ┌────────────┐
          │  GENERAL   │  │   CODING   │  │   IMAGE    │
          └─────┬──────┘  └──────┬─────┘  └──────┬─────┘
                │                │                │
                ▼                ▼                ▼
          ┌──────────┐     ┌──────────────┐  ┌─────────────┐
          │ Qwen3 8B │     │ Qwen2.5      │  │   ComfyUI   │
          │          │     │ Coder 7B     │  │ + Qwen Image │
          └──────────┘     └──────────────┘  └─────────────┘
                │                │                │
                └────────────────┼────────────────┘
                                 ▼
                         ┌─────────────────┐
                         │     RESULT      │
                         └─────────────────┘
```

---

## ✨ Features

### 🧠 Intelligent Routing

JEV uses Noul to evaluate the user's request against three categories:

- General purpose
- Coding
- Image generation

The category with the highest confidence is selected.

Example:

```text
User:
Explain the OSI model.

GENERAL : 0.96
CODING  : 0.18
IMAGE   : 0.02

SELECTED: GENERAL
```

---

### 💻 Specialized Coding Model

Programming requests are routed to:

```text
Qwen2.5 Coder 7B
```

Example:

```text
User:
Write a Python function to reverse a linked list.
```

JEV:

```text
GENERAL : 0.62
CODING  : 0.99
IMAGE   : 0.01

SELECTED: CODING
```

The request is then executed locally through Ollama.

---

### 🎨 Local Image Generation

Image requests are routed to:

```text
ComfyUI → Qwen Image
```

Example:

```text
User:
Create an image of a futuristic robot.
```

JEV identifies the request as an image task and sends the workflow to the local ComfyUI API.

Generated images are saved locally in:

```text
generated_images/
```

---

## 🧩 Technology Stack

| Technology | Role |
|---|---|
| 🐍 Python | Core application |
| 🧠 Noul | Query classification |
| 🌐 OpenRouter | Noul API backend |
| 🦙 Ollama | Local LLM inference |
| 🤖 Qwen3 8B | General-purpose model |
| 💻 Qwen2.5 Coder 7B | Coding model |
| 🎨 ComfyUI | Local image-generation backend |
| 🖼️ Qwen Image | Image-generation model |
| 📦 Requests | API communication |
| 🔐 python-dotenv | Environment variable management |

---

## 📁 Project Structure

```text
jev-multimodel/
│
├── main.py
├── jev_router.py
├── ollama_client.py
├── comfyui_client.py
├── workflow_api.json
├── requirements.txt
├── .env.example
├── .gitignore
└── generated_images/
```

### File Overview

#### `main.py`

Main entry point for JEV.

Responsible for:

- Accepting user input
- Calling the router
- Sending the request to the correct backend
- Displaying results

#### `jev_router.py`

Contains the Noul-based classification system.

It determines whether the request is:

```text
GENERAL
CODING
IMAGE
```

#### `ollama_client.py`

Handles communication with local Ollama models.

Currently used for:

```text
qwen3:8b
qwen2.5-coder:7b
```

#### `comfyui_client.py`

Handles communication with the local ComfyUI API.

The workflow is submitted to ComfyUI and the generated image is retrieved and saved locally.

#### `workflow_api.json`

Contains the ComfyUI API workflow used for Qwen Image generation.

The workflow can be modified independently from the Python application.

---

## ⚙️ Requirements

JEV is designed to work with local AI models, so hardware requirements depend on the models being used.

Example setup:

```text
GPU: NVIDIA GeForce RTX 3050
VRAM: 4 GB
```

Because local models can exceed available VRAM, Ollama may use CPU/GPU offloading.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/dishambha/jev-multimodel.git
cd jev-multimodel
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuration

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

You can use `.env.example` as a template.

### ⚠️ Important

Never commit your real `.env` file.

The repository includes `.env` inside `.gitignore`.

---

## 🦙 Ollama Setup

Install Ollama and download the required models.

### General Model

```bash
ollama pull qwen3:8b
```

### Coding Model

```bash
ollama pull qwen2.5-coder:7b
```

Verify:

```bash
ollama list
```

---

## 🎨 ComfyUI Setup

JEV's image-generation route requires a locally running ComfyUI instance.

For the Windows NVIDIA portable version, start ComfyUI using:

```text
run_nvidia_gpu.bat
```

ComfyUI should become available at:

```text
http://127.0.0.1:8188
```

Keep ComfyUI running while using the IMAGE route.

---

## ▶️ Running JEV

Start Ollama.

Start ComfyUI if you want image generation.

Then run:

```bash
python main.py
```

You should see:

```text
=======================================================
                 JEV MULTIMODEL
=======================================================

Available routes:
GENERAL → Qwen3 8B
CODING  → Qwen2.5 Coder 7B
IMAGE   → ComfyUI / Qwen Image

Type 'exit', 'quit', or '/bye' to stop.
=======================================================
```

---

## 🧪 Example Usage

### General Question

```text
You: What is an API?
```

Example routing:

```text
GENERAL : 0.96
CODING  : 0.95
IMAGE   : 0.02

SELECTED: GENERAL
```

The request is sent to:

```text
Qwen3 8B
```

---

### Coding Request

```text
You: Write a Python function to reverse a linked list.
```

JEV routes the request to:

```text
Qwen2.5 Coder 7B
```

---

### Image Request

```text
You: Create an image of a futuristic robot.
```

JEV routes the request to:

```text
ComfyUI / Qwen Image
```

The generated image is then saved locally.

---

## 🔄 Current Workflow

The current JEV pipeline is intentionally simple:

```text
User Query
     │
     ▼
Noul Classification
     │
     ├──────────────┐
     │              │
     ▼              ▼
 GENERAL          CODING
     │              │
     ▼              ▼
 Qwen3 8B      Qwen2.5 Coder
     │              │
     └───────┬──────┘
             │
             ▼
           Result


IMAGE
  │
  ▼
ComfyUI
  │
  ▼
Qwen Image
  │
  ▼
Generated PNG
```

---

## 🛣️ Future Plans

JEV is currently a **single-intent router**.

A future version could support complex requests containing multiple tasks.

For example:

```text
What is an API?
Give me a FastAPI example.
Create an image showing the FastAPI workflow.
```

A future JEV planner could break this into:

```text
                USER
                  │
                  ▼
             TASK PLANNER
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
     GENERAL   CODING     IMAGE
        │         │         │
      Qwen3     Coder    ComfyUI
        │         │         │
        └─────────┼─────────┘
                  ▼
             FINAL RESULT
```

This is intentionally **not implemented yet**.

The current architecture focuses on keeping the system lightweight and suitable for local hardware.

---

## 🔒 Privacy

JEV is designed around local inference for the actual task execution.

### Local

The following run locally:

```text
Qwen3
Qwen2.5 Coder
ComfyUI
Qwen Image
```

### Cloud

The routing/classification request currently uses:

```text
Noul
   ↓
OpenRouter
```

Therefore, users should understand that the query used for routing is sent to the configured routing service.

---

## ⚠️ Limitations

- Only one primary route is selected per query.
- Multiple tasks in a single request are not yet orchestrated.
- Local model performance depends heavily on available RAM and VRAM.
- Image generation requires a working ComfyUI installation and compatible workflow.
- The current image workflow is tied to the configured Qwen Image setup.
- Different hardware may require different Ollama/ComfyUI configurations.

---

## 🎯 Why I Built This

Most AI assistants try to solve every problem with a single model.

JEV explores a different approach:

> **Use an intelligent router to decide which specialized model should handle the task.**

This project is an experiment in building a practical local AI system where:

```text
Routing
   +
Specialized Models
   +
Local Inference
   +
Image Generation
```

work together as one assistant.

---

## 📌 Project Status

### Current

```text
🟢 Query routing
🟢 General model
🟢 Coding model
🟢 Image generation
🟢 Ollama integration
🟢 ComfyUI integration
🟢 Local image saving
🟢 Environment configuration
🟢 GitHub repository
```

### Planned

```text
🔵 Multi-intent task planning
🔵 Sequential task orchestration
🔵 Better conversation memory
🔵 Improved model selection
🔵 More specialized models
🔵 Better UI
```

---

## 👨‍💻 Author

**Dishambha Awasthi**

Computer Science Engineering student interested in:

```text
Artificial Intelligence
Machine Learning
LLMs
AI Agents
Local AI
Backend Development
Data Engineering
```

---

## ⭐ Support

If you find the project interesting, consider giving the repository a ⭐ on GitHub.

---

<p align="center">

### 🤖 JEV

**One assistant. Multiple models. One intelligent router.**

</p>
