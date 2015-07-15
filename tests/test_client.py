import botocore
import pytest
import uuid


def test_batch_get_one_item(User, client):
    ''' A single call for a single item '''
    user1 = User(id=uuid.uuid4())

    request = {'User': {'Keys': [{'id': {'S': str(user1.id)}}],
                        'ConsistentRead': False}}
    # When batching input with less keys than the batch size, the request
    # will look identical
    expected_request = request
    response = {"Responses": {"User": [{'id': {'S': str(user1.id)},
                                        'age': {'N': '4'}}]}}
    # Expected response is a single list of users
    expected_response = {'User': [{'id': {'S': str(user1.id)},
                                   'age': {'N': '4'}}]}

    def handle(RequestItems):
        assert RequestItems == expected_request
        return response
    client.client.batch_get_item = handle

    response = client.batch_get_items(request)
    assert response == expected_response


def test_batch_get_one_batch(User, client):
    ''' A single call when the number of requested items is <= batch size '''
    # Simulate a full batch
    client.batch_size = 2

    user1 = User(id=uuid.uuid4())
    user2 = User(id=uuid.uuid4())

    request = {'User': {'Keys': [{'id': {'S': str(user1.id)}},
                                 {'id': {'S': str(user2.id)}}],
                        'ConsistentRead': False}}
    # When batching input with less keys than the batch size, the request
    # will look identical
    expected_request = request
    response = {"Responses": {"User": [{'id': {'S': str(user1.id)},
                                        'age': {'N': '4'}},
                                       {'id': {'S': str(user2.id)},
                                        'age': {'N': '5'}}]}}
    # Expected response is a single list of users
    expected_response = {'User': [{'id': {'S': str(user1.id)},
                                   'age': {'N': '4'}},
                                  {'id': {'S': str(user2.id)},
                                   'age': {'N': '5'}}]}

    def handle(RequestItems):
        assert RequestItems == expected_request
        return response
    client.client.batch_get_item = handle

    response = client.batch_get_items(request)
    assert response == expected_response


def test_batch_get_paginated(User, client):
    ''' Paginate requests to fit within the max batch size '''
    # Minimum batch size so we can force pagination with 2 users
    client.batch_size = 1

    user1 = User(id=uuid.uuid4())
    user2 = User(id=uuid.uuid4())

    request = {'User': {'Keys': [{'id': {'S': str(user1.id)}},
                                 {'id': {'S': str(user2.id)}}],
                        'ConsistentRead': False}}

    expected_requests = [
        {'User': {'Keys': [{'id': {'S': str(user1.id)}}],
                  'ConsistentRead': False}},
        {'User': {'Keys': [{'id': {'S': str(user2.id)}}],
                  'ConsistentRead': False}}
    ]
    responses = [
        {"Responses": {"User": [{'id': {'S': str(user1.id)},
                                 'age': {'N': '4'}}]}},
        {"Responses": {"User": [{'id': {'S': str(user2.id)},
                                 'age': {'N': '5'}}]}}
    ]
    expected_response = {'User': [{'id': {'S': str(user1.id)},
                                   'age': {'N': '4'}},
                                  {'id': {'S': str(user2.id)},
                                   'age': {'N': '5'}}]}
    calls = 0

    def handle(RequestItems):
        nonlocal calls
        expected = expected_requests[calls]
        response = responses[calls]
        calls += 1
        assert RequestItems == expected
        return response
    client.client.batch_get_item = handle

    response = client.batch_get_items(request)

    assert calls == 2
    assert response == expected_response


def test_batch_get_unprocessed(User, client):
    ''' Re-request unprocessed keys '''
    user1 = User(id=uuid.uuid4())

    request = {'User': {'Keys': [{'id': {'S': str(user1.id)}}],
                        'ConsistentRead': False}}
    expected_requests = [
        {'User': {'Keys': [{'id': {'S': str(user1.id)}}],
                  'ConsistentRead': False}},
        {'User': {'Keys': [{'id': {'S': str(user1.id)}}],
                  'ConsistentRead': False}}
    ]
    responses = [
        {"UnprocessedKeys": {'User': {'Keys': [{'id': {'S': str(user1.id)}}],
                             'ConsistentRead': False}}},
        {"Responses": {"User": [{'id': {'S': str(user1.id)},
                                 'age': {'N': '4'}}]}}
    ]
    expected_response = {'User': [{'id': {'S': str(user1.id)},
                                   'age': {'N': '4'}}]}
    calls = 0

    def handle(RequestItems):
        nonlocal calls
        expected = expected_requests[calls]
        response = responses[calls]
        calls += 1
        assert RequestItems == expected
        return response
    client.client.batch_get_item = handle

    response = client.batch_get_items(request)

    assert calls == 2
    assert response == expected_response


def test_batch_write_one_item(User, client):
    ''' A single call for a single item '''
    user1 = User(id=uuid.uuid4())

    request = {'User': [
        {'PutRequest': {'Item': {'id': {'S': str(user1.id)}}}}]
    }
    # When batching input with less keys than the batch size, the request
    # will look identical
    expected_request = request

    calls = 0

    def handle(RequestItems):
        nonlocal calls
        calls += 1
        assert RequestItems == expected_request
        return {}
    client.client.batch_write_item = handle
    client.batch_write_items(request)
    assert calls == 1


def test_batch_write_one_batch(User, client):
    ''' A single call when the number of requested items is <= batch size '''
    # Simulate a full batch
    client.batch_size = 2

    user1 = User(id=uuid.uuid4())
    user2 = User(id=uuid.uuid4())

    request = {'User': [
        {'PutRequest': {'Item': {'id': {'S': str(user1.id)}}}},
        {'PutRequest': {'Item': {'id': {'S': str(user2.id)}}}}]
    }
    # When batching input with less keys than the batch size, the request
    # will look identical
    expected_request = request

    calls = 0

    def handle(RequestItems):
        nonlocal calls
        calls += 1
        assert RequestItems == expected_request
        return {}
    client.client.batch_write_item = handle

    client.batch_write_items(request)
    assert calls == 1


def test_batch_write_paginated(User, client):
    ''' Paginate requests to fit within the max batch size '''
    # Minimum batch size so we can force pagination with 2 users
    client.batch_size = 1

    user1 = User(id=uuid.uuid4())
    user2 = User(id=uuid.uuid4())

    request = {'User': [
        {'PutRequest': {'Item': {'id': {'S': str(user1.id)}}}},
        {'PutRequest': {'Item': {'id': {'S': str(user2.id)}}}}]
    }
    expected_requests = [
        {'User': [
            {'PutRequest': {'Item': {'id': {'S': str(user1.id)}}}}]},
        {'User': [
            {'PutRequest': {'Item': {'id': {'S': str(user2.id)}}}}]}
    ]
    calls = 0

    def handle(RequestItems):
        nonlocal calls
        expected = expected_requests[calls]
        calls += 1
        assert RequestItems == expected
        return {}
    client.client.batch_write_item = handle

    client.batch_write_items(request)
    assert calls == 2


def test_batch_write_unprocessed(User, client):
    ''' Re-request unprocessed items '''
    user1 = User(id=uuid.uuid4())

    request = {'User': [
        {'PutRequest': {'Item': {'id': {'S': str(user1.id)}}}}]
    }
    expected_requests = [
        {'User': [
            {'PutRequest': {'Item': {'id': {'S': str(user1.id)}}}}]},
        {'User': [
            {'PutRequest': {'Item': {'id': {'S': str(user1.id)}}}}]}
    ]
    responses = [
        {"UnprocessedItems": {'User': [
            {'PutRequest': {'Item': {'id': {'S': str(user1.id)}}}}]}},
        {}
    ]
    calls = 0

    def handle(RequestItems):
        nonlocal calls
        expected = expected_requests[calls]
        response = responses[calls]
        calls += 1
        assert RequestItems == expected
        return response
    client.client.batch_write_item = handle

    client.batch_write_items(request)
    assert calls == 2


def test_create_table(User, client):
    expected = {
        'AttributeDefinitions': [
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'email', 'AttributeType': 'S'}],
        'ProvisionedThroughput': {'ReadCapacityUnits': 1,
                                  'WriteCapacityUnits': 1},
        'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
        'TableName': 'User',
        'GlobalSecondaryIndexes': [
            {'Projection': {'ProjectionType': 'ALL'},
             'ProvisionedThroughput': {'ReadCapacityUnits': 1,
                                       'WriteCapacityUnits': 1},
             'IndexName': 'by_email',
             'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}]}]}

    called = False

    def create_table(**table):
        nonlocal called
        called = True
        assert table == expected
    client.client.create_table = create_table
    client.create_table(User)
    assert called


def test_create_raises_unknown(User, client):
    def create_table(**table):
        error_response = {'Error': {
            'Code': 'FooError',
            'Message': 'FooMessage'}}
        raise botocore.exceptions.ClientError(error_response, 'OperationName')
    client.client.create_table = create_table

    with pytest.raises(botocore.exceptions.ClientError) as excinfo:
        client.create_table(User)
    assert excinfo.value.response['Error']['Code'] == 'FooError'
    assert excinfo.value.response['Error']['Message'] == 'FooMessage'


def test_create_already_exists(User, client):
    called = False

    def create_table(**table):
        nonlocal called
        called = True
        error_response = {'Error': {
            'Code': 'ResourceInUseException',
            'Message': 'FooMessage'}}
        raise botocore.exceptions.ClientError(error_response, 'OperationName')
    client.client.create_table = create_table

    client.create_table(User)
    assert called
