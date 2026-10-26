# Genshin Impact Wish Simulator API
A REST API built with Python and FastAPI for a Monte Carlo Simulation for the gacha system of Genshin Impact.
Grants you information about resources spent for any given goal, alongside your chances to obtain them, based on the state
of your account, averaged through a set of iterations.

View live demo: https://gacha-simulator-vtbh.onrender.com/

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
cd gacha-simulator-api
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

Docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Simulation Structure
This simulation is intended to provide a higher accuracy and personalization than a simple chance calculator.
It comes at the cost of a higher configuration complexity, which ideally, should be mitigated by the frontend.

The simulation parameters are split in different categories:

### Resources
Intertwined Fates, Primogems, Genesis Crystals, and Starglitter. The main wishing resources.

### Pity
Baseline pity mechanics and special ones such as an estimate of the capturing radiance system and a replica of the epitomized path.

### Goals and Banners
What you wish to get, and where it pulls it from.
The chosen structure is one where all goals require you to make a complete replica of a Genshin Impact Banner.
This is to provide a closer estimate to what it might actually be like to pull, making starglitter refund and off-shoot items more realistic.

### Characters
Inventory of characters, to allow for proper starglitter refund.

### Settings
**Mandatory:**
- Iteration count int. Higher amount leads to more accurate results at the cost of higher processing time. Set to 50,000 max by default.
- Starglitter Refund bool.

**Optional:**
- Changes to the inner calculations of soft-pity systems, chances, currency rewards, currency costs, etc. 

## API Endpoints

### Simulation
Simulation endpoints are used to run and to retrieve the progress or result of a simulation job.

**POST /simulation** - Creates and run a simulation. Returns its ID.
**GET /simulation/{job_id}** - Retrieves an instanced or completed simulation given an ID. 

#### Simulation Workflow

- Send a POST /simulation request with the simulation configuration.
- The job can be retrieved after, and lives for up to an hour in memory.
- Poll GET /simulation/{job_id} using that ID to track progress.
- Once the job is completed, retrieve the results from the result field. If the job fails, check the error field.

**Example: Initial response**
{
  "job_id": "6f5d507b-3292-4225-81e3-0fa3f9258a05",
  "status": "running",
  "completed_iterations": 40,
  "total_iterations": 1000,
  "result": null,
  "error": null
}

**Example: Completed response**
{
  "job_id": "6f5d507b-3292-4225-81e3-0fa3f9258a05",
  "status": "completed",
  "completed_iterations": 1000,
  "total_iterations": 1000,
  "result": {
    "finished_goals": {
      "C2 Arlecchino": 933
    },
    "simulation_time": 0.7105541000000812,
    "average_wishes_used": 335.224,
    "average_masterless_starglitter_earned": 128.167,
    "average_masterless_starglitter_refund": 1.082797733522917,
    "average_masterless_fortuna_earned": 0,
    "average_masterless_stardust_earned": 4304.13,
    "starting_wishes": 310,
    "average_wishes_per_goal": {
      "C2 Arlecchino": 235.199
    }
  },
  "error": null
}
### Goals and Banners
These endpoints provide operations to create and edit goals and banners, without messing with the simulation workflow.
They offer a convenient way to create or edit any goal or banner, to get them ready for a simulation request.
The API does not persist these objects in memory or in a database. They are simply retrieved and can be used in a simulation.

**POST /banners** - Creates a banner
**POST /banners/edit** - Edits a banner.

**POST /goals** - Creates a goal.
**POST /goals/edit** - Edits a goal. 

For request schemas and additional details, see the interactive API documentation at /docs.

### Notes 
**Job retention** is kept at a maximum of one hour by default, and in memory.

### To-Do
Upkeep of new items and mechanics.
Additional statistics.

## Disclaimer

This is an unofficial, fan-made Genshin Impact wish simulator. It is not affiliated with, endorsed by, or sponsored by HoYoverse or Cognosphere.

Genshin Impact and its associated characters, names, trademarks, artwork, and other intellectual property belong to their respective rights holders. This project's license applies only to its original code and does not grant rights to third-party intellectual property.

Genshin Impact is a trademark of its respective rights holders.