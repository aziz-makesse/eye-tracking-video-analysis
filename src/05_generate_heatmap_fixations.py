#!/usr/bin/env python3
import os
import argparse
import re
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

def frame_index_from_name(name):
    m = re.search(r'(\d+)', name)
    return int(m.group(1)) if m else None

def generate_heatmap_from_fixations(frames_dir, fixations_csv, out_video, sigma=15, alpha=0.5, resize_width=None, fps=None):
    df = pd.read_csv(fixations_csv)
    print("[INFO] Colonnes du CSV fixations :", df.columns.tolist())

    # Regroupe les points de fixation par frame (moyenne des points entre start_frame et end_frame)
    gaze_by_frame = {}
    for _, r in df.iterrows():
        for f in range(int(r.start_frame), int(r.end_frame) + 1):
            gaze_by_frame.setdefault(f, []).append((int(round(r.x)), int(round(r.y))))

    files = sorted(
        [f for f in os.listdir(frames_dir) if f.lower().endswith(('.jpg', '.png'))],
        key=lambda x: frame_index_from_name(x)
    )
    if len(files) == 0:
        raise SystemExit(f"[ERROR] Aucune image trouvée dans {frames_dir}")

    first_img = cv2.imread(os.path.join(frames_dir, files[0]))
    H0, W0 = first_img.shape[:2]

    if resize_width:
        scale = resize_width / float(W0)
        W, H = int(W0 * scale), int(H0 * scale)
    else:
        W, H = W0, H0
        scale = 1.0

    fps = fps or 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    os.makedirs(os.path.dirname(out_video) or ".", exist_ok=True)
    out = cv2.VideoWriter(out_video, fourcc, fps, (W, H))

    print(f"[INFO] Génération vidéo heatmap : {out_video} ({W}x{H}, fps={fps})")
    for fname in tqdm(files, desc="Génération vidéo heatmap"):
        path = os.path.join(frames_dir, fname)
        img = cv2.imread(path)
        if img is None:
            img = np.zeros((H, W, 3), dtype=np.uint8)
        if scale != 1.0:
            img = cv2.resize(img, (W, H))

        heat = np.zeros((H, W), dtype=np.float32)
        fidx = frame_index_from_name(fname)
        points = gaze_by_frame.get(fidx, [])
        for (x_px, y_px) in points:
            x = int(round(x_px * scale))
            y = int(round(y_px * scale))
            if 0 <= x < W and 0 <= y < H:
                heat[y, x] += 1.0

        if heat.max() > 0:
            heat_blur = cv2.GaussianBlur(heat, (0, 0), sigmaX=sigma, sigmaY=sigma)
            normalized = np.uint8(np.clip(heat_blur / heat_blur.max() * 255, 0, 255))
            colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
            overlay = cv2.addWeighted(img, 1.0 - alpha, colored, alpha, 0)
        else:
            overlay = img

        out.write(overlay)

    out.release()
    print(f"[OK] Vidéo heatmap sauvegardée dans {out_video}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Générer vidéo heatmap à partir des fixations")
    parser.add_argument("--frames_dir", required=True, help="Dossier des frames images")
    parser.add_argument("--fixations_csv", required=True, help="CSV fixations détectées")
    parser.add_argument("--out_video", required=True, help="Chemin de sortie vidéo heatmap (mp4)")
    parser.add_argument("--sigma", type=float, default=15, help="Sigma du flou gaussien")
    parser.add_argument("--alpha", type=float, default=0.5, help="Transparence overlay heatmap")
    parser.add_argument("--resize_width", type=int, default=None, help="Redimensionner largeur vidéo (optionnel)")
    parser.add_argument("--fps", type=int, default=None, help="FPS vidéo (optionnel)")
    args = parser.parse_args()

    generate_heatmap_from_fixations(
        args.frames_dir,
        args.fixations_csv,
        args.out_video,
        sigma=args.sigma,
        alpha=args.alpha,
        resize_width=args.resize_width,
        fps=args.fps
    )
