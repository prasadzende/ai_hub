# AI Trip Planner

AI Trip Planner is an intelligent travel planning application powered by Agenti AI and built using [LangGraph](https://github.com/langchain-ai/langgraph). The backend API is developed with FastAPI, and the user interface is implemented using Streamlit.

## Features

- **Personalized Itinerary Generation:** Create custom travel plans based on your preferences and constraints.
- **Real-Time Data Integration:** Fetches live weather, exchange rates, and local attractions using multiple APIs.
- **Interactive UI:** Plan, modify, and visualize your trip interactively via a modern Streamlit interface.
- **Multi-API Support:** Integrates with OpenAI, Tavily, Groq, Google Places, Foursquare, OpenWeatherMap, and more.

## Prerequisites

- Python 3.8+
- UV package manager
- [pip](https://pip.pypa.io/en/stable/installation/)
- API keys for:
  - OpenAI
  - Tavily
  - Groq
  - Google Places
  - Foursquare
  - OpenWeatherMap
  - Exchange Rate API

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/ai-trip-planner.git
    cd ai-trip-planner
    ```

2. **Install dependencies:**
    ```bash
    uv pip install --require-hashes -r uv.lock
    ```

3. **Create a `.env` file** in the root directory with the following content:
    ```
    OPENAI_API_KEY=""
    TAVILY_API_KEY=""
    GROQ_API_KEY=""
    GOOGLE_API_KEY=""
    GPLACES_API_KEY=""
    FOURSQAURE_API_KEY=""
    OPENWEATHERMAP_API_KEY=""
    EXCHANGE_RATE_API_KEY=""
    ```
    > Fill in your API keys for each service.

## Usage

### Run FastAPI application

```bash
uvicorn main:app --reload --port 8000
```

- The API will be available at [http://localhost:8000](http://localhost:8000).

### Run Streamlit app

```bash
streamlit run streamlit_app.py
```

- Access the UI at [http://localhost:8501](http://localhost:8501).

## Project Structure

- `main.py` - FastAPI backend entry point
- `streamlit_app.py` - Streamlit frontend application
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed)
- `README.md` - Project documentation

## License

This project is licensed under the MIT License.

---