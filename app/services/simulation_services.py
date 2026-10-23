from collections.abc import Callable
from uuid import UUID, uuid4
from threading import Lock
from time import monotonic

from concurrent.futures import ThreadPoolExecutor

from app.models.iteration_state import IterationState
from app.models.goals_state import Goal
from app.models.simulation.simulation_settings import SimulationSettings, DebugState
from app.models.simulation.simulation_results import SimulationResults, SimulationOutput
from app.models.simulation.simulation_job import SimulationJob
from app.schemas.simulation import SimulationRequest
from app.simulation.simulation_engine import run_simulation
from app.services.inventory_services import calculate_initial_wishes

simulation_jobs_lock = Lock()
simulation_jobs: dict[UUID, SimulationJob] = {}
simulation_executor = ThreadPoolExecutor(max_workers=2)

MAX_JOB_AGE = 3600 # Simulations can live in memory for up to an hour.

def create_simulation_job(request: SimulationRequest) -> SimulationJob:
    clean_up_old_jobs(simulation_jobs)
    # First clears old jobs
   
    job_uuid = uuid4()
    job = SimulationJob(
        job_id=job_uuid,
        status="pending",
        completed_iterations=0,
        total_iterations=request.simulation_settings.iteration_count)
    with simulation_jobs_lock:
        simulation_jobs[job_uuid] = job
        
    simulation_executor.submit(run_simulation_job, job_uuid, request)
    return job

def get_simulation_job(job_id: UUID) -> SimulationJob:
    clean_up_old_jobs(simulation_jobs)
    # First clears old jobs
    
    job = simulation_jobs.get(job_id)   
    return job

def run_simulation_job(job_id: UUID, request: SimulationRequest) -> None:
    def update_progress(completed_iterations: int, total_iterations: int) -> None:
        with simulation_jobs_lock:
            job = simulation_jobs.get(job_id)

            if job is not None:
                job.completed_iterations = completed_iterations
                job.total_iterations = total_iterations

    with simulation_jobs_lock:
        job = simulation_jobs.get(job_id)
        if job is None:
            return
    
        job.status = "running"
        
    try:
        result = instance_simulation(request, progress_callback=update_progress)
        with simulation_jobs_lock:
            job = simulation_jobs.get(job_id)
            if job is not None:
                job.result = result
                job.status = "completed"
            
    except Exception:
        with simulation_jobs_lock:
            job = simulation_jobs.get(job_id)

            if job is not None:
                job.status = "failed"
                job.error = "The simulation failed."

def instance_simulation(
    request: SimulationRequest,
    progress_callback: Callable[[int, int], None] | None = None,
) -> SimulationOutput:
    simulation_settings = SimulationSettings(
        request.simulation_settings.iteration_count,
        request.simulation_settings.starglitter_refund,
        request.simulation_settings.continue_after_goals_are_finished

    )
    starting_wishes, masterless_starglitter = calculate_initial_wishes(
        simulation_settings, 
        request.resources.intertwined_fates,
        request.resources.primogems,
        request.resources.genesis_crystals,
        request.resources.masterless_starglitter
    )

    iteration_state = IterationState(
        intertwined_fates=starting_wishes,
        masterless_starglitter=masterless_starglitter,
        five_character_pity=request.pity.five_character_pity,
        four_character_pity=request.pity.four_character_pity,
        five_weapon_pity=request.pity.five_weapon_pity,
        four_weapon_pity=request.pity.four_weapon_pity,
        five_character_guarantee=request.pity.five_character_guarantee,
        four_character_guarantee=request.pity.four_character_guarantee,
        five_weapon_guarantee=request.pity.five_weapon_guarantee,
        four_weapon_guarantee=request.pity.four_weapon_guarantee,
        epitomized_path=request.pity.epitomized_path,
        capturing_radiance=request.pity.capturing_radiance,
        characters=request.characters.model_dump(),
        weapons = {"five" : {},"four" : {}},
        goals=request.goals,
        banners=request.banners
    )
    initialized_simulation_results = SimulationResults()
    initialized_debug_state = DebugState()



    results = run_simulation(
        iteration_state,
        initialized_simulation_results,
        simulation_settings,
        initialized_debug_state,
        progress_callback,
    )
    return results

def clean_up_old_jobs(job_list: dict[UUID, SimulationJob]):
    for job_index in list(job_list):
        job = job_list[job_index]
        if job.status == "completed" and monotonic() - job.time_of_job_schedule > MAX_JOB_AGE:
            job_list.pop(job_index)
            
     