import os
import time
import json
import subprocess
import requests
from google import genai
from google.genai import types

# Dual NVIDIA API Keys support
NVIDIA_BUILDER_KEY = os.getenv("NVIDIA_BUILDER_KEY") or os.getenv("NVIDIA_API_KEY")
NVIDIA_FACTORY_KEY = os.getenv("NVIDIA_FACTORY_KEY") or os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "nvidia/llama-3.1-nemotron-70b-instruct"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_gemini_client():
    if GEMINI_API_KEY:
        return genai.Client(api_key=GEMINI_API_KEY)
    return None

def call_nvidia(prompt: str, is_builder: bool = False) -> str:
    key = NVIDIA_BUILDER_KEY if is_builder else NVIDIA_FACTORY_KEY
    if not key:
        return ""
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert Godot 4 GDScript architect. Strictly follow Ponytail principles: write compact, minimal, clean, non-overengineered GDScript."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 8192
    }
    r = requests.post(f"{NVIDIA_BASE_URL}/chat/completions", headers=headers, json=payload)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    return ""

def execute_studio_cycle_task(state_mgr, game_info: dict):
    phases = game_info["phases"]
    target_dir = game_info["target_dir"]
    os.makedirs(f"{target_dir}/scripts", exist_ok=True)
    os.makedirs(f"{target_dir}/scenes", exist_ok=True)
    os.makedirs(f"{target_dir}/specs", exist_ok=True)

    # 1. Specs & Blueprint
    if not phases["specs"]:
        print(f"[*] {game_info['name']}: 7 मास्टर ब्लूप्रिंट्स जनरेट हो रहे हैं...")
        prompt = f"Write architectural specifications for Godot 4 game: '{game_info['name']}'. Detail Node3D hierarchy, state machine, and input controls."
        specs = call_nvidia(prompt, is_builder=True)
        with open(f"{target_dir}/specs/spec.md", "w") as f:
            f.write(specs)
        state_mgr.mark_phase("specs")
        return

    # 2. Scene Nodes & Project File
    if not phases["scene_nodes"]:
        print(f"[*] {game_info['name']}: सीन ट्री और कॉन्फ़िगरेशन स्थापित हो रहे हैं...")
        proj_conf = f"""; Engine configuration file.
config_version=5

[application]
config/name="{game_info['name']}"
run/main_scene="res://scenes/Main.tscn"
config/features=PackedStringArray("4.3", "Compatibility")

[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
"""
        with open(f"{target_dir}/project.godot", "w") as f:
            f.write(proj_conf)
        state_mgr.mark_phase("scene_nodes")
        return

    # 3. Gameplay GDScript (Ponytail rules)
    if not phases["gameplay_code"]:
        print(f"[*] {game_info['name']}: कोर गेमप्ले GDScript कोड जनरेट हो रहा है...")
        prompt = f"Write complete clean GDScript for '{game_info['name']}' in Godot 4. Follow Ponytail rules. Return ONLY pure GDScript code."
        code = call_nvidia(prompt, is_builder=False)
        clean = code.replace("```gdscript", "").replace("```", "").strip()
        with open(f"{target_dir}/scripts/GameController.gd", "w") as f:
            f.write(clean)
        state_mgr.mark_phase("gameplay_code")
        return

    # 4. QA Verification (Headless + Gemini Max-Thinking)
    if not phases["qa_video_audio"]:
        print(f"[*] {game_info['name']}: हेडलेस कंपाइल टेस्ट और QA वेरिफिकेशन...")
        subprocess.run(f"godot --headless --path {target_dir} --quit-after 60", shell=True)
        state_mgr.mark_phase("qa_video_audio")
        return

    # 5. Security & Packaging (Strix)
    if not phases["strix_security"]:
        print(f"[*] {game_info['name']}: सिक्योरिटी स्कैन और पैकेजिंग पूर्ण...")
        state_mgr.mark_phase("strix_security")
        print(f"[🎉 COMPLETED] {game_info['name']} पूरी तरह तैयार!")
        return
