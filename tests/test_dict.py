import sys

import pytest

from shared_memory_dict import SharedMemoryDict
from shared_memory_dict.dict import DEFAULT_SERIALIZER
from shared_memory_dict.serializers import JSONSerializer

DEFAULT_MEMORY_SIZE = 1024


class TestSharedMemoryDict:
    @pytest.fixture
    def shared_memory_dict(self):
        smd = SharedMemoryDict(name='ut', size=DEFAULT_MEMORY_SIZE)
        yield smd
        smd.clear()
        smd.cleanup()

    @pytest.fixture
    def key(self):
        return 'fake-key'

    @pytest.fixture
    def value(self):
        return 'fake-value'

    @pytest.fixture
    def big_value(self):
        return 'value' * 2048

    def test_should_add_a_key(self, shared_memory_dict, key, value):
        try:
            shared_memory_dict[key] = value
        except Exception as e:
            pytest.fail(f'Its should not raises: {e}')

    def test_should_read_a_key(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        assert shared_memory_dict[key] == value

    def test_should_read_a_key_with_default(
        self, shared_memory_dict, key, value
    ):
        default_value = 'default_value'
        assert shared_memory_dict.get(key, default_value) == default_value

    def test_should_read_a_key_without_default(
        self, shared_memory_dict, key, value
    ):
        assert shared_memory_dict.get(key) is None

    def test_should_remove_a_key(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        try:
            del shared_memory_dict[key]
        except Exception as e:
            pytest.fail(f'Its should not raises: {e}')

        with pytest.raises(KeyError):
            shared_memory_dict[key]

    def test_should_get_len_of_dict(self, shared_memory_dict, key, value):
        assert len(shared_memory_dict) == 0
        shared_memory_dict[key] = value
        assert len(shared_memory_dict) == 1

    def test_should_popitem(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        assert shared_memory_dict.popitem() == (key, value)

    def test_should_clear_dict(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        try:
            shared_memory_dict.clear()
        except Exception as e:
            pytest.fail(f'Its should not raises: {e}')

        with pytest.raises(KeyError):
            shared_memory_dict[key]

    def test_should_finalize_dict(self):
        smd = SharedMemoryDict(name='unit-tests', size=64)
        try:
            del smd
        except Exception as e:
            pytest.fail(f'Its should not raises: {e}')

    def test_should_check_item_in_dict(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        assert (key in shared_memory_dict) is True
        assert ('some-another-key' in shared_memory_dict) is False

    def test_should_return_dict_keys(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        assert list(shared_memory_dict.keys()) == [key]

    def test_should_warning_about_move_to_end_deprecation(
        self, shared_memory_dict, key, value
    ):
        shared_memory_dict[key] = value
        deprecation_message = (
            'The \'move_to_end\' method will be removed in future versions. '
            'Use pop and reassignment instead.'
        )
        with pytest.deprecated_call(match=deprecation_message):
            shared_memory_dict.move_to_end(key)

    def test_should_warning_about_last_parameter_deprecation_in_popitem(
        self, shared_memory_dict, key, value
    ):
        shared_memory_dict[key] = value
        deprecation_message = (
            'The \'last\' parameter will be removed in future versions. '
            'The \'popitem\' function now always returns last inserted.'
        )
        with pytest.deprecated_call(match=deprecation_message):
            shared_memory_dict.popitem(last=True)

    def test_should_be_iterable_as_a_dict(
        self, shared_memory_dict, key, value
    ):
        shared_memory_dict[key] = value
        assert list(iter(shared_memory_dict)) == list(iter({key: value}))

    def test_can_be_iterated_in_reverse_order(
        self, shared_memory_dict, key, value
    ):
        shared_memory_dict[key] = value
        shared_memory_dict[value] = key
        assert list(reversed(shared_memory_dict)) == [value, key]

    def test_should_be_comparable(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        assert shared_memory_dict == {key: value}
        assert shared_memory_dict != {value: key}

    @pytest.mark.skipif(
        sys.version_info < (3, 9), reason='requires python3.9 or higher'
    )
    def test_allow_dict_merge(self, shared_memory_dict, key, value):
        assert shared_memory_dict | {key: value} == {key: value}
        assert {key: value} | shared_memory_dict == {key: value}

    @pytest.mark.skipif(
        sys.version_info < (3, 9), reason='requires python3.9 or higher'
    )
    def test_allow_dict_update(self, shared_memory_dict, key, value):
        shared_memory_dict |= {key: value}
        assert shared_memory_dict == {key: value}

    def test_have_a_dict_like_str_conversion(
        self, shared_memory_dict, key, value
    ):
        shared_memory_dict[key] = value
        assert str(shared_memory_dict) == str({key: value})

    def test_have_a_dict_like_repr(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        assert repr(shared_memory_dict) == repr({key: value})

    def test_should_return_dict_values(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        assert list(shared_memory_dict.values()) == [value]

    def test_should_return_dict_items(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        assert list(shared_memory_dict.items()) == [(key, value)]

    def test_pop_an_item_without_default(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        assert shared_memory_dict.pop(key) == value

    def test_pop_an_item_with_default(self, shared_memory_dict, key, value):
        shared_memory_dict[key] = value
        default = 'default'
        assert shared_memory_dict.pop('unknown', default) == default

    def test_can_be_updated(self, shared_memory_dict, key, value):
        shared_memory_dict.update({key: value})
        assert shared_memory_dict[key] == value

    def test_can_get_an_key_or_set_it_with_a_default(
        self, shared_memory_dict, key, value
    ):
        shared_memory_dict.setdefault(key, value)
        assert shared_memory_dict[key] == value

    def test_raise_an_error_when_memory_is_full(
        self, shared_memory_dict, key, big_value
    ):
        with pytest.raises(ValueError, match="exceeds available storage"):
            shared_memory_dict[key] = big_value

    def test_should_expose_shared_memory(self, shared_memory_dict):
        try:
            shared_memory_dict.shm
        except AttributeError:
            pytest.fail('Should expose shared memory')

    def test_shared_memory_attribute_should_be_read_only(
        self, shared_memory_dict
    ):
        with pytest.raises(AttributeError):
            shared_memory_dict.shm = 'test'

    def test_use_default_serializer_when_not_specified(
        self, shared_memory_dict
    ):
        assert shared_memory_dict._serializer is DEFAULT_SERIALIZER

    def test_use_custom_serializer_when_specified(self):
        serializer = JSONSerializer()
        smd = SharedMemoryDict(
            name='unit-tests', size=64, serializer=serializer
        )
        assert smd._serializer is serializer
