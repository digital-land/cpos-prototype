from application.data import LocalAuthorityMapping
la_mapping = LocalAuthorityMapping()


def map_la_code_to_name(id):
	if la_mapping.get_local_authority_name(id) is not None:
		return la_mapping.get_local_authority_name(id)
	return id


def flatten_tuples(tuplist, ind=0):
	if ind == 1:
		flattened = [b for (a, b) in tuplist]
	else:
		flattened = [a for (a, b) in tuplist]
	return flattened
