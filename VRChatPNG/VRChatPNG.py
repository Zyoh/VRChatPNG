from pathlib import Path
from tqdm import tqdm
from PIL import Image
import requests
import shutil
import json
import time
import sys

from VRChatThumbnail import VRChatThumbnail
from options import Options


class Downloader:
	def __init__(self):
		self.Session = requests.session()
		self.Session.headers.update({'User-Agent': 'Requests/{}'.format(requests.__version__)})

	def is_url(self, url: str):
		assert isinstance(url, str)
		return url.lower().startswith('http')

	def download(self, url: str, destination: Path):
		assert self.is_url(url)
		assert isinstance(destination, Path)

		# Ty to https://stackoverflow.com/a/10744565
		response = self.Session.get(url, stream=True)
		with open(destination, "wb") as handle:
			try:
				for data in tqdm(response.iter_content(chunk_size=8192)):
					handle.write(data)
			except NameError:
				for data in response.iter_content(chunk_size=8192):
					handle.write(data)

	@classmethod
	def qdownload(cls, url: str, destination: Path):
		dler = cls()
		dler.download(url, destination)


class App:
	def __init__(self, json_file_path: Path, wait_to_compress: bool = False, no_zip: bool = False):
		assert isinstance(json_file_path, Path)
		self.json_file_path = json_file_path
		assert isinstance(wait_to_compress, bool)
		self.wait_to_compress = wait_to_compress
		assert isinstance(no_zip, bool)
		self.no_zip = no_zip

		# If error: delete these
		self.floating_dir: Path = None
		self.floating_files: list = []

	@staticmethod
	def vrc_url_filename(file_url):
		return '.'.join(file_url.split('/')[6:-1])

	def delete_floating(self):
		for file in self.floating_files:
			assert isinstance(file, Path)
			assert file.exists()

			file.unlink()
		self.floating_files = []
		
		if self.floating_dir is not None:
			assert isinstance(self.floating_dir, Path)
			assert self.floating_dir.is_dir()

			shutil.rmtree(self.floating_dir)
		self.floating_dir = None

	def run(self):
		with open(self.json_file_path, 'r', encoding='utf-8') as f:
			data = json.load(f)
			assert type(data) in (list, dict)

			if isinstance(data, list):
				for c, avatar_data in enumerate(data):
					self._run(avatar_data)
					if c < len(data)-1:
						time.sleep(1)
						print()
			elif isinstance(data, dict):
				self._run(data)
		
	def _run(self, data: dict):
		assert isinstance(data, dict)

		if "favoriteId" in data:
			del data["favoriteId"]
		if "favoriteGroup" in data:
			del data["favoriteGroup"]

		print(f"Downloading: {data.get('id')}")

		unique_name = f"{data.get('id')}.{data.get('version')}"

		# Make folder for files
		working_dir = self.json_file_path.parent / f"{unique_name}"
		working_dir.mkdir()
		self.floating_dir = working_dir

		# Copy json to folder
		with open(working_dir / (unique_name + ".json"), 'w', encoding='utf-8', errors='ignore') as f:
			json.dump(data, f, indent=4, ensure_ascii=False)

		# Download image
		image_url = data.get('imageUrl')
		image_path = working_dir / (self.vrc_url_filename(image_url) + ".png")
		Downloader.qdownload(image_url, image_path)

		# Get avatar asset files - No longer available
		pass

		# Add file with timestamp
		(working_dir / str(int(time.time()))).touch()

		# ---

		# Get platforms	
		platform_support = []
		for p in ["standalonewindows", "android"]:
			platform_support.append(
				len(list(filter(lambda x: x['platform'] == p, data.get('unityPackages')))) > 0
			)

		if platform_support[0] and not platform_support[1]:
			platform = VRChatThumbnail.Platform.PC
		elif platform_support[1] and not platform_support[0]:
			platform = VRChatThumbnail.Platform.Quest
		else:
			platform = VRChatThumbnail.Platform.Both

		# Make thumbnail
		VRChatThumbnail.make_thumbnail(
			Image.open(str(image_path)),
			platform=platform,
			avatar_name=data.get('name'),
			author_name=data.get('authorName'),
			data_dir=Path(__file__).parent / "data"
		).save(
			str(working_dir / 'image.png')
		)
		self.floating_files.append(working_dir / 'image.png')

		# ---
		
		# Wait for user to add or modify files
		if self.wait_to_compress:
			input("Press enter to continue...")

		if not self.no_zip:
			# Compress folder to zip
			shutil.make_archive(working_dir.parent / unique_name, 'zip', working_dir)
			self.floating_files.append(working_dir.parent / (unique_name + ".zip"))

			# Combine image with zip
			with open(working_dir.parent / (unique_name + ".png"), 'wb') as f_out:
				with open(working_dir / 'image.png', 'rb') as in_img:
					f_out.write(in_img.read())
				with open(working_dir.parent / (unique_name + ".zip"), 'rb') as in_zip:
					f_out.write(in_zip.read())
		else:
			shutil.copy(working_dir / 'image.png', working_dir.parent / (unique_name + ".png"))

		# Delete temp stuff
		self.delete_floating()


def main():
	options = Options(sys.argv)
	HELP = """
Help:
    -h, --help          Display help message and exit.

Main:
    -i <path>           Path to JSON file containing avatar data.
    [-P]                Keep temp directory on app failure. Must be manually deleted.
    [-W, --wait]        Wait for user to add|remove|modify files in temp directory before compressing.
    [-X, --no-zip]      Generate only thumbnail without embedding zip.
"""

	if options.get("-h", False) or options.get("--help", False):
		pass
	elif json_path := options.get("-i", True):
		json_path = Path(json_path).resolve()
		wait_to_compress = options.get("-W", False) or options.get("--wait", False)
		no_zip = options.get("-X", False) or options.get("--no-zip", False)
		
		app = App(json_path, wait_to_compress, no_zip)
		try:
			app.run()
		except Exception as e:
			if not options.get("-P", False):
				app.delete_floating()
			raise e

		return
	
	print(HELP)


if __name__ == "__main__":
	main()
