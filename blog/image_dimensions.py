"""Known intrinsic image dimensions used by post cards.

The default post image is a static asset whose dimensions are stable. Uploaded
post images are recorded on ``Post`` after the resized file has been written so
request rendering never has to inspect storage.
"""

DEFAULT_METAIMG_WIDTH = 1207
DEFAULT_METAIMG_HEIGHT = 1392

DEFAULT_METAIMG_DIMENSIONS = (DEFAULT_METAIMG_WIDTH, DEFAULT_METAIMG_HEIGHT)


def is_default_metaimg(name):
    """Return whether ``name`` is the model's unuploaded default value."""
    return name == "default.webp"
