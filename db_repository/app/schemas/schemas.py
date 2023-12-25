from app.schemas import VideoBase, FrameBase


class VideoPayload(VideoBase):
    pass


class VideoResponse(VideoBase):
    id: int
    created_at: str


class FramePayload(FrameBase):
    pass


class FrameResponse(FrameBase):
    id: int
    created_at: str
