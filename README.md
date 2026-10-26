# Genshin Impact Wish Simulator API
A REST API built with Python and FastAPI for a Monte Carlo Simulation for the gacha system of Genshin Impact.
Grants you information about resources spent for any given goal, alongside your chances to obtain them, based on the state
of your account, averaged through a set of iterations.

## Features
- Character and weapon wish simulations with configurable simulation settings.
- Pity system supporting four-star and five-star outcomes, including soft pity and hard pity.
- Guarantee mechanics for limited characters and weapons.
- Capturing Radiance mechanics for character banners.
- Epitomized Path mechanics for weapon banners.
- Simulated Starglitter Refund based on your account's characters.
- Multi-goal management for tracking desired characters and weapons.
- Background simulation jobs with progress reporting and status polling.
- Structured API errors for consistent error handling.
- Automated tests using pytest.

## Tech Stack
- Python
- FastAPI
- Pydantic
- Uvicorn
- pytest

## Architecture

The project separates API endpoints, request and response schemas, simulation logic, and supporting services.

```
app/
├── api/ # API Routes
├── models/ # Simulation State, Settings, and Result Models.
├── schemas/ # API request and response schemas
├── services/ # Simulation mechanics and logic
└── simulation/ # Simulation Instancing and engine
```


## Getting Started

### Prerequisites

- Python 3.14.6
- Git

### Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/luxuaniside/gacha-simulator-api
cd <repository-directory>
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Run the API

Start the development server from the project root:

```bash
uvicorn app.main:app --reload
```

Replace `app.main:app` if your FastAPI application is exposed from a different module.

Once running, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
