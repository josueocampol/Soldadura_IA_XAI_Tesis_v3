# main.py
import json
import logging
import os
import pkgutil
import importlib
import inspect
from typing import Dict

import lib.configs  # paquete local con los TaskConfig
from lib.activelearning import Last
from lib.infers.deepgrow_pipeline import InferDeepgrowPipeline
from lib.infers.vertebra_pipeline import InferVertebraPipeline

import monailabel
from monailabel.interfaces.app import MONAILabelApp
from monailabel.interfaces.config import TaskConfig
from monailabel.interfaces.datastore import Datastore
from monailabel.interfaces.tasks.infer_v2 import InferTask
from monailabel.interfaces.tasks.scoring import ScoringMethod
from monailabel.interfaces.tasks.strategy import Strategy
from monailabel.interfaces.tasks.train import TrainTask
from monailabel.tasks.activelearning.first import First
from monailabel.tasks.activelearning.random import Random
from monailabel.tasks.infer.bundle import BundleInferTask
from monailabel.tasks.train.bundle import BundleTrainTask
from monailabel.utils.others.generic import get_bundle_models, strtobool
from monailabel.utils.others.planner import HeuristicPlanner

logger = logging.getLogger(__name__)


class MyApp(MONAILabelApp):
    def __init__(self, app_dir, studies, conf):
        """
        App inicializada por monailabel. Firma requerida:
          __init__(self, app_dir, studies, conf)
        """
        self.app_dir = app_dir
        self.model_dir = os.path.join(app_dir, "model")

        # --- Planner y opciones (establecer ANTES de instanciar TaskConfig) ---
        spatial_size = json.loads(conf.get("spatial_size", "[48, 48, 32]"))
        target_spacing = json.loads(conf.get("target_spacing", "[1.0, 1.0, 1.0]"))
        self.heuristic_planner = strtobool(conf.get("heuristic_planner", "false"))
        self.planner = HeuristicPlanner(spatial_size=spatial_size, target_spacing=target_spacing)

        # --- Detectar TaskConfig dinámicamente desde lib.configs ---
        logger.info("+++ Detectando TaskConfig en lib.configs ...")
        configs: Dict[str, type] = {}
        try:
            pkg = lib.configs
            for modinfo in pkgutil.iter_modules(pkg.__path__):
                modname = modinfo.name
                try:
                    module = importlib.import_module(f"{pkg.__name__}.{modname}")
                except Exception as e:
                    logger.warning(f"  -> No se pudo importar módulo {modname}: {e}")
                    continue
                # buscar clases que hereden TaskConfig
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if obj is TaskConfig:
                        continue
                    try:
                        if issubclass(obj, TaskConfig):
                            key = modname.lower()
                            configs[key] = obj
                            logger.info(f"  -> Encontrado config: {key} => {module.__name__}.{obj.__name__}")
                    except Exception:
                        # issubclass puede fallar si obj no viene del mismo contexto, ignorar
                        continue
        except Exception as e:
            logger.exception(f"Error detectando configs: {e}")

        logger.info(f"✅ Configs detectadas: {list(configs.keys())}")

        # --- Parsear modelos pedidos por conf ---
        models_cfg = conf.get("models")
        if not models_cfg:
            print("\n---------------------------------------------------------------------------------------")
            print("Provide --conf models <name>")
            print("Following are the available models. You can pass comma (,) separated names to load multiple:")
            print(f"    all, {', '.join(configs.keys())}")
            print("---------------------------------------------------------------------------------------\n")
            exit(-1)

        requested_models = [m.strip() for m in models_cfg.split(",")]

        invalid = [m for m in requested_models if m != "all" and not configs.get(m)]
        if invalid:
            print("\n---------------------------------------------------------------------------------------")
            print(f"Invalid Model(s) provided: {invalid}")
            print(f"Available: all, {', '.join(configs.keys())}")
            print("---------------------------------------------------------------------------------------\n")
            exit(-1)

        # --- Instanciar modelos de forma robusta ---
        self.scribbles = conf.get("scribbles", "true") == "true"
        self.models: Dict[str, TaskConfig] = {}

        for req in requested_models:
            for name, cls in configs.items():
                if self.models.get(name):
                    continue
                if req != "all" and req != name:
                    continue
                logger.info(f"+++ Adding Model: {name} => {cls.__module__}.{cls.__name__}")
                try:
                    instance = cls()  # intento estándar
                except TypeError as e:
                    logger.error(f"❌ No se pudo instanciar {name}: {e}")
                    continue
                except Exception as e:
                    logger.exception(f"❌ Error instanciando {name}: {e}")
                    continue

                # llamar init() del TaskConfig (algunos módulos lo esperan)
                try:
                    # muchos TaskConfig implementan init(name, model_dir, conf, planner)
                    if hasattr(instance, "init"):
                        instance.init(name, self.model_dir, conf, self.planner)
                except Exception as e:
                    logger.exception(f"❌ Error al inicializar {name}: {e}")
                    continue

                self.models[name] = instance

        logger.info(f"+++ Using Models: {list(self.models.keys())}")

        # --- Bundles (si existen en conf) ---
        self.bundles = get_bundle_models(app_dir, conf, conf_key="bundles") if conf.get("bundles") else None

        # SAM2 disabled por el momento
        self.sam = False

        # --- Inicialización de MONAILabelApp padre ---
        super().__init__(
            app_dir=app_dir,
            studies=studies,
            conf=conf,
            name=f"MONAILabel - Radiology ({monailabel.__version__})",
            description="Deep Learning models for radiology (no SAM2)",
            version=monailabel.__version__,
        )

    def init_datastore(self) -> Datastore:
        datastore = super().init_datastore()

        # FORZAR REFRESCO E INFO PARA DEBUG (no obligatorio)
        try:
            if hasattr(datastore, "refresh"):
                logger.info("Datastore: calling refresh()")
                datastore.refresh()
            info = datastore.info() if hasattr(datastore, "info") else None
            logger.info(f"Datastore info returned: {info}")
        except Exception as e:
            logger.warning(f"Datastore refresh/info failed: {e}")

        if self.heuristic_planner:
            # planner pudo haberse definido arriba
            try:
                self.planner.run(datastore)
            except Exception as e:
                logger.warning(f"Planner run failed: {e}")

        return datastore

    def init_infers(self) -> Dict[str, InferTask]:
        infers: Dict[str, InferTask] = {}

        # Models -> cada TaskConfig debe exponer .infer()
        for n, task_config in self.models.items():
            try:
                c = task_config.infer()
                c = c if isinstance(c, dict) else {n: c}
                for k, v in c.items():
                    logger.info(f"+++ Adding Inferer:: {k} => {v}")
                    infers[k] = v
            except Exception as e:
                logger.error(f"Error al crear inferer para {n}: {e}")

        # Bundles
        if self.bundles:
            for n, b in self.bundles.items():
                i = BundleInferTask(b, self.conf)
                logger.info(f"+++ Adding Bundle Inferer:: {n} => {i}")
                infers[n] = i

        # Scribbles (opcional)
        if self.scribbles:
            from monailabel.scribbles.infer import GMMBasedGraphCut, HistogramBasedGraphCut

            labels = list(self.models.values())[0].labels if self.models else {}

            infers.update(
                {
                    "Histogram+GraphCut": HistogramBasedGraphCut(
                        intensity_range=(-300, 200, 0.0, 1.0, True),
                        pix_dim=(2.5, 2.5, 5.0),
                        lamda=1.0,
                        sigma=0.1,
                        num_bins=64,
                        labels=labels,
                    ),
                    "GMM+GraphCut": GMMBasedGraphCut(
                        intensity_range=(-300, 200, 0.0, 1.0, True),
                        pix_dim=(2.5, 2.5, 5.0),
                        lamda=5.0,
                        sigma=0.5,
                        num_mixtures=20,
                        labels=labels,
                    ),
                }
            )

        # Pipelines
        if infers.get("deepgrow_2d") and infers.get("deepgrow_3d"):
            try:
                infers["deepgrow_pipeline"] = InferDeepgrowPipeline(
                    path=self.models["deepgrow_2d"].path,
                    network=self.models["deepgrow_2d"].network,
                    model_3d=infers["deepgrow_3d"],
                    description="Combines Deepgrow 2D and 3D models",
                )
            except Exception as e:
                logger.warning(f"Couldn't create deepgrow_pipeline: {e}")

        if (
            infers.get("localization_spine")
            and infers.get("localization_vertebra")
            and infers.get("segmentation_vertebra")
        ):
            try:
                infers["vertebra_pipeline"] = InferVertebraPipeline(
                    task_loc_spine=infers["localization_spine"],
                    task_loc_vertebra=infers["localization_vertebra"],
                    task_seg_vertebra=infers["segmentation_vertebra"],
                    description="Three-stage vertebra segmentation pipeline",
                )
            except Exception as e:
                logger.warning(f"Couldn't create vertebra_pipeline: {e}")

        logger.info(infers)
        return infers

    def init_trainers(self) -> Dict[str, TrainTask]:
        trainers: Dict[str, TrainTask] = {}
        if strtobool(self.conf.get("skip_trainers", "false")):
            return trainers

        for n, task_config in self.models.items():
            try:
                t = task_config.trainer()
                if not t:
                    continue
                logger.info(f"+++ Adding Trainer:: {n} => {t}")
                trainers[n] = t
            except Exception as e:
                logger.error(f"Error creando trainer para {n}: {e}")

        if self.bundles:
            for n, b in self.bundles.items():
                t = BundleTrainTask(b, self.conf)
                if not t or not t.is_valid():
                    continue
                logger.info(f"+++ Adding Bundle Trainer:: {n} => {t}")
                trainers[n] = t
        return trainers

    def init_strategies(self) -> Dict[str, Strategy]:
        strategies: Dict[str, Strategy] = {
            "random": Random(),
            "first": First(),
            "last": Last(),
        }

        if strtobool(self.conf.get("skip_strategies", "true")):
            return strategies

        for n, task_config in self.models.items():
            s = task_config.strategy()
            if not s:
                continue
            s = s if isinstance(s, dict) else {n: s}
            for k, v in s.items():
                logger.info(f"+++ Adding Strategy:: {k} => {v}")
                strategies[k] = v

        logger.info(f"Active Learning Strategies:: {list(strategies.keys())}")
        return strategies

    def init_scoring_methods(self) -> Dict[str, ScoringMethod]:
        methods: Dict[str, ScoringMethod] = {}
        if strtobool(self.conf.get("skip_scoring", "true")):
            return methods

        for n, task_config in self.models.items():
            try:
                s = task_config.scoring_method()
                if not s:
                    continue
                s = s if isinstance(s, dict) else {n: s}
                for k, v in s.items():
                    logger.info(f"+++ Adding Scoring Method:: {k} => {v}")
                    methods[k] = v
            except Exception as e:
                logger.error(f"Error creando scoring method para {n}: {e}")

        logger.info(f"Active Learning Scoring Methods:: {list(methods.keys())}")
        return methods


def main():
    print("✅ MONAI Label Radiology app (patched main.py) loaded.")


if __name__ == "__main__":
    main()
