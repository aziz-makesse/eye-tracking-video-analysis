#!/usr/bin/env python3
import os
import argparse
import pandas as pd
import numpy as np

def fixation_stats_enriched(fixations_csv, out_dir):
    df = pd.read_csv(fixations_csv)

    n_fix = len(df)
    durations = df['duration_frames']
    mean_dur = durations.mean()
    median_dur = durations.median()
    std_dur = durations.std()
    min_dur = durations.min()
    max_dur = durations.max()

    # Moyenne position X et Y des fixations
    mean_x = df['x'].mean()
    mean_y = df['y'].mean()

    # Dispersion (écart-type) des positions X et Y
    std_x = df['x'].std()
    std_y = df['y'].std()

    # Durée totale d'observation en frames
    total_duration = durations.sum()

    # Stats avancées : quartiles des durées
    q1 = durations.quantile(0.25)
    q3 = durations.quantile(0.75)

    # Créer un résumé sous forme dict
    summary = {
        "nombre_fixations": n_fix,
        "duree_moyenne_frames": mean_dur,
        "duree_mediane_frames": median_dur,
        "duree_min_frames": min_dur,
        "duree_max_frames": max_dur,
        "duree_std_frames": std_dur,
        "total_duree_frames": total_duration,
        "mean_x_px": mean_x,
        "mean_y_px": mean_y,
        "std_x_px": std_x,
        "std_y_px": std_y,
        "duree_q1_frames": q1,
        "duree_q3_frames": q3
    }

    # Affichage console
    print("[INFO] --- Statistiques des fixations ---")
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"{k}: {v:.2f}")
        else:
            print(f"{k}: {v}")

    # Sauvegarder CSV résumé
    os.makedirs(out_dir, exist_ok=True)
    summary_csv_path = os.path.join(out_dir, "fixations_summary_stats.csv")
    pd.Series(summary).to_csv(summary_csv_path)
    print(f"[OK] Résumé statistiques sauvegardé dans {summary_csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse statistique enrichie des fixations")
    parser.add_argument("--fixations_csv", required=True, help="CSV fixations détectées")
    parser.add_argument("--out_dir", default="outputs/metrics", help="Dossier sortie")
    args = parser.parse_args()

    fixation_stats_enriched(args.fixations_csv, args.out_dir)
