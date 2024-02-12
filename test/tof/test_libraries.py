import pytest
import utils

@pytest.mark.parametrize("name", utils.get_built_libs(get_mode = 'lib_dir'))
def test_libraries(host, name):
    lib_dir = host.file(name)
    assert lib_dir.is_directory