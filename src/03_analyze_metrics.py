#!/usr/bin/env python3
import os
import re
import argparse
import pandas as pd
import numpy as np
import cv2

def detect_fixations(df, fps, disp_thresh_px=40, min_duration_ms=100):
    min_len = max(1, int((min_duration_ms/1000.0) * fps))
    fixs = []
    i = 0
    n = len(df)
    while i < n:
        j = i
        xs = [df.iloc[j].x_px]; ys = [df.iloc[j].y_px]
        while j+1 < n:
            xs.append(df.iloc[j+1].x_px); ys.append(df.iloc[j+1].y_px)
            disp = (max(xs)-min(xs)) + (max(ys)-min(ys))
            if disp > disp_thresh_px:
                break
            j += 1
        if (j - i + 1) >= min_len:
            fixs.append({'start_frame': int(df.iloc[i].frame_idx),
                         'end_frame': int(df.iloc[j].frame_idx),
                         'duration_frames': j-i+1,
                         'x': float(np.mean(xs)),
                         'y': float(np.mean(ys))})
            i = j + 1
        else:
            i += 1
    return pd.DataFrame(fixs)

def percent_in_aoi(df, W, H, aoi_w=0.4, aoi_h=0.25):
    x0 = (1.0 - aoi_w) / 2.0
    y0 = (1.0 - aoi_h) / 2.0
    left = x0 * W; right = (x0 + aoi_w) * W
    top = y0 * H; bottom = (y0 + aoi_h) * H
    inside = ((df.x_px >= left) & (df.x_px <= right) & (df.y_px >= top) & (df.y_px <= bottom))
    pct = inside.sum() / len(df) if len(df)>0 else 0.0
    return pct, (left, right, top, bottom)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse métriques gaze et détection fixations")
    parser.add_argument("--gaze_csv", required=True, help="CSV coordonnées gaze (frame_idx,x_px,y_px)")
    parser.add_argument("--frames_dir", required=True, help="Dossier frames images")
    parser.add_argument("--out_dir", default="outputs/metrics", help="Dossier sortie métriques")
    parser.add_argument("--aoi_w", type=float, default=0.4, help="Largeur AOI relative (0-1)")
    parser.add_argument("--aoi_h", type=float, default=0.25, help="Hauteur AOI relative (0-1)")
    parser.add_argument("--disp_px", type=float, default=40, help="Seuil dispersion pixels")
    parser.add_argument("--min_fix_ms", type=int, default=100, help="Durée minimale fixation en ms")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    df = pd.read_csv(args.gaze_csv)
    print(f"[INFO] Données gaze : {len(df)} points, frames {df.frame_idx.min()} - {df.frame_idx.max()}")

    files = sorted([f for f in os.listdir(args.frames_dir) if f.lower().endswith(('.jpg','.png'))],
                   key=lambda x: int(re.search(r'(\d+)', x).group(1)) if re.search(r'(\d+)', x) else 0)
    first = cv2.imread(os.path.join(args.frames_dir, files[0]))
    H, W = first.shape[:2]

    pct, bbox = percent_in_aoi(df, W, H, aoi_w=args.aoi_w, aoi_h=args.aoi_h)
    print(f"[INFO] Pourcentage points dans AOI centrale: {pct*100:.2f}%, bbox (px) = {bbox}")

    fps = 30
    fixs = detect_fixations(df, fps=fps, disp_thresh_px=args.disp_px, min_duration_ms=args.min_fix_ms)
    print(f"[INFO] Fixations détectées : {len(fixs)}")

    fixs.to_csv(os.path.join(args.out_dir, "fixations.csv"), index=False)

    summary = {
        "n_gaze": int(len(df)),
        "pct_in_aoi": float(pct),
        "n_fixations": int(len(fixs))
    }
    pd.Series(summary).to_csv(os.path.join(args.out_dir, "summary.csv"))
    print(f"[OK] Métriques sauvegardées dans {args.out_dir}")
