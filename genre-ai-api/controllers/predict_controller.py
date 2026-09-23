import os
import shutil
import tempfile
import traceback
from typing import Set
from fastapi import UploadFile, HTTPException

from interfaces.iaudio_converter import IAudioConverter
from interfaces.iaudio_processor import IAudioProcessor
from interfaces.igenre_classifier import IGenreClassifier
from models.domain.config_model import ModelConfig
from models.schemas.predict_schema import PredictResponseSchema


class PredictController:
    ALLOWED_EXTENSIONS: Set[str] = {
        ".mp3",
        ".wav",
        ".mp4",
        ".ogg",
        ".flac",
        ".m4a",
        ".aac",
    }

    def __init__(
        self,
        converter: IAudioConverter,
        processor: IAudioProcessor,
        classifier: IGenreClassifier,
        config: ModelConfig,
    ):
        self.converter = converter
        self.processor = processor
        self.classifier = classifier
        self.config = config

    def predict(self, file: UploadFile) -> PredictResponseSchema:
        ext = os.path.splitext(file.filename)[-1].lower()

        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Extensão '{ext}' não suportada. Suportadas: {list(self.ALLOWED_EXTENSIONS)}",
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_original_path = tmp_file.name

        tmp_wav_path = None

        try:
            tmp_wav_path = self.converter.convert_to_wav(tmp_original_path, ext)
            features = self.processor.extract_features(tmp_wav_path, self.config)
            result = self.classifier.predict(features, self.config, file.filename)

            return PredictResponseSchema(
                filename=result.filename,
                predicted_genre=result.predicted_genre,
                confidence=round(result.confidence, 4),
                confidence_percentage=result.confidence_percentage,
                all_probabilities=result.all_probabilities,
            )

        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail=f"Erro ao processar o áudio: {str(e)}"
            )

        finally:
            if tmp_wav_path and os.path.exists(tmp_wav_path) and tmp_wav_path != tmp_original_path:
                os.remove(tmp_wav_path)
            if os.path.exists(tmp_original_path):
                os.remove(tmp_original_path)