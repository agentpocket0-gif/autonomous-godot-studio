import os
import time
import threading
import subprocess
from state_manager import StateManager
from factory_engine import execute_studio_cycle_task

class CheckpointDaemon(threading.Thread):
    def __init__(self, interval_seconds=1800):
        super().__init__()
        self.interval = interval_seconds
        self.running = True
        self.daemon = True

    def run(self):
        while self.running:
            time.sleep(self.interval)
            self.save_checkpoint()

    def save_checkpoint(self):
        try:
            print("[*] 30-मिनट का बैकग्राउंड ऑटो-कमिट शुरू...")
            subprocess.run(["git", "add", "."], check=True)
            diff = subprocess.run(["git", "diff", "--staged", "--quiet"])
            if diff.returncode != 0:
                msg = f"checkpoint: automated 30-min snapshot [Factory Cycle]"
                subprocess.run(["git", "commit", "-m", msg], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=True)
                print("[✓ CHECKPOINT] प्रोग्रेस GitHub पर सफलतापूर्वक सुरक्षित!")
        except Exception as e:
            print(f"[!] Checkpoint warning: {e}")

def run_relay():
    MAX_SESSION_SECONDS = 285 * 60  # 4h 45m
    start_time = time.time()

    state_mgr = StateManager()
    state_mgr.increment_cycle()
    current_cycle = state_mgr.state["cycle_count"]

    print(f"\n==================================================")
    print(f"🚀 गेम फैक्ट्री रिले सत्र: साइकिल #{current_cycle}")
    print(f"⏱️ अधिकतम सत्र सीमा: 285 मिनट (4h 45m)")
    print(f"==================================================\n")

    checkpoint_thread = CheckpointDaemon(interval_seconds=1800)
    checkpoint_thread.start()

    while True:
        elapsed = time.time() - start_time
        if elapsed >= MAX_SESSION_SECONDS:
            print("[⌛ HANDOFF] 285 मिनट पूर्ण। वर्तमान रनर अगले रनर को रिले सौंप रहा है...")
            break

        if state_mgr.is_all_complete():
            print("🎉 [ALL COMPLETE] पाठ्यक्रम के सभी गेम्स 100% तैयार हैं! रिले समाप्त।")
            break

        current_game = state_mgr.get_current_game()
        print(f"\n[ACTIVE GAME] {current_game['name']} (ID: {current_game['id']})")

        try:
            execute_studio_cycle_task(state_mgr, current_game)
        except Exception as e:
            print(f"[!] टास्क एरर: {e}")
            time.sleep(10)

        time.sleep(5)

    checkpoint_thread.running = False
    print(f"[✓] साइकिल #{current_cycle} संपन्न।")

if __name__ == "__main__":
    run_relay()
