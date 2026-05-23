import pytest
from bson.objectid import ObjectId
from app import app, comments_collection

@pytest.fixture
def client():
    # Set up the Flask test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Clean up the test database data after tests finish
    comments_collection.delete_many({})

# ==========================================
# POSITIVE TEST CASES (HAPPY PATHS)
# ==========================================

def test_create_comment_success(client):
    """Test creating a comment with valid data"""
    valid_task_id = str(ObjectId())
    payload = {
        "task_id": valid_task_id,
        "text": "This is a wonderful test comment!",
        "author": "Augi"
    }
    response = client.post('/api/comments', json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data['text'] == "This is a wonderful test comment!"
    assert data['author'] == "Augi"
    assert '_id' in data

def test_get_comments_all(client):
    """Test retrieving all comments"""
    # Insert a dummy comment manually
    valid_task_id = ObjectId()
    comments_collection.insert_one({"task_id": valid_task_id, "text": "Hello", "author": "Tester"})

    response = client.get('/api/comments')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['text'] == "Hello"

def test_get_comments_by_task_id(client):
    """Test retrieving comments filtered by task_id"""
    valid_task_id = ObjectId()
    comments_collection.insert_one({"task_id": valid_task_id, "text": "Filtered", "author": "Tester"})

    response = client.get(f'/api/comments?task_id={str(valid_task_id)}')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1

def test_update_comment_success(client):
    """Test successfully updating an existing comment"""
    valid_task_id = ObjectId()
    result = comments_collection.insert_one({"task_id": valid_task_id, "text": "Old text", "author": "Tester"})
    comment_id = str(result.inserted_id)

    payload = {"text": "Brand new text!"}
    response = client.put(f'/api/comments/{comment_id}', json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['text'] == "Brand new text!"

def test_delete_comment_success(client):
    """Test successfully deleting a comment"""
    valid_task_id = ObjectId()
    result = comments_collection.insert_one({"task_id": valid_task_id, "text": "Going away", "author": "Tester"})
    comment_id = str(result.inserted_id)

    response = client.delete(f'/api/comments/{comment_id}')
    data = response.get_json()

    assert response.status_code == 200
    assert data['message'] == "Comment successfully deleted"

# ==========================================
# NEGATIVE TEST CASES (ERROR HANDLING)
# ==========================================

def test_create_comment_missing_fields(client):
    """Test creating a comment with missing fields"""
    payload = {"text": "Missing task id"}
    response = client.post('/api/comments', json=payload)
    assert response.status_code == 400

def test_create_comment_invalid_task_id(client):
    """Test creating a comment with a malformed task_id"""
    payload = {"task_id": "not-an-object-id", "text": "Valid text"}
    response = client.post('/api/comments', json=payload)
    assert response.status_code == 400

def test_get_comments_invalid_task_id_query(client):
    """Test filtering comments by an invalid task_id format"""
    response = client.get('/api/comments?task_id=invalid-id')
    assert response.status_code == 400

def test_update_comment_invalid_id_format(client):
    """Test updating with an invalid comment ID string format"""
    response = client.put('/api/comments/not-a-valid-id', json={"text": "text"})
    assert response.status_code == 400

def test_update_comment_missing_text(client):
    """Test updating without providing text field"""
    valid_id = str(ObjectId())
    response = client.put(f'/api/comments/{valid_id}', json={})
    assert response.status_code == 400

def test_update_comment_not_found(client):
    """Test updating a comment ID that doesn't exist in DB"""
    valid_id = str(ObjectId())
    response = client.put(f'/api/comments/{valid_id}', json={"text": "text"})
    assert response.status_code == 404

def test_delete_comment_invalid_id_format(client):
    """Test deleting with an invalid comment ID string format"""
    response = client.delete('/api/comments/not-a-valid-id')
    assert response.status_code == 400

def test_delete_comment_not_found(client):
    """Test deleting a comment ID that doesn't exist in DB"""
    valid_id = str(ObjectId())
    response = client.delete(f'/api/comments/{valid_id}')
    assert response.status_code == 404