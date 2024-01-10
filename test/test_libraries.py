import pytest
import utils

@pytest.mark.parametrize("name", utils.get_built_libs('default'))
def test_libraries(host, name):
    pkg = host.file(name)
    assert pkg.is_directory