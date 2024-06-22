import gc
import math
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Reversible

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


def print_indented(val, *, prefix: str = ''):
	global _GLOBAL_INDENT_LVL
	indent_str = (INDENT * (_GLOBAL_INDENT_LVL))
	text = indent_multiline_str(str(val), indent=indent_str, prefix=prefix)
	print(text)


INDENT = "    "
_GLOBAL_INDENT_LVL = 0


@contextmanager
def print_and_indent(msg: str):
	"""
	contextmanager that increases th indentation for all contained logging operations.
	:return:
	"""
	global _GLOBAL_INDENT_LVL
	print_indented(msg)
	_GLOBAL_INDENT_LVL += 1
	try:
		yield
	finally:
		_GLOBAL_INDENT_LVL = max(0, _GLOBAL_INDENT_LVL - 1)


@contextmanager
def time_and_indent(msg: str):
	"""
	contextmanager that increases th indentation for all contained logging operations.
	:return:
	"""
	timer = Timer()
	timer.tic()
	try:
		with print_and_indent(msg):
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
class Operation[I, T]:
	label: str
	prepare: Callable[[I], T]
	operation: Callable[[I, T], Any]
	check_prepared: Callable[[I, T], str | None] | None = None
	share_prepared: bool = False
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


def time[I, T](operation: Operation[I, T], input: I, *, repetitions: int) -> SingleResult:
	share_prepared = operation.share_prepared
	with print_action(f"{operation.label}"):
		prepared = _prepare(operation.prepare, input, share_prepared=share_prepared, repetitions=repetitions)
		if operation.check_prepared is not None:
			_check_prepared(operation.check_prepared, input, prepared, share_prepared=share_prepared)
		return _run_timers(operation.operation, input, prepared, label=operation.label, repetitions=repetitions)


def _run_timers[I, T](operation: Callable[[I, T], Any], input: I, prepared: list[T], label: str, repetitions: int):
	with print_and_indent(f"Running..."):
		timerit = Timerit(repetitions, label, verbose=0)
		for i, timer in enumerate(timerit):
			with timer:
				res = operation(input, prepared[i])
		# print_indented(f"time: {timer.elapsed:.4f}.")
	return SingleResult(label, timerit.min())


def _prepare[I, T](prepare: Callable[[I], T], input: I, share_prepared: bool, repetitions: int) -> list[T]:
	with print_and_indent(f"Preparing..."):
		if share_prepared:
			prep = prepare(input)
			return [prep for _ in range(repetitions)]
		else:
			return [prepare(input) for _ in range(repetitions)]


def _check_prepared[I, T](check_prepared: Callable[[I, T], str | None], input: I, prepared: list[T], share_prepared: bool):
	with print_and_indent(f"Checking..."):
		if share_prepared:
			_check_prepared_single(check_prepared, input, prepared[0])
		else:
			for prep in prepared:
				_check_prepared_single(check_prepared, input, prep)


def _check_prepared_single[I, T](check_prepared: Callable[[I, T], str | None], input: I, prep: T):
	if error := check_prepared(input, prep):
		raise ValueError(error)


def compare_times[I](operations: Reversible[Operation[I, Any]], input: I, *, repetitions: int = 10, outer_repetitions: int = 2) -> dict[str, Result]:
	orderings = [iter, reversed]
	results = defaultdict(list)
	for rep in range(outer_repetitions):
		order = orderings[rep % len(orderings)]
		for operation in order(operations):
			res = time(operation, input, repetitions=repetitions)
			results[operation.label].append(res.min)

	return {label: Result(label, min_times) for label, min_times in results.items()}


def run_tests[I](tests: Iterable[tuple[str, Reversible[Operation[I, Any]]]], input: I, *, repetitions: int = 10, outer_repetitions: int = 2) -> dict[str,  dict[str, Result]]:
	result = {}
	with time_and_indent("all tests:"):
		for name, operations in tests:
			print_indented("")
			with print_action(name):
				result[name] = compare_times(operations, input, repetitions=repetitions, outer_repetitions=outer_repetitions)
			gc.collect()
	return result


def format_results_table(results: dict[str,  dict[str, Result]], format_results: Callable[[dict[str, Result]], dict[str, str]], get_label: Callable[[str], str]) -> str:
	formatted_results = {
		name: format_results(result)
		for name, result in results.items()
	}
	column_keys = {}
	for variations in formatted_results.values():
		for variation in variations.keys():
			column_keys.setdefault(variation, get_label(variation))

	# build table:
	table: list[list[str]] = []
	for category, variations in formatted_results.items():
		row = [category]
		table.append(row)
		for column in column_keys:
			val = variations.get(column)
			row.append('' if val is None else val)

	column_keys = ['', *column_keys.values()]

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


def lerp(a: float, b: float, t: float) -> float:
	return a*(1-t) + b*t


def default_format_results(results: dict[str, Result], format_val: Callable[[float], str], highlight_fastest: bool = False) -> dict[str, str]:
	min_min = min(result.min_min for result in results.values())
	max_min = max(result.min_min for result in results.values())
	# all values within the top 10% of the spread are considered good. e.g.:
	#   for the values [90, 90.8, 91, 91.1, 100]
	#   the maximum good value is: 91 = 90 + (100 - 90) * 10%.
	#   only these are considered good: [90, 90.8, 91]
	considered_good_delta = (max_min - min_min) * 0.1
	considered_good_delta = max(considered_good_delta, 0.1 / 1000.0)  # within .1 ms of top result is always considered good. (because of measurement inaccuracies).
	considered_good = min_min + considered_good_delta
	return {
		name: f"**<u>{format_val(result.min_min)}</u>**" if highlight_fastest and result.min_min <= considered_good else format_val(result.min_min)
		for name, result in results.items()
	}


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


def format_result(secs: float) -> str:
	mill_secs = secs * 1000
	if mill_secs < 0.1:
		return f"&lt; 0.1 ms"
	return f"{mill_secs:1.1f} ms"


def format_float(number: float, precision: int, max_decimals: int = 20) -> str:
	if number == 0.:
		return '0.' + ('0'*precision)

	magnitude_f = math.log10(abs(number))
	magnitude = math.ceil(magnitude_f)
	decimals = precision - int(magnitude)
	decimals = max(0, min(decimals, max_decimals))
	f_str = f"{{:.{decimals}f}}"
	return f_str.format(number)


__all__ = [
	'Operation',
	# 'SingleResult',
	'Result',
	'time',
	'compare_times',
	'run_tests',
	'format_results_table',
	'format_table',
	'default_format_results',
	'format_result',
]
