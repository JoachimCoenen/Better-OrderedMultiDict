import sys
from os.path import dirname, join
import random
from collections import OrderedDict
from operator import itemgetter
from typing import Callable

from bprofile import BProfile
from orderedmultidict import omdict

try:
	from better_orderedmultidict import OrderedMultiDict
except ImportError:
	sys.path.insert(0, join(dirname(dirname(__file__)), 'src'))
	from better_orderedmultidict import OrderedMultiDict
from performance_helper import *


PROFILING_DIR = join(dirname(dirname(__file__)), 'profiling')


def testCreateDict(init_list: list) -> dict[str, Result]:
	return compare_times([
		Operation(
			label="Better <br/>OrderedMultiDict",
			prepare=lambda: None,
			operation=lambda _: OrderedMultiDict(init_list)
		),
		Operation(
			label="omdict",
			prepare=lambda: None,
			operation=lambda _: omdict(init_list)
		),
		# Operation(
		# 	label="OrderedDict",
		# 	prepare=lambda: None,
		# 	operation=lambda _: OrderedDict(init_list)
		# ),
	], repetitions=5, outer_repetitions=2)


def _testIterateDict(sum_dict, init_list: list) -> dict[str, Result]:
	return compare_times([
		Operation(
			label="Better <br/>OrderedMultiDict",
			prepare=lambda: OrderedMultiDict(init_list),
			operation=lambda better_omd: sum_dict(better_omd),
			check_prepared=lambda better_omd: f"expected {len(init_list)} elements, but got {len(better_omd)}." if (len(better_omd) != len(init_list)) else None
		),
		Operation(
			label="omdict",
			prepare=lambda: omdict(init_list),
			operation=lambda omd: sum_dict(omd),
			check_prepared=lambda omd: f"expected {len(init_list)} elements, but got {omd.size()}." if (omd.size() != len(init_list)) else None
		),
		# Operation(
		# 	label="OrderedDict",
		# 	prepare=lambda: OrderedDict(init_list),
		# 	operation=lambda od: sum_dict(od),
		# 	check_prepared=lambda od: None
		# ),
	], repetitions=5, outer_repetitions=2)


def testIterateItems(init_list: list) -> dict[str, Result]:
	def sum_dict(dict_):
		if isinstance(dict_, omdict):
			total = sum(map(itemgetter(1), dict_.iterallitems()))
		else:
			total = sum(map(itemgetter(1), dict_.items()))
	return _testIterateDict(sum_dict, init_list)


def testIterateValues(init_list: list) -> dict[str, Result]:
	def sum_dict(dict_):
		if isinstance(dict_, omdict):
			total = sum(dict_.iterallvalues())
		else:
			total = sum(dict_.values())
	return _testIterateDict(sum_dict, init_list)


def testIterateKeys(init_list: list) -> dict[str, Result]:
	def sum_dict(dict_):
		if isinstance(dict_, omdict):
			total = sum(dict_.iterallkeys())
		else:
			total = sum(dict_.keys())
	return _testIterateDict(sum_dict, init_list)


def testIterateUniqueKeys(init_list: list) -> dict[str, Result]:
	def sum_dict(dict_):
		if isinstance(dict_, OrderedMultiDict):
			total = sum(dict_.unique_keys())
		else:
			total = sum(dict_.keys())
	return _testIterateDict(sum_dict, init_list)


def testAddAll(init_list: list) -> dict[str, Result]:
	add_list = list(range(VALUES_COUNT // KEY_COUNT))
	return compare_times([
		Operation(
			label="Better <br/>OrderedMultiDict",
			prepare=lambda: OrderedMultiDict(init_list),
			operation=lambda better_omd: [better_omd.addall(i, add_list) for i in range(KEY_COUNT)],
			check_prepared=lambda better_omd: f"expected {len(init_list)} elements, but got {len(better_omd)}." if (len(better_omd) != len(init_list)) else None
		),
		Operation(
			label="omdict",
			prepare=lambda: omdict(init_list),
			operation=lambda omd: [omd.addlist(i, add_list) for i in range(KEY_COUNT)],
			check_prepared=lambda omd: f"expected {len(init_list)} elements, but got {omd.size()}." if (omd.size() != len(init_list)) else None
		),
	], repetitions=5, outer_repetitions=2)


def testUpdate(update_list: list) -> dict[str, Result]:
	init_list = get_long_list_common_keys(key_count=100, values_count=5_000)
	return compare_times([
		Operation(
			label="Better <br/>OrderedMultiDict",
			prepare=lambda: OrderedMultiDict(init_list),
			operation=lambda better_omd: better_omd.update(update_list),
			check_prepared=lambda better_omd: f"expected {len(init_list)} elements, but got {len(better_omd)}." if (len(better_omd) != len(init_list)) else None
		),
		Operation(
			label="omdict",
			prepare=lambda: omdict(init_list),
			operation=lambda omd: omd.updateall(update_list),
			check_prepared=lambda omd: f"expected {len(init_list)} elements, but got {omd.size()}." if (omd.size() != len(init_list)) else None
		),
		# Operation(
		# 	label="OrderedDict",
		# 	prepare=lambda: OrderedDict(init_list),
		# 	operation=lambda od: od.update(update_list),
		# 	check_prepared=lambda od: None
		# ),
	], repetitions=5, outer_repetitions=2)


def testCopy(init_list: list) -> dict[str, Result]:
	return compare_times([
		Operation(
			label="Better <br/>OrderedMultiDict",
			prepare=lambda: OrderedMultiDict(init_list),
			operation=lambda better_omd: better_omd.copy(),
			check_prepared=lambda better_omd: f"expected {len(init_list)} elements, but got {len(better_omd)}." if (len(better_omd) != len(init_list)) else None
		),
		Operation(
			label="omdict",
			prepare=lambda: omdict(init_list),
			operation=lambda omd: omd.copy(),
			check_prepared=lambda omd: f"expected {len(init_list)} elements, but got {omd.size()}." if (omd.size() != len(init_list)) else None
		),
		# Operation(
		# 	label="OrderedDict",
		# 	prepare=lambda: OrderedDict(init_list),
		# 	operation=lambda od: od.update(update_list),
		# 	check_prepared=lambda od: None
		# ),
	], repetitions=5, outer_repetitions=2)


VALUES_COUNT = 5_000
KEY_COUNT = 100


def get_long_list():
	return [(i, i) for i in range(VALUES_COUNT)]


def get_long_list_common_keys(*, key_count: int = None, values_count: int = None):
	if key_count is None:
		key_count = KEY_COUNT
	if values_count is None:
		values_count = VALUES_COUNT
	return [(random.randint(0, key_count - 1), i) for i in range(values_count)]


def get_test_lists():
	LONG_LIST = get_long_list()
	LONG_LIST_COMMON_KEYS = get_long_list_common_keys()

	def create_tests(init_list):
		return [
			("create", lambda: testCreateDict(init_list)),
			("addall / addlist", lambda: testAddAll(init_list)),
			("update / updateall", lambda: testUpdate(init_list)),
			("copy", lambda: testCopy(init_list)),
			("iterate over items", lambda: testIterateItems(init_list)),
			("iterate over values", lambda: testIterateValues(init_list)),
			("iterate over keys", lambda: testIterateKeys(init_list)),
			("iterate over unique keys", lambda: testIterateUniqueKeys(init_list)),
		]

	return [
			create_tests(LONG_LIST),
			create_tests(LONG_LIST_COMMON_KEYS),
			# create_tests([]),
	]


def profile_unique_keys():
	LONG_LIST_COMMON_KEYS = get_long_list_common_keys()
	profiler = BProfile(PROFILING_DIR + '/unique_keys_01.png')
	omd = OrderedMultiDict(LONG_LIST_COMMON_KEYS)
	with profiler:
		total1 = sum(omd.unique_keys())
		total2 = sum(omd.unique_keys())
		total3 = sum(omd.unique_keys())
	print(f"{total1=}, {total2=}, {total3=}")


def profile_keys():
	LONG_LIST_COMMON_KEYS = get_long_list_common_keys()
	profiler = BProfile(PROFILING_DIR + '/keys_01.png')
	omd = OrderedMultiDict(LONG_LIST_COMMON_KEYS)
	with profiler:
		total1 = sum(omd.keys())
		total2 = sum(omd.keys())
		total3 = sum(omd.keys())
	print(f"{total1=}, {total2=}, {total3=}")


def _profile_create(init_list, kind):
	profiler = BProfile(PROFILING_DIR + f'/create_{kind}_01.png')
	with profiler:
		omd = OrderedMultiDict(init_list)


def profile_create_llck():
	LONG_LIST_COMMON_KEYS = get_long_list_common_keys()
	_profile_create(LONG_LIST_COMMON_KEYS, 'llck')


def profile_create_ll():
	LONG_LIST = get_long_list()
	_profile_create(LONG_LIST, 'll')


def _get_speedup_percentage(t1: float, t2: float) -> str:
	return f"{t2 / t1 - 1:3.1%}" if t1 != 0 else "<i>NaN</i>"


def _get_speedup_factor(t1: float, t2: float) -> str:
	if t1 > t2:
		return f"<i>slower</i>"
	else:
		return f"{t2 / t1:1.1f}x" if t1 != 0 else "<i>NaN</i>"


def default_format_results(results: dict[str, Result], format_val: Callable[[Result], str]) -> dict[str, str]:
	results = list(results.items())
	return {
		results[0][0]: f"{results[0][1].min_min * 1000:1.2f} ms",
		results[1][0]: f"{results[1][1].min_min * 1000:1.2f} ms",
		"speedup": _get_speedup_factor(results[0][1].min_min, results[1][1].min_min)
	}


def run_the_tests(test_lists):
	result_tables = []
	for tests in test_lists:
		results = run_tests(tests)
		result = format_results_table(results, lambda results: default_format_results(results, format_result))
		result_tables.append(result)
		print("")
	print("")

	for result in result_tables:
		print(result)
		print("")
		print("")


def run():
	run_the_tests(get_test_lists())
	# profile_keys()
	# profile_unique_keys()
	# profile_create_ll()
	# profile_create_llck()


if __name__ == '__main__':
	if len(sys.argv) > 1:
		VALUES_COUNT = int(sys.argv[1])
	run()
