import os
import argparse
import numpy as np
import nibabel as nib

def unique_vals(path):
    img = nib.load(path)
    data = img.get_fdata().astype(np.int64)
    vals = np.unique(data)
    return vals, data.shape, img.header.get_zooms()

def remap_and_save(in_path, mapping, out_path):
    img = nib.load(in_path)
    data = img.get_fdata().astype(np.int64)
    out = np.zeros_like(data, dtype=np.int64)
    for old, new in mapping.items():
        out[data == old] = new
    new_img = nib.Nifti1Image(out.astype(np.uint8), img.affine, img.header)
    nib.save(new_img, out_path)

def parse_map(s):
    # "10:1,20:2" -> {10:1,20:2}
    m = {}
    if not s:
        return m
    pairs = s.split(",")
    for p in pairs:
        a,b = p.split(":")
        m[int(a)] = int(b)
    return m

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--labels-dir", required=True, help="Folder with label .nii.gz files")
    p.add_argument("--remap", default="", help='remap string like "10:1,20:2"')
    p.add_argument("--inplace", action="store_true", help="Overwrite existing files (use carefully)")
    p.add_argument("--out-dir", default=None, help="If not inplace, remapped files go here")
    args = p.parse_args()

    labdir = args.labels_dir
    mapping = parse_map(args.remap)

    if not os.path.isdir(labdir):
        raise SystemExit(f"Labels dir not found: {labdir}")
    if args.remap and not args.inplace and not args.out_dir:
        args.out_dir = os.path.join(labdir, "_remap")
        os.makedirs(args.out_dir, exist_ok=True)

    print("Scanning labels in:", labdir)
    for f in sorted(os.listdir(labdir)):
        if not (f.endswith(".nii") or f.endswith(".nii.gz")): continue
        full = os.path.join(labdir, f)
        vals, shape, zooms = unique_vals(full)
        print(f"{f}  shape={shape}  spacing={zooms}  unique={vals}")
        if mapping:
            tgt = full if args.inplace else os.path.join(args.out_dir, f)
            remap_and_save(full, mapping, tgt)
            print("  -> remapped saved to:", tgt)

    print("Done.")
