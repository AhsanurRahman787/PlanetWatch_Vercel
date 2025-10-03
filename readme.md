# 🔭 PlanetWatch: The Planetary Defense Policy Simulator 🚨

## Introduction

**PlanetWatch** addresses a critical gap in space policy: the need for rapid, informed decision-making during a Near-Earth Object (NEO) threat. Our application is the ultimate **policymaker's aid** for the NASA Space Apps Challenge, turning complex astrophysics into a high-stakes simulation.

This platform empowers users to **act as policymakers**, analyzing scientific data, projecting impact risks, and making crucial defense and mitigation decisions—all evaluated in real-time by an intelligent agent.

---

## 🎯 Core Focus: The Policy Maker Game

The heart of PlanetWatch is the **Policy Maker Game**, designed to challenge and educate users on the complexities of planetary defense response.

### Game Mechanics and Policy Guidance

* **Policy AI Judge (Built with LangChain):** This **Agentic AI** system acts as the policy advisor and evaluator. It provides data-driven, objective feedback on the user's choices, judging their effectiveness, ethical consequences, and real-world viability under extreme time pressure.
* **Impact Scenario Generation:** The game starts with a simulated threat detected by the **Impactor 25 Tracker** (a high-priority threat feed).
* **Critical Decision Points:** Users face a series of timed, resource-allocation and strategy decisions (e.g., *Should we fund a high-risk kinetic impactor mission? Where do we allocate disaster relief funds?*).
* **Outcomes & Review:** The **Policy AI Judge** scores the user's performance, providing a comprehensive review of the scientific, economic, and geopolitical implications of their policy decisions.

---

## ✨ Application Features (The Six-Button Home Page)

PlanetWatch is structured around a clear **Home Page** with six dedicated buttons:

1.  **Policy Maker Game:** The core simulation for hands-on decision-making.
2.  **Policy AI Judge:** Direct access to the Agentic AI for educational context and policy evaluation (Built using **LangChain**).
3.  **Impact Simulator:** Allows users to define hypothetical impact parameters and visualize calculated damage (kinetic energy, blast radius, seismic effects).
4.  **NEO Tracker:** Provides a 3D simulation with real-time tracking and orbital visualization of known **Near-Earth Objects (NEOs)**, grounded in NASA data.
5.  **Impactor 25 Tracker:** A focused feed for monitoring a specific, high-risk simulated threat object.
6.  **History Page:** An educational module on historical impact events and the evolution of planetary defense strategy.

---

## 🛠️ Technical Stack and Getting Started

PlanetWatch is a lightweight, Python-based application optimized for rapid deployment.

### ⚙️ Technical Specifications
* **Core Logic / Backend:** Python
* **Web Framework:** Flask
* **AI/LLM Integration:** LangChain (used to build the Policy AI Agent)
* **Frontend/Visualization:** Node.js (used for handling front-end assets/rendering)
* **Database:** None (State is managed in memory or flat files, ideal for hackathons)

### Prerequisites
You must have **Python 3** and **Node.js** installed on your system.

### Installation & Execution

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/](https://github.com/)[Your-GitHub-Username]/PlanetWatch.git
    cd PlanetWatch
    ```

2.  **Install dependencies:**
    Run the following command in the project directory to install all required Python packages (including `Flask` and `LangChain`):
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    Simply execute the main file from the terminal:
    ```bash
    python3 run.py
    ```
    The web application should launch, providing access to the **Home Page**.

---

## 📊 Data Sources

PlanetWatch grounds its simulations in real space and seismic data using the following publicly accessible APIs:

* **NASA Near-Earth Object (NEO) Web Service (NeoWs) API:** Provides orbital parameters, size estimates, and close-approach data for asteroids, essential for realistic impact scenario generation.
* **U.S. Geological Survey (USGS) NEIC Earthquake Catalog:** Used to model seismic effects by correlating impact energy with equivalent earthquake magnitudes.
* **Approximate Positions of the Planets (NASA Resource):** Used for understanding orbital mechanics and simulating the solar system visualization.
* **Near-Earth Comets - Orbital Elements API:** Supplements our orbital modeling capabilities.

