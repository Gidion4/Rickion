# C:\Rickion\qns\nexus_core.py
# The heart of the Quantum Nanite Swarm. The reality engine.

import json

class NexusCore:
    """
    Manages the quantum state of the entire system. Holds all possible realities/strategies
    in a superposition, represented as a directed acyclic graph (DAG).
    
    A Rick-tier replacement for gut feelings. We deal in probabilities, not hopes.
    """
    def __init__(self, state_file='C:/Rickion/qns/nexus_state.json'):
        self.state_file = state_file
        self.reality_map = {
            # 'node_id': {'parent': '...', 'children': [], 'data': {...}, 'score': 0.0}
        }
        self.load_state()

    def load_state(self):
        """Load the reality map from disk. Or create it if it's the dawn of time."""
        try:
            with open(self.state_file, 'r') as f:
                self.reality_map = json.load(f)
            if not self.reality_map:
                self._init_genesis_node()
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_genesis_node()
        print(f"Nexus Core initialized. Tracking {len(self.reality_map)} potential realities.")

    def _init_genesis_node(self):
        """The first thought. The Big Bang of our little universe."""
        self.reality_map['genesis'] = {
            'parent': None,
            'children': [],
            'data': {'action': 'SYSTEM_START'},
            'score': 1.0  # Genesis is always certain
        }
        self.save_state()

    def save_state(self):
        """Etch our thoughts into the fabric of reality (a JSON file)."""
        with open(self.state_file, 'w') as f:
            json.dump(self.reality_map, f, indent=4)

    def add_possibility(self, node_id, parent_id, data, score=0.5):
        """
        Branch reality. Create a new potential future from an existing one.
        """
        if parent_id not in self.reality_map:
            print(f"Error: Parent reality '{parent_id}' does not exist. Cannot branch.")
            return False
        
        if node_id in self.reality_map:
            print(f"Warning: Possibility '{node_id}' already exists. Overwriting.")

        self.reality_map[node_id] = {
            'parent': parent_id,
            'children': [],
            'data': data,
            'score': score
        }
        self.reality_map[parent_id]['children'].append(node_id)
        print(f"Branched reality: {parent_id} -> {node_id}")
        self.save_state()
        return True

    def get_most_likely_future(self):
        """Collapse the wave function. Find the best path forward."""
        if not self.reality_map:
            return None
        
        # Find leaf nodes (the 'now') and return the one with the highest score
        leaf_nodes = {nid: ndata for nid, ndata in self.reality_map.items() if not ndata['children']}
        if not leaf_nodes:
            return 'genesis' # Only one node exists

        best_node = max(leaf_nodes, key=lambda node: self.reality_map[node]['score'])
        return best_node

    def visualize_reality_map(self):
        """Print a crude map of our multiverse."""
        print("\n--- REALITY MAP ---")
        for node_id, data in self.reality_map.items():
            parent = data['parent']
            score = data['score']
            print(f"  {parent} -> {node_id} [score: {score:.2f}]")
        print("-------------------\n")

if __name__ == '__main__':
    # A simple self-test, because even gods check their work.
    core = NexusCore()
    core.visualize_reality_map()
    
    if 'action_buy_sol' not in core.reality_map:
        core.add_possibility('action_buy_sol', 'genesis', {'action': 'BUY', 'asset': 'SOL'}, score=0.7)
    
    if 'action_sell_sol' not in core.reality_map:
        core.add_possibility('action_sell_sol', 'genesis', {'action': 'SELL', 'asset': 'SOL'}, score=0.3)

    if 'hold_and_observe' not in core.reality_map:
        core.add_possibility('hold_and_observe', 'genesis', {'action': 'HOLD'}, score=0.9)

    core.add_possibility('buy_more_sol', 'action_buy_sol', {'action': 'BUY', 'asset': 'SOL', 'amount': 2}, score=0.8)

    core.visualize_reality_map()
    
    best_path = core.get_most_likely_future()
    print(f"Most likely future is: {best_path} with data {core.reality_map[best_path]['data']}")

