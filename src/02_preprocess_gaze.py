#!/usr/bin/env python3
import os
import pandas as pd
import argparse
import cv2
import re

def get_frame_index_from_filename(name):
    m = re.search(r'(\d+)', name)
    return int(m.group(1)) if m else None

def preprocess(etg_path, frames_dir, out_csv, event_filter=['Fixation', 'Saccade']):
    print(f"[INFO] Lecture du fichier ETG : {etg_path}")
    df = pd.read_csv(etg_path, delim_whitespace=True)

    print(f"[INFO] Total lignes dans ETG : {len(df)}")
    
    # Nettoyer NaN sur X et Y
    df = df.dropna(subset=['X', 'Y'])
    print(f"[INFO] Lignes après suppression NaN : {len(df)}")

    # Filtrer par event_type
    df = df[df['event_type'].isin(event_filter)]
    print(f"[INFO] Lignes après filtrage événements {event_filter} : {len(df)}")

    # Liste des frames images dans frames_dir
    files = sorted([f for f in os.listdir(frames_dir) if f.lower().endswith(('.jpg', '.png'))],
                   key=lambda x: get_frame_index_from_filename(x))
    if not files:
        raise SystemExit(f"[ERROR] Aucun fichier image trouvé dans {frames_dir}")
    
    # Dimensions image (première frame)
    first_img = cv2.imread(os.path.join(frames_dir, files[0]))
    H, W = first_img.shape[:2]
    print(f"[INFO] {len(files)} frames trouvées, taille image : {W}x{H}")

    # Ensemble des indices frames valides
    valid_indices = set(get_frame_index_from_filename(f) for f in files)

    rows = []
    for _, row in df.iterrows():
        fidx = int(row['frame_etg'])
        if fidx not in valid_indices:
            continue

        x_raw = float(row['X'])
        y_raw = float(row['Y'])

        # Ici coord en pixels, on clamp simplement
        x_px = max(0, min(W - 1, int(round(x_raw))))
        y_px = max(0, min(H - 1, int(round(y_raw))))

        # Nom fichier image correspondant
        fname = next((f for f in files if get_frame_index_from_filename(f) == fidx), None)
        if not fname:
            continue

        rows.append({'frame_idx': fidx,
                     'frame_name': fname,
                     'x_px': x_px,
                     'y_px': y_px})

    out_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    out_df.to_csv(out_csv, index=False)
    print(f"[OK] Sauvegardé {len(out_df)} points gaze dans : {out_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prétraitement fichier ETG vers CSV gaze")
    parser.add_argument("--etg", required=True, help="Fichier ETG (ex: etg_samples.txt)")
    parser.add_argument("--frames_dir", required=True, help="Dossier des frames images")
    parser.add_argument("--out_csv", required=True, help="Fichier CSV sortie (gaze)")
    args = parser.parse_args()

    preprocess(args.etg, args.frames_dir, args.out_csv)
