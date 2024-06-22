import sys
from os.path import dirname, join
import random
from typing import Any, Callable, Iterable, MutableMapping

from orderedmultidict import omdict
from boltons.dictutils import OrderedMultiDict as BoltonOrderedMultiDict, FastIterOrderedMultiDict

from performance_helper import print_action

try:
	from better_orderedmultidict import OrderedMultiDict, DeOrderedMultiDict
except ImportError:
	sys.path.insert(0, join(dirname(dirname(__file__)), 'src'))
	from better_orderedmultidict import OrderedMultiDict, DeOrderedMultiDict
from performance_helper import *


PROFILING_DIR = join(dirname(dirname(__file__)), 'profiling')


def _check_omd_size(expected_size: int, actual_size: int) -> str | None:
	return f"expected {expected_size} elements, but got {actual_size}." if (actual_size != expected_size) else None


def _check_better_omd_size(expected_size: int, better_omd: OrderedMultiDict) -> str | None:
	return _check_omd_size(expected_size, len(better_omd))


def _check_omdict_size(expected_size: int, omd: omdict) -> str | None:
	return _check_omd_size(expected_size, omd.size())


CREATE_DICT_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in [
	Operation(
		label="OrMuDi",
		prepare=lambda init_list: None,
		operation=lambda init_list, _: OrderedMultiDict(init_list)
	),
	Operation(
		label="DeOrMuDi",
		prepare=lambda init_list: None,
		operation=lambda init_list, _: DeOrderedMultiDict(init_list)
	),
	Operation(
		label="omdict",
		prepare=lambda init_list: None,
		operation=lambda init_list, _: omdict(init_list)
	),
	Operation(
		label="bOrMuDi",
		prepare=lambda init_list: None,
		operation=lambda init_list, _: BoltonOrderedMultiDict(init_list)
	),
	Operation(
		label="bFIOrMuDi",
		prepare=lambda init_list: None,
		operation=lambda init_list, _: FastIterOrderedMultiDict(init_list)
	),
]}


def _get_iterate_dict_ops(get_iter: Callable[[MutableMapping[int, int]], Iterable]) -> list[Operation[list, Any]]:
	def sum_items(dict_):
		list(get_iter(dict_))

	return [
		Operation(
			label="OrMuDi",
			prepare=lambda init_list: OrderedMultiDict(init_list),
			operation=lambda init_list, better_omd: sum_items(better_omd),
			check_prepared=lambda init_list, better_omd: _check_omd_size(len(init_list), len(better_omd)),
			share_prepared=True
		),
		Operation(
			label="DeOrMuDi",
			prepare=lambda init_list: DeOrderedMultiDict(init_list),
			operation=lambda init_list, better_omd: sum_items(better_omd),
			check_prepared=lambda init_list, better_omd: _check_omd_size(len(init_list), len(better_omd)),
			share_prepared=True
		),
		Operation(
			label="omdict",
			prepare=lambda init_list: omdict(init_list),
			operation=lambda init_list, omd: sum_items(omd),
			check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), omd.size()),
			share_prepared=True
		),
		Operation(
			label="bOrMuDi",
			prepare=lambda init_list: BoltonOrderedMultiDict(init_list),
			operation=lambda init_list, omd: sum_items(omd),
			check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), len(omd.items(multi=True))),
			share_prepared=True
		),
		Operation(
			label="bFIOrMuDi",
			prepare=lambda init_list: FastIterOrderedMultiDict(init_list),
			operation=lambda init_list, omd: sum_items(omd),
			check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), len(omd.items(multi=True))),
			share_prepared=True
		),
	]


ITERATE_ITEMS_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in _get_iterate_dict_ops(
	lambda dict_: {
		omdict: lambda: dict_.iterallitems(),
		OrderedMultiDict: lambda: dict_.items(),
		DeOrderedMultiDict: lambda: dict_.items(),
		BoltonOrderedMultiDict: lambda: dict_.iteritems(multi=True),
		FastIterOrderedMultiDict: lambda: dict_.iteritems(multi=True),
	}[type(dict_)]()
)}


ITERATE_VALUES_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in _get_iterate_dict_ops(
	lambda dict_: {
		omdict: lambda: dict_.iterallvalues(),
		OrderedMultiDict: lambda: dict_.values(),
		DeOrderedMultiDict: lambda: dict_.values(),
		BoltonOrderedMultiDict: lambda: dict_.itervalues(multi=True),
		FastIterOrderedMultiDict: lambda: dict_.itervalues(multi=True),
	}[type(dict_)]()
)}


ITERATE_KEYS_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in _get_iterate_dict_ops(
	lambda dict_: {
		omdict: lambda: dict_.iterallkeys(),
		OrderedMultiDict: lambda: dict_.keys(),
		DeOrderedMultiDict: lambda: dict_.keys(),
		BoltonOrderedMultiDict: lambda: dict_.iterkeys(multi=True),
		FastIterOrderedMultiDict: lambda: dict_.iterkeys(multi=True),
	}[type(dict_)]()
)}


ITERATE_UNIQUE_KEYS_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in _get_iterate_dict_ops(
	lambda dict_: {
		omdict: lambda: dict_.iterkeys(),
		OrderedMultiDict: lambda: dict_.unique_keys(),
		DeOrderedMultiDict: lambda: dict_.unique_keys(),
		BoltonOrderedMultiDict: lambda: dict_.keys(multi=False),
		FastIterOrderedMultiDict: lambda: dict_.keys(multi=False),
	}[type(dict_)]()
)}


ADD_ALL_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in [
	Operation(
		label="OrMuDi",
		prepare=lambda init_list: (OrderedMultiDict(init_list), list(range(VALUES_COUNT // KEY_COUNT))),
		operation=lambda init_list, better_omd_add_list: [better_omd_add_list[0].addall(i, better_omd_add_list[1]) for i in range(KEY_COUNT)],
		check_prepared=lambda init_list, better_omd_add_list: _check_omd_size(len(init_list), len(better_omd_add_list[0]))
	),
	Operation(
		label="DeOrMuDi",
		prepare=lambda init_list: (DeOrderedMultiDict(init_list), list(range(VALUES_COUNT // KEY_COUNT))),
		operation=lambda init_list, better_omd_add_list: [better_omd_add_list[0].addall(i, better_omd_add_list[1]) for i in range(KEY_COUNT)],
		check_prepared=lambda init_list, better_omd_add_list: _check_omd_size(len(init_list), len(better_omd_add_list[0]))
	),
	Operation(
		label="omdict",
		prepare=lambda init_list: (omdict(init_list), list(range(VALUES_COUNT // KEY_COUNT))),
		operation=lambda init_list, omd_add_list: [omd_add_list[0].addlist(i, omd_add_list[1]) for i in range(KEY_COUNT)],
		check_prepared=lambda init_list, omd_add_list: _check_omd_size(len(init_list), omd_add_list[0].size())
	),
	Operation(
		label="bOrMuDi",
		prepare=lambda init_list: (BoltonOrderedMultiDict(init_list), list(range(VALUES_COUNT // KEY_COUNT))),
		operation=lambda init_list, omd_add_list: [omd_add_list[0].addlist(i, omd_add_list[1]) for i in range(KEY_COUNT)],
		check_prepared=lambda init_list, omd_add_list: _check_omd_size(len(init_list), len(omd_add_list[0].items(multi=True)))
	),
	Operation(
		label="bFIOrMuDi",
		prepare=lambda init_list: (FastIterOrderedMultiDict(init_list), list(range(VALUES_COUNT // KEY_COUNT))),
		operation=lambda init_list, omd_add_list: [omd_add_list[0].addlist(i, omd_add_list[1]) for i in range(KEY_COUNT)],
		check_prepared=lambda init_list, omd_add_list: _check_omd_size(len(init_list), len(omd_add_list[0].items(multi=True)))
	),
]}


UPDATE_KEY_COUNT: int = 100
UPDATE_VALUES_COUNT: int = 5_000
UPDATE_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in [
	Operation(
		label="OrMuDi",
		prepare=lambda update_list: OrderedMultiDict(get_long_list_common_keys(key_count=UPDATE_KEY_COUNT, values_count=UPDATE_VALUES_COUNT)),
		operation=lambda update_list, better_omd: better_omd.update(update_list),
		check_prepared=lambda init_list, better_omd: _check_omd_size(UPDATE_VALUES_COUNT, len(better_omd))
	),
	Operation(
		label="DeOrMuDi",
		prepare=lambda update_list: DeOrderedMultiDict(get_long_list_common_keys(key_count=UPDATE_KEY_COUNT, values_count=UPDATE_VALUES_COUNT)),
		operation=lambda update_list, better_omd: better_omd.update(update_list),
		check_prepared=lambda init_list, better_omd: _check_omd_size(UPDATE_VALUES_COUNT, len(better_omd))
	),
	Operation(
		label="omdict",
		prepare=lambda update_list: omdict(get_long_list_common_keys(key_count=UPDATE_KEY_COUNT, values_count=UPDATE_VALUES_COUNT)),
		operation=lambda update_list, omd: omd.updateall(update_list),
		check_prepared=lambda init_list, omd: _check_omd_size(UPDATE_VALUES_COUNT, omd.size())
	),
	Operation(
		label="bOrMuDi",
		prepare=lambda update_list: BoltonOrderedMultiDict(get_long_list_common_keys(key_count=UPDATE_KEY_COUNT, values_count=UPDATE_VALUES_COUNT)),
		operation=lambda update_list, omd: omd.update(update_list),
		check_prepared=lambda init_list, omd: _check_omd_size(UPDATE_VALUES_COUNT, len(omd.items(multi=True)))
	),
	Operation(
		label="bFIOrMuDi",
		prepare=lambda update_list: FastIterOrderedMultiDict(get_long_list_common_keys(key_count=UPDATE_KEY_COUNT, values_count=UPDATE_VALUES_COUNT)),
		operation=lambda update_list, omd: omd.update(update_list),
		check_prepared=lambda init_list, omd: _check_omd_size(UPDATE_VALUES_COUNT, len(omd.items(multi=True)))
	),
]}

EXTEND_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in [
	Operation(
		label="OrMuDi",
		prepare=lambda update_list: OrderedMultiDict(get_long_list_common_keys(key_count=UPDATE_KEY_COUNT, values_count=UPDATE_VALUES_COUNT)),
		operation=lambda update_list, better_omd: better_omd.extend(update_list),
		check_prepared=lambda init_list, better_omd: _check_omd_size(UPDATE_VALUES_COUNT, len(better_omd))
	),
	Operation(
		label="DeOrMuDi",
		prepare=lambda update_list: DeOrderedMultiDict(get_long_list_common_keys(key_count=UPDATE_KEY_COUNT, values_count=UPDATE_VALUES_COUNT)),
		operation=lambda update_list, better_omd: better_omd.extend(update_list),
		check_prepared=lambda init_list, better_omd: _check_omd_size(UPDATE_VALUES_COUNT, len(better_omd))
	),
	Operation(
		label="bOrMuDi",
		prepare=lambda update_list: BoltonOrderedMultiDict(get_long_list_common_keys(key_count=UPDATE_KEY_COUNT, values_count=UPDATE_VALUES_COUNT)),
		operation=lambda update_list, omd: omd.update_extend(update_list),
		check_prepared=lambda init_list, omd: _check_omd_size(UPDATE_VALUES_COUNT, len(omd.items(multi=True)))
	),
	Operation(
		label="bFIOrMuDi",
		prepare=lambda update_list: FastIterOrderedMultiDict(get_long_list_common_keys(key_count=UPDATE_KEY_COUNT, values_count=UPDATE_VALUES_COUNT)),
		operation=lambda update_list, omd: omd.update_extend(update_list),
		check_prepared=lambda init_list, omd: _check_omd_size(UPDATE_VALUES_COUNT, len(omd.items(multi=True)))
	),
]}


COPY_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in [
	Operation(
		label="OrMuDi",
		prepare=lambda init_list: OrderedMultiDict(init_list),
		operation=lambda init_list, better_omd: better_omd.copy(),
		check_prepared=lambda init_list, better_omd: _check_omd_size(len(init_list), len(better_omd)),
		share_prepared=True
	),
	Operation(
		label="DeOrMuDi",
		prepare=lambda init_list: DeOrderedMultiDict(init_list),
		operation=lambda init_list, better_omd: better_omd.copy(),
		check_prepared=lambda init_list, better_omd: _check_omd_size(len(init_list), len(better_omd)),
		share_prepared=True
	),
	Operation(
		label="omdict",
		prepare=lambda init_list: omdict(init_list),
		operation=lambda init_list, omd: omd.copy(),
		check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), omd.size()),
		share_prepared=True
	),
	Operation(
		label="bOrMuDi",
		prepare=lambda init_list: BoltonOrderedMultiDict(init_list),
		operation=lambda init_list, omd: omd.copy(),
		check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), len(omd.items(multi=True))),
		share_prepared=True
	),
	Operation(
		label="bFIOrMuDi",
		prepare=lambda init_list: FastIterOrderedMultiDict(init_list),
		operation=lambda init_list, omd: omd.copy(),
		check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), len(omd.items(multi=True))),
		share_prepared=True
	),
]}


def pop_first_better_omd(init_list: list, better_omd: DeOrderedMultiDict):
	for _ in range(len(init_list)):
		better_omd.popfirstitem()


def pop_first_omdict(init_list: list, omd: omdict):
	for _ in range(len(init_list)):
		omd.popitem(True, False)


def pop_last_better_omd(init_list: list, better_omd: OrderedMultiDict):
	for _ in range(len(init_list)):
		better_omd.poplastitem()


def pop_last_omdict(init_list: list, omd: omdict):
	for _ in range(len(init_list)):
		omd.popitem(True, True)


def pop_last_bolton(init_list: list, omd: BoltonOrderedMultiDict):
	for k in omd.keys(multi=False):
		try:
			while True:
				omd.poplast(k)
		except KeyError:
			continue


def pop_last_bolton_fast_iter(init_list: list, omd: FastIterOrderedMultiDict):
	for k in omd.keys(multi=False):
		try:
			while True:
				omd.poplast(k)
		except KeyError:
			continue


POP_FIRST_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in [
	# Operation( too slow!
	# 	label="OrMuDi",
	# 	prepare=lambda init_list: OrderedMultiDict(init_list),
	# 	operation=pop_first_better_omd,
	# 	check_prepared=lambda init_list, better_omd: _check_omd_size(len(init_list), len(better_omd)),
	# 	share_prepared=False
	# ),
	Operation(
		label="DeOrMuDi",
		prepare=lambda init_list: DeOrderedMultiDict(init_list),
		operation=pop_first_better_omd,
		check_prepared=lambda init_list, better_omd: _check_omd_size(len(init_list), len(better_omd)),
		share_prepared=False
	),
	Operation(
		label="omdict",
		prepare=lambda init_list: omdict(init_list),
		operation=pop_first_omdict,
		check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), omd.size()),
		share_prepared=False
	),
]}


POP_LAST_OPS: dict[str, Operation[list, Any]] = {op.label: op for op in [
	Operation(
		label="OrMuDi",
		prepare=lambda init_list: OrderedMultiDict(init_list),
		operation=pop_last_better_omd,
		check_prepared=lambda init_list, better_omd: _check_omd_size(len(init_list), len(better_omd)),
		share_prepared=False
	),
	Operation(
		label="DeOrMuDi",
		prepare=lambda init_list: DeOrderedMultiDict(init_list),
		operation=pop_last_better_omd,
		check_prepared=lambda init_list, better_omd: _check_omd_size(len(init_list), len(better_omd)),
		share_prepared=False
	),
	Operation(
		label="omdict",
		prepare=lambda init_list: omdict(init_list),
		operation=pop_last_omdict,
		check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), omd.size()),
		share_prepared=False
	),
	Operation(
		label="bOrMuDi",
		prepare=lambda init_list: BoltonOrderedMultiDict(init_list),
		operation=pop_last_bolton,
		check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), len(omd.items(multi=True))),
		share_prepared=False
	),
	Operation(
		label="bFIOrMuDi",
		prepare=lambda init_list: FastIterOrderedMultiDict(init_list),
		operation=pop_last_bolton_fast_iter,
		check_prepared=lambda init_list, omd: _check_omd_size(len(init_list), len(omd.items(multi=True))),
		share_prepared=False
	),
]}

VALUES_COUNT = 5_000
KEY_COUNT = 100


def get_long_list():
	return [(i, i) for i in range(VALUES_COUNT)]


def get_long_list_common_keys(*, key_count: int = None, values_count: int = None):
	if key_count is None:
		key_count = KEY_COUNT
	if values_count is None:
		values_count = VALUES_COUNT
	return [(random.randint((values_count - key_count) // 2, (values_count + key_count) // 2), i) for i in range(values_count)]


def _get_speedup_percentage(t1: float, t2: float) -> str:
	return f"{t2 / t1 - 1:3.1%}" if t1 != 0 else "<i>NaN</i>"


def _get_speedup_factor(t1: float, t2: float) -> str:
	if t1 > t2:
		return f"<i>slower</i>"
	else:
		return f"{t2 / t1:1.1f}x" if t1 != 0 else "<i>NaN</i>"


def compare_format_results(results: dict[str, Result], format_val: Callable[[float], str], highlight_fastest: bool = False) -> dict[str, str]:
	results = list(results.items())
	if len(results) == 2:
		return {
			results[0][0]: f"{format_val(results[0][1].min_min)}",
			results[1][0]: f"{format_val(results[1][1].min_min)}",
			"speedup": _get_speedup_factor(results[0][1].min_min, results[1][1].min_min)
		}
	else:
		return {}


def run_the_tests[I](*, tests: dict[str, list[Operation[I, Any]]], inputs: list[tuple[str, I]], format_results: Callable[[dict[str, Result]], dict[str, str]], repetitions: int, outer_repetitions: int):
	result_tables = []
	for input_name, input in inputs:
		with print_action(input_name):
			results = run_tests(tests.items(), input, repetitions=repetitions, outer_repetitions=outer_repetitions)
			result = format_results_table(results, format_results, lambda label: LABELS.get(label, label))
			result_tables.append((input_name, result))
		print("")
	print("")

	for input_name, result in result_tables:
		print(f"{input_name}:")
		print("")
		print(result)
		print("")
		print("")
		

LABELS = {
	"OrMuDi": "OrderedMultiDict",
	"DeOrMuDi": "DeOrderedMultiDict",
	"omdict": "omdict",
	"bOrMuDi": "bolton </br>OrderedMultiDict",
	"bFIOrMuDi": "bolton </br>FastIterOrderedMultiDict",
}


TESTS: dict[str, dict[str, Operation[list, Any]]] = {
	"create": CREATE_DICT_OPS,
	"addall / addlist": ADD_ALL_OPS,
	"update / updateall<sup>1)</sup>": UPDATE_OPS,
	"extend / update_extend": EXTEND_OPS,
	"copy": COPY_OPS,
	"iterate over items": ITERATE_ITEMS_OPS,
	"iterate over values": ITERATE_VALUES_OPS,
	"iterate over keys": ITERATE_KEYS_OPS,
	"iterate over unique keys": ITERATE_UNIQUE_KEYS_OPS,
	"pop first item until empty": POP_FIRST_OPS,
	"pop last item until empty": POP_LAST_OPS,
}


def run():
	filter_test_to_run = [
		"OrMuDi",
		"DeOrMuDi",
		"omdict",
		"bOrMuDi",
		"bFIOrMuDi",
	]
	LONG_LIST = get_long_list()
	LONG_LIST_COMMON_KEYS = get_long_list_common_keys()
	inputs = [
		(f"Creating / iterating over dictionary with {VALUES_COUNT} entries with all keys being different", LONG_LIST),
		(f"Creating / iterating over dictionary with {VALUES_COUNT} entries, but only {KEY_COUNT} unique keys distributed randomly", LONG_LIST_COMMON_KEYS)
	]

	tests_to_run: dict[str, list[Operation[list[tuple[int, int]], Any]]] = {
		category_name: [tests[test_name] for test_name in filter_test_to_run if test_name in tests]
		for category_name, tests in TESTS.items()
	}

	run_the_tests(
		tests=tests_to_run,
		inputs=inputs,
		format_results=lambda results: default_format_results(results, format_result, highlight_fastest=True),
		repetitions=5,
		outer_repetitions=2
	)


if __name__ == '__main__':
	if len(sys.argv) > 1:
		VALUES_COUNT = int(sys.argv[1])
	run()
