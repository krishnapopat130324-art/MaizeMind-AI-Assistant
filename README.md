# 🧠 MaizeMind

<div align="center">

### **Visual Reasoning Assistant** · **Local** · **Privacy-First** · **Free**

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**An AI-powered visual reasoning assistant that transforms plain text into interactive argument maps using a local Large Language Model.**

</div>

---

# 📖 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Example Output](#-example-output)
- [Tech Stack](#-tech-stack)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Contact](#-contact)

---

# 📖 About

**MaizeMind** is a lightweight AI-powered visual reasoning assistant that extracts logical structures from written text and converts them into interactive argument maps.

Instead of reading long paragraphs to understand someone's reasoning, MaizeMind automatically identifies:

- Main Claims
- Supporting Claims
- Counter Arguments
- Evidence
- Relationships
- Missing Evidence (Argument Gaps)

Everything runs **locally** using **Ollama**, ensuring complete privacy with no cloud APIs or paid services.

### 🎯 Perfect For

- 🎓 Students
- 📚 Researchers
- ✍️ Writers
- 👨‍⚖️ Debate Preparation
- 📄 Essay Analysis
- 📊 Research Papers
- 🧠 Critical Thinking

---

# ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Argument Extraction** | Automatically detects claims, evidence, and logical relationships. |
| 📊 **Interactive Visualization** | Displays argument structures as interactive graphs. |
| 🎨 **Color-Coded Nodes** | Different colors for claims, evidence, and counter arguments. |
| 🔎 **Gap Detection** | Identifies unsupported claims that need evidence. |
| 🔒 **Privacy First** | Runs completely offline using Ollama. |
| ⚡ **Fast Processing** | Generates visualizations within seconds. |
| 💰 **100% Free** | No subscriptions or API keys required. |
| 🖥️ **Modern UI** | Responsive HTML/CSS/JavaScript interface. |

---

# 🚀 Quick Start

## Prerequisites

Before running the project, install:

- Python **3.10+**
- Ollama
- Git (optional)

Download Ollama:

https://ollama.com/download

---

## Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/krishnapopat130324-art/MaizeMind-AI-Assistant.git
cd MaizeMind-AI-Assistant
```

### 2️⃣ Create Virtual Environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Download the AI Model

```bash
ollama pull llama3.2:1b
```

---

# ▶️ Running the Project

## Terminal 1

Start Ollama

```bash
ollama serve
```

---

## Terminal 2

Start FastAPI

```bash
python app.py
```

You should see:

```text
🚀 Starting MaizeMind API...
🧠 Using model: llama3.2:1b
✅ Ollama connected
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

## Open the Frontend

Navigate to:

```
frontend/index.html
```

Open it in your browser.

---

# 📊 How It Works

```text
          User Text
               │
               ▼
      Ollama (LLM Analysis)
               │
               ▼
   Claim & Evidence Extraction
               │
               ▼
      NetworkX Graph Builder
               │
               ▼
      vis.js Visualization
               │
               ▼
      Interactive Argument Map
```

### Workflow

1. User enters text.
2. Ollama analyzes the text.
3. Claims and evidence are extracted.
4. Relationships are identified.
5. NetworkX creates a graph.
6. vis.js renders an interactive visualization.
7. Unsupported claims are highlighted.

---

# 📁 Project Structure

```text
MaizeMind/
│
├── app.py                     # FastAPI backend
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation
├── .gitignore                 # Git ignore rules
│
├── core/
│   ├── __init__.py
│   ├── extractor.py           # Argument extraction
│   └── graph.py               # Graph builder
│
├── llm/
│   ├── __init__.py
│   └── client.py              # Ollama client
│
├── frontend/
│   ├── index.html             # HTML + CSS UI
│   └── script.js              # JavaScript logic
│
└── data/
    ├── input.txt              # Sample input
    └── output.json            # Generated output
```

---

# 🎯 Example Output

## Input

```text
Social media has a negative impact on mental health.

Studies show excessive social media usage increases anxiety and depression.

However, some researchers argue moderate use improves social connection.
```

---

## Generated Output

```text
Claims Found

C1 [MAIN]
Social media has a negative impact on mental health.

C2 [SUPPORTING]
Studies show excessive social media increases anxiety.

C3 [COUNTER]
Moderate social media use improves social connection.

Evidence

E1
Studies show excessive social media usage increases anxiety and depression.

Relationships

E1 → supports → C1

C2 → supports → C1

C3 → challenges → C1

Gaps

No unsupported claims detected.
```

---

# 🛠️ Tech Stack

| Component | Technology |
|------------|------------|
| Backend | FastAPI |
| Language | Python |
| LLM | Ollama + Llama 3.2 |
| Graph Engine | NetworkX |
| Visualization | vis.js |
| Frontend | HTML, CSS, JavaScript |

---

# 🔧 Configuration

## Change the AI Model

Open:

```
llm/client.py
```

Example:

```python
def query_ollama(prompt, model="llama3.2", temperature=0.1):
```

Available Models

| Model | Size | Command |
|--------|------|----------|
| llama3.2:1b | 1.3GB | `ollama pull llama3.2:1b` |
| llama3.2 | 2.0GB | `ollama pull llama3.2` |
| llama3.1 | 4.7GB | `ollama pull llama3.1` |
| phi3 | 2.2GB | `ollama pull phi3` |

---

## Change API Port

Edit:

```python
uvicorn.run(app, host="127.0.0.1", port=8001)
```

---


# 📞 Author

**Krishna Popat**

---

# ⭐ Support

If you found this project useful, please consider giving it a **⭐ Star** on GitHub.

Your support motivates further development of free and privacy-first AI tools.

---

<div align="center">

### ⭐ Star the Repository • 🐞 Report Issues • 💡 Suggest Features

**Made with ❤️, Python, FastAPI, Ollama & Local AI**

</div>
