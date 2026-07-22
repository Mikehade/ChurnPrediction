from dependency_injector import containers, providers

from src.config.settings import get_settings

from src.infrastructure.db.session import Database

from src.infrastructure.ml.loader import ModelArtifactLoader

from src.infrastructure.repositories.prediction import SQLAlchemyPredictionRepository

from src.core.inference import ChurnInference

from src.infrastructure.services.prediction import PredictionService


class Container(containers.DeclarativeContainer):
    """Dependency injection container for application resources and services."""

    config = providers.Singleton(get_settings)

    database = providers.Singleton(
        Database,
        db_url=providers.Callable(lambda cfg: cfg.database_url, config),
        engine_kwargs=providers.Callable(
            lambda cfg: cfg.database_engine_kwargs, config
        ),
    )

    # mnodel loader
    model_loader = providers.Singleton(
        ModelArtifactLoader,
        model_path=providers.Callable(lambda cfg: cfg.model_artifact_path, config),
        metadata_path=providers.Callable(lambda cfg: cfg.model_metadata_path, config),
        schema_path=providers.Callable(lambda cfg: cfg.feature_schema_path, config),
    )

    # repositories
    prediction_repository = providers.Factory(
        SQLAlchemyPredictionRepository,
        session_factory=database.provided.session
    )

    # services
    prediction_service = providers.Factory(
        PredictionService,
        repository=prediction_repository
    )

    # inferences
    inference = providers.Factory(
        ChurnInference,
        model_loader=model_loader,
        prediction_service=prediction_service
    )

