from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....models.audio import AudioFile, Metadata, Tag
from ....schemas.audio import (
    Metadata as MetadataSchema,
    MetadataCreate,
    Tag as TagSchema,
    TagCreate
)
from ....core.metadata.enricher import MetadataEnricher
from ....db.session import get_db
from sqlalchemy import or_

router = APIRouter()
enricher = MetadataEnricher()

@router.get("/files/{file_id}", response_model=MetadataSchema)
async def get_file_metadata(file_id: int, db: Session = Depends(get_db)):
    """Get metadata for a specific file"""
    metadata = db.query(Metadata).filter(Metadata.audio_file_id == file_id).first()
    if not metadata:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return metadata

@router.put("/files/{file_id}", response_model=MetadataSchema)
async def update_file_metadata(
    file_id: int,
    metadata: MetadataCreate,
    db: Session = Depends(get_db)
):
    """Update metadata for a specific file"""
    db_metadata = db.query(Metadata).filter(Metadata.audio_file_id == file_id).first()
    if not db_metadata:
        raise HTTPException(status_code=404, detail="Metadata not found")
    
    # Update metadata fields
    for field, value in metadata.dict(exclude_unset=True).items():
        setattr(db_metadata, field, value)
    
    db.commit()
    db.refresh(db_metadata)
    return db_metadata

@router.post("/files/{file_id}/refresh", response_model=MetadataSchema)
async def refresh_metadata(
    file_id: int,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """
    Refresh metadata from external sources.
    If force=True, overwrites all fields; otherwise, only fills empty fields.
    """
    audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()
    if not audio_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get current metadata
    current_metadata = audio_file.metadata
    if not current_metadata:
        raise HTTPException(status_code=404, detail="Metadata not found")
    
    # Get fresh metadata from sources
    try:
        new_metadata = await enricher.enrich_metadata({
            'title': current_metadata.title,
            'artist': current_metadata.artist,
            'album': current_metadata.album
        })
        
        # Update fields
        for field, value in new_metadata.items():
            if force or not getattr(current_metadata, field):
                setattr(current_metadata, field, value)
        
        db.commit()
        db.refresh(current_metadata)
        return current_metadata
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[MetadataSchema])
async def search_metadata(
    query: str,
    field: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search metadata across all files.
    If field is specified, search only that field; otherwise, search all text fields.
    """
    base_query = db.query(Metadata)
    
    if field:
        # Search specific field
        if not hasattr(Metadata, field):
            raise HTTPException(status_code=400, detail=f"Invalid field: {field}")
        base_query = base_query.filter(getattr(Metadata, field).ilike(f"%{query}%"))
    else:
        # Search all text fields
        text_fields = [
            Metadata.title,
            Metadata.artist,
            Metadata.album,
            Metadata.genre,
            Metadata.style,
            Metadata.label
        ]
        base_query = base_query.filter(
            or_(*[field.ilike(f"%{query}%") for field in text_fields])
        )
    
    results = base_query.limit(limit).all()
    return results

@router.get("/tags", response_model=List[TagSchema])
async def get_tags(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all tags, optionally filtered by category"""
    query = db.query(Tag)
    if category:
        query = query.filter(Tag.category == category)
    return query.all()

@router.post("/tags", response_model=TagSchema)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag"""
    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.post("/files/{file_id}/tags/{tag_id}")
async def add_tag_to_file(
    file_id: int,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Add a tag to a file"""
    audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()
    if not audio_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    audio_file.tags.append(tag)
    db.commit()
    return {"message": "Tag added successfully"}

@router.delete("/files/{file_id}/tags/{tag_id}")
async def remove_tag_from_file(
    file_id: int,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Remove a tag from a file"""
    audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()
    if not audio_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    audio_file.tags.remove(tag)
    db.commit()
    return {"message": "Tag removed successfully"}

@router.get("/stats")
async def get_metadata_stats(db: Session = Depends(get_db)):
    """Get statistics about metadata coverage and quality"""
    total_files = db.query(AudioFile).count()
    
    stats = {
        "total_files": total_files,
        "coverage": {},
        "sources": {},
        "tags": {
            "total": db.query(Tag).count(),
            "by_category": {}
        }
    }
    
    # Calculate metadata coverage
    for field in [
        "title", "artist", "album", "year",
        "genre", "label", "key", "bpm"
    ]:
        filled = db.query(Metadata).filter(
            getattr(Metadata, field).isnot(None)
        ).count()
        stats["coverage"][field] = round(filled / total_files * 100, 2) if total_files > 0 else 0
    
    # Count metadata sources
    sources = db.query(Metadata.primary_source).distinct().all()
    for source in sources:
        if source[0]:  # source is a tuple
            count = db.query(Metadata).filter(
                Metadata.primary_source == source[0]
            ).count()
            stats["sources"][source[0]] = count
    
    # Count tags by category
    categories = db.query(Tag.category).distinct().all()
    for category in categories:
        if category[0]:
            count = db.query(Tag).filter(Tag.category == category[0]).count()
            stats["tags"]["by_category"][category[0]] = count
    
    return stats