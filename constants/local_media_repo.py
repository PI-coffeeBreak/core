import os

# tree division has 2^bits per level (4 bits -> 16 subfolders)
MEDIA_SYMBOLS_PER_LEVEL = 2 # each symbol has 4 bits (2^4 = 16)
MEDIA_TREE_DEPTH = 2 # 2 levels of directories
MEDIA_REPO_PATH = os.path.join(os.path.dirname(__file__), "media")
