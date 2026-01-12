import time
import csv
import os
# Importa le funzioni dal tuo file principale (assumendo si chiami homework_main.py)
# Se il tuo file ha un altro nome, cambia l'import qui sotto
from homework_main import PuzzleState, solve_astar, generate_pddl, run_planner_and_parse, generate_random_instance

# --- CONFIGURAZIONE ---
PLANNER_PATH = "/home/sam/Desktop/AI/HomeWork/Code/fast-downward/fast-downward.py"
OUTPUT_CSV = "benchmark_results.csv"

# Definiamo gli esperimenti: (Dimensione N, Numero di passi di mescolamento)
# Nota: N=3 è l'8-puzzle (facile). N=4 è il 15-puzzle (difficile per Python).
EXPERIMENTS = [
    # N=4 (15-Puzzle) - Facile, Medio, Difficile, Estremo
    (4, 30), 
    (4, 40), 
    (4, 50),
    (4, 60),
    (5, 20),
    (5, 60),
    (5, 100),
    (6, 30),
    (6, 100)
]

NUM_RUNS = 3 # Quante volte ripetere ogni configurazione per fare la media

def run_benchmark():
    # Prepariamo il file CSV
    with open(OUTPUT_CSV, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Intestazione colonne
        writer.writerow([
            "N", "Shuffle_Steps", "Run_ID", 
            "A*_Status", "A*_Time", "A*_Nodes", "A*_Len",
            "Planner_Status", "Planner_Time", "Planner_Nodes", "Planner_Len"
        ])
        
        print(f"Inizio benchmark. I risultati saranno salvati in {OUTPUT_CSV}")
        
        for N, steps in EXPERIMENTS:
            print(f"\n--- Testing N={N}, Shuffle={steps} ---")
            
            for run_id in range(1, NUM_RUNS + 1):
                print(f"  Run {run_id}/{NUM_RUNS}...", end="", flush=True)
                
                # 1. Genera Istanza
                start_node = generate_random_instance(N, steps)
                
                # 2. Esegui A* (Python)
                # Nota: A* in Python puri su 15-puzzle complessi può metterci minuti.
                astar_res = solve_astar(start_node, timeout=120) 
                
                # Gestisci il caso di timeout per la lunghezza
                if astar_res['status'] == 'success':
                    astar_len = len(astar_res['path']) - 1
                else:
                    astar_len = 0 # O -1 per indicare fallimento
                
                # Normalizziamo lunghezza A* (sottraiamo 1 per contare le mosse, non gli stati)
                astar_len = len(astar_res['path']) - 1 if astar_res['status'] == 'success' else 0
                
                print(f" A* done ({astar_res['time']:.4f}s) |", end="", flush=True)
                
                # 3. Esegui Planner
                dom, prob = generate_pddl(start_node)
                # Nota: Usiamo un alias veloce ma ottimale
                # Se il tuo planner fallisce spesso, prova a cambiare l'argomento search dentro run_planner_and_parse
                plan_res = run_planner_and_parse(dom, prob, planner_path=PLANNER_PATH)
                
                print(f" Planner done ({plan_res.get('time', 0)}s)")
                
                # 4. Salva riga nel CSV
                writer.writerow([
                    N, steps, run_id,
                    astar_res['status'], 
                    f"{astar_res['time']:.4f}", 
                    astar_res.get('nodes_expanded', 0), 
                    astar_len,
                    plan_res['status'], 
                    plan_res.get('time', 0), 
                    plan_res.get('expanded_nodes', 0), 
                    plan_res.get('plan_length', 0)
                ])
                
                # Pulizia file PDDL generati
                if os.path.exists(dom): os.remove(dom)
                if os.path.exists(prob): os.remove(prob)

    print(f"\nBenchmark completato! Apri {OUTPUT_CSV} per vedere i dati.")

if __name__ == "__main__":
    run_benchmark()