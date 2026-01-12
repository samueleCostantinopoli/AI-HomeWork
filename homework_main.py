import heapq
import math
import time
import subprocess
import re
import os
import random



class PuzzleState:
    """Rappresenta uno stato del Generalized N-Puzzle."""
    def __init__(self, board, size, empty_pos=None):
        self.board = tuple(board)  # Tupla per renderlo hashable
        self.size = size # N (es. 3 per 8-puzzle, 4 per 15-puzzle)
        # Trova la posizione dello 0 (vuoto) se non fornita
        if empty_pos is None:
            self.empty_pos = self.board.index(0)
        else:
            self.empty_pos = empty_pos

    def __hash__(self):
        return hash(self.board)

    def __eq__(self, other):
        return self.board == other.board

    def is_goal(self):
        expected = tuple(list(range(1, self.size**2)) + [0])
        return self.board == expected

    def get_neighbors(self):
        neighbors = []
        x, y = divmod(self.empty_pos, self.size)
        
        # Movimenti possibili: Su, Giù, Sinistra, Destra
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
        
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                # Calcolo nuovo indice lineare
                new_pos = nx * self.size + ny
                
                # Scambio le tessere
                new_board = list(self.board)
                new_board[self.empty_pos], new_board[new_pos] = new_board[new_pos], new_board[self.empty_pos]
                
                neighbors.append(PuzzleState(tuple(new_board), self.size, new_pos))
        return neighbors

    def __str__(self):
        # Utility per stampare la griglia
        res = []
        for i in range(0, len(self.board), self.size):
            res.append(str(self.board[i:i+self.size]))
        return "\n".join(res)

# --- Euristiche ---

def heuristic_manhattan(state):
    """Calcola la distanza di Manhattan totale."""
    distance = 0
    for i, val in enumerate(state.board):
        if val == 0: continue # Non calcoliamo distanza per il vuoto
        
        # Posizione corrente (riga, colonna)
        curr_row, curr_col = divmod(i, state.size)
        
        # Posizione target per il valore 'val'
        # Il valore k dovrebbe stare all'indice k-1 (es. 1 all'indice 0)
        target_idx = val - 1
        target_row, target_col = divmod(target_idx, state.size)
        
        distance += abs(curr_row - target_row) + abs(curr_col - target_col)
    return distance

# --- Algoritmo A* ---

def solve_astar(start_state, timeout=60):
    """Implementazione A* come da Slide 32 (No reopening)."""
    
    # Priority Queue: (f_score, g_score, state_object)
    # g_score serve anche come tie-breaker parziale o solo informativo
    # Aggiungo un contatore 'c' per evitare confronti tra stati in caso di parità di f
    count = 0 
    open_list = []
    start_time = time.time()
    
    
    h = heuristic_manhattan(start_state)
    heapq.heappush(open_list, (h, 0, count, start_state))
    
    # Per ricostruire il percorso: came_from[state] = parent_state
    came_from = {start_state: None}
    
    # Costo g per arrivare a uno stato
    g_score = {start_state: 0}
    
    # Closed set (stati esplorati)
    closed_set = set()
    
    nodes_expanded = 0
    
    start_time = time.time()
    
    while open_list:
        if time.time() - start_time > timeout:
            return {"status": "timeout", "time": timeout, "nodes_expanded": nodes_expanded}
        
        f, current_g, _, current = heapq.heappop(open_list)
        
        if current in closed_set:
            continue
            
        if current.is_goal():
            end_time = time.time()
            return {
                "status": "success",
                "path": reconstruct_path(came_from, current),
                "nodes_expanded": nodes_expanded,
                "time": end_time - start_time
            }
        
        closed_set.add(current)
        nodes_expanded += 1
        
        for neighbor in current.get_neighbors():
            if neighbor in closed_set:
                continue
            
            tentative_g = current_g + 1 # Costo passo sempre 1
            
            # Se è un nuovo stato o abbiamo trovato una via migliore (anche se 'no reopening' 
            # implica che non riapriamo closed, dobbiamo gestire se è in open)
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_neighbor = tentative_g + heuristic_manhattan(neighbor)
                count += 1
                heapq.heappush(open_list, (f_neighbor, tentative_g, count, neighbor))
                
    return {"status": "failure"}

def reconstruct_path(came_from, current):
    path = [current]
    while came_from[current]:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def get_goal_state(size):
    """Restituisce lo stato obiettivo per una griglia size x size."""
    # Goal: 1, 2, ..., N^2-1, 0
    board = list(range(1, size**2)) + [0]
    return PuzzleState(tuple(board), size)

def generate_random_instance(size, steps=20):
    """
    Genera un'istanza valida partendo dal goal e applicando 'steps' mosse casuali.
    """
    current_state = get_goal_state(size)
    seen_boards = {current_state.board} # Per evitare cicli immediati se possibile
    
    for _ in range(steps):
        neighbors = current_state.get_neighbors()
        # Scegliamo un vicino a caso
        next_state = random.choice(neighbors)
        
        # Opzionale: evitiamo di tornare subito indietro allo stato appena visitato
        # per rendere il mescolamento più efficace
        if next_state.board in seen_boards and len(neighbors) > 1:
             # Se possibile, proviamo a sceglierne un altro
             pass 
        
        current_state = next_state
        seen_boards.add(current_state.board)
        
    return current_state



def run_planner_and_parse(domain_file, problem_file, planner_path="fast-downward.py"):
    """
    Esegue il planner, cattura l'output e legge il file sas_plan.
    """
    # Fast Downward preferisce: script -> domain -> problem -> search_options
    command = [
        "python3", planner_path, 
        domain_file, 
        problem_file,
        "--search", "astar(lmcut())" 
    ]
    
    # command = ["python3", planner_path, "--alias", "seq-opt-lmcut", domain_file, problem_file]
    
    print(f"Esecuzione planner: {' '.join(command)} ...")
    
    try:
        # CORREZIONE: Catturiamo anche stderr per il debugging
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        error_out = result.stderr
        
        # Se il return code non è 0, qualcosa è andato storto nell'esecuzione
        if result.returncode != 0:
            print("\n!!! ERRORE PLANNER !!!")
            print(error_out) # Stampa dell'errore reale
            return {"status": "error", "reason": "Planner crashed/failed", "details": error_out}

        # --- Parsing delle Metriche ---
        # Cerchiamo stringhe tipiche dell'output di Fast Downward
        time_match = re.search(r"Total time: (\d+\.\d+)s", output)
        search_time = float(time_match.group(1)) if time_match else None
        
        nodes_match = re.search(r"Expanded (\d+) state\(s\)", output)
        expanded_nodes = int(nodes_match.group(1)) if nodes_match else None
        
        # --- Parsing della Soluzione (sas_plan) ---
        plan = []
        # Controlliamo se esiste il file
        if os.path.exists("sas_plan"):
            with open("sas_plan", "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith(";"): 
                        continue
                    clean_action = line.replace("(", "").replace(")", "")
                    plan.append(clean_action)
            
            os.remove("sas_plan")
            return {
                "status": "success",
                "plan_length": len(plan),
                "plan": plan,
                "time": search_time,
                "expanded_nodes": expanded_nodes
            }
        else:
            # Se non c'è il file ma il planner ha girato, stampiamo l'output per capire
            print("\n!!! FILE sas_plan NON TROVATO. Output del planner: !!!")
            # Stampiamo solo le ultime 20 righe 
            print("\n".join(output.splitlines()[-20:]))
            return {"status": "failure", "reason": "No sas_plan found"}

    except FileNotFoundError:
        return {"status": "error", "reason": "Planner executable not found"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}
    



def generate_pddl(state, problem_name="15puzzle"):
    """
    Genera due file: domain.pddl e problem.pddl per l'istanza corrente.
    """
    size = state.size
    
    # --- 1. Generazione DOMAIN.pddl ---
    domain_str = """(define (domain n-puzzle)
  (:requirements :strips :typing)
  (:types location tile)
  (:predicates 
    (at ?t - tile ?l - location)
    (empty ?l - location)
    (adjacent ?l1 ?l2 - location)
  )

  (:action slide
    :parameters (?t - tile ?from - location ?to - location)
    :precondition (and (at ?t ?from) (empty ?to) (adjacent ?from ?to))
    :effect (and (not (at ?t ?from)) (not (empty ?to)) 
                 (at ?t ?to) (empty ?from))
  )
)
"""
    with open("domain.pddl", "w") as f:
        f.write(domain_str)

    # --- 2. Generazione PROBLEM.pddl ---
    # Dobbiamo definire oggetti (tessere e posizioni) e le adiacenze statiche della griglia.
    
    objects_str = ""
    # Locations: pos_x_y
    for r in range(size):
        for c in range(size):
            objects_str += f"pos_{r}_{c} "
    objects_str += "- location\n"
    
    # Tiles: tile_1 ... tile_N^2-1
    for i in range(1, size**2):
        objects_str += f"tile_{i} "
    objects_str += "- tile\n"
    
    init_str = ""
    # Definiamo le adiacenze (grafo della griglia)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for r in range(size):
        for c in range(size):
            for dr, dc in moves:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size:
                    init_str += f"(adjacent pos_{r}_{c} pos_{nr}_{nc}) \n"
    
    # Posizionamento iniziale delle tessere
    for i, val in enumerate(state.board):
        r, c = divmod(i, size)
        if val == 0:
            init_str += f"(empty pos_{r}_{c}) \n"
        else:
            init_str += f"(at tile_{val} pos_{r}_{c}) \n"
            
    # Goal state
    goal_str = ""
    # Goal standard: 1, 2, 3 ... ordinati
    target_idx = 0
    for val in range(1, size**2):
        # La tessera 1 va in (0,0), tessera 2 in (0,1)...
        tr, tc = divmod(target_idx, size)
        goal_str += f"(at tile_{val} pos_{tr}_{tc}) \n"
        target_idx += 1

    problem_str = f"""(define (problem {problem_name})
  (:domain n-puzzle)
  (:objects 
    {objects_str}
  )
  (:init 
    {init_str}
  )
  (:goal (and 
    {goal_str}
  ))
)
"""
    with open("problem.pddl", "w") as f:
        f.write(problem_str)
    
    return "domain.pddl", "problem.pddl"

def solve_with_planner(domain_file, problem_file):
    """
    Esegue un planner esterno. 
    Nota: Devi avere un planner installato (es. Fast Downward).
    Qui simuliamo la chiamata.
    """
    print(f"Eseguendo il planner su {domain_file} e {problem_file}...")
    
    # command = ["./fast-downward.py", domain_file, problem_file, "--search", "astar(lmcut())"]
    
    # result = subprocess.run(command, capture_output=True, text=True)
    
    
    # return parsed_results
    pass



if __name__ == "__main__":
    # 1. Setup
    N = 4 # nxn = N^2 - 1 -puzzle (partiamo facile)
    steps = 30 # Difficoltà iniziale (numero di passi dal goal)
    
    print(f"--- Generazione istanza (N={N}, steps={steps}) ---")
    start_node = generate_random_instance(N, steps)
    print("Stato Iniziale:")
    print(start_node)
    print("-" * 30)

    # 2. Esecuzione A* (Task 2.1)
    print("\n>>> Running A*...")
    res_astar = solve_astar(start_node)
    if res_astar["status"] == "success":
        print(f"A* Success! Costo: {len(res_astar['path'])}, Nodi: {res_astar['nodes_expanded']}, Tempo: {res_astar['time']:.4f}s")
    else:
        print("A* Failed.")

    # 3. Esecuzione Planning (Task 2.2)
    print("\n>>> Running Planner...")
    # Genera i file PDDL
    dom_file, prob_file = generate_pddl(start_node)
    
    

    path_to_planner = "/home/sam/Desktop/AI/HomeWork/Code/fast-downward/fast-downward.py"

    res_plan = run_planner_and_parse(dom_file, prob_file, planner_path=path_to_planner)
    
    if res_plan["status"] == "success":
        print(f"Planner Success! Lunghezza Piano: {res_plan['plan_length']}, Tempo: {res_plan['time']}s")
        print(f"Prime 3 azioni: {res_plan['plan'][:3]}...")
    else:
        print(f"Planner Failed: {res_plan.get('reason')}")