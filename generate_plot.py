import pandas as pd
import matplotlib.pyplot as plt

def generate_plots():
    # Leggiamo il CSV
    try:
        df = pd.read_csv("benchmark_results.csv")
    except FileNotFoundError:
        print("Errore: File benchmark_results.csv non trovato.")
        return

    # Configurazioni da graficare
    configurations = [
        (3, "8-Puzzle"),
        (4, "15-Puzzle")
    ]

    for N, title in configurations:
        data = df[df["N"] == N]
        if data.empty:
            continue

        # Calcoliamo la media per ogni step di shuffle
        grouped = data.groupby("Shuffle_Steps")[["A*_Time", "Planner_Time", "A*_Nodes", "Planner_Nodes"]].mean()

        # Creiamo la figura con 2 grafici affiancati
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f'Benchmark Results: {title} ({N}x{N})', fontsize=16)

        # --- Grafico 1: TEMPO ---
        ax1.plot(grouped.index, grouped["A*_Time"], marker='o', label='Custom A* (Python)', color='blue')
        ax1.plot(grouped.index, grouped["Planner_Time"], marker='s', label='Planner (Fast Downward)', color='red')
        ax1.set_xlabel('Shuffle Steps (Difficulty)')
        ax1.set_ylabel('Time (seconds)')
        ax1.set_title('Execution Time')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)

        # --- Grafico 2: NODI ESPANSI ---
        ax2.plot(grouped.index, grouped["A*_Nodes"], marker='o', label='Custom A*', color='blue')
        ax2.plot(grouped.index, grouped["Planner_Nodes"], marker='s', label='Planner (LM-Cut)', color='red')
        ax2.set_xlabel('Shuffle Steps (Difficulty)')
        ax2.set_ylabel('Expanded Nodes')
        ax2.set_title('Search Efficiency (Nodes)')
        
        # Usiamo scala logaritmica se i numeri sono molto diversi
        if grouped["A*_Nodes"].max() > 100:
             ax2.set_yscale('log')
        
        ax2.legend()
        ax2.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        
        # Salvataggio file
        filename = f"plot_{title}.png"
        plt.savefig(filename, dpi=300)
        print(f"Generato grafico: {filename}")
        plt.close()

if __name__ == "__main__":
    generate_plots()