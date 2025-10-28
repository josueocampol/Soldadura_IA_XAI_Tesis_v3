import os, json
from glob import glob

# === CONFIGURACIÓN ===
base_dir = r"D:\MONAI_STUDIES"
imagesTr = os.path.join(base_dir, "imagesTr")
labelsTr = os.path.join(base_dir, "labelsTr", "_remap")  # usa tus máscaras corregidas
output_json = os.path.join(base_dir, "dataset.json")

# === INFORMACIÓN DEL DATASET ===
dataset = {
    "name": "WeldCT",
    "description": "Dataset de soldaduras escaneadas por TC para segmentación",
    "tensorImageSize": "3D",
    "reference": "Josue Ocampo - proyecto TG2",
    "licence": "for research use",
    "modality": {"0": "CT"},
    "labels": {
        "0": "background",
        "1": "base_material",
        "2": "fusion_zone",
        "3": "defect_small",
        "4": "defect_large"
    },
    "numTraining": 0,
    "numTest": 0,
    "training": [],
    "test": []
}

# === CREAR LISTA DE TRAIN ===
images = sorted(glob(os.path.join(imagesTr, "*.nii.gz")))
labels = sorted(glob(os.path.join(labelsTr, "*.nii.gz")))

for img, lbl in zip(images, labels):
    case = os.path.basename(img).replace(".nii.gz", "")
    dataset["training"].append({
        "image": f"./imagesTr/{case}.nii.gz",
        "label": f"./labelsTr/_remap/{case}.nii.gz"
    })

dataset["numTraining"] = len(dataset["training"])

# === GUARDAR JSON ===
with open(output_json, "w") as f:
    json.dump(dataset, f, indent=4)

print(f"✅ dataset.json generado en: {output_json}")
print(f"Total de casos: {dataset['numTraining']}")
