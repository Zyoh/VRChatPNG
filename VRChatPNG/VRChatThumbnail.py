from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from enum import Enum
import numpy as np
import time
import sys

from options import Options


class VRChatThumbnail:

	class Platform(Enum):
		Both = 0
		PC = 1
		Quest = 2

	@staticmethod
	def make_thumbnail(avatar_image: Image, platform, avatar_name: str, author_name: str, data_dir: Path, contains_asset: bool = False) -> Image:
		assert isinstance(platform, VRChatThumbnail.Platform)
		assert isinstance(avatar_name, str)
		assert isinstance(author_name, str)

		if isinstance(platform, VRChatThumbnail.Platform):
			platform = platform.value

		text_overlay = Image.open(data_dir / 'text_overlay.png')
		corner_mask = Image.open(data_dir / 'corner_mask.png')
		platform_icon = Image.open(data_dir / 'vrc_platform.png')
		file_icon = Image.open(data_dir / 'file.png')

		if (data_dir / 'font.ttf').is_file():
			font_path = data_dir / 'font.ttf'
		elif (data_dir / 'font.otf').is_file():
			font_path = data_dir / 'font.otf'

		# --- Set up images ---
		
		# Base
		avatar_image = avatar_image.convert('RGBA')
		avatar_image = avatar_image.resize((1200, 900))

		# Dark bg for text
		if avatar_image.size != text_overlay.size:
			# Resize to match
			text_overlay.resize( avatar_image.size, Image.ANTIALIAS )
		text_overlay = text_overlay.convert('RGBA')

		# Cut corners to match VRChat UI
		if avatar_image.size != corner_mask.size:
			# Resize to match
			corner_mask.resize( avatar_image.size, Image.ANTIALIAS )
		corner_mask = corner_mask.convert('L')

		# - Platform support icon -
		platform_icon = platform_icon.convert('RGBA')
		# Set alpha
		platform_icon.putalpha(
			Image.fromarray(np.asarray(platform_icon.split()[-1]) * 0.85).convert("L")
		)

		# - File icon -
		file_icon = file_icon.convert("RGBA")
		# Set alpha
		file_icon.putalpha(
			Image.fromarray(np.asarray(file_icon.split()[-1]) * 0.85).convert("L")
		)
		
		# Width should be 512 on a background with a width of 1200
		_icon_width = int( 320 / 1200 * avatar_image.size[0] )
		_icon_height = int( platform_icon.size[1] / platform_icon.size[0] * _icon_width )
		platform_icon = platform_icon.resize( (_icon_width, _icon_height), Image.ANTIALIAS )
		file_icon = file_icon.resize( (_icon_width//2, _icon_width//2), Image.ANTIALIAS )

		# Crop icon set to the correct icon
		platform_icon = platform_icon.crop((
			0,
			int( platform_icon.size[1]/3 * platform ),
			platform_icon.size[0],
			int( platform_icon.size[1]/3 * (platform+1) )
		))

		# --- Merge images ---
		avatar_image.paste( text_overlay, (0,0), text_overlay )
		
		_icon_offset = int( 25/900 * avatar_image.size[1] )
		avatar_image.paste( platform_icon, (_icon_offset,_icon_offset), platform_icon )
		avatar_image.putalpha(corner_mask)

		if contains_asset:
			avatar_image.paste(
				file_icon, 
				(
					int(_icon_offset * 1.5),
					(_icon_offset * 2) + platform_icon.size[1]
				), 
				file_icon
			)

		# --- Write text ---
		_font_title = ImageFont.truetype( str(font_path) , int(avatar_image.size[0]*0.1) )
		_text_offset_x_title = int( avatar_image.size[0] * 0.1 )
		_text_offset_y_title = int( avatar_image.size[1] - avatar_image.size[1] * 0.3 )
		ImageDraw.Draw(avatar_image).text(
			( _text_offset_x_title, _text_offset_y_title ),
			avatar_name,
			(255,255,255),
			font=_font_title
		)

		_font_small = ImageFont.truetype( str(font_path) , int(avatar_image.size[0]*0.065) )
		_text_offset_x_small = int( avatar_image.size[0] * 0.2 )
		_text_offset_y_small = int( avatar_image.size[1] - avatar_image.size[1] * 0.125 )
		ImageDraw.Draw(avatar_image).text(
			( _text_offset_x_small, _text_offset_y_small ),
			author_name,
			(255,255,0),
			font=_font_small
		)

		return avatar_image


def main():
	options = Options(sys.argv)

	HELP = """
Help:
    -h, --help                      Display help message and exit.

Main:
    -i <path>                       Path to image.
    [-o <path>, --output <path>]    Output result to this path. Defaults to auto-generating file in input file's directory.
    -p <int>, --platform <int>      Supported platforms.
        - 0 | PC & Quest
        - 1 | PC
        - 2 | Quest
    -n <str>, --name <str>          Name of avatar.
    -a <str>, --author <str>        Name of avatar author.
"""

	if options.get("-h", False) or options.get("--help", False):
		pass
	elif (image_path := options.get("-i")) and \
		(platform := options.get("-p") or options.get("--platform")) and \
		(platform in ["0", "1", "2"]) and \
		(avatar_name := options.get("-n") or options.get("--name")) and \
		(author_name := options.get("-a") or options.get("--author")):

		image_path = Path(image_path).resolve()
		assert image_path.exists()

		if out_path := options.get("-o") or options.get("--output"):
			out_path = Path(out_path).resolve()
			if out_path.is_dir():
				out_path = out_path / (f"{time.time()}." + image_path.stem + ".png")
		else:
			out_path = image_path.parent / (f"{time.time()}." + image_path.stem + ".png")

		platform = VRChatThumbnail.Platform(int(platform))

		img = VRChatThumbnail.make_thumbnail(
			avatar_image=Image.open(image_path),
			platform=platform,
			avatar_name=avatar_name,
			author_name=author_name,
			data_dir=Path(__file__).parent / "data"
		)
		img.save(out_path)

		return
	
	print(HELP)


if __name__ == "__main__":
	main()
