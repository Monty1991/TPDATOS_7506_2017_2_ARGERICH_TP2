def LimpiarNumero(word):
	"""Esta funcion magica devuelve un numero, independientemente de toda la basura que le siga"""
	offset = 0
	hasDot = False
	for d in word:
		if d in '.,':
			if hasDot:
				break
			hasDot = True
		elif not d.isdigit():
			break
		offset += 1
	return float(word[0:offset].replace(',', '.'))
