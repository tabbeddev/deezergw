from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from deezergw.api import IMAGE_URL, DeezerAPI
from deezergw.exceptions import UnauthorizedException, UnknownException
from deezergw.resources.track import Track
from deezergw.utils import normalize_track_ids


class Playlist:
    def __init__(
        self,
        playlist_metadata: Any,
        api: DeezerAPI,
        favorite_tracks: Dict[str, datetime],
        is_favorite: Optional[bool] = None,
    ) -> None:
        self._api = api
        data = playlist_metadata["DATA"]

        self.id: str = data["PLAYLIST_ID"]
        self.name: str = data["TITLE"]
        self.is_favorite: Optional[bool] = None
        if is_favorite is not None:
            self.is_favorite = is_favorite
        elif "IS_FAVORITE" in data:
            self.is_favorite = data["IS_FAVORITE"]

        self.author_name: str = data["PARENT_USERNAME"]
        self.author_id: str = data["PARENT_USER_ID"]

        self.description: Optional[str] = (
            data["DESCRIPTION"] if "DESCRIPTION" in data else None
        )
        self.duration: Optional[int] = (
            int(data["DURATION"]) if "DURATION" in data else None
        )

        self.last_edited: Optional[datetime] = (
            datetime.fromisoformat(data["DATA_MOD"])
            if "DATA_MOD" in data
            else None
        )
        self.editable: bool = data["STATUS"] == 1

        state = api.get_playlist_state(self.id)
        self.is_private = state["isPrivate"]
        self.is_collaborative = state["isCollaborative"]

        self._author_pic: Optional[str] = (
            data["PARENT_USER_PICTURE"]
            if "PARENT_USER_PICTURE" in data
            else None
        )
        self._playlist_pic: str = data["PLAYLIST_PICTURE"]

        self.songs: Optional[List[Track]] = (
            [
                Track(metadata, api, favorite_tracks)
                for metadata in playlist_metadata["SONGS"]["data"]
            ]
            if "SONGS" in playlist_metadata
            else None
        )

    def favorite(self, forced_value: Optional[bool] = None):
        if forced_value is None:
            if self.is_favorite is None:
                raise UnknownException(
                    "IsFavorite is unknown as the Playlist wasn't directly initialized. You need to specify forced_value in this case."
                )
            forced_value = not self.is_favorite

        if forced_value == self.is_favorite:
            return forced_value

        if forced_value is True:
            self._api.add_favorite_playlist(self.id)
        else:
            self._api.remove_favorite_playlist(self.id)
        self.is_favorite = forced_value
        return self.is_favorite

    def cover_url(self, size: Union[str, int]) -> str:
        return IMAGE_URL.format("playlist", self._playlist_pic, size, size)

    def author_picture_url(self, size: Union[str, int]):
        if not self._author_pic:
            return
        return IMAGE_URL.format("user", self._author_pic, size, size)
    
    def add_tracks(self, tracks: List[Track], offset: int = -1):
        """
        Add tracks to this playlist.

        :param tracks: A list of Tracks or track ids to add to the playlist
        :type tracks: List[Union[str, Track]]
        :param offset: The position to insert the songs at. Default is -1 (add to end of playlist)
        :type offset: int
        """
        if not self.editable:
            raise UnauthorizedException("This playlist doesn't seem editable")

        ids = normalize_track_ids(tracks)
        self._api.add_tracks_to_playlist(self.id, ids, offset)

        if not self.songs:
            self.songs = []
        self.songs += tracks

        if not self.duration:
            self.duration = 0
        for track in tracks:
            self.duration += track.duration

        self.last_edited = datetime.now()
 
    def remove_tracks(self, tracks: List[Track]):
        """
        Remove tracks from this playlist.

        :param tracks: A list of Tracks or track ids to remove from the playlist
        :type tracks: List[Union[str, Track]]
        """
        if not self.editable:
            raise UnauthorizedException("This playlist doesn't seem editable")

        ids = normalize_track_ids(tracks)
        self._api.remove_tracks_from_playlist(self.id, ids)

        if self.songs:
            for song in self.songs:
                if song.id in ids:
                    self.songs.remove(song)

        if self.duration:
            for track in tracks:
                self.duration -= track.duration
        
        self.last_edited = datetime.now()

    def edit_playlist(self, name: Optional[str] = None, description: Optional[str] = None, is_private: Optional[bool] = None, is_collaborative: Optional[bool] = None):
        """
        Edit a playlist. Returns the playlist ID. Playlist cannot be both private and collaborative.

        :param name: The new name of the playlist
        :type name: Optional[str]
        :param description: The new description of the playlist
        :type description: Optional[str]
        :param is_private: Whether the playlist should be private
        :type is_private: Optional[bool]
        :param is_collaborative: Whether the playlist should be collaborative
        :type is_collaborative: Optional[bool]
        """
        self._api.edit_playlist(self.id, name, description, is_private, is_collaborative)
        if name:
            self.name = name
        if description:
            self.description = description
        if is_private is not None:
            self.is_private = is_private
        if is_collaborative is not None:
            self.is_collaborative = is_collaborative


    def delete(self):
        """Delete this playlist. Use with care!"""
        self._api.delete_playlist(self.id)

    def __repr__(self) -> str:
        return f'<Deezer - Playlist: "{self.name}" by "{self.author_name}">'
