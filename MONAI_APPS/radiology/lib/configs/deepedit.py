from monailabel.interfaces.tasks.infer import InferTask
from monailabel.interfaces.tasks.train import TrainTask
from monailabel.tasks.infer.basic_infer import BasicInferTask
from monai.transforms import (
    LoadImaged,
    EnsureChannelFirstd,
    SaveImaged,
    Compose
)
import logging

logger = logging.getLogger(__name__)

class DeepEdit:
    """
    Versión mínima funcional del modelo DeepEdit
    """

    def __init__(self):
        self.path = None
        logger.info("✅ DeepEdit inicializado correctamente")

    def infer(self) -> InferTask:
        # Define la tarea de inferencia
        return BasicInferTask(
            path=None,  # Aquí podrías luego poner tu modelo entrenado .pt
            network=None,
            labels={"background": 0, "defect": 1},
            load_strict=False,
            pre_transforms=Compose([
                LoadImaged(keys=["image"]),
                EnsureChannelFirstd(keys=["image"]),
            ]),
            post_transforms=Compose([
                SaveImaged(keys="pred", output_dir="./", output_postfix="pred", output_ext=".nii.gz"),
            ])
        )

    def trainer(self) -> TrainTask:
        # Este modelo no entrena (placeholder)
        logger.info("⚠️ DeepEdit: entrenamiento no implementado")
        return None
