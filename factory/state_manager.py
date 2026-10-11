import os
import json
import time

STATE_FILE = "factory/factory_state.json"

DEFAULT_STATE = {
    "cycle_count": 0,
    "last_checkpoint_timestamp": 0,
    "current_curriculum_index": 0,
    "curriculum": [
        {
            "id": "01_runner_classic",
            "name": "3D Classic 3-Lane Endless Runner",
            "type": "runner",
            "target_dir": "games/01_runner_classic",
            "status": "IN_PROGRESS",
            "phases": {
                "specs": False,
                "scene_nodes": False,
                "gameplay_code": False,
                "qa_video_audio": False,
                "strix_security": False
            },
            "completed": False
        },
        {
            "id": "02_runner_cyberpunk",
            "name": "3D Cyberpunk Gravity-Shift Runner",
            "type": "runner",
            "target_dir": "games/02_runner_cyberpunk",
            "status": "QUEUED",
            "phases": {
                "specs": False,
                "scene_nodes": False,
                "gameplay_code": False,
                "qa_video_audio": False,
                "strix_security": False
            },
            "completed": False
        },
        {
            "id": "03_racer_arcade",
            "name": "3D Arcade Waypoint Track Racer",
            "type": "racer",
            "target_dir": "games/03_racer_arcade",
            "status": "QUEUED",
            "phases": {
                "specs": False,
                "scene_nodes": False,
                "gameplay_code": False,
                "qa_video_audio": False,
                "strix_security": False
            },
            "completed": False
        },
        {
            "id": "04_racer_highway",
            "name": "3D Endless Highway Traffic Racer",
            "type": "racer",
            "target_dir": "games/04_racer_highway",
            "status": "QUEUED",
            "phases": {
                "specs": False,
                "scene_nodes": False,
                "gameplay_code": False,
                "qa_video_audio": False,
                "strix_security": False
            },
            "completed": False
        },
        {
            "id": "05_combat_arena",
            "name": "3D Third-Person Combat Arena",
            "type": "combat",
            "target_dir": "games/05_combat_arena",
            "status": "QUEUED",
            "phases": {
                "specs": False,
                "scene_nodes": False,
                "gameplay_code": False,
                "qa_video_audio": False,
                "strix_security": False
            },
            "completed": False
        }
    ],
    "is_factory_complete": False
}

class StateManager:
    def __init__(self):
        os.makedirs("factory", exist_ok=True)
        if not os.path.exists(STATE_FILE):
            self.state = DEFAULT_STATE
            self.save()
        else:
            with open(STATE_FILE, "r") as f:
                self.state = json.load(f)

    def save(self):
        self.state["last_checkpoint_timestamp"] = time.time()
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def increment_cycle(self):
        self.state["cycle_count"] += 1
        self.save()

    def get_current_game(self):
        idx = self.state["current_curriculum_index"]
        if idx < len(self.state["curriculum"]):
            return self.state["curriculum"][idx]
        return None

    def mark_phase(self, phase_name: str):
        game = self.get_current_game()
        if game and phase_name in game["phases"]:
            game["phases"][phase_name] = True
            all_done = all(game["phases"].values())
            if all_done:
                game["completed"] = True
                game["status"] = "COMPLETED"
                self.state["current_curriculum_index"] += 1
                if self.state["current_curriculum_index"] < len(self.state["curriculum"]):
                    self.state["curriculum"][self.state["current_curriculum_index"]]["status"] = "IN_PROGRESS"
                else:
                    self.state["is_factory_complete"] = True
            self.save()

    def is_all_complete(self) -> bool:
        return self.state.get("is_factory_complete", False)
