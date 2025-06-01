# TravelBud - AI-Powered Travel Assistant 

## 🌍 Overview

TravelBud is an intelligent travel assistant that leverages the Fetch.ai ecosystem to help you effortlessly plan personalized travel itineraries. It uses specialized AI agents to handle flight bookings, hotel reservations, food recommendations, attraction suggestions, and local tips through natural language conversations.

---

## ⚡ Features

- Personalized Itinerary Creation: Get custom travel plans based on your interests, budget, and schedule.
- Live Travel Data: Access up-to-date information on flights, hotels, and attractions via the Amadeus API.
- Real-Time Search: Fetch the latest destination insights and recommendations using the Tavily Search API.
- Conversational AI: Interact naturally with TravelBud, powered by ASI1 LLM and OpenAI API for rich, context-aware dialogue.
- Chat Protocol: Seamless agent-to-agent communication.
- Multi-Agent Coordination: Sophisticated workflow management using LangGraph and uAgents for seamless, multi-step planning.
- Privacy & Security: All communications and data are secured using the uAgents framework.
- Hosting Platform: Agentverse deployment for decentralized operation

---

## 🛠️ Tech Stack

### Core Infrastructure

🧠 **ASI LLM** - Advanced reasoning and explainable outputs

🤖 **uAgents** - Autonomous, secure agent execution

🌐 **Agentverse** - Agent deployment & discovery platform

🔍 **Tavily** - Real-time search for travel content and news

🧠 **OpenAI** - Natural language understanding and conversation

### Supporting Technologies

🐍 **LangGraph** - Multi-agent workflow orchestration 

📡 **REST API** - Frontend-backend communication

🎨 **Streamlit** - User interface

🔄 **Chat Protocol** - Agent communication standard

---

## 🔗 Agent Communication Flow

- User query → Streamlit frontend
- REST API → User Assistant Agent
- ASI LLM classifies query type
- Route to specialized agent
- Agent uses Tavily for real-time search
- Response → User Assistant → Frontend

---

## 🚀 Quickstart

#### Clone the Repository

    https://github.com/deebhikakumaran/TravelBud.git
    cd TravelBud

#### Install Dependencies

    pip install -r requirements.txt

#### Set Up API Keys

Create a `.env` file in the root directory and add your keys:

    OPENAI_API_KEY=your-openai-key
    ASI_API_KEY=your-asi1-key
    AGENTVERSE_API_KEY=your-agentverse-key
    LANGCHAIN_TRACING_V2=false  
    LANGSMITH_API_KEY=your-langsmith-key
    TAVILY_API_KEY=your-tavily-key
    AMADEUS_API_KEY=your-amadeus-key

#### Running the System

    1. Start Agents (in separate terminals):

        python user_assistant.py
        python flight_agent.py
        python hotel_agent.py
        python food_agent.py
        python attraction_agent.py
        python local_tips_agent.py

    2. Launch Streamlit UI:

        streamlit run ui.py

---

## 🧑‍💻 Team

- [Deebhika Kumaran](https://github.com/deebhikakumaran)
- [Syed Zakiyuddin](https://github.com/zakiy7)

---

## 🤝 Contributing (Coming soon)

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.

---

## 📜 License (Not yet licensed)

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

Built during **AI Agent Hackathon 2.0 @ Paradox'25 IIT Madras**

[![Powered by Fetch.ai](https://img.shields.io/badge/Powered%20by-Fetch.ai-000000?style=flat&logo=fetch.ai)](https://fetch.ai)

TravelBud – Your smart travel companion. Plan less, explore more!

---