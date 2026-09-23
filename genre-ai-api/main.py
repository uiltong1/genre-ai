from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File

from models.domain.config_model import ModelConfig
from models.schemas.predict_schema import PredictResponseSchema
from controllers.predict_controller import PredictController
from services.config_loader_service import JsonConfigLoaderService
from services.audio_converter_service import PydubAudioConverterService
from services.audio_processor_service import LibrosaAudioProcessorService
from services.genre_classifier_service import KerasGenreClassifierService


class Container:
    config: ModelConfig = None
    predict_controller: PredictController = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando container de dependências...")

    config_loader = JsonConfigLoaderService()
    Container.config = config_loader.load_config("config.json")

    converter = PydubAudioConverterService()
    processor = LibrosaAudioProcessorService()
    classifier = KerasGenreClassifierService("modelo_generos_musicais.keras")

    Container.predict_controller = PredictController(
        converter=converter,
        processor=processor,
        classifier=classifier,
        config=Container.config,
    )

    print("✅ Serviços, Controllers e Schemas prontos!")
    yield
    print("Encerrando a aplicação...")


app = FastAPI(
    title="API de Classificação de Gêneros Musicais",
    description="Arquitetura limpa com SOLID, separação de Controllers, Services, Domain e Schemas Pydantic.",
    version="2.2.0",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {
        "status": "Ok",
        "message": "API de Classificação de Gêneros Musicais está funcionando!",
    }


@app.post("/predict", response_model=PredictResponseSchema)
async def predict_genre(file: UploadFile = File(...)):
    return Container.predict_controller.predict(file)