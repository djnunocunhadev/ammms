from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True)
    filename = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audio properties
    duration = Column(Float)
    sample_rate = Column(Integer)
    channels = Column(Integer)
    bit_depth = Column(Integer)
    format = Column(String)
    
    # Relationships
    features = relationship("AudioFeatures", back_populates="audio_file", uselist=False)
    metadata = relationship("Metadata", back_populates="audio_file", uselist=False)
    tags = relationship("Tag", secondary="audio_tags")

class AudioFeatures(Base):
    __tablename__ = "audio_features"

    id = Column(Integer, primary_key=True, index=True)
    audio_file_id = Column(Integer, ForeignKey("audio_files.id"))
    
    # Temporal features
    tempo = Column(Float)
    tempo_confidence = Column(Float)
    beat_positions = Column(JSON)  # List of beat positions in seconds
    
    # Spectral features
    spectral_centroid = Column(Float)
    spectral_rolloff = Column(Float)
    spectral_bandwidth = Column(Float)
    
    # MFCC features
    mfcc_mean = Column(JSON)  # List of mean MFCC coefficients
    mfcc_var = Column(JSON)   # List of MFCC variances
    
    # Key detection
    key = Column(String)
    key_confidence = Column(Float)
    
    # Fingerprint
    acoustid_fingerprint = Column(String)
    
    # Neural network features
    embedding = Column(JSON)  # Neural network embedding for similarity search
    
    # Relationships
    audio_file = relationship("AudioFile", back_populates="features")

class Metadata(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True, index=True)
    audio_file_id = Column(Integer, ForeignKey("audio_files.id"))
    
    # Basic metadata
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    year = Column(Integer)
    genre = Column(String)
    style = Column(String)
    label = Column(String)
    
    # Source-specific IDs
    musicbrainz_id = Column(String)
    discogs_id = Column(String)
    beatport_id = Column(String)
    
    # Additional metadata
    bpm = Column(Float)
    key = Column(String)
    energy = Column(Float)
    mood = Column(String)
    
    # Source tracking
    primary_source = Column(String)  # Which source provided the most reliable data
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audio_file = relationship("AudioFile", back_populates="metadata")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)  # e.g., 'genre', 'mood', 'instrument', 'custom'
    
    # Relationships
    audio_files = relationship("AudioFile", secondary="audio_tags")

# Association table for audio files and tags
audio_tags = Table(
    "audio_tags",
    Base.metadata,
    Column("audio_file_id", Integer, ForeignKey("audio_files.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)