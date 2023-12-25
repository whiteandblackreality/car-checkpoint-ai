from app.schemas import VideoBase, FrameBase


class VideoPayload(VideoBase):
    created_at: str


class VideoResponse(VideoBase):
    id: int
    created_at: str


class FramePayload(FrameBase):
    created_at: str


class FrameResponse(FrameBase):
    id: int
    created_at: str
