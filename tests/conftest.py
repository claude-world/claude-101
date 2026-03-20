"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_csv():
    return "name,score,grade\nAlice,95,A\nBob,87,B\nCharlie,92,A\nDiana,78,C"


@pytest.fixture
def sample_code_python():
    return '''
def fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class Calculator:
    def add(self, a, b):
        return a + b
'''


@pytest.fixture
def sample_email_context():
    return "Follow-up to client meeting about Q3 budget proposal. Please review the attached document by Friday."


@pytest.fixture
def sample_sql():
    return "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id WHERE o.total > 100"
