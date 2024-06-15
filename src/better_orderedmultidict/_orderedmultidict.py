from __future__ import annotations

from collections import deque, defaultdict
from operator import eq, itemgetter
from typing import Any, Hashable, Iterable, Iterator, Optional, Protocol, Self, overload, Union, MutableMapping


_BUGREPORT_MSG: str = "Please file a bugreport if ypu have not fiddled with any internal fields or methods of OrderedMultiDict."
_DESYNCED_ERROR_MSG: str = f"OrderedMultiDict._items and OrderedMultiDict._map have de-synced. {_BUGREPORT_MSG}"
_EMPTY_DEQUE_ERROR_MSG: str = f"OrderedMultiDict._map contained an empty deque. OrderedMultiDict._items and OrderedMultiDict._map might have de-synced. {_BUGREPORT_MSG}"

_SENTINEL = object()
_SENTINEL2 = object()


class _SupportsKeysAndGetItem[TK: Hashable, TV](Protocol):
	def keys(self) -> Iterable[TK]: ...
	def __getitem__(self, __key: TK) -> TV: ...


def _pop_first[TK: Hashable, TV](d: dict[TK, TV]) -> tuple[TK, TV]:
	return (k := next(iter(d)), d.pop(k))


def _pop_last[TK: Hashable, TV](d: dict[TK, TV]) -> tuple[TK, TV]:
	return d.popitem()


def _iter_keys[TK](values: Iterable[tuple[TK, Any]]) -> Iterator[TK]:
	return map(itemgetter(0), values)


def _iter_values[TV](values: Iterable[tuple[Any, TV]]) -> Iterator[TV]:
	return map(itemgetter(1), values)


class OrderedMultiDict[TK: Hashable, TV](MutableMapping[TK, TV]):
	
	@overload
	def __init__(self) -> None: ...
	@overload
	def __init__(self, __map: _SupportsKeysAndGetItem[TK, TV], /) -> None: ...
	@overload
	def __init__(self, __iterable: Iterable[tuple[TK, TV]], /) -> None: ...
	@overload
	def __init__(self: OrderedMultiDict[str, TV], /, **kwargs: TV) -> None: ...
	@overload
	def __init__(self: OrderedMultiDict[str, TV], /, __map: _SupportsKeysAndGetItem[str, TV], **kwargs: TV) -> None: ...
	@overload
	def __init__(self: OrderedMultiDict[str, TV], /, __iterable: Iterable[tuple[str, TV]], **kwargs: TV) -> None: ...

	# Next two overloads are for OrderedMultiDict(string.split(sep) for string in iterable)
	# Cannot be Iterable[Sequence[_T]] or otherwise dict(["foo", "bar", "baz"]) is not an error
	@overload
	def __init__(self: OrderedMultiDict[str, str], __iterable: Iterable[list[str]], /) -> None: ...
	@overload
	def __init__(self: OrderedMultiDict[bytes, bytes], __iterable: Iterable[list[bytes]], /) -> None: ...

	def __init__(self, iterable_or_map: Iterable[tuple[TK, TV]] | _SupportsKeysAndGetItem[TK, TV] = _SENTINEL, /, **kwargs: TV):
		self._items: dict[int, tuple[TK, TV]] = {}
		self._map: defaultdict[TK, deque[tuple[int, TV]]] = defaultdict(deque)
		self._index: int = 0

		if iterable_or_map is not _SENTINEL:
			self._load(iterable_or_map)
		if kwargs:
			self._extend_fast(kwargs.items())

	def _load(self, iterable_or_map: Iterable[tuple[TK, TV]] | _SupportsKeysAndGetItem[TK, TV]):
		"""
		Clear all existing key:value items and import all key:value items from
		<mapping>. If multiple values exist for the same key in <mapping>, they
		are all be imported.
		"""
		if isinstance(iterable_or_map, OrderedMultiDict):
			self._copy_from(iterable_or_map)  # special case
		else:
			self.clear()
			self._extend(iterable_or_map)

	@overload
	def update(self, __m: _SupportsKeysAndGetItem[TK, TV], /) -> None: ...
	@overload
	def update(self, __m: Iterable[tuple[TK, TV]], /) -> None: ...
	@overload
	def update(self: OrderedMultiDict[str, TV], /, **kwargs: TV) -> None: ...
	@overload
	def update(self: OrderedMultiDict[str, TV], __m: _SupportsKeysAndGetItem[str, TV], /, **kwargs: TV) -> None: ...
	@overload
	def update(self: OrderedMultiDict[str, TV], __m: Iterable[tuple[str, TV]], /, **kwargs: TV) -> None: ...

	def update(self, iterable_or_map: Iterable[tuple[TK, TV]] | _SupportsKeysAndGetItem[TK, TV] = _SENTINEL, /, **kwargs: TV):
		"""
		Clear all existing key:value entries that have a key which is present in <iterable_or_map>. And then import all
		key:value items from <iterable_or_map>. If multiple values exist for the same key in <mapping>, they are all
		imported. Keys that are not present in <iterable_or_map> are not touched.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3)])
			>>> omd.update([(1, '1'), (3, '3'), (1, '11')])
			>>> print(omd.items())    # _ItemsView([(2, 2), (2, 22), (1, '1'), (3, '3'), (1, '11')])
		"""

		if iterable_or_map is not _SENTINEL:
			self._try_telete_all_keys(iterable_or_map)
		if kwargs:
			self._try_telete_all_keys(kwargs)

		self.extend(iterable_or_map, **kwargs)

	def _try_telete_all_keys(self, iterable_or_map: Iterable[tuple[TK, TV]] | _SupportsKeysAndGetItem[TK, TV]):
		if hasattr(iterable_or_map, 'keys'):
			for k in iterable_or_map.keys():
				self._try_delete_all(k)
		elif hasattr(iterable_or_map, 'items'):
			for k in dict.fromkeys(_iter_keys(iterable_or_map.items)):
				self._try_delete_all(k)
		else:
			for k in dict.fromkeys(_iter_keys(iterable_or_map)):
				self._try_delete_all(k)

	@overload
	def extend(self, __m: _SupportsKeysAndGetItem[TK, TV], /) -> None: ...
	@overload
	def extend(self, __m: Iterable[tuple[TK, TV]], /) -> None: ...
	@overload
	def extend(self: OrderedMultiDict[str, TV], /, **kwargs: TV) -> None: ...
	@overload
	def extend(self: OrderedMultiDict[str, TV], __m: _SupportsKeysAndGetItem[str, TV], /, **kwargs: TV) -> None: ...
	@overload
	def extend(self: OrderedMultiDict[str, TV], __m: Iterable[tuple[str, TV]], /, **kwargs: TV) -> None: ...

	def extend(self, iterable_or_map: Iterable[tuple[TK, TV]] | _SupportsKeysAndGetItem[TK, TV] = _SENTINEL, /, **kwargs: TV):
		"""
		Adds all key:value items from <iterable_or_map>. If multiple values exist for the same key in <mapping>, they are all
		imported.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3)])
			>>> omd.extend([(1, '1'), (3, '3'), (1, '11'), )   # list(omd.items()) == [(1,1)]
			>>> print(omd.items())    # _ItemsView([(1,1), (2,2), (1,11), (2, 22), (3,3), (1, '1'), (3, '3'), (1, '11')])
		"""
		if iterable_or_map is not _SENTINEL:
			self._extend(iterable_or_map)
		if kwargs:
			self._extend(kwargs)

	def _extend(self, iterable_or_map: Iterable[tuple[TK, TV]] | _SupportsKeysAndGetItem[TK, TV]):
		if hasattr(iterable_or_map, 'items'):
			self._extend_fast(iterable_or_map.items())
		elif hasattr(iterable_or_map, 'keys'):
			for k, in iterable_or_map.keys():
				self.add(k, iterable_or_map[k])
		elif hasattr(iterable_or_map, '__len__'):
			self._extend_fast(iterable_or_map)
		else:
			self._extend_slow(iterable_or_map)

	def _extend_fast(self, items) -> None:
		index: int = self._index
		self._index += len(items)
		self._items.update(enumerate(items, index))

		s_map = self._map
		for it0, it1 in items:
			s_map[it0].append((index, it1))  # entry in _map is created here if necessary, because _map is a defaultdict
			index += 1

	def _extend_slow(self, items) -> None:
		index: int = self._index

		s_map = self._map
		s_items = self._items
		try:
			for item in items:
				# Split herre, so we are sure that item can be split into exactly two items,
				# before we start to update any internal state. This avoids leaving the
				# OrderedMultiDict in an invalid state if item cannot be split.
				k, v = item
				# entry in _map is created here if necessary, because _map is a defaultdict
				s_map[k].append((index, v))
				s_items[index] = item
				index += 1
		finally:
			self._index = index

	def _copy_from(self, others: OrderedMultiDict[TK, TV]) -> Self:
		self._items = others._items.copy()
		self._index = others._index
		self._map = defaultdict(deque, {key: que.copy() for key, que in others._map.items()})
		return self

	def copy(self) -> OrderedMultiDict[TK, TV]:
		return type(self)()._copy_from(self)

	def clear(self):
		self._map.clear()  # important! clear _map first!!
		self._items.clear()
		self._index = 0

	def _get_all_or_none(self, key: TK) -> Optional[deque[tuple[int, TV]]]:
		result = self._map.get(key)
		if result is not None:  # if key in self:
			assert result, _EMPTY_DEQUE_ERROR_MSG  # result must not be empty!
			return result
		else:
			return None

	def get[TT](self, key: TK, default: TT = None) -> TV | TT:
		""" same as getlast(...)
		"""
		if (values := self._get_all_or_none(key)) is not None:  # if key in self:
			return values[-1][1]
		return default

	def getfirst[TT](self, key, default: TT = None) -> TV | TT:
		if (values := self._get_all_or_none(key)) is not None:  # if key in self:
			return values[0][1]
		return default

	def getlast[TT](self, key: TK, default: TT = None) -> TV | TT:
		""" same as get(...)
		"""
		if (values := self._get_all_or_none(key)) is not None:  # if key in self:
			return values[-1][1]
		return default

	@overload
	def getall(self, key: TK) -> list[TV]:
		"""
		Returns: The list of values for <key> if <key> is in the dictionary,
		else <default>. If <default> is not provided, an empty list is
		returned.
		"""
		...

	@overload
	def getall[TT](self, key: TK, default: TT) -> list[TV] | TT:
		"""
		Returns: The list of values for <key> if <key> is in the dictionary,
		else <default>. If <default> is not provided, an empty list is
		returned.
		"""
		...

	def getall[TT](self, key: TK, default: TT = _SENTINEL) -> list[TV] | TT:
		"""
		Returns: The list of values for <key> if <key> is in the dictionary,
		else <default>. If <default> is not provided, an empty list is
		returned.
		"""
		if (values := self._get_all_or_none(key)) is not None:  # if key in self:
			return [v[1] for v in values]
		elif default is _SENTINEL:
			return []
		else:
			return default

	def setdefault(self, key: TK, /, default: TV) -> TV:
		if (values := self._get_all_or_none(key)) is not None:  # if key in self:
			return values[-1][1]
		self.add(key, default)
		return default

	def setdefaultall(self, key: TK, defaultlist: list[TV]) -> list[TV]:
		"""
		Similar to setdefault() except <defaultlist> is a list of values to set
		for <key>. If <key> already exists, its existing list of values is
		returned.

		If <key> isn't a key and <defaultlist> is an empty list, [], no values
		are added for <key> and <key> will not be added as a key.

		Returns: List of <key>'s values if <key> exists in the dictionary,
		otherwise <defaultlist>.
		"""
		if (values := self.getall(key, _SENTINEL2)) is not _SENTINEL2:
			return values
		self.addall(key, defaultlist)
		return defaultlist

	def setall(self, key: TK, value_list: list[TV]) -> None:
		self._try_delete_all(key)
		self.addall(key, value_list)

	def add(self, key: TK, value: TV) -> None:
		"""
		Add <value> to the list of values for <key>. If <key> is not in the
		dictionary, then <value> is added as the sole value for <key>.

		Example:
			>>> omd = OrderedMultiDict()
			>>> omd.add(1, 1)   # list(omd.items()) == [(1,1)]
			>>> omd.add(1, 11)  # list(omd.items()) == [(1,1), (1,11)]
			>>> omd.add(2, 2)   # list(omd.items()) == [(1,1), (1,11), (2,2)]
			>>> omd.add(1, 111) # list(omd.items()) == [(1,1), (1,11), (2,2), (1, 111)]

		Returns: <self>.
		"""
		index: int = self._index
		self._index += 1

		# entry in _map is created here if necessary, because _map is a defaultdict:
		self._map[key].append((index, value))
		self._items[index] = (key, value)

	def addall(self, key: TK, value_list: list[TV]) -> None:
		"""
		Add the values in <valueList> to the list of values for <key>. If <key>
		is not in the dictionary, the values in <valueList> become the values
		for <key>.

		Example:
			>>> omd: OrderedMultiDict[int, int | str] = OrderedMultiDict([(1,1)])
			>>> omd.addall(1, [11, 111]) # list(omd.items()) == [(1, 1), (1, 11), (1, 111)]
			>>> omd.addall(2, [2])       # list(omd.items()) == [(1, 1), (1, 11), (1, 111), (2, 2)]
			>>> omd.addall(1, ['one'])   # list(omd.items()) == [(1, 1), (1, 11), (1, 111), (2, 2), (1, 'one')]

		Returns: <self>.
		"""
		if not value_list:
			return
		index: int = self._index
		self._index += len(value_list)
		self._map[key].extend(enumerate(value_list, index))

		items = self._items
		for value in value_list:
			items[index] = (key, value)
			index += 1

	@overload
	def popall(self, key: TK, /) -> Union[list[TV]]:
		"""
		If <key> is in the dictionary, pop it and return its list of values. If
		<key> is not in the dictionary, return <default>. KeyError is raised if
		<default> is not provided and <key> is not in the dictionary.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3), (1,111)])
			>>> print(omd.popall(2))  # [2, 22]
			>>> print(omd.items())    # _ItemsView([(1, 1), (1, 11), (3,3), (1, 111)])
			>>> print(omd.popall(1))  # [1, 11, 111]
			>>> print(omd.items())    # _ItemsView([(3,3)])
			>>> omd.popall(1)         # raises KeyError

		Raises: KeyError if <key> is absent in the dictionary and <default> isn't
			provided.
		Returns: List of <key>'s values.
		"""
		...

	@overload
	def popall[TT](self, key: TK, /, default: TT) -> list[TV] | TT:
		"""
		If <key> is in the dictionary, pop it and return its list of values. If
		<key> is not in the dictionary, return <default>. KeyError is raised if
		<default> is not provided and <key> is not in the dictionary.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3), (1,111)])
			>>> print(omd.popall(2, None))  # [2, 22]
			>>> print(omd.items())          # _ItemsView([(1, 1), (1, 11), (3,3), (1, 111)])
			>>> print(omd.popall(1, None))  # [1, 11, 111]
			>>> print(omd.items())          # _ItemsView([(3,3)])
			>>> print(omd.popall(1, None))  # None

		Raises: KeyError if <key> is absent in the dictionary and <default> isn't
			provided.
		Returns: List of <key>'s values.
		"""
		...

	def popall[TT](self, key: TK, /, default: TT = _SENTINEL) -> list[TV] | TT:
		"""
		If <key> is in the dictionary, pop it and return its list of values. If
		<key> is not in the dictionary, return <default>. KeyError is raised if
		<default> is not provided and <key> is not in the dictionary.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3), (1,111)])
			>>> print(omd.popall(2))  # [2, 22]
			>>> print(omd.items())    # _ItemsView([(1, 1), (1, 11), (3,3), (1, 111)])
			>>> print(omd.popall(1))  # [1, 11, 111]
			>>> print(omd.items())    # _ItemsView([(3,3)])

		Raises: KeyError if <key> is absent in the dictionary and <default> isn't
			provided.
		Returns: List of <key>'s values.
		"""
		if (values := self._get_all_or_none(key)) is not None:  # if key in self:
			# we might be able to improve performance a little bit here...
			result = []
			for val in values:
				result.append(val[1])
				del self._items[val[0]]
			del self._map[key]
			return result
		elif default is not _SENTINEL:
			return default
		raise KeyError(key)

	@overload
	def popfirstitem(self) -> tuple[TK, TV]:
		""" """
		...

	@overload
	def popfirstitem[TT](self, *, default: TT) -> tuple[TK, TV] | TT:
		""" """
		...

	def popfirstitem[TT](self, *, default: TT = _SENTINEL) -> tuple[TK, TV] | TT:
		return self._popitem(default, last=False)

	@overload
	def poplastitem(self) -> tuple[TK, TV]:
		""" """
		...

	@overload
	def poplastitem[TT](self, *, default: TT) -> tuple[TK, TV] | TT:
		""" """
		...

	def poplastitem[TT](self, *, default: TT = _SENTINEL) -> tuple[TK, TV] | TT:
		return self._popitem(default, last=True)

	def _popitem[TT](self, default: TT, *, last: bool) -> tuple[TK, TV] | TT:
		try:
			item = (_pop_last(self._items) if last else _pop_first(self._items))[1]
		except (StopIteration, KeyError):
			if default is not _SENTINEL:
				return default
			raise KeyError("dictionary is empty") from None

		values = self._get_all_or_none(item[0])
		assert values is not None, _DESYNCED_ERROR_MSG

		popped = values.pop() if last else values.popleft()
		if not values:
			del self._map[item[0]]

		assert popped[1] is item[1], _DESYNCED_ERROR_MSG
		return item

	@overload
	def popfirst(self, key: TK, /) -> TV:
		"""
		Raises: KeyError if <key> is absent.
		"""
		pass

	@overload
	def popfirst[TT](self, key: TK, /, default: TT) -> TV | TT:
		"""
		returns default if <key> is absent.
		"""
		pass

	def popfirst[TT](self, key: TK, /, default: TT = _SENTINEL) -> TV | TT:
		return self._pop(key, default, last=False)

	@overload
	def poplast(self, key: TK, /) -> TV:
		"""

		Raises: KeyError if <key> is absent.
		"""
		pass

	@overload
	def poplast[TT](self, key: TK, /, default: TT) -> TV | TT:
		"""
		returns default if <key> is absent.
		"""
		pass

	def poplast[TT](self, key: TK, /, default: TT = _SENTINEL) -> TV | TT:
		"""
		"same as .pop(...)"
		"""
		return self._pop(key, default, last=True)

	@overload
	def pop(self, key: TK, /) -> TV: ...
	@overload
	def pop(self, key: TK, /, default: TV) -> TV: ...
	@overload
	def pop[TT](self, key: TK, /, default: TT) -> TV | TT: ...

	def pop[TT](self, key: TK, /, default: TT = _SENTINEL) -> TV | TT:
		return self._pop(key, default, last=True)

	def _pop[TT](self, key: TK, default: TT, *, last: bool) -> TV | TT:
		if (values := self._get_all_or_none(key)) is not None:  # if key in self:
			popped = values.pop() if last else values.popleft()
			assert popped[0] in self._items, _DESYNCED_ERROR_MSG
			del self._items[popped[0]]
			if not values:
				del self._map[key]
			return popped[1]
		elif default is not _SENTINEL:
			return default
		raise KeyError(key)

	def delete_all(self, key: TK) -> None:
		"""
		Removes all entries for key. Raises a KeyError if key is not in the dictionary.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3), (1,111)])
			>>> omd.delete_all(1)
			>>> print(omd.items())  # _ItemsView([(2,2), (3,3)])
			>>> omd.delete_all(99)  # raises KeyError
		"""
		if not self._try_delete_all(key):
			raise KeyError(key)

	def _try_delete_all(self, key: TK) -> bool:
		"""
		Removes all entries for key.
		Returns True if key was in the dictionary, otherwise False.
		"""
		if (values := self._get_all_or_none(key)) is not None:  # if key in self:
			for val in values:
				del self._items[val[0]]
			del self._map[key]
			return True
		else:
			return False

	def items(self) -> _ItemsView[TK, TV]:
		"""
		Returns: An ItemsView of all (key, value) pairs in insertion order.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3), (1,111)])
			>>> print(omd.items())  # _ItemsView([(1,1), (2,2), (1,11), (2, 22), (3,3), (1,111)])
		"""
		return _ItemsView(self)

	def keys(self) -> _KeysView[TK, TV]:
		"""
		Returns: A KeysView of all keys in insertion order. Keys can appear multiple times.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3), (1,111)])
			>>> print(omd.keys())  # _KeysView([1, 2, 1, 2, 3, 1])
		"""
		return _KeysView(self)

	def unique_keys(self) -> _UniqueKeysView[TK, TV]:
		"""
		Returns: A KeysView of all unique keys in order of first appearance. Keys only appear once.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3), (1,111)])
			>>> print(omd.unique_keys())  # _UniqueKeysView([1, 2, 3])
		"""
		return _UniqueKeysView(self)

	def values(self) -> _ValuesView[TV, TV]:
		"""
		Returns: A ValuesView of all values in insertion order.

		Example:
			>>> omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3), (1,111)])
			>>> print(omd.values())  # _ValuesView([1, 2, 11, 22, 3, 111])
		"""
		return _ValuesView(self)

	# def sort(self, *, key: Optional[Callable[[tuple[TK, TV]], Any]] = None, reverse: bool = False):
	# 	self._items = dict(enumerate(sorted(self._items.values(), key=key, reverse=reverse)))
	# 	todo: update self._map
	# 	self._index = len(self._items)

	def contains_item(self, key: TK, value: TV) -> bool:
		if (values := self._get_all_or_none(key)) is not None:
			return value in _iter_values(values)
		return False

	def contains_value(self, value: TV) -> bool:
		# the same implementation as in _ValuesView.__contains__()
		return value in _iter_values(self._items.values())

	def __eq__(self, other) -> bool:
		if type(self) is not type(other):
			return NotImplemented
		if len(self) != len(other):
			return False
		return all(map(eq, self._items.values(), other._items.values()))

	def __ne__(self, other) -> bool:
		return not self.__eq__(other)

	def __len__(self) -> int:
		return len(self._items)

	def __iter__(self) -> Iterator[TK]:
		return iter(self.keys())

	def __contains__(self, key: TK) -> bool:
		return self._map.__contains__(key)

	def __getitem__(self, key: TK) -> TV:
		if (values := self._get_all_or_none(key)) is not None:  # if key in self:
			return values[-1][1]
		raise KeyError(key)

	def __setitem__(self, key: TK, value: TV) -> None:
		self.setall(key, [value])

	def __delitem__(self, key: TK) -> None:
		self.pop(key)

	def __bool__(self) -> bool:
		return bool(self._map)

	def __str__(self) -> str:
		return '{%s}' % ', '.join(f'{repr(p[0])}: {repr(p[1])}' for p in self._items.values())

	def __repr__(self) -> str:
		return f'{self.__class__.__name__}({list(self._items.values())!r})'

	def __getstate__(self) -> list[tuple[TK, TV]]:
		return list(self._items.values())

	def __setstate__(self, state: list[tuple[TK, TV]]):  # (self, TK, List[Tuple[TK, TV]])
		self._load(state)


class _ViewBase[TK: Hashable, TV]:

	def __init__(self, impl: OrderedMultiDict[TK, TV]):
		self._impl: OrderedMultiDict[TK, TV] = impl
		self._items = impl._items.values()

	def __len__(self):
		return self._items.__len__()

	def __iter__(self) -> Iterator[Any]:
		raise NotImplementedError(f"{type(self).__name__}.__iter__()")

	def __reversed__(self) -> Iterator[Any]:
		raise NotImplementedError(f"{type(self).__name__}.__reversed__()")

	def __repr__(self):
		return f'{type(self).__name__}({list(self)})'


class _ItemsView[TK: Hashable, TV](_ViewBase[TK, TV]):

	def __init__(self, impl: OrderedMultiDict[TK, TV]):
		super().__init__(impl)

	def __contains__(self, item: tuple[TK, TV]) -> bool:
		if not isinstance(item, tuple) or len(item) != 2:
			return False
		return self._impl.contains_item(*item)

	def __iter__(self) -> Iterator[tuple[TK, TV]]:
		return iter(self._items)

	def __reversed__(self) -> Iterator[tuple[TK, TV]]:
		return reversed(self._items)


class _ValuesView[TV](_ViewBase[Any, TV]):

	def __contains__(self, value: TV) -> bool:
		return value in _iter_values(self._items)

	def __iter__(self) -> Iterator[TV]:
		return _iter_values(self._items)

	def __reversed__(self) -> Iterator[TV]:
		return _iter_values(reversed(self._items))


class _KeysView[TK: Hashable](_ViewBase[TK, Any]):

	def __contains__(self, key: TK) -> bool:
		return self._impl.__contains__(key)

	def __iter__(self) -> Iterator[TK]:
		return _iter_keys(self._items)

	def __reversed__(self) -> Iterator[TK]:
		return _iter_keys(reversed(self._items))


class _UniqueKeysView[TK: Hashable](_ViewBase[TK, Any]):

	def __contains__(self, key: TK) -> bool:
		return self._impl.__contains__(key)

	def __iter__(self) -> Iterator[TK]:
		# we cannot iterate over self._impl._map, because its order might not be up-to-date.
		return iter(dict.fromkeys(_iter_keys(self._items)))

	def __reversed__(self) -> Iterator[TK]:
		# we cannot iterate over self._impl._map, because its order might not be up-to-date.
		return reversed(dict.fromkeys(_iter_keys(self._items)))

	def __len__(self):
		return len(self._impl._map)


__all__ = ['OrderedMultiDict']
