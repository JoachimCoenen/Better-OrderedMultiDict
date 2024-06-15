import gc
import math
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable

from timerit import Timer, Timerit


def indent_multiline_str(text: str, *, indent: str, prefix: str = '') -> str:
	if not indent and not prefix:
		return text

	split_lines = text.splitlines()
	indent = indent + prefix

	result = "\n".join(map(indent.__add__, split_lines))
	if text.endswith('\n'):
		result += '\n'
	return result


def print_indented(val, *, prefix: str = '', additional_indent_lvl: int = 0, ):
	global _GLOBAL_INDENT_LVL
	indent_str = (INDENT * (_GLOBAL_INDENT_LVL + additional_indent_lvl))
	text = indent_multiline_str(str(val), indent=indent_str, prefix=prefix)
	print(text)


INDENT = "    "
_GLOBAL_INDENT_LVL = 0


@contextmanager
def print_and_indent(msg: str, *, additional_indent_lvl: int = 0):
	"""
	contextmanager that increases th indentation for all contained logging operations.
	:return:
	"""
	global _GLOBAL_INDENT_LVL
	print_indented(msg, additional_indent_lvl=additional_indent_lvl)
	_GLOBAL_INDENT_LVL += 1
	try:
		yield
	finally:
		_GLOBAL_INDENT_LVL = max(0, _GLOBAL_INDENT_LVL - 1)


@contextmanager
def time_and_indent(msg: str, *, additional_indent_lvl: int = 0):
	"""
	contextmanager that increases th indentation for all contained logging operations.
	:return:
	"""
	timer = Timer()
	timer.tic()
	try:
		with print_and_indent(msg, additional_indent_lvl=additional_indent_lvl):
			yield
	finally:
		timer.toc()
		print_indented(f"time: {timer.elapsed:.4f}s.")


@contextmanager
def print_action(msg: str):
	"""
	contextmanager that increases th indentation for all contained logging operations.
	:return:
	"""
	try:
		with print_and_indent(f"{msg}:"):
			yield
	except Exception as e:
		print_indented(f"EXCEPTION: {e}.")
		raise


@dataclass
class Operation[T]:
	label: str
	prepare: Callable[[], T]
	operation: Callable[[T], Any]
	check_prepared: Callable[[T], str | None] | None = None
	# check_result: Callable[[T], bool] | None = None


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


def time(operation: Operation, repetitions: int) -> SingleResult:
	with print_action(f"{operation.label}"):
		with print_and_indent(f"Preparing..."):
			prepared = [operation.prepare() for _ in range(repetitions)]
		with print_and_indent(f"Checking..."):
			if operation.check_prepared is not None:
				for prep in prepared:
					if error := operation.check_prepared(prep):
						raise ValueError(error)

		with print_and_indent(f"Running..."):
			timerit = Timerit(repetitions, operation.label, verbose=0)
			for i, timer in enumerate(timerit):
				with timer:
					operation.operation(prepared[i])
				# print_indented(f"time: {timer.elapsed:.4f}.")

	return SingleResult(operation.label, timerit.min())


def compare_times(operations: list[Operation], repetitions: int = 10, outer_repetitions: int = 2) -> dict[str, Result]:
	orderings = [iter, reversed]
	results = defaultdict(list)
	for rep in range(outer_repetitions):
		order = orderings[rep % len(orderings)]
		for operation in order(operations):
			res = time(operation, repetitions)
			results[operation.label].append(res.min)

	return {label: Result(label, min_times) for label, min_times in results.items()}


def run_tests(tests: list[tuple[str, Callable[[], dict[str, Result]]]]) -> dict[str,  dict[str, Result]]:
	result = {}
	with time_and_indent("all tests:"):
		for name, test in tests:
			print_indented("")
			with print_action(name):
				result[name] = test()
			gc.collect()
	return result


def default_format_results(results: dict[str, Result], format_val: Callable[[Result], str]) -> dict[str, str]:
	return {
		name: format_val(result)
		for name, result in results.items()
	}


def format_results_table(results: dict[str,  dict[str, Result]], format_results: Callable[[dict[str, Result]], dict[str, str]]) -> str:
	formatted_results = {
		name: format_results(result)
		for name, result in results.items()
	}
	column_keys = {}
	for variations in formatted_results.values():
		for variation in variations.keys():
			column_keys.setdefault(variation)

	column_keys = list(column_keys)

	# build table:
	table: list[list[str]] = []
	for category, variations in formatted_results.items():
		row = [category]
		table.append(row)
		for column in column_keys:
			val = variations.get(column)
			row.append('' if val is None else val)

	column_keys = ['', *column_keys]

	cols = len(column_keys)

	# layout cells:
	return format_table(
		table,
		column_keys,
		[ColumnLayout(col != 0) for col in range(cols)]
	)


@dataclass
class ColumnLayout:
	right_align: bool


def format_table(table: list[list[str]], headers: list[str], column_layouts: list[ColumnLayout]) -> str:

	rows = len(table)
	cols = len(headers)

	# layout cells:
	col_layout = [
		(max(max(len(table[row][col]) for row in range(rows)), len(header)), layout)
		for col, (header, layout) in enumerate(zip(headers, column_layouts))
	]

	header = build_row(headers, col_layout)

	row_strs = [
		header,
		build_header_seperator(col_layout),
		*(build_row(row, col_layout) for row in table)
	]

	return '\n'.join(row_strs)


def build_row(row: list[str], layout: list[tuple[int, ColumnLayout]]) -> str:
	row_str = ' | '.join(align_text(cell, *col_layout) for cell, col_layout in zip(row, layout))
	return f'| {row_str} |'


def build_header_seperator(column_layouts: list[tuple[int, ColumnLayout]]) -> str:
	row_str = '|'.join(
		'-' + '-'*width + (':' if layout.right_align else '-')
		for width, layout
		in column_layouts
	)
	return f'|{row_str}|'


def align_text(text: str, length: int, layout: ColumnLayout) -> str:
	if len(text) >= length:
		return text
	space = ' ' * (length - len(text))
	return (space + text) if layout.right_align else (text + space)


def format_result(result: Result) -> str:
	mean = result.min_mean * 1000
	# std = result.min_std * 1000
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


def run_tests_and_format_table(tests: list[tuple[str, Callable[[], dict[str, Result]]]]) -> str:
	results = run_tests(tests)
	result = format_results_table(results, lambda results: default_format_results(results, format_result))
	return result


__all__ = [
	'Operation',
	# 'SingleResult',
	'Result',
	'time',
	'compare_times',
	'run_tests',
	'format_result',
	'format_results_table',
	'run_tests_and_format_table',
]
