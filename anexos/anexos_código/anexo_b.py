# ==========================
# ANEXO B: Generación de Grad-CAM 3D
# Anexo B: Generación de mapa Grad-CAM sobre volumen 3D

# Este fragmento ilustra cómo se calculó el mapa de activación visual Grad-CAM 3D 
# a partir del modelo, para interpretar las regiones del volumen relevantes para 
# la predicción.
# ==========================

from monai.visualize import GradCAM
import matplotlib.pyplot as plt
import numpy as np

# Crear objeto Grad-CAM para el modelo UNet
target_layer = model.encoder4[-1]  # última capa convolucional significativa
cam = GradCAM(nn_module=model, target_layers=[target_layer], reshape_transform=None)

# Calcular mapa Grad-CAM para la clase de interés (defecto)
cam_map = cam(x=image, class_idx=1)
gradcam = cam_map[0, 0].detach().cpu().numpy()

# Visualización de una sección intermedia
plt.imshow(np.rot90(gradcam[:, :, gradcam.shape[2]//2]), cmap='jet', alpha=0.6)
plt.title("Mapa Grad-CAM 3D – Corte Axial")
plt.axis('off')
plt.show()

# El módulo GradCAM de MONAI permite analizar la interpretabilidad del modelo.
# Se visualiza la intensidad de activación por voxel, facilitando la correlación entre regiones activas y defectos reales del cordón.
