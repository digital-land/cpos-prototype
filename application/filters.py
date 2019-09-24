from application.data import LocalAuthorityMapping
la_mapping = LocalAuthorityMapping()

from application.utils import has_investigation_counts


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


def tuple_list_to_dict(tuplist):
	if len(tuplist) > 0 and isinstance(tuplist[0], tuple):
		return dict(tuplist)
	return tuplist


def map_cpo_status_to_tag_class(status):
	class_ = ""
	if 'confirmed' in status:
		class_ = "govuk-tag--confirmed"
	if status in ['not confirmed', 'invalid']:
		class_ = "govuk-tag--error"
	if 'withdrawn' in status:
		class_ = "govuk-tag--disabled"
	if 'inquiry' in status:
		class_ = "govuk-tag--warning"
	return class_


def remove_item(list_, item):
	if item in list_:
		list_.remove(item)
	return list_


def count_with_investigation(cpos, has=True):
	if isinstance(cpos, list):
		counts = has_investigation_counts(cpos)
		return counts[has]
	return cpos
