# VRChatPNG

Create previews of VRChat avatars and worlds.

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
Ex.
```bash
python VRChatPNG.py -h
python VRChatPNG.py --help

python VRChatPNG.py -i ...
python VRChatPNG.py -i ... -P
python VRChatPNG.py -i ... -X --wait

python VRChatThumbnail.py -h
python VRChatThumbnail.py --help
python VRChatThumbnail.py -i ... --platform 0 -n name --author "author_name"
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

```Python
import VRChatPNG

# Path to JSON file containing VRChat avatar data.
json_path = ...

app = VRChatPNG.App(json_file_path=json_path)

# Recommended to delete generated files on app failure!
# App will fail if folder exists on next run.
try:
	app.run()
except Exception as e:
	app.delete_floating()
	raise e

```

# License

[MIT license](LICENSE), excluding files within the [data](VRChatPNG/data) directory.
