import librosa
import numpy as np
from typing import Dict, Any, Optional
import tensorflow as tf
from pathlib import Path
import acoustid
from ..config import settings

class AudioAnalyzer:
    def __init__(self):
        self.model = self._load_model()
        
    def _load_model(self) -> tf.keras.Model:
        """Load the audio classification model"""
        # TODO: Implement model loading from saved model
        # For now, return None as we'll implement this later
        return None
        
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze an audio file and extract features"""
        try:
            # Load the audio file
            y, sr = librosa.load(file_path)
            
            # Extract basic features
            features = {
                'duration': float(librosa.get_duration(y=y, sr=sr)),
                'sample_rate': sr,
                'tempo': self._get_tempo(y, sr),
                'spectral_features': self._get_spectral_features(y, sr),
                'mfcc': self._get_mfcc(y, sr),
                'fingerprint': await self._get_fingerprint(file_path),
                'key': self._get_key(y, sr),
                'genre': await self._predict_genre(y, sr) if settings.ENABLE_NEURAL_PROCESSING else None
            }
            
            return features
            
        except Exception as e:
            raise AudioAnalysisError(f"Error analyzing file: {str(e)}")
    
    def _get_tempo(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract tempo and beat information"""
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beat_frames = librosa.frames_to_time(beats, sr=sr)
        
        return {
            'tempo': float(tempo),
            'beat_frames': beat_frames.tolist(),
            'confidence': float(librosa.beat.tempo_confidence(y, sr=sr))
        }
    
    def _get_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract spectral features"""
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        
        return {
            'centroid_mean': float(np.mean(spectral_centroids)),
            'rolloff_mean': float(np.mean(spectral_rolloff)),
            'bandwidth_mean': float(np.mean(spectral_bandwidth))
        }
    
    def _get_mfcc(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract MFCC features"""
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        return {
            'coefficients': mfcc.tolist(),
            'mean': np.mean(mfcc, axis=1).tolist(),
            'var': np.var(mfcc, axis=1).tolist()
        }
    
    async def _get_fingerprint(self, file_path: str) -> Optional[str]:
        """Generate acoustic fingerprint"""
        try:
            duration, fp = acoustid.fingerprint_file(file_path)
            return fp
        except Exception as e:
            print(f"Warning: Could not generate fingerprint: {str(e)}")
            return None
    
    def _get_key(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Detect musical key"""
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key = librosa.feature.key_detect(chroma)
        
        return {
            'key': int(key),
            'confidence': float(np.max(key))
        }
    
    async def _predict_genre(self, y: np.ndarray, sr: int) -> Optional[Dict[str, float]]:
        """Predict genre using the neural network model"""
        if not self.model:
            return None
            
        try:
            # Preprocess audio for model input
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Resize to expected input shape
            mel_spec_db = tf.image.resize(mel_spec_db[np.newaxis, ..., np.newaxis], 
                                        (128, 128))
            
            # Make prediction
            predictions = self.model.predict(mel_spec_db)
            
            # Get top 3 genres
            top_indices = np.argsort(predictions[0])[-3:][::-1]
            
            return {
                self.genre_labels[idx]: float(predictions[0][idx])
                for idx in top_indices
            }
            
        except Exception as e:
            print(f"Warning: Genre prediction failed: {str(e)}")
            return None

class AudioAnalysisError(Exception):
    pass