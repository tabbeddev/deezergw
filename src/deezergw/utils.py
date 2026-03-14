from typing import List, Union
from deezergw.resources.track import Track


def normalize_track_ids(tracks: List[Union[str, Track]]) -> List[str]:
    return [track.id if isinstance(track, Track) else track for track in tracks]