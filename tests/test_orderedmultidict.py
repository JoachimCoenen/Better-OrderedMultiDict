from unittest import TestCase

from better_orderedmultidict import OrderedMultiDict


_unique = object()


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
			for items, omd in get_original_omds():
				omd.update(update)
				self.assertEqual(list(omd.items()), items + items_list(update))

		# init by OrderedMultiDict
		for update in self.list_updates:
			for items, omd in get_original_omds():
				omdUpdate = OrderedMultiDict(update)
				omd.update(omdUpdate)
				self.assertEqual(list(omd.items()), items + items_list(update))

		# Support **kwargs dictionary initialization.
		items = [('Herr Kules', 42158), ('Freitag', 648), ('jack', 65477)]
		updates = [items, dict(items), OrderedMultiDict(items)]
		kwargs = [('Donald', 1122), ('Freitag', 2900), ('Mr Banks', 0)]

		for update in updates:
			for items, omd in get_original_omds():
				omd.update(update, **dict(kwargs))
				self.assertEqual(list(omd.items()), items + items_list(update) + kwargs)

		for items, omd in get_original_omds():
			omd.update(**dict(kwargs))
			self.assertEqual(list(omd.items()), items + kwargs)
	def test_clear(self):
		for init in self.list_inits + self.dict_inits:
			omd = OrderedMultiDict(init)
			omd.clear()
			self.assertFalse(omd)

	def _test_get(self, getter, idx):
		for init in self.list_inits + self.dict_inits:
			omd = OrderedMultiDict(init)
			for key in omd.keys():
				self.assertEqual(getter(omd, key), omd.getall(key)[idx])
			for nonkey in self.nonkeys:
				self.assertIs(getter(omd, nonkey), None)
				self.assertEqual(getter(omd, nonkey, _unique), _unique)
				self.assertIs(getter(omd, nonkey, False), False)

	def test_getitem(self):
		for init in self.list_inits + self.dict_inits:
			omd = OrderedMultiDict(init)
			for key in omd.keys():
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
			for key in omd.keys():
				self.assertEqual(omd.getall(key), [v for k, v in init if k == key])
			for nonkey in self.nonkeys:
				self.assertEqual(omd.getall(nonkey), [])
				self.assertEqual(omd.getall(nonkey, _unique), _unique)
				self.assertIs(omd.getall(nonkey, False), False)
