"""Custom exceptions for the agent package."""


class AgentError(Exception):
    """Base exception for all agent errors."""


class ImageGenerationError(AgentError):
    """Raised when image generation fails."""


class FFmpegNotFoundError(AgentError):
    """Raised when ffmpeg binary cannot be found."""


class FFmpegExecutionError(AgentError):
    """Raised when ffmpeg command fails."""
