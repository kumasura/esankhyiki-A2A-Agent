#!/usr/bin/env python3
"""
IIP (Index of Industrial Production) Tests
Tests all IIP API calls with proper validation
"""

import pytest
import pytest_asyncio
from fastmcp import Client

# Test Configuration - uses HTTP transport
MCP_SERVER_URL = "http://localhost:8000/mcp"


@pytest_asyncio.fixture
async def client():
    """Fixture for MCP client connection using HTTP transport"""
    async with Client(MCP_SERVER_URL) as c:
        yield c


async def call_tool(client, tool_name, **params):
    """Helper to call MCP tool and extract data"""
    result = await client.call_tool(tool_name, params)
    return result.data if hasattr(result, 'data') else result


def assert_valid_api_response(response):
    """Assert response is a valid API response with data"""
    assert response is not None, "Response should not be None"
    assert isinstance(response, dict), "Response should be a dict"

    # Check for successful response
    if "error" in response and response.get("statusCode") is False:
        pytest.fail(f"API returned error: {response.get('error')}")

    # Valid responses should have data or statusCode
    assert "data" in response or "statusCode" in response, \
        f"Response should have 'data' or 'statusCode': {response}"


# ============================================================================
# IIP METADATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_iip_metadata_annually(client):
    """Test IIP metadata for Annual frequency"""
    result = await call_tool(client, "get_iip_metadata",
                            base_year="2011-12", frequency="Annually")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    filters = result["data"]
    assert isinstance(filters, dict), "Metadata should be a dict of filters"

    # Annual should have these filters
    expected_filters = ["financial_year", "type", "category", "subcategory"]
    for f in expected_filters:
        assert f in filters, f"Annual metadata should have '{f}' filter"


@pytest.mark.asyncio
async def test_iip_metadata_monthly(client):
    """Test IIP metadata for Monthly frequency"""
    result = await call_tool(client, "get_iip_metadata",
                            base_year="2011-12", frequency="Monthly")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    filters = result["data"]
    assert isinstance(filters, dict), "Metadata should be a dict of filters"

    # Monthly should have these filters
    expected_filters = ["year", "month", "type", "category", "subcategory"]
    for f in expected_filters:
        assert f in filters, f"Monthly metadata should have '{f}' filter"


@pytest.mark.asyncio
async def test_iip_metadata_has_categories(client):
    """Test IIP metadata contains category information"""
    result = await call_tool(client, "get_iip_metadata",
                            base_year="2011-12", frequency="Annually")

    assert_valid_api_response(result)
    categories = result["data"]["category"]
    assert isinstance(categories, list), "Categories should be a list"
    assert len(categories) >= 5, f"Should have 5+ categories, got {len(categories)}"

    # Check category structure
    cat = categories[0]
    assert "category_code" in cat, "Category should have category_code"
    assert "category_name" in cat, "Category should have category_name"


@pytest.mark.asyncio
async def test_iip_metadata_has_subcategories(client):
    """Test IIP metadata contains subcategory information"""
    result = await call_tool(client, "get_iip_metadata",
                            base_year="2011-12", frequency="Annually")

    assert_valid_api_response(result)
    subcats = result["data"]["subcategory"]
    assert isinstance(subcats, list), "Subcategories should be a list"
    assert len(subcats) >= 10, f"Should have 10+ subcategories, got {len(subcats)}"


# ============================================================================
# IIP ANNUAL DATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_iip_annual_default(client):
    """Test basic IIP annual query with defaults"""
    result = await call_tool(client, "get_iip_annual")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_annual_with_year(client):
    """Test IIP annual with financial year filter"""
    result = await call_tool(client, "get_iip_annual",
                            financial_year="2023-24")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_annual_with_category(client):
    """Test IIP annual with category filter"""
    result = await call_tool(client, "get_iip_annual",
                            category_code="1")  # Mining

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_annual_with_type_sectoral(client):
    """Test IIP annual with type=Sectoral"""
    result = await call_tool(client, "get_iip_annual",
                            type="Sectoral")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_annual_with_type_usebased(client):
    """Test IIP annual with type=Use-based category"""
    result = await call_tool(client, "get_iip_annual",
                            type="Use-based category")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_annual_base_year_2004(client):
    """Test IIP annual with base year 2004-05"""
    result = await call_tool(client, "get_iip_annual",
                            base_year="2004-05")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_annual_pagination(client):
    """Test IIP annual with pagination"""
    result = await call_tool(client, "get_iip_annual",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_annual_csv_format(client):
    """Test IIP annual with CSV format"""
    result = await call_tool(client, "get_iip_annual",
                            Format="CSV",
                            limit=10)

    assert result is not None
    assert isinstance(result, dict)
    assert "data" in result


# ============================================================================
# IIP MONTHLY DATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_iip_monthly_default(client):
    """Test basic IIP monthly query with defaults"""
    result = await call_tool(client, "get_iip_monthly")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_monthly_with_year(client):
    """Test IIP monthly with year filter"""
    result = await call_tool(client, "get_iip_monthly",
                            year="2023")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_monthly_with_month(client):
    """Test IIP monthly with month filter"""
    result = await call_tool(client, "get_iip_monthly",
                            year="2023",
                            month_code="6")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_monthly_with_category(client):
    """Test IIP monthly with category filter"""
    result = await call_tool(client, "get_iip_monthly",
                            category_code="2")  # Manufacturing

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_monthly_with_type(client):
    """Test IIP monthly with type filter"""
    result = await call_tool(client, "get_iip_monthly",
                            type="General")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_monthly_pagination(client):
    """Test IIP monthly with pagination"""
    result = await call_tool(client, "get_iip_monthly",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_iip_monthly_csv_format(client):
    """Test IIP monthly with CSV format"""
    result = await call_tool(client, "get_iip_monthly",
                            Format="CSV",
                            limit=10)

    assert result is not None
    assert isinstance(result, dict)
    assert "data" in result


# ============================================================================
# SUMMARY
# ============================================================================
# Total: 20 tests covering:
# - Metadata endpoint (both frequencies)
# - Annual data (all filter parameters)
# - Monthly data (all filter parameters)
# - Pagination and format options
