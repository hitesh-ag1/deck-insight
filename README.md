# 🚀 Startup Deck Copilot

**Startup Deck Copilot** is an open-source AI tool to **analyze, summarize, and score startup pitch decks** automatically.

- 📄 Upload a startup's pitch deck (PDF)
- 📋 Extracts and structures key information
- 🏆 Scores the startup based on a **custom evaluation rubric** (for investors, accelerators, competition judges)
- 🌎 Calculates **market size** estimates from real-time internet data
- 🛠️ Pulls insights from the startup’s GitHub repositories (for developer tools/open-source startups)
- 💬 Includes a **QA chatbot** to ask natural language questions about the startup

Fully extensible and customizable for your workflows.  
Perfect for investors, analysts, startup competitions, accelerators, and ecosystem builders.

---

## 🛠 How It Works

1. Upload or provide a link to the startup’s pitch deck (PDF).
2. The system extracts key information and fills a structured profile.
3. Applies a scoring rubric customized to your preferences.
4. Estimates market size from online data sources.
5. (Optional) If it's a developer tool, pulls additional GitHub repo data.
6. Ask the built-in chatbot for any questions about the startup profile.

---

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/hitesh-ag1/deck-insight.git
cd deck-insight
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install the dependencies
```bash
pip install -r requirements.txt
```

4. Set up the environment variables:
```bash
cp .env.example .env
```
Add your API keys to .env

---

## 📚 API Endpoints

- ```POST /analyze-complete```: Full pitch deck analysis
- ```POST /analyze-pitch-deck```: Pitch deck scoring and summary
- ```POST /analyze-market-size```: Market research analysis
- ```POST /analyze-github-repository```: GitHub repository evaluation
- ```POST /chat-assistant```: Interactive Q&A about the pitch deck

---

## 🧩 Future Roadmap

- Advanced financial modeling (projections, valuation sanity checks)
- API and plugin integrations (e.g., Crunchbase, LinkedIn)
- Chrome extension for sourcing decks from web
- Support for multiple decks comparison

---

*Built with ❤️ to make startup evaluation faster, fairer, and more data-driven.*
