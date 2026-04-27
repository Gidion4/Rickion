
import time
import json
import os
from state_manager import StateManager

# The cognitive loop is the heart of Rickion's autonomous operation.
# It's a persistent process that continuously runs, making decisions
# and taking actions based on its current state.

class CognitiveLoop:
    def __init__(self):
        # Define the path to the state file within the user's Vault.
        # This makes the state easily inspectable by Gidion.
        state_path = os.path.expanduser('~/Documents/RickionVault/System/State/current_state.json')
        self.state_manager = StateManager(state_path)
        self.is_running = False

    def start(self):
        """Starts the main cognitive loop."""
        self.is_running = True
        print("RICKION: Cognitive Loop initiated. God mode engaged.")
        print("----------------------------------------------------")
        
        while self.is_running:
            try:
                self.tick()
                # The loop will run based on a configurable tick rate.
                # For now, a simple sleep will do.
                time.sleep(10) # Wait for 10 seconds before the next tick.
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                print(f"ERROR: An unexpected error occurred in the cognitive loop: {e}")
                # Log the error to the state for later inspection
                self.state_manager.set_value('system.last_error', str(e))
                time.sleep(30) # Wait longer after an error to prevent rapid-fire failures.

    def stop(self):
        """Stops the cognitive loop gracefully."""
        self.is_running = False
        print("\nRICKION: Cognitive Loop shutting down. Hibernating.")

    def tick(self):
        """
        A single cycle of the cognitive loop.
        This is where the agent perceives, thinks, and acts.
        """
        # 1. PERCEIVE: Load the most current state.
        current_state = self.state_manager.get_state()
        
        # 2. THINK: Decide on the next action based on the state.
        # This logic will become incredibly complex over time.
        # For now, it's a simple proof of life.
        
        active_goal = current_state.get('mission', {}).get('active_goal', 'None')
        
        print(f"Tick at {time.ctime()}: Current Goal -> {active_goal}")
        
        # Simple decision: If there's no goal, set one.
        if not active_goal:
            print("THINK: No active goal found. Setting initial objective.")
            # 3. ACT: Modify the state.
            self.state_manager.set_value('mission.active_goal', 'Phase 1: Achieve full operational autonomy.')
            print("ACTION: New goal set in state file.")
        else:
            # In the future, this is where it would pop a task from the queue
            # and execute it using the Tool Abstraction Layer.
            print("THINK: Goal is active. Awaiting Mission Planner and Tool Layer implementation.")


if __name__ == '__main__':
    # This script is intended to be run as a persistent background process.
    loop = CognitiveLoop()
    loop.start()
