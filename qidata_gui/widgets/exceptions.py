
class UserCancelation(Exception):
	"""
	File selection changed, by user decided to cancel the change
	"""
	pass

class AttributeIsReadOnly(Exception):
	"""
	User tried to modify something with read-only access
	"""
	pass