from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AudioFeatureBase(BaseModel):
    tempo: float
    tempo_confidence: float
    beat_positions: List[float]
    spectral_centroid: float
    spectral_rolloff: float
    spectral_bandwidth: float
    mfcc_mean: List[float]
    mfcc_var: List[float]
    key: str
    key_confidence: float
    acoustid_fingerprint: Optional[str] = None
    embedding: Optional[List[float]] = None

class AudioFeatureCreate(AudioFeatureBase):
    pass

class AudioFeature(AudioFeatureBase):
    id: int
    audio_file_id: int

    class Config:
        from_attributes = True

class MetadataBase(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    style: Optional[str] = None
    label: Optional[str] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    mood: Optional[str] = None
    musicbrainz_id: Optional[str] = None
    discogs_id: Optional[str] = None
    beatport_id: Optional[str] = None
    primary_source: Optional[str] = None

class MetadataCreate(MetadataBase):
    pass

class Metadata(MetadataBase):
    id: int
    audio_file_id: int
    last_updated: datetime

    class Config:
        from_attributes = True

class TagBase(BaseModel):
    name: str
    category: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

class AudioFileBase(BaseModel):
    path: str
    filename: str
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    format: str

class AudioFileCreate(AudioFileBase):
    pass

class AudioFile(AudioFileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    features: Optional[AudioFeature] = None
    metadata: Optional[Metadata] = None
    tags: List[Tag] = []

    class Config:
        from_attributes = True

class AudioAnalysisResult(BaseModel):
    features: AudioFeatureCreate
    metadata: MetadataCreate
    suggested_tags: List[TagCreate] = []

class SimilaritySearchResult(BaseModel):
    audio_file: AudioFile
    similarity_score: float
    matching_features: Dict[str, Any]