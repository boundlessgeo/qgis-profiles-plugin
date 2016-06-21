def apply():
	try:
		from processing.core.Processing import Processing
		Processing.activateProvider("ntv2_transformations")
	except:
		pass
