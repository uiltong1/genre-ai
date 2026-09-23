import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File

from models.config_model import ModelConfig
from models.schemas.predict_schema import PredictResponseSchema
from controllers.predict_controller import PredictController

from models.schemas.predict_schema import PredictResponseSchema
from controllers.predict_controller import PredictController

from services.http_model_downloader_service import HttpModelDownloaderService
from services.config_loader_service import JsonConfigLoaderService
from services.audio_converter_service import PydubAudioConverterService
from services.audio_processor_service import LibrosaAudioProcessorService
from services.genre_classifier_service import KerasGenreClassifierService


class Container:
    config: ModelConfig = None
    predict_controller: PredictController = None

MODEL_LOCAL_PATH = "modelo_generos_musicais.keras"
CONFIG_LOCAL_PATH = "config_modelo.json"

MODEL_URL = os.getenv(
    "MODEL_URL",
    "https://huggingface.co/uiltong1/generos-musicais-cnn/resolve/main/modelo_generos_musicais.keras"
)
CONFIG_URL = os.getenv(
    "CONFIG_URL",
    "https://huggingface.co/uiltong1/generos-musicais-cnn/resolve/main/config_modelo.json"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Inicializando servidor e dependências...")

    # 1. Garante que o modelo e config estejam baixados
    downloader = HttpModelDownloaderService(
        model_url=MODEL_URL,
        config_url=CONFIG_URL
    )
    downloader.ensure_model_files(
        model_path=MODEL_LOCAL_PATH,
        config_path=CONFIG_LOCAL_PATH
    )

    # 2. Carrega as configurações e inicializa os serviços de ML
    config_loader = JsonConfigLoaderService()
    Container.config = config_loader.load_config(CONFIG_LOCAL_PATH)

    converter = PydubAudioConverterService()
    processor = LibrosaAudioProcessorService()
    classifier = KerasGenreClassifierService(MODEL_LOCAL_PATH)

    # 3. Injeta as dependências no Controller
    Container.predict_controller = PredictController(
        converter=converter,
        processor=processor,
        classifier=classifier,
        config=Container.config,
    )

    print("✅ Servidor pronto para receber requisições!")
    yield
    print("Encerrando a aplicação...")


app = FastAPI(
    title="API de Classificação de Gêneros Musicais",
    description="API desacoplada com download automático de modelo remoto.",
    version="2.3.0",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Envie um arquivo para POST /predict para classificar o gênero.",
    }


@app.post("/predict", response_model=PredictResponseSchema)
async def predict_genre(file: UploadFile = File(...)):
    return Container.predict_controller.predict(file)