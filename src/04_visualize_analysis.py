#!/usr/bin/env python3
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def plot_fixation_durations(fixations_csv, out_dir):
    fixs = pd.read_csv(fixations_csv)
    plt.figure(figsize=(8,5))
    plt.hist(fixs['duration_frames'], bins=30, color='skyblue', edgecolor='black')
    plt.title("Histogramme des durées de fixations (en frames)")
    plt.xlabel("Durée (frames)")
    plt.ylabel("Nombre de fixations")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fixation_durations_histogram.png"))
    plt.close()
    print(f"[OK] Histogramme durées fixations sauvegardé dans {out_dir}")

def plot_fixation_positions(fixations_csv, out_dir):
    fixs = pd.read_csv(fixations_csv)
    plt.figure(figsize=(8,6))
    plt.scatter(fixs['x'], fixs['y'], alpha=0.5, s=10)
    plt.title("Scatter plot des positions des fixations")
    plt.xlabel("Coordonnée X (pixels)")
    plt.ylabel("Coordonnée Y (pixels)")
    plt.gca().invert_yaxis()  # (0,0) en haut à gauche, comme dans les images
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fixation_positions_scatter.png"))
    plt.close()
    print(f"[OK] Scatter des positions fixations sauvegardé dans {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualisation simple des métriques de fixation")
    parser.add_argument("--fixations_csv", required=True, help="CSV des fixations détectées")
    parser.add_argument("--out_dir", default="outputs/metrics", help="Dossier de sortie des graphiques")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    plot_fixation_durations(args.fixations_csv, args.out_dir)
    plot_fixation_positions(args.fixations_csv, args.out_dir)
    print("[OK] Visualisations terminées.")
