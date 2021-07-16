class Options:
	def __init__(self, args: list):
		assert isinstance(args, list)
		self.args = args

	def get(self, key: str, has_value: bool = True):
		assert isinstance(key, str)
		assert isinstance(has_value, bool)
		
		if has_value:
			if (key in self.args[:-1]) and (path_index := self.args[:-1].index(key)) and (value := self.args[path_index+1]):
				return value
			else:
				return None
		else:
			return key in self.args
