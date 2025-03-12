import musicbrainzngs
import discogs_client
import requests
from typing import Dict, Any, List, Optional
from ..config import settings
import asyncio
import aiohttp
from datetime import datetime

class MetadataEnricher:
    def __init__(self):
        self._setup_clients()
        
    def _setup_clients(self):
        """Initialize API clients"""
        # MusicBrainz
        musicbrainzngs.set_useragent(
            settings.MUSICBRAINZ_APP_NAME,
            settings.MUSICBRAINZ_VERSION
        )
        
        # Discogs
        self.discogs = discogs_client.Client(
            'AMMMS',
            user_token=settings.DISCOGS_TOKEN
        )
        
    async def enrich_metadata(self, basic_metadata: Dict[str, Any], 
                            genre_prediction: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Enrich metadata from multiple sources"""
        tasks = [
            self._query_musicbrainz(basic_metadata),
            self._query_discogs(basic_metadata)
        ]
        
        # Add Beatport query for electronic music
        if genre_prediction and self._is_electronic(genre_prediction):
            tasks.append(self._query_beatport(basic_metadata))
            
        # Add Last.fm query
        tasks.append(self._query_lastfm(basic_metadata))
        
        # Gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle errors
        processed_results = {}
        for result in results:
            if isinstance(result, Exception):
                print(f"Warning: Metadata source error: {str(result)}")
                continue
            processed_results.update(result)
            
        return self._reconcile_metadata(processed_results)
        
    async def _query_musicbrainz(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Query MusicBrainz API"""
        try:
            query = self._build_musicbrainz_query(metadata)
            result = musicbrainzngs.search_recordings(query)
            
            if result['recording-list']:
                recording = result['recording-list'][0]
                return {
                    'title': recording.get('title'),
                    'artist': recording.get('artist-credit-phrase'),
                    'release': recording.get('release-list', [{}])[0].get('title'),
                    'year': recording.get('release-list', [{}])[0].get('date', '').split('-')[0],
                    'source': 'musicbrainz',
                    'confidence': 0.8  # Example confidence score
                }
        except Exception as e:
            raise MetadataError(f"MusicBrainz query failed: {str(e)}")
            
        return {}
        
    async def _query_discogs(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Query Discogs API"""
        try:
            results = self.discogs.search(
                type='release',
                artist=metadata.get('artist'),
                track=metadata.get('title')
            )
            
            if results:
                release = results[0]
                return {
                    'title': release.title,
                    'artist': release.artists[0].name if release.artists else None,
                    'label': release.labels[0].name if release.labels else None,
                    'year': release.year,
                    'genre': release.genres[0] if release.genres else None,
                    'style': release.styles[0] if release.styles else None,
                    'source': 'discogs',
                    'confidence': 0.7  # Example confidence score
                }
        except Exception as e:
            raise MetadataError(f"Discogs query failed: {str(e)}")
            
        return {}
        
    async def _query_beatport(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Query Beatport API"""
        async with aiohttp.ClientSession() as session:
            try:
                # Note: This is a simplified example. Real Beatport API integration
                # would require OAuth2 authentication and proper API endpoints
                url = 'https://api.beatport.com/v4/catalog/search'
                params = {
                    'q': f"{metadata.get('artist')} {metadata.get('title')}",
                    'type': 'tracks'
                }
                headers = {
                    'Authorization': f"Bearer {settings.BEATPORT_CLIENT_ID}"
                }
                
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['results']:
                            track = data['results'][0]
                            return {
                                'title': track.get('name'),
                                'artist': track.get('artists', [{}])[0].get('name'),
                                'label': track.get('label', {}).get('name'),
                                'genre': track.get('genre', {}).get('name'),
                                'key': track.get('key', {}).get('name'),
                                'bpm': track.get('bpm'),
                                'source': 'beatport',
                                'confidence': 0.9  # Example confidence score
                            }
            except Exception as e:
                raise MetadataError(f"Beatport query failed: {str(e)}")
                
        return {}
        
    async def _query_lastfm(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Query Last.fm API"""
        async with aiohttp.ClientSession() as session:
            try:
                url = 'http://ws.audioscrobbler.com/2.0/'
                params = {
                    'method': 'track.getInfo',
                    'api_key': settings.LASTFM_API_KEY,
                    'artist': metadata.get('artist'),
                    'track': metadata.get('title'),
                    'format': 'json'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        track = data.get('track', {})
                        return {
                            'title': track.get('name'),
                            'artist': track.get('artist', {}).get('name'),
                            'album': track.get('album', {}).get('title'),
                            'tags': [tag['name'] for tag in track.get('toptags', {}).get('tag', [])],
                            'source': 'lastfm',
                            'confidence': 0.6  # Example confidence score
                        }
            except Exception as e:
                raise MetadataError(f"Last.fm query failed: {str(e)}")
                
        return {}
        
    def _build_musicbrainz_query(self, metadata: Dict[str, Any]) -> str:
        """Build MusicBrainz search query"""
        query_parts = []
        
        if metadata.get('title'):
            query_parts.append(f"recording:\"{metadata['title']}\"~2")
        if metadata.get('artist'):
            query_parts.append(f"artist:\"{metadata['artist']}\"~2")
            
        return ' AND '.join(query_parts)
        
    def _is_electronic(self, genre_prediction: Dict[str, float]) -> bool:
        """Check if the predicted genre is electronic music"""
        electronic_genres = {
            'techno', 'house', 'trance', 'drum_and_bass', 'dubstep',
            'electronic', 'edm', 'ambient'
        }
        return any(genre.lower() in electronic_genres 
                  for genre in genre_prediction.keys())
        
    def _reconcile_metadata(self, metadata_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile metadata from different sources based on confidence"""
        reconciled = {}
        confidence_threshold = 0.5
        
        # Group metadata by field
        field_sources = {}
        for source, data in metadata_sources.items():
            confidence = data.get('confidence', 0)
            if confidence < confidence_threshold:
                continue
                
            for field, value in data.items():
                if field != 'confidence' and field != 'source':
                    if field not in field_sources:
                        field_sources[field] = []
                    field_sources[field].append({
                        'value': value,
                        'confidence': confidence,
                        'source': source
                    })
        
        # Select best value for each field
        for field, sources in field_sources.items():
            if not sources:
                continue
                
            # Sort by confidence
            sources.sort(key=lambda x: x['confidence'], reverse=True)
            reconciled[field] = sources[0]['value']
            
        return reconciled

class MetadataError(Exception):
    pass