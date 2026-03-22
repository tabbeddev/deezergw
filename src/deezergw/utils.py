from typing import List, Union, Sequence
from deezergw.resources.track import Track


def normalize_track_ids(tracks: Sequence[Union[str, Track]]) -> List[str]:
    return [track.id if isinstance(track, Track) else track for track in tracks]