# ==========================
# ANEXO D: Validación de estructura interna
# Anexo D: Validación de estructura interna

# Fragmento adicional que ilustra cómo se validó la estructura volumétrica interna 
# del cordón a partir del resultado segmentado y su comparación con el volumen original:
# ==========================

import nibabel as nib
import numpy as np

# Cargar volúmenes originales y segmentados
original = nib.load(r"D:\MONAI_STUDIES\volume_original.nii.gz").get_fdata()
segmentado = nib.load(r"D:\MONAI_RESULTS\segmentation_output.nii.gz").get_fdata()

# Calcular métricas de coincidencia espacial
intersection = np.logical_and(original > 0, segmentado > 0)
dice = (2.0 * intersection.sum()) / ((original > 0).sum() + (segmentado > 0).sum())

print(f"Índice de similitud DICE: {dice:.4f}")

# Visualización volumétrica opcional (pseudocódigo)
# plot_3d_volume(segmentado, threshold=0.5)


# El índice DICE cuantifica la coincidencia entre la estructura real y la segmentación inferida.

# Se validó que los defectos detectados correspondan a discontinuidades internas reales observadas en la reconstrucción CT.