from pytest import mark

@mark.engine
def test_widget_functions_as_expected():
    assert True

@mark.smoke
@mark.engine
def test_false_body():
    assert False == False