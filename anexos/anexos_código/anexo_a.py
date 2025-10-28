# ==========================
# ANEXO A: Inferencia sobre volumen DICOM convertido a NIfTI
# Anexo A: Ejecución de inferencia sobre volúmenes DICOM convertidos a NIfTI

# Este fragmento muestra el proceso de conversión, carga y ejecución de inferencia 
# en un modelo MONAI previamente entrenado, aplicado sobre un cordón de soldadura 
# escaneado por tomografía computarizada (CT).
# ==========================

from monai.inferers import SlidingWindowInferer
from monai.transforms import (
    LoadImage,
    EnsureChannelFirst,
    ScaleIntensity,
    CropForeground,
    EnsureType
)
from monai.networks.nets import UNet
import torch
import os

# Ruta del volumen ya convertido a NIfTI (.nii.gz)
input_path = r"D:\MONAI_STUDIES\weld_sample01\nifti\volume_001.nii.gz"
output_path = r"D:\MONAI_RESULTS\segmentation_output.nii.gz"

# Cargar imagen y aplicar transformaciones necesarias
transform = Compose([
    LoadImage(image_only=True),
    EnsureChannelFirst(),
    ScaleIntensity(),
    CropForeground(),
    EnsureType()
])

image = transform(input_path)
image = image.unsqueeze(0)  # [B, C, H, W, D]

# Cargar el modelo entrenado
model = UNet(
    spatial_dims=3,
    in_channels=1,
    out_channels=2,
    channels=(16, 32, 64, 128, 256),
    strides=(2, 2, 2, 2),
    num_res_units=2
)
model.load_state_dict(torch.load("D:/MONAI_MODELS/best_metric_model.pth"))
model.eval()

# Inferencia con ventana deslizante
inferer = SlidingWindowInferer(roi_size=(64, 64, 64), sw_batch_size=1, overlap=0.25)
with torch.no_grad():
    prediction = inferer(inputs=image, network=model)

# Guardar resultado segmentado en formato NIfTI
from monai.data import write_nifti
write_nifti(prediction.argmax(dim=1)[0], output_path)
print("✅ Inferencia completada y guardada en:", output_path)

# La función SlidingWindowInferer() permite inferencia eficiente en volúmenes 3D grandes.
# Se aplican transformaciones MONAI para garantizar compatibilidad de formato.
# El modelo UNet se carga con pesos entrenados para la detección de defectos en soldadura.
