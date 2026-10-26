import pytest 
from app.services.simulation_services import create_simulation_job
from app.schemas.simulation import SimulationRequest
from app.schemas.inventory import Resources, Pity
from app.models.simulation.simulation_job import SimulationJob

@pytest.fixture
def simulation_request():
    return SimulationRequest(
        resources=Resources(),
        pity=Pity(),
        goals=[{
            "goal_name": "string",
            "item_name": "string",
            "goal_banner": {
                "banner_name": "string",
                "banner_five_item_primary": "string",
                "banner_five_item_secondary": "string",
                "banner_four_items": [
                "string"
                ],
                "item_type": "character",
                "banner_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
            },
            "item_type": "character",
            "item_rarity": "five",
            "item_target_count": 0,
            "item_high_priority": True,
            "goal_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
            }],
        banners=[
                    {
                    "banner_name": "string",
                    "banner_five_item_primary": "string",
                    "banner_five_item_secondary": "string",
                    "banner_four_items": [
                        "string"
                    ],
                    "item_type": "character",
                    "banner_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                    }
                ],
        simulation_settings={
            "iteration_count": 10000,
            "starglitter_refund": True,
            "continue_after_goals_are_finished": True
        },
        characters={
            "five" : {},
            "four" : {}
        }
        
    )

def test_create_simulation_job(simulation_request: SimulationRequest):
    job: SimulationJob = create_simulation_job(simulation_request)
    assert job.status == "running"
    assert job.completed_iterations == 0
    assert job.total_iterations == job.request.simulation_settings.iteration_count
    

