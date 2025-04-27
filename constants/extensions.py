from enum import Enum

class Extension(Enum):
    """File extensions enumeration"""
    JPG = ".jpg"
    JPEG = ".jpeg"
    PNG = ".png"
    WEBP = ".webp"
    GIF = ".gif"
    SVG = ".svg"
    PDF = ".pdf"
    DOC = ".doc"
    DOCX = ".docx"
    PPT = ".ppt"
    PPTX = ".pptx"
    XLS = ".xls"
    XLSX = ".xlsx"
    CSV = ".csv"
    JSON = ".json"
    XML = ".xml"
    YAML = ".yaml"
    TOML = ".toml"
    INI = ".ini"
    TXT = ".txt"
    MD = ".md"
    ZIP = ".zip"
    RAR = ".rar"
    TAR = ".tar"
    GZ = ".gz"
    TGZ = ".tgz"
    MP4 = ".mp4"
    WEBM = ".webm"
    MOV = ".mov"
    AVI = ".avi"
    MP3 = ".mp3"
    M4A = ".m4a"
    AAC = ".aac"
    WAV = ".wav"
    OGG = ".ogg"
    FLAC = ".flac"
    

# !!!-------------------- important note --------------------!!!
# All classes below are used to validate the file extensions and
#  the size of the file in default values.
# Plugins and other services can simply ignore the default
#  values and use their own measures for their particular use
#  case.
# !!! ------------------------------------------------------ !!!

class ImageExtension:
    """Image file extensions configuration"""
    ALLOWED = [
        Extension.JPG,
        Extension.JPEG,
        Extension.PNG,
        Extension.WEBP,
        Extension.GIF,
        Extension.SVG
    ]
    MAX_SIZE = 50 * 1024 * 1024  # 50MB

class VideoExtension:
    """Video file extensions configuration"""
    ALLOWED = [
        Extension.MP4,
        Extension.WEBM,
        Extension.MOV,
        Extension.AVI
    ]
    MAX_SIZE = 500 * 1024 * 1024  # 500MB

class AudioExtension:
    """Audio file extensions configuration"""
    ALLOWED = [
        Extension.MP3,
        Extension.M4A,
        Extension.AAC,
        Extension.WAV,
        Extension.OGG,
        Extension.FLAC
    ]
    MAX_SIZE = 50 * 1024 * 1024  # 50MB

class DocumentExtension:
    """Document file extensions configuration"""
    ALLOWED = [
        Extension.PDF,
        Extension.DOC,
        Extension.DOCX,
        Extension.XLS,
        Extension.XLSX,
        Extension.PPT,
        Extension.PPTX,
        Extension.TXT
    ]
    MAX_SIZE = 50 * 1024 * 1024  # 50MB

class PlainTextExtension:
    """Plain text file extensions configuration"""
    ALLOWED = [
        Extension.TXT,
        Extension.MD
    ]
    MAX_SIZE = 50 * 1024 * 1024  # 50MB

class ArchiveExtension:
    """Archive file extensions configuration"""
    ALLOWED = [
        Extension.ZIP,
        Extension.RAR,
        Extension.TAR,
        Extension.GZ,
        Extension.TGZ
    ]
    MAX_SIZE = 200 * 1024 * 1024  # 200MB

class DataExtension:
    """Data file extensions configuration"""
    ALLOWED = [
        Extension.XLS,
        Extension.XLSX,
        Extension.CSV,
        Extension.JSON,
        Extension.XML,
        Extension.YAML,
        Extension.TOML,
        Extension.INI
    ]
    MAX_SIZE = 50 * 1024 * 1024  # 50MB
