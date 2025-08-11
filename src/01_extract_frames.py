#!/usr/bin/env python3
import cv2
import os
import sys

def extract_frames(video_path, out_dir):
    if not os.path.isfile(video_path):
        print(f"[ERROR] Vidéo introuvable : {video_path}")
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Impossible d'ouvrir la vidéo {video_path}")
        sys.exit(1)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[INFO] Nombre total de frames dans la vidéo : {frame_count}")

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        filename = os.path.join(out_dir, f"frame_{count:06d}.jpg")
        cv2.imwrite(filename, frame)
        if count % 100 == 0:
            print(f"[INFO] {count} frames extraites...")

    cap.release()
    print(f"[OK] Extraction terminée, {count} frames sauvegardées dans {out_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extraction frames depuis vidéo")
    parser.add_argument("--video", required=True, help="Chemin vers la vidéo (ex: video_etg.avi)")
    parser.add_argument("--out_dir", required=True, help="Dossier de sortie des frames")
    args = parser.parse_args()

    extract_frames(args.video, args.out_dir)
