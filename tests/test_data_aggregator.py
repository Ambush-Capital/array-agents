# test_data_aggregator.py
import pytest
import inspect
from agents.data_aggregator import DataAggregator

@pytest.fixture
def aggregator():
    return DataAggregator()

def test_aggregated_data(aggregator):
    # Explicit test for the aggregated_data method
    result = aggregator.aggregated_data()
    # Replace the expected value with the correct expected result from your business logic
    expected_result = 'expected output'  
    assert result == expected_result, f"aggregated_data() returned {result}, expected {expected_result}"

def test_all_public_methods(aggregator):
    # Retrieve all public methods of DataAggregator
    methods = [method_name for method_name in dir(aggregator) if callable(getattr(aggregator, method_name)) and not method_name.startswith('_')]
    for method_name in methods:
        method = getattr(aggregator, method_name)
        params = inspect.signature(method).parameters
        # Only test methods that require no parameters besides 'self'
        if len(params) == 1:
            try:
                result = method()
            except Exception as e:
                pytest.fail(f"Method {method_name} raised an exception: {e}")
            # Here you can add more assertions on the result if you have expected outputs
            # For now, we simply ensure the method executes without error
            assert True
        else:
            pytest.skip(f"Method {method_name} requires additional parameters, skipping automated test")