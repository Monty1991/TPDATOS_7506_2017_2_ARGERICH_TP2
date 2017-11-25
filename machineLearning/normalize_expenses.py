from .utils import *

def isNumber(posibleNumber):
	"""Indica si es un numero valido"""
	if type(posibleNumber) != str:
		return True
	else:
		return (posibleNumber[0] == '$') | (posibleNumber[0].isdigit())

def Normalize_ExpenseValue(value):
	"""Se encarga de que ninguna expensa sea menor a 50, a menos que sea 0"""
	if value < 50:
		value *= 1000
	else:
		while value > 10000:
			value /= 10
	return value

def GetNumbers(x):
	"""Extrae una cantidad de expensa valida"""
	if '/' in x:
		value = x.split('/')
		if value[1][0].isdigit():
			return Normalize_ExpenseValue(GetValidNumber(value[1]))
		else:
			y = value[0]
	else:
		y = x
	if y[0] == '$':
		value = y.split('$')
		try:
			value = Normalize_ExpenseValue(GetValidNumber(value[1]))
		except ValueError:
			1+1
		return value
	return Normalize_ExpenseValue(GetValidNumber(y))

def NormalizeExpenses(expenses):
	"""Normaliza un valor posible de expensas"""
	if type(expenses) != str:
		return GetValidNumber(expenses)
	if expenses[0].isdigit():
		return GetValidNumber(expenses)
	expenses = expenses.lower().replace('u$s', '$').replace('  ', ' ').replace('$ ', '$').replace('+', ' ')
	expenses = Filter(expenses.split(), isNumber)
	return Reduce(Map(expenses, GetNumbers), lambda x,y: x + y, 0)
