# VRChatPNG

## `VRChatPNG.py`

[Source](VRChatPNG/VRChatPNG.py)

Converts VRChat API's JSON response for worlds and avatars into PNG files similar to VRChat's thumbnails - generated using [VRChatThumbnail.py](#vrchatthumbnailpy).

Also embeds a zip file in the images containing the JSON response at the time of creation and the full-size image used to generate the thumbnail.

## `VRChatThumbnail.py`

[Source](VRChatPNG/VRChatThumbnail.py)

Generates a thumbnail similar to how VRChat avatars are displayed in-game - showing name, author, and supported platforms.

# Installation

**Python >= 3.9 required.**

Update your environment according to [requirements.txt](requirements.txt)

# Usage

### **Command Line**
```bash
python VRChatPNG.py [-h|--help] [-P] [-W|--wait] [-X|--no-zip] -i <path>
python VRChatThumbnail.py [-h|--help] -i <path> {-p <int>|--platform <int>} {-n <str>|--name <str>} {-a <str>|--author <str>}
```

### **Python**
```Python
from PIL import Image
from VRChatThumbnail import VRChatThumbnail


platform = VRChatThumbnail.Platform.PC

# Path to data folder in repo
data_dir: Path = Path("VRChatPNG/data/")

img: Image = VRChatThumbnail.make_thumbnail(
	Image.open(...),
	platform=platform,
	avatar_name="Avatar name",
	author_name="Author username",
	data_dir=data_dir
)

img.save(...)
```
