from app5 import app, preprocess_expression, calculate_roots_from_expression, factorize_polynomial, simplify_expression
import pytest

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Test 1 : Test de la route Flask avec une expression valide
def test_valid_expression(client):
    response = client.post('/calculateWithNumpy', json={
        'expression': 'x^2 + 2x + 1',
        'userId': '8'
    })
    data = response.get_json()
    
    assert response.status_code == 200
    assert 'simplifiedExpression' in data
    assert 'factoredExpression' in data
    assert 'roots' in data
    assert data['userId'] == '8'

# Test 2 : Expression invalide (pas d'expression)
def test_no_expression(client):
    response = client.post('/calculateWithNumpy', json={
        'userId': '8'
    })
    data = response.get_json()
    
    assert response.status_code == 400
    assert data['error'] == 'No expression provided'

# Test 3 : userId manquant
def test_no_user_id(client):
    response = client.post('/calculateWithNumpy', json={
        'expression': 'x^2 - 4'
    })
    data = response.get_json()
    
    assert response.status_code == 400
    assert data['error'] == 'No userId provided'

# Test 4 : Test de prétraitement d'expression
def test_preprocess_expression():
    assert preprocess_expression('x2 + 2x + 1') == 'x**2 + 2*x + 1'
    assert preprocess_expression('3x3 - 4x') == '3*x**3 - 4*x'

# Test 5 : Simplification de polynôme
def test_simplify_expression():
    result = simplify_expression('x^2 + 2x + 1')
    assert str(result) == 'x**2 + 2*x + 1'

# Test 6 : Factorisation de polynôme
def test_factorize_polynomial():
    result = factorize_polynomial('x^2 + 2x + 1')
    assert str(result) == '(x + 1)**2'

