from django.conf import settings

import time
from logging import Logger
from statistics import mean


def subset_aggregates(subsets: dict) -> dict:
    keys = {key for value in subsets.values() for key in value.keys()}
    value_ls_dict = {
        key: [
            val.get(key, {}).get("runtime") for val in subsets.values() 
            if val.get(key, {}).get("runtime") is not None
        ] for key in keys
    }
    results = {
        key: {
            "records": len(subsets.values()),
            "sum": None if value_ls_dict[key] == [] else round(sum(value_ls_dict[key]), 4),
            "avg": None if value_ls_dict[key] == [] else round(mean(value_ls_dict[key]), 4),
            "min": None if value_ls_dict[key] == [] else min(value_ls_dict[key]),
            "max": None if value_ls_dict[key] == [] else max(value_ls_dict[key])
        }
        for key in keys
    }
    return results


class CodeProfiler(object):
    """
    Code Profiler that easily records step progress within a larger process
        
    Example
    ---------
    process = CodeProfiler(process_name="location_search", logger=service_logger)
    
    process.start_step("queryset")
    <code>
    process.complete_step("queryset")

    process.start_step("scoring")
    <code>
    process.complete_step("scoring", meta={"records": len(results)})

    process.stop()

    """

    def __init__(self, process_name: str, logger: Logger, active: bool = settings.DEBUG):
        self.process_name = process_name
        self.logger = logger
        self.active = active
        self.start = time.perf_counter()
        self.profile = {}

    def info(self, step_name: str, msg: str):
        self.logger.info(
            f"[process={self.process_name} step={step_name}] {msg}"
        )

    def start_step(self, step_name: str):
        if not self.active:
            return
        
        # Record Start of Process
        self.profile.update({step_name: {"start": time.perf_counter()}})
        self.logger.info(f"[process={self.process_name} step={step_name}] start")

    def complete_step(self, step_name: str, meta: dict = None):
        if not self.active:
            return
        step = self.profile.get(step_name, None)
        
        # Record end if step not already existing
        if step is None:
            self.profile.update({step_name: {"end": time.perf_counter()}})
            self.logger.info(f"[process={self.process_name} step={step_name}] complete")
        
        elif step.get("start", None) is not None:
            runtime = round(time.perf_counter() - step.get("start"), 4)
            step.update({"end": time.perf_counter(), "runtime": runtime})
            
            # TODO: Process Substep Meta
            subsets = step.pop("subsets", None)
            if subsets is not None:
                step["subsets"] = subset_aggregates(subsets=subsets)
            
            # Store Meta like number of records processsed
            if meta is not None:
                step.update({"meta": meta})
            
            # Update Profile
            self.profile.update({step_name: step})
            self.logger.info(
                f"[process={self.process_name} step={step_name}] complete runtime={runtime}"
            )

    def start_substep(self, step_name: str, subprocces_id: str, substep_name: str):
        if not self.active:
            return
        
        # Step Name does not exist
        step =  self.profile.get(step_name, None)
        if step is None:
            return
        
        # Get All Subsets
        subsets = step.get("subsets", {})
        subprocess = subsets.get(subprocces_id, {})
        subprocess.update({substep_name: {"start": time.perf_counter()}})
        subsets.update({subprocces_id: subprocess})
        step.update({"subsets": subsets})

    def complete_substep(self, step_name: str, subprocces_id: str, substep_name: str, meta: dict = None):
        if not self.active:
            return
        subprocess = self.profile.get(step_name, {}).get("subsets", {}).get(subprocces_id)
        # Record end if step not already existing
        if subprocess is None:
            if self.profile.get(step_name, None) is None:
                return
        substep = subprocess.get(substep_name, {})
        if substep.get("start", None) is not None:
            runtime = round(time.perf_counter() - substep.get("start"), 4)
            substep.update({"end": time.perf_counter(), "runtime": runtime})
            # Store Meta like number of records processsed
            if meta is not None:
                substep.update({"meta": meta})


    def stop(self):
        if not self.active:
            return
        runtime = time.perf_counter() - self.start
        self.logger.info(
            f"[process={self.process_name}] complete runtime={runtime} profile={str(self.profile)}"
        )