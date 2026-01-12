import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime # Import necessario

def plot_benchmark():
    try:
        df = pd.read_csv("benchmark_results.csv")
    except FileNotFoundError:
        print("Il file benchmark_results.csv non esiste!")
        return

    # Generiamo un timestamp unico per questo salvataggio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    datasets = {
        "8-Puzzle (3x3)": df[df["N"] == 3],
        "15-Puzzle (4x4)": df[df["N"] == 4],
        "24-Puzzle (5x5)": df[df["N"] == 5] # Nel caso lo aggiungessi
    }

    for title, data in datasets.items():
        if data.empty:
            continue
            
        grouped = data.groupby("Shuffle_Steps").mean(numeric_only=True)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f'Confronto Prestazioni: {title}', fontsize=16)

        # --- Grafico 1: TEMPO ---
        ax1.plot(grouped.index, grouped["A*_Time"], marker='o', label='A* (Python)', color='blue')
        ax1.plot(grouped.index, grouped["Planner_Time"], marker='s', label='Planner (FD)', color='red')
        ax1.set_xlabel('Shuffle Steps (Difficoltà)')
        ax1.set_ylabel('Tempo (secondi)')
        ax1.set_title('Tempo di Esecuzione')
        ax1.legend()
        ax1.grid(True)

        # --- Grafico 2: NODI ---
        ax1.set_yscale('log') # Scala logaritmica spesso aiuta anche col tempo
        
        ax2.plot(grouped.index, grouped["A*_Nodes"], marker='o', label='A* Nodes', color='blue')
        ax2.plot(grouped.index, grouped["Planner_Nodes"], marker='s', label='Planner Nodes', color='red')
        ax2.set_xlabel('Shuffle Steps (Difficoltà)')
        ax2.set_ylabel('Nodi Espansi (log scale)')
        ax2.set_yscale('log')
        ax2.set_title('Nodi Visitati')
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout()
        
        # Nome file con timestamp: plot_15-Puzzle_20240111_123059.png
        safe_title = title.split()[0] # Prende solo "15-Puzzle"
        filename = f"plot_{safe_title}_{timestamp}.png"
        
        plt.savefig(filename)
        print(f"Grafico salvato come: {filename}")
        # plt.show() # Decommenta se vuoi vederli a schermo

if __name__ == "__main__":
    plot_benchmark()