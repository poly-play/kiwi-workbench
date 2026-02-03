from .jeetup import JeetupSource
from .larkup import LarkupSource
from .mena.kanzplay_sa import KanzplaySaSource
from .mena.falcowin_ae import FalcowinAeSource
from .mena.sakerwin_ae import SakerwinAeSource
from .mena.sakerwin_sa import SakerwinSaSource

ALL_SOURCES = [
    JeetupSource,
    LarkupSource,
    KanzplaySaSource,
    FalcowinAeSource,
    SakerwinAeSource,
    SakerwinSaSource
]
