import math
import random
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from operator import itemgetter
from typing import Any, Callable

from timerit import Timerit

from better_orderedmultidict import OrderedMultiDict
from orderedmultidict import omdict


@dataclass
class Operation:
	label: str
	operation: Callable[[], Any]


@dataclass
class SingleResult:
	label: str
	min: float


@dataclass
class Result:
	label: str
	min_times: list[float]

	@property
	def min_mean(self) -> float:
		return sum(self.min_times) / len(self.min_times)

	@property
	def min_min(self) -> float:
		return min(self.min_times)

	@property
	def min_std(self) -> float:
		import math
		times = self.min_times
		mean = self.min_mean
		return math.sqrt(sum((t - mean) ** 2 for t in times) / len(times))


class TestPerformance:

	@classmethod
	def time(cls, operation: Operation, repetitions: int) -> SingleResult:
		timerit = Timerit(repetitions, operation.label, verbose=0)
		for timer in timerit:
			with timer:
				operation.operation()
		return SingleResult(operation.label, timerit.min())

	@classmethod
	def compare_times(cls, operations: list[Operation], repetitions: int = 10, outer_repetitions: int = 2) -> dict[str, Result]:
		orderings = [iter, reversed]
		results = defaultdict(list)
		for rep in range(outer_repetitions):
			order = orderings[rep % len(orderings)]
			for operation in order(operations):
				res = cls.time(operation, repetitions)
				results[operation.label].append(res.min)

		return {label: Result(label, min_times) for label, min_times in results.items()}

	@classmethod
	def testCreateDict(cls, long_list: list) -> dict[str, Result]:
		return cls.compare_times([
			Operation("Better <br/>OrderedMultiDict", lambda: OrderedMultiDict(long_list)),
			Operation("omdict", lambda: omdict(long_list)),
			Operation("OrderedDict", lambda: OrderedDict(long_list)),
		], outer_repetitions=3)

	@classmethod
	def _testIterateDict(cls, sum_dict, long_list: list) -> dict[str, Result]:
		better_omd = OrderedMultiDict(long_list)
		if len(better_omd) != VALUES_COUNT:
			raise ValueError(f"expected {VALUES_COUNT} elements, but got {len(better_omd)}.")
		omd = omdict(long_list)
		if omd.size() != VALUES_COUNT:
			raise ValueError(f"expected {VALUES_COUNT} elements, but got {omd.size()}.")
		od = OrderedDict(long_list)

		return cls.compare_times([
			Operation("Better <br/>OrderedMultiDict", lambda: sum_dict(better_omd)),
			Operation("omdict", lambda: sum_dict(omd)),
			Operation("OrderedDict", lambda: sum_dict(od)),
		], outer_repetitions=3)

	@classmethod
	def testIterateItems(cls, long_list: list) -> dict[str, Result]:
		def sum_dict(dict_):
			if isinstance(dict_, omdict):
				total = sum(map(itemgetter(1), dict_.iterallitems()))
			else:
				total = sum(map(itemgetter(1), dict_.items()))
		return cls._testIterateDict(sum_dict, long_list)

	@classmethod
	def testIterateValues(cls, long_list: list) -> dict[str, Result]:
		def sum_dict(dict_):
			if isinstance(dict_, omdict):
				total = sum(dict_.iterallvalues())
			else:
				total = sum(dict_.values())
		return cls._testIterateDict(sum_dict, long_list)

	@classmethod
	def testIterateKeys(cls, long_list: list) -> dict[str, Result]:
		def sum_dict(dict_):
			if isinstance(dict_, omdict):
				total = sum(dict_.iterallkeys())
			else:
				total = sum(dict_.keys())
		return cls._testIterateDict(sum_dict, long_list)

	@classmethod
	def testIterateUniqueKeys(cls, long_list: list) -> dict[str, Result]:
		def sum_dict(dict_):
			if isinstance(dict_, OrderedMultiDict):
				total = sum(dict_.unique_keys())
			else:
				total = sum(dict_.keys())
		return cls._testIterateDict(sum_dict, long_list)


VALUES_COUNT = 500_000
LONG_LIST = [(i, i) for i in range(VALUES_COUNT)]
KEY_COUNT = 100
LONG_LIST_COMMON_KEYS = [(random.randint(0, KEY_COUNT-1), i) for i in range(VALUES_COUNT)]

TESTS_1 = [
	("create", lambda: TestPerformance.testCreateDict(LONG_LIST)),
	("iterate over items", lambda: TestPerformance.testIterateItems(LONG_LIST)),
	("iterate over values", lambda: TestPerformance.testIterateValues(LONG_LIST)),
	("iterate over keys", lambda: TestPerformance.testIterateKeys(LONG_LIST)),
	("iterate over unique keys", lambda: TestPerformance.testIterateUniqueKeys(LONG_LIST)),
]

TESTS_2 = [
	("create", lambda: TestPerformance.testCreateDict(LONG_LIST_COMMON_KEYS)),
	("iterate over items", lambda: TestPerformance.testIterateItems(LONG_LIST_COMMON_KEYS)),
	("iterate over values", lambda: TestPerformance.testIterateValues(LONG_LIST_COMMON_KEYS)),
	("iterate over keys", lambda: TestPerformance.testIterateKeys(LONG_LIST_COMMON_KEYS)),
	("iterate over unique keys", lambda: TestPerformance.testIterateUniqueKeys(LONG_LIST_COMMON_KEYS)),
]


def run_tests(tests: list[tuple[str, Callable[[], dict[str, Result]]]]) -> dict[str,  dict[str, Result]]:
	result = {}
	for name, test in tests:
		print(f"{name}:")
		result[name] = test()
	return result


def format_results(results: dict[str,  dict[str, Result]], format_val: Callable[[Result], str]) -> str:
	column_keys = {}
	for variations in results.values():
		for variation in variations.keys():
			column_keys.setdefault(variation)

	column_keys = list(column_keys)

	# build table:
	table: list[list[str]] = []
	for category, variations in results.items():
		row = [category]
		table.append(row)
		for column in column_keys:
			val = variations.get(column)
			row.append('' if val is None else format_val(val))

	column_keys = ['', *column_keys]

	rows = len(table)
	cols = len(column_keys)

	# layout cells:
	col_layout = [
		(max(len(table[row][col]) for row in range(rows)), col != 0)
		for col in range(cols)
	]
	# account for headers
	col_layout = [
		(max(len(key), col[0]), col[1])
		for key, col in zip(column_keys, col_layout)
	]

	header = build_row(column_keys, col_layout)

	row_strs = [
		header,
		build_header_seperator(col_layout),
		*(build_row(row, col_layout) for row in table)
	]

	return '\n'.join(row_strs)


def build_row(row: list[str], layout: list[tuple[int, bool]]) -> str:
	row_str = ' | '.join(align_text(cell, *col_layout) for cell, col_layout in zip(row, layout))
	return f'| {row_str} |'


def build_header_seperator(layout: list[tuple[int, bool]]) -> str:
	row_str = '|'.join(
		'-' + '-'*width + (':' if right else '-')
		for width, right
		in layout
	)
	return f'|{row_str}|'


def align_text(text: str, length: int, right: bool) -> str:
	if len(text) >= length:
		return text
	space = ' ' * (length - len(text))
	return (space + text) if right else (text + space)


def format_result(result: Result) -> str:
	mean = result.min_mean * 1000
	std = result.min_std * 1000
	return f"{mean:1.2f} ms"


def format_float(number: float, precision: int, max_decimals: int = 20) -> str:
	if number == 0.:
		return '0.' + ('0'*precision)

	magnitude_f = math.log10(abs(number))
	magnitude = math.ceil(magnitude_f)
	decimals = precision - int(magnitude)
	decimals = max(0, min(decimals, max_decimals))
	f_str = f"{{:.{decimals}f}}"
	return f_str.format(number)


def run_and_format_tests(tests: list[tuple[str, Callable[[], dict[str, Result]]]]) -> str:
	results = run_tests(tests)
	result = format_results(results, format_result)
	return result


def run():
	result_tables = []
	for tests in [TESTS_1, TESTS_2]:
		result_tables.append(run_and_format_tests(tests))
		print("")
	print("")
	for result in result_tables:
		print(result)
		print("")
		print("")


if __name__ == '__main__':
	run()
