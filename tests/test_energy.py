#!/usr/bin/env python3
"""
Energy Statistics Tests
Tests all Energy API calls with proper validation
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
# ENERGY INDICATORS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_energy_indicators(client):
    """Test getting Energy indicators list"""
    result = await call_tool(client, "get_energy_indicators")

    assert_valid_api_response(result)
    assert "data" in result, "Should return indicators data"

    data = result["data"]
    assert isinstance(data, dict), "Data should be a dict"


@pytest.mark.asyncio
async def test_energy_indicators_has_indicator(client):
    """Test indicators include indicator array"""
    result = await call_tool(client, "get_energy_indicators")

    assert_valid_api_response(result)
    assert "indicator" in result["data"], "Should have indicator array"
    indicators = result["data"]["indicator"]
    assert isinstance(indicators, list), "Indicators should be a list"
    assert len(indicators) >= 2, "Should have at least 2 indicators"


@pytest.mark.asyncio
async def test_energy_indicators_has_balance(client):
    """Test indicators include use_of_energy_balance array"""
    result = await call_tool(client, "get_energy_indicators")

    assert_valid_api_response(result)
    assert "use_of_energy_balance" in result["data"], "Should have use_of_energy_balance array"
    balance = result["data"]["use_of_energy_balance"]
    assert isinstance(balance, list), "Balance should be a list"
    assert len(balance) >= 2, "Should have at least 2 balance types"


# ============================================================================
# ENERGY METADATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_energy_metadata_default(client):
    """Test Energy metadata with defaults"""
    result = await call_tool(client, "get_energy_metadata")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"


@pytest.mark.asyncio
async def test_energy_metadata_ktoe_supply(client):
    """Test Energy metadata for KToE, Supply"""
    result = await call_tool(client, "get_energy_metadata",
                            indicator_code=1,
                            use_of_energy_balance_code=1)

    assert_valid_api_response(result)
    assert "data" in result

    data = result["data"]
    assert "year" in data, "Should have year filter"


@pytest.mark.asyncio
async def test_energy_metadata_petajoules_consumption(client):
    """Test Energy metadata for PetaJoules, Consumption"""
    result = await call_tool(client, "get_energy_metadata",
                            indicator_code=2,
                            use_of_energy_balance_code=2)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_energy_metadata_has_commodities(client):
    """Test Energy metadata contains energy_commodities"""
    result = await call_tool(client, "get_energy_metadata",
                            indicator_code=1,
                            use_of_energy_balance_code=1)

    assert_valid_api_response(result)
    assert "energy_commodities" in result["data"], "Should have energy_commodities filter"


# ============================================================================
# ENERGY DATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_energy_data_default(client):
    """Test basic Energy data query with defaults"""
    result = await call_tool(client, "get_energy_data",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_energy_data_with_year(client):
    """Test Energy data with year filter"""
    result = await call_tool(client, "get_energy_data",
                            year="2020-21",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_energy_data_ktoe(client):
    """Test Energy data with KToE indicator"""
    result = await call_tool(client, "get_energy_data",
                            indicator_code="1",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_energy_data_petajoules(client):
    """Test Energy data with PetaJoules indicator"""
    result = await call_tool(client, "get_energy_data",
                            indicator_code="2",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_energy_data_supply(client):
    """Test Energy data with Supply balance"""
    result = await call_tool(client, "get_energy_data",
                            use_of_energy_balance_code="1",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_energy_data_consumption(client):
    """Test Energy data with Consumption balance"""
    result = await call_tool(client, "get_energy_data",
                            use_of_energy_balance_code="2",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_energy_data_pagination(client):
    """Test Energy data with pagination"""
    result = await call_tool(client, "get_energy_data",
                            limit=5,
                            page=1)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_energy_data_csv_format(client):
    """Test Energy data with CSV format"""
    result = await call_tool(client, "get_energy_data",
                            Format="CSV",
                            limit=10)

    assert result is not None
    assert isinstance(result, dict)
    assert "data" in result


# ============================================================================
# SUMMARY
# ============================================================================
# Total: 16 tests covering:
# - Indicators endpoint
# - Metadata endpoint (different indicators and balance types)
# - Data endpoint (various filters)
# - Pagination and format options
