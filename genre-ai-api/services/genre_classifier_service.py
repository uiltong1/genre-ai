import os
import numpy as np
import tensorflow as tf
from interfaces.igenre_classifier import IGenreClassifier
from models.config_model import ModelConfig
from models.prediction_model import PredictionResult


class KerasGenreClassifierService(IGenreClassifier):
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modelo Keras não encontrado no caminho: {model_path}"
            )
        self.model = tf.keras.models.load_model(model_path)

    def predict(
        self,
        features: np.ndarray,
        config: ModelConfig,
        filename: str,
    ) -> PredictionResult:
        predictions = self.model.predict(features, verbose=0)
        avg_probabilities = np.mean(predictions, axis=0)

        predicted_idx = int(np.argmax(avg_probabilities))
        predicted_genre = config.genre_names[predicted_idx]
        confidence = float(avg_probabilities[predicted_idx])

        all_probs = {
            genre: float(prob)
            for genre, prob in zip(config.genre_names, avg_probabilities)
        }
        all_probs_sorted = dict(
            sorted(all_probs.items(), key=lambda item: item[1], reverse=True)
        )

        return PredictionResult(
            filename=filename,
            predicted_genre=predicted_genre,
            confidence=confidence,
            all_probabilities=all_probs_sorted,
        )