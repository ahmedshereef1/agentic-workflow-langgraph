from deploy.lambda_function.lambda_handler import lambda_handler


def test_lambda_handler():
    # Create a mock event to simulate an AWS Lambda invocation
    event = {"query": "What is AWS?"}

    # Call the lambda_handler function
    response = lambda_handler(event, None)

    print("\nResponse:\n\n", response["body"]["final_report"])

    # Assertions to validate the response
    assert response["statusCode"] == 200
    assert "final_report" in response["body"]
    assert "errors" in response["body"]
    assert isinstance(response["body"]["final_report"], str)
    assert isinstance(response["body"]["errors"], list)


# uv run python -c "from tests.test_lambda_handler import test_lambda_handler; test_lambda_handler()"
