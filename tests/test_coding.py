"""Tests for coding tools."""

from claude_101.coding.codegen import scaffold_code
from claude_101.coding.review import analyze_code
from claude_101.coding.sql import process_sql
from claude_101.coding.apidoc import scaffold_api_doc
from claude_101.coding.testgen import generate_test_cases
from claude_101.coding.architecture import create_adr


class TestScaffoldCode:
    def test_python_class(self):
        r = scaffold_code("python", "class", "UserService")
        assert r["language"] == "python"
        assert r["naming_convention"] == "snake_case"
        assert "class" in r["code"].lower() or "Class" in r["code"]
        assert r["file_extension"] == ".py"

    def test_javascript_function(self):
        r = scaffold_code("javascript", "function", "fetchData")
        assert r["language"] == "javascript"
        assert r["file_extension"] == ".js"

    def test_with_description(self):
        r = scaffold_code(
            "python",
            "function",
            "calculate_tax",
            "Calculate sales tax for a given amount",
        )
        assert "code" in r


class TestAnalyzeCode:
    def test_python(self):
        code = '''
def fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
'''
        r = analyze_code(code, language="python")
        assert r["language"] == "python"
        assert r["metrics"]["total_lines"] > 0
        assert r["metrics"]["code_lines"] > 0
        assert r["complexity"]["functions"] >= 2

    def test_auto_detect(self):
        code = "function hello() { console.log('hi'); }"
        r = analyze_code(code)
        assert r["language"] == "javascript"

    def test_complexity_grade(self):
        simple_code = "x = 1\ny = 2\nz = x + y"
        r = analyze_code(simple_code, language="python")
        assert r["complexity"]["complexity_grade"] in ("A", "B")


class TestProcessSql:
    def test_format(self):
        r = process_sql("select * from users where id=1", operation="format")
        assert r["operation"] == "format"
        assert r["query_type"] == "SELECT"
        assert "users" in r["tables"]

    def test_validate(self):
        r = process_sql(
            "SELECT name FROM users WHERE active = true", operation="validate"
        )
        assert r["operation"] == "validate"

    def test_explain(self):
        r = process_sql(
            "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id",
            operation="explain",
        )
        assert r["operation"] == "explain"
        assert len(r["tables"]) >= 2

    def test_extract(self):
        r = process_sql(
            "SELECT name, email FROM users WHERE age > 18", operation="extract"
        )
        assert "users" in r["tables"]

    def test_statement_count(self):
        r = process_sql("SELECT 1; SELECT 2;")
        assert r["statement_count"] >= 2


class TestScaffoldApiDoc:
    def test_openapi(self):
        r = scaffold_api_doc(
            "GET /users - List users, POST /users - Create user, GET /users/{id} - Get user"
        )
        assert r["endpoint_count"] == 3
        assert len(r["endpoints"]) == 3
        assert "document" in r

    def test_path_params(self):
        r = scaffold_api_doc("GET /users/{id} - Get user by ID")
        endpoint = r["endpoints"][0]
        path_params = [p for p in endpoint["parameters"] if p["in"] == "path"]
        assert len(path_params) >= 1

    def test_markdown_format(self):
        r = scaffold_api_doc("GET /health - Health check", output_format="markdown")
        assert r["format"] == "markdown"


class TestGenerateTestCases:
    def test_python(self):
        r = generate_test_cases("def add(a: int, b: int) -> int", language="python")
        assert r["function_name"] == "add"
        assert r["language"] == "python"
        assert len(r["test_cases"]) >= 1
        assert r["coverage_analysis"]["total"] >= 1

    def test_comprehensive(self):
        r = generate_test_cases(
            "def validate_email(email: str) -> bool", strategy="comprehensive"
        )
        categories = r["coverage_analysis"]["categories"]
        assert categories.get("happy_path", 0) >= 1
        assert categories.get("edge_case", 0) >= 1

    def test_happy_only(self):
        r = generate_test_cases("def greet(name: str) -> str", strategy="happy")
        assert all(tc["category"] == "happy_path" for tc in r["test_cases"])


class TestCreateAdr:
    def test_proposed(self):
        r = create_adr(
            "Choose database",
            "Need a database for user service",
            "PostgreSQL, MongoDB, DynamoDB",
        )
        assert r["adr"]["status"] == "proposed"
        assert len(r["adr"]["options"]) == 3
        assert "trade_off_matrix" in r
        assert "markdown" in r

    def test_accepted(self):
        r = create_adr(
            "Choose framework",
            "Need a web framework",
            "Express, FastAPI, Django",
            decision="FastAPI",
        )
        assert r["adr"]["status"] == "accepted"
        assert r["adr"]["decision"] == "FastAPI"


# ---------------------------------------------------------------------------
# New: API doc analysis tests
# ---------------------------------------------------------------------------


class TestScaffoldApiDocAnalysis:
    def test_consistency_check(self):
        r = scaffold_api_doc(
            "GET /users - List users, POST /users - Create user, GET /users/{id} - Get user"
        )
        assert "consistency" in r
        assert 0 <= r["consistency"]["score"] <= 100

    def test_example_bodies(self):
        r = scaffold_api_doc("POST /users - Create user, PUT /users/{id} - Update user")
        assert "example_bodies" in r
        assert len(r["example_bodies"]) >= 1

    def test_consistency_issue_post_with_id(self):
        r = scaffold_api_doc("POST /users/{id} - Bad pattern")
        assert len(r["consistency"]["issues"]) >= 1

    def test_no_code_analysis_without_code(self):
        r = scaffold_api_doc("GET /health - Health check")
        assert "code_analysis" not in r

    def test_code_route_extraction(self):
        code = """
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users():
    pass

@app.post("/users")
def create_user():
    pass
"""
        r = scaffold_api_doc("GET /users - List users", code=code)
        assert "code_analysis" in r
        assert r["code_analysis"]["route_count"] >= 2

    def test_auth_detection(self):
        code = 'headers = {"Authorization": f"Bearer {token}"}\njwt.decode(token)'
        r = scaffold_api_doc("GET /users - List users", code=code)
        assert r["code_analysis"]["auth"]["type"] == "bearer_token"
