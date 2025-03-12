from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from sqlalchemy.orm import Session
from ....core.audio.analyzer import AudioAnalyzer
from ....core.metadata.enricher import MetadataEnricher
from ....models.audio import AudioFile, AudioFeatures, Metadata, Tag
from ....schemas.audio import (
    AudioFile as AudioFileSchema,
    AudioAnalysisResult,
    SimilaritySearchResult
)
from ....db.session import get_db
import aiofiles
import os
from pathlib import Path
import shutil
import asyncio
from datetime import datetime

router = APIRouter()
analyzer = AudioAnalyzer()
enricher = MetadataEnricher()

@router.post("/analyze", response_model=AudioAnalysisResult)
async def analyze_audio(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Analyze an audio file and extract features and metadata.
    The file will be processed in the background if background_tasks is provided.
    """
    # Create temporary file
    temp_file = Path(settings.TEMP_DIR) / f"temp_{datetime.now().timestamp()}_{file.filename}"
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Save uploaded file
        async with aiofiles.open(temp_file, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Start analysis
        features = await analyzer.analyze_file(str(temp_file))
        
        # Get metadata based on analysis
        metadata = await enricher.enrich_metadata(
            basic_metadata={'filename': file.filename},
            genre_prediction=features.get('genre')
        )
        
        # Create database entries
        audio_file = AudioFile(
            path=str(temp_file),
            filename=file.filename,
            duration=features['duration'],
            sample_rate=features['sample_rate'],
            channels=2,  # TODO: Get from file
            bit_depth=16,  # TODO: Get from file
            format=file.filename.split('.')[-1].lower()
        )
        db.add(audio_file)
        db.flush()
        
        # Create features entry
        audio_features = AudioFeatures(
            audio_file_id=audio_file.id,
            tempo=features['tempo']['tempo'],
            tempo_confidence=features['tempo']['confidence'],
            beat_positions=features['tempo']['beat_frames'],
            spectral_centroid=features['spectral_features']['centroid_mean'],
            spectral_rolloff=features['spectral_features']['rolloff_mean'],
            spectral_bandwidth=features['spectral_features']['bandwidth_mean'],
            mfcc_mean=features['mfcc']['mean'],
            mfcc_var=features['mfcc']['var'],
            key=features['key']['key'],
            key_confidence=features['key']['confidence'],
            acoustid_fingerprint=features['fingerprint'],
            embedding=features.get('embedding')
        )
        db.add(audio_features)
        
        # Create metadata entry
        audio_metadata = Metadata(
            audio_file_id=audio_file.id,
            **metadata
        )
        db.add(audio_metadata)
        
        # Commit changes
        db.commit()
        
        # Schedule cleanup in background
        if background_tasks:
            background_tasks.add_task(cleanup_temp_file, temp_file)
        
        return AudioAnalysisResult(
            features=audio_features,
            metadata=audio_metadata,
            suggested_tags=[]  # TODO: Implement tag suggestions
        )
        
    except Exception as e:
        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{file_id}", response_model=List[SimilaritySearchResult])
async def find_similar(
    file_id: int,
    limit: int = Query(10, ge=1, le=100),
    threshold: float = Query(0.5, ge=0, le=1),
    db: Session = Depends(get_db)
):
    """
    Find similar audio files based on the features of the given file.
    """
    # Get source file features
    source_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()
    if not source_file or not source_file.features:
        raise HTTPException(status_code=404, detail="File not found or not analyzed")
    
    # Get all other files with features
    candidates = db.query(AudioFile).join(AudioFeatures).filter(
        AudioFile.id != file_id
    ).all()
    
    # Calculate similarity scores
    results = []
    for candidate in candidates:
        score = calculate_similarity(
            source_file.features,
            candidate.features
        )
        
        if score >= threshold:
            results.append(SimilaritySearchResult(
                audio_file=candidate,
                similarity_score=score,
                matching_features=get_matching_features(
                    source_file.features,
                    candidate.features
                )
            ))
    
    # Sort by similarity score and return top results
    results.sort(key=lambda x: x.similarity_score, reverse=True)
    return results[:limit]

@router.get("/stream/{file_id}")
async def stream_audio(file_id: int, db: Session = Depends(get_db)):
    """
    Stream an audio file.
    """
    audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()
    if not audio_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not os.path.exists(audio_file.path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    def iterfile():
        with open(audio_file.path, 'rb') as f:
            while chunk := f.read(8192):
                yield chunk
    
    return StreamingResponse(
        iterfile(),
        media_type=f"audio/{audio_file.format}"
    )

def calculate_similarity(source_features: AudioFeatures, candidate_features: AudioFeatures) -> float:
    """
    Calculate similarity score between two audio files based on their features.
    Returns a score between 0 and 1, where 1 is most similar.
    """
    weights = {
        'tempo': 0.2,
        'spectral': 0.3,
        'mfcc': 0.4,
        'key': 0.1
    }
    
    scores = {
        'tempo': compare_tempo(
            source_features.tempo,
            candidate_features.tempo,
            source_features.tempo_confidence,
            candidate_features.tempo_confidence
        ),
        'spectral': compare_spectral(
            source_features,
            candidate_features
        ),
        'mfcc': compare_mfcc(
            source_features.mfcc_mean,
            candidate_features.mfcc_mean
        ),
        'key': compare_key(
            source_features.key,
            candidate_features.key,
            source_features.key_confidence,
            candidate_features.key_confidence
        )
    }
    
    return sum(score * weights[feature] for feature, score in scores.items())

def compare_tempo(tempo1: float, tempo2: float, conf1: float, conf2: float) -> float:
    """Compare tempos with confidence weighting"""
    diff = abs(tempo1 - tempo2)
    max_diff = 20  # Maximum tempo difference to consider
    base_score = max(0, 1 - (diff / max_diff))
    confidence = (conf1 + conf2) / 2
    return base_score * confidence

def compare_spectral(features1: AudioFeatures, features2: AudioFeatures) -> float:
    """Compare spectral features"""
    centroid_diff = abs(features1.spectral_centroid - features2.spectral_centroid)
    rolloff_diff = abs(features1.spectral_rolloff - features2.spectral_rolloff)
    bandwidth_diff = abs(features1.spectral_bandwidth - features2.spectral_bandwidth)
    
    # Normalize differences
    max_diffs = {
        'centroid': 5000,
        'rolloff': 5000,
        'bandwidth': 2000
    }
    
    scores = {
        'centroid': max(0, 1 - (centroid_diff / max_diffs['centroid'])),
        'rolloff': max(0, 1 - (rolloff_diff / max_diffs['rolloff'])),
        'bandwidth': max(0, 1 - (bandwidth_diff / max_diffs['bandwidth']))
    }
    
    return sum(scores.values()) / len(scores)

def compare_mfcc(mfcc1: List[float], mfcc2: List[float]) -> float:
    """Compare MFCC features using cosine similarity"""
    import numpy as np
    from scipy.spatial.distance import cosine
    
    return 1 - cosine(mfcc1, mfcc2)

def compare_key(key1: str, key2: str, conf1: float, conf2: float) -> float:
    """Compare musical keys with confidence weighting"""
    # Convert keys to numerical values (0-11 for C through B)
    key_map = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
               'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    
    key1_val = key_map[key1.split()[0]]
    key2_val = key_map[key2.split()[0]]
    
    # Calculate minimum distance between keys (considering circle of fifths)
    diff = min((key1_val - key2_val) % 12, (key2_val - key1_val) % 12)
    max_diff = 6  # Maximum difference in semitones
    
    base_score = 1 - (diff / max_diff)
    confidence = (conf1 + conf2) / 2
    
    return base_score * confidence

def get_matching_features(features1: AudioFeatures, features2: AudioFeatures) -> Dict[str, Any]:
    """
    Identify which features are most similar between two audio files.
    Returns a dictionary of feature names and their similarity scores.
    """
    return {
        'tempo': compare_tempo(
            features1.tempo,
            features2.tempo,
            features1.tempo_confidence,
            features2.tempo_confidence
        ),
        'spectral': compare_spectral(features1, features2),
        'mfcc': compare_mfcc(features1.mfcc_mean, features2.mfcc_mean),
        'key': compare_key(
            features1.key,
            features2.key,
            features1.key_confidence,
            features2.key_confidence
        )
    }

async def cleanup_temp_file(file_path: Path):
    """Clean up temporary file after processing"""
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Error cleaning up temporary file {file_path}: {e}")