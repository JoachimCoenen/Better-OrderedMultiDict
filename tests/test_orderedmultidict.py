from typing import Any, Callable
from unittest import TestCase

from better_orderedmultidict import OrderedMultiDict


_unique = object()
_unique_unused = object()


def items_list(a):
	if isinstance(a, list):
		return a
	return list(a.items())


class TestOrderedMultiDict(TestCase):

	def setUp(self):
		self.list_inits = [
			[], [(1, 1)], [(1, '1'), (2, 2)], [(1, 7), (2, 2), (1, 1)],
			[(1, 1), (1, 1), (1, '1')], [(None, None), (None, None)],
			[(False, True)],
			[(None, 1), (1, None), (None, None), (None, 1), (1, None)],
		]
		self.dict_inits = [
			{}, {1: 1}, {1: 1, 2: 2}, {None: None}, {False: False}, {None: 1, 1: None, 3: 5},
		]

		self.list_updates = [
			[], [(7, 7)], [(7, 7), (8, 8), (9, 9)], [(None, 'none')],
			[(9, 9), (1, 2)], [(7, 7), (7, 7), (8, 8), (7, 77)],
			[(1, 11), (1, 111), (1, 1111), (2, 22), (2, 222), ('a', 'a'), ('a', 'aa')],
		]
		self.dict_updates = [
			{}, {7: 7}, {7: 7, 8: 8, 9: 9}, {None: None}, {1: 1, 2: 2}, {None: 1, 1: None, 3: 5},
		]
		self.kw_updates = [
			{}, {'1': 1}, {'1': 1, '2': 2}, {'sup': 'innit?', 'Knuth': None}, {'aa': 'aa'},
		]
		self.nonkeys = [_unique, 'asdfasdosduf', 'oaisfiapsn', 'ioausopdaui']
		self.new_values = [1, 2, 3, None, 'a', 'omnibus', object()]
		self.new_values_lists = [
			[],
			[object(), "bonobo", "bat", 9, (-1)**.5, None],
			[object()],
			[None]
		]

	def test_init(self):
		# init by list & dicts
		for init in self.list_inits + self.dict_inits:
			omd = OrderedMultiDict(init)
			self.assertEqual(list(omd.items()), items_list(init))

		# init by OrderedMultiDict
		for init in self.list_inits:
			omd1 = OrderedMultiDict(init)
			omd2 = OrderedMultiDict(omd1)
			self.assertEqual(list(omd1.items()), list(omd2.items()))
			omd2.add(77, 3210)
			self.assertNotEqual(list(omd1.items()), list(omd2.items()))

		# Support **kwargs dictionary initialization.
		items = [('Herr Kules', 42158), ('Freitag', 648), ('jack', 65477)]
		inits = [items, dict(items), OrderedMultiDict(items)]
		kwargs = [('Donald', 1122), ('Freitag', 2900), ('Mr Banks', 0)]

		for init in inits:
			omd = OrderedMultiDict(init, **dict(kwargs))
			self.assertEqual(list(omd.items()), items_list(init) + kwargs)

		omd = OrderedMultiDict(**dict(kwargs))
		self.assertEqual(list(omd.items()), kwargs)

	def test_update(self):
		def get_original_omds():
			return [
				(items, OrderedMultiDict(items)) for items in [
					[], [(1, 1), (3, 1), (1, 4)], [(None, None), (None, None)], [(False, False)]
				]
			]

		# update by list & dicts
		for update in self.list_updates + self.dict_updates:
			new_items = items_list(update)
			update_keys = {key for key, _ in new_items}
			for items, omd in get_original_omds():
				omd.update(update)
				filtered_items = [item for item in items if item[0] not in update_keys]
				self.assertEqual(list(omd.items()), filtered_items + new_items)

		# update by OrderedMultiDict
		for update in self.list_updates:
			new_items = items_list(update)
			update_keys = {key for key, _ in new_items}
			for items, omd in get_original_omds():
				omdUpdate = OrderedMultiDict(update)
				omd.update(omdUpdate)
				filtered_items = [item for item in items if item[0] not in update_keys]
				self.assertEqual(list(omd.items()), filtered_items + new_items)

		# Support **kwargs dictionary initialization.
		items = [('Herr Kules', 42158), ('Freitag', 648), ('jack', 65477)]
		updates = [items, dict(items), OrderedMultiDict(items)]
		kwargs = [('Donald', 1122), ('Freitag', 2900), ('Mr Banks', 0)]

		for update in updates:
			new_items = items_list(update) + kwargs
			update_keys = {key for key, _ in new_items}
			for items, omd in get_original_omds():
				omd.update(update, **dict(kwargs))
				filtered_items = [item for item in items if item[0] not in update_keys]
				self.assertEqual(list(omd.items()), filtered_items + new_items)

		new_items = kwargs
		update_keys = {key for key, _ in new_items}
		for items, omd in get_original_omds():
			omd.update(**dict(kwargs))
			filtered_items = [item for item in items if item[0] not in update_keys]
			self.assertEqual(list(omd.items()), filtered_items + kwargs)

	def test_expand(self):
		def get_original_omds():
			return [
				(items, OrderedMultiDict(items)) for items in [
					[], [(1, 1), (3, 1), (1, 4)], [(None, None), (None, None)], [(False, False)]
				]
			]

		# update by list & dicts
		for update in self.list_updates + self.dict_updates:
			for items, omd in get_original_omds():
				omd.extend(update)
				self.assertEqual(list(omd.items()), items + items_list(update))

		# update by OrderedMultiDict
		for update in self.list_updates:
			for items, omd in get_original_omds():
				omdUpdate = OrderedMultiDict(update)
				omd.extend(omdUpdate)
				self.assertEqual(list(omd.items()), items + items_list(update))

		# Support **kwargs dictionary initialization.
		items = [('Herr Kules', 42158), ('Freitag', 648), ('jack', 65477)]
		updates = [items, dict(items), OrderedMultiDict(items)]
		kwargs = [('Donald', 1122), ('Freitag', 2900), ('Mr Banks', 0)]

		for update in updates:
			for items, omd in get_original_omds():
				omd.extend(update, **dict(kwargs))
				self.assertEqual(list(omd.items()), items + items_list(update) + kwargs)

		for items, omd in get_original_omds():
			omd.extend(**dict(kwargs))
			self.assertEqual(list(omd.items()), items + kwargs)
	def test_clear(self):
		for init in self.list_inits + self.dict_inits:
			omd = OrderedMultiDict(init)
			omd.clear()
			self.assertFalse(omd)

	def _test_get(self, getter, idx):
		for init in self.list_inits + self.dict_inits:
			omd = OrderedMultiDict(init)
			for key in omd.unique_keys():
				self.assertEqual(getter(omd, key), omd.getall(key)[idx])
			for nonkey in self.nonkeys:
				self.assertIs(getter(omd, nonkey), None)
				self.assertEqual(getter(omd, nonkey, _unique), _unique)
				self.assertIs(getter(omd, nonkey, False), False)

	def test___getitem__(self):
		for init in self.list_inits + self.dict_inits:
			omd = OrderedMultiDict(init)
			for key in omd.unique_keys():
				self.assertEqual(omd[key], omd[key])
				self.assertEqual(omd[key], omd.getall(key)[-1])
			for nonkey in self.nonkeys:
				self.assertRaises(KeyError, lambda: omd[nonkey])

	def test_get(self):
		self._test_get(OrderedMultiDict.get, -1)

	def test_getfirst(self):
		self._test_get(OrderedMultiDict.getfirst, +0)

	def test_getlast(self):
		self._test_get(OrderedMultiDict.getlast, -1)

	def test_getall(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			for key in omd.unique_keys():
				self.assertEqual(omd.getall(key), [v for k, v in init if k == key])
			for nonkey in self.nonkeys:
				self.assertEqual(omd.getall(nonkey), [])
				self.assertEqual(omd.getall(nonkey, _unique), _unique)
				self.assertIs(omd.getall(nonkey, False), False)

	def test_setdefault(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			for key in omd.unique_keys():
				old_values = list(omd.getall(key))
				value = old_values[-1]
				self.assertEqual(omd.setdefault(key, default=_unique_unused), value)
				self.assertEqual(omd.getall(key), old_values)  # no change to dict
			omd = OrderedMultiDict(init)  # re-init the omd, so we have a fresh one
			for nonkey in self.nonkeys:
				self.assertEqual(omd.setdefault(nonkey, default=_unique), _unique)
				self.assertEqual(omd.getall(nonkey), [_unique])  # yes change to dict

	def test_setdefaultall(self):
		for defaultlist in self.new_values_lists:
			for init in self.list_inits:
				omd = OrderedMultiDict(init)
				for key in omd.unique_keys():
					old_values = list(omd.getall(key))
					self.assertEqual(omd.setdefaultall(key, defaultlist=defaultlist), old_values)
					self.assertEqual(omd.getall(key), old_values)  # no change to dict
				omd = OrderedMultiDict(init)  # re-init the omd, so we have a fresh one
				for nonkey in self.nonkeys:
					self.assertEqual(omd.setdefaultall(nonkey, defaultlist=defaultlist), defaultlist)
					self.assertEqual(omd.getall(nonkey), defaultlist)  # yes change to dict

	def test_setall(self):
		for new_values in self.new_values_lists:
			for init in self.list_inits:
				omd = OrderedMultiDict(init)
				for key in omd.unique_keys():
					omd.setall(key, new_values)
					self.assertEqual(omd.getall(key), new_values)
				omd = OrderedMultiDict(init)  # re-init the omd, so we have a fresh one
				for nonkey in self.nonkeys:
					omd.setall(nonkey, new_values)
					self.assertEqual(omd.getall(nonkey), new_values)

	def test_add(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			for key in omd.unique_keys():
				all_old_values = list(omd.values())
				old_values = list(omd.getall(key))
				omd.add(key, "bat mobil")
				self.assertEqual(omd[key], "bat mobil")
				self.assertEqual(omd.getall(key), old_values + ["bat mobil"])
				self.assertEqual(list(omd.values()), all_old_values + ["bat mobil"])
			omd = OrderedMultiDict(init)  # re-init the omd, so we have a fresh one
			for nonkey in self.nonkeys:
				all_old_values = list(omd.values())
				omd.add(nonkey, "bat mobil")
				self.assertEqual(omd.getall(nonkey), ["bat mobil"])
				self.assertEqual(list(omd.values()), all_old_values + ["bat mobil"])

	def test_addall(self):
		for new_values in self.new_values_lists:
			for init in self.list_inits:
				omd = OrderedMultiDict(init)
				for key in omd.unique_keys():
					all_old_values = list(omd.values())
					old_values = list(omd.getall(key))
					omd.addall(key, new_values)
					self.assertEqual(omd.getall(key), old_values + new_values)
					self.assertEqual(list(omd.values()), all_old_values + new_values)
				omd = OrderedMultiDict(init)  # re-init the omd, so we have a fresh one
				for nonkey in self.nonkeys:
					all_old_values = list(omd.values())
					omd.addall(nonkey, new_values)
					self.assertEqual(omd.getall(nonkey), new_values)
					self.assertEqual(list(omd.values()), all_old_values + new_values)

	def test_popall_with_default(self):
		#
		for new_values in self.new_values_lists + self.new_values:
			for init in self.list_inits:
				omd = OrderedMultiDict(init)
				for key in omd.unique_keys():
					all_keys = list(omd.keys())
					old_values = list(omd.getall(key))
					self.assertEqual(omd.popall(key, default=new_values), old_values)
					self.assertEqual(list(omd.keys()), [k for k in all_keys if k != key])
				omd = OrderedMultiDict(init)  # re-init the omd, so we have a fresh one
				for nonkey in self.nonkeys:
					all_keys = list(omd.keys())
					self.assertEqual(omd.popall(nonkey, default=new_values), new_values)
					self.assertEqual(list(omd.keys()), all_keys)

	def test_popall_without_default(self):
		for new_values in self.new_values_lists + self.new_values:
			for init in self.list_inits:
				omd = OrderedMultiDict(init)
				for key in omd.unique_keys():
					all_keys = list(omd.keys())
					old_values = list(omd.getall(key))
					self.assertEqual(omd.popall(key), old_values)
					self.assertEqual(list(omd.keys()), [k for k in all_keys if k != key])
				omd = OrderedMultiDict(init)  # re-init the omd, so we have a fresh one
				for nonkey in self.nonkeys:
					all_keys = list(omd.keys())
					self.assertRaises(KeyError, lambda: omd.popall(nonkey))
					self.assertEqual(list(omd.keys()), all_keys)

	def test_popfirstitem_with_default(self):
		for new_value in self.new_values:
			for init in self.list_inits:
				omd = OrderedMultiDict(init)
				if init:
					self.assertEqual(omd.popfirstitem(), init[0])
					self.assertEqual(list(omd.items()), init[1:])
				else:
					self.assertEqual(omd.popfirstitem(default=new_value), new_value)

	def test_popfirstitem_without_default(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			if init:
				self.assertEqual(omd.popfirstitem(), init[0])
				self.assertEqual(list(omd.items()), init[1:])
			else:
				self.assertRaises(KeyError, lambda: omd.popfirstitem())

	def test_poplastitem_with_default(self):
		for new_value in self.new_values:
			for init in self.list_inits:
				omd = OrderedMultiDict(init)
				if init:
					self.assertEqual(omd.poplastitem(), init[-1])
					self.assertEqual(list(omd.items()), init[:-1])
				else:
					self.assertEqual(omd.poplastitem(default=new_value), new_value)

	def test_poplastitem_without_default(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			if init:
				self.assertEqual(omd.poplastitem(), init[-1])
				self.assertEqual(list(omd.items()), init[:-1])
			else:
				self.assertRaises(KeyError, lambda: omd.poplastitem())

	def test_popfirst_with_default(self):
		for new_value in self.new_values:
			self._test_pop(lambda omd, key: omd.popfirst(key, default=new_value), 0, slice(1, None), default=new_value)

	def test_popfirst_without_default(self):
			self._test_pop(lambda omd, key: omd.popfirst(key), 0, slice(1, None))

	def test_poplast_with_default(self):
		for new_value in self.new_values:
			self._test_pop(lambda omd, key: omd.poplast(key, default=new_value), -1, slice(None, -1), default=new_value)

	def test_poplast_without_default(self):
		self._test_pop(lambda omd, key: omd.poplast(key), -1, slice(None, -1))

	def test_pop_with_default(self):  # same as poplast()
		for new_value in self.new_values:
			self._test_pop(lambda omd, key: omd.pop(key, default=new_value), -1, slice(None, -1), default=new_value)

	def test_pop_without_default(self):  # same as poplast()
		self._test_pop(lambda omd, key: omd.pop(key), -1, slice(None, -1))

	_SENTINEL = object

	def _test_pop(self, pop_func: Callable[[OrderedMultiDict, Any], Any], popped_idx: int, remaining_slice: slice, *, default: Any=_SENTINEL):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			for key in omd.unique_keys():
				old_values = list(omd.getall(key))
				self.assertEqual(pop_func(omd, key), old_values[popped_idx])
				self.assertEqual(omd.getall(key), old_values[remaining_slice])
				# todo test ordering of all
			omd = OrderedMultiDict(init)  # re-init the omd, so we have a fresh one
			for nonkey in self.nonkeys:
				all_old_values = list(omd.values())
				if default is self._SENTINEL:
					self.assertRaises(KeyError, lambda: pop_func(omd, nonkey))
				else:
					self.assertEqual(pop_func(omd, nonkey), default)
				self.assertEqual(list(omd.values()), all_old_values)

	def delete_all(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			for key in omd.unique_keys():
				all_keys = list(omd.keys())
				omd.delete_all(key)
				self.assertEqual(omd.getall(key), [])
				self.assertEqual(list(omd.keys()), [k for k in all_keys if k != key])
			omd = OrderedMultiDict(init)  # re-init the omd, so we have a fresh one
			for nonkey in self.nonkeys:
				all_keys = list(omd.keys())
				omd.delete_all(nonkey)
				self.assertEqual(list(omd.keys()), all_keys)

	def test_items(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			self.assertEqual(list(omd.items()), init)

	def test_keys(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			self.assertEqual(list(omd.keys()), [item[0] for item in init])

	def test_unique_keys(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			self.assertEqual(list(omd.unique_keys()), list(dict(init).keys()))

	def test_values(self):
		for init in self.list_inits:
			omd = OrderedMultiDict(init)
			self.assertEqual(list(omd.values()), [item[1] for item in init])
