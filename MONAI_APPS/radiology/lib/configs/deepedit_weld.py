from monailabel.interfaces.tasks.infer import InferTask
from monailabel.interfaces.tasks.train import TrainTask
from monailabel.tasks.infer.basic_infer import BasicInferTask
from monai.transforms import LoadImaged, EnsureChannelFirstd, SaveImaged, Compose
import logging

logger = logging.getLogger(__name__)

class DeepEditWeld(BasicInferTask):
    """
    Versión funcional mínima de DeepEditWeld
    """

    def __init__(self):
        super().__init__(
            path=None,  # Puedes dejarlo None si no hay modelo entrenado aún
            network=None,
            labels={"background": 0, "defect": 1},
            load_strict=False
        )
        logger.info("✅ DeepEditWeld inicializado correctamente")

    def pre_transforms(self):
        return Compose([
            LoadImaged(keys=["image"]),
            EnsureChannelFirstd(keys=["image"]),
        ])

    def post_transforms(self):
        return Compose([
            SaveImaged(keys="pred", output_dir="./", output_postfix="pred", output_ext=".nii.gz"),
        ])
