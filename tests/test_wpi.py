#!/usr/bin/env python3
"""
WPI (Wholesale Price Index) Tests
Tests all WPI API calls with proper validation
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
# WPI METADATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_wpi_metadata(client):
    """Test getting WPI metadata"""
    result = await call_tool(client, "get_wpi_metadata")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    data = result["data"]
    assert isinstance(data, dict), "Data should be a dict"


@pytest.mark.asyncio
async def test_wpi_metadata_has_year(client):
    """Test WPI metadata contains year information"""
    result = await call_tool(client, "get_wpi_metadata")

    assert_valid_api_response(result)
    assert "year" in result["data"], "Should have year filter"
    years = result["data"]["year"]
    assert isinstance(years, list), "Years should be a list"
    assert len(years) >= 10, f"Should have 10+ years, got {len(years)}"


@pytest.mark.asyncio
async def test_wpi_metadata_has_month(client):
    """Test WPI metadata contains month information"""
    result = await call_tool(client, "get_wpi_metadata")

    assert_valid_api_response(result)
    assert "month" in result["data"], "Should have month filter"
    months = result["data"]["month"]
    assert isinstance(months, list), "Months should be a list"
    assert len(months) == 12, f"Should have 12 months, got {len(months)}"


@pytest.mark.asyncio
async def test_wpi_metadata_has_major_group(client):
    """Test WPI metadata contains major_group information"""
    result = await call_tool(client, "get_wpi_metadata")

    assert_valid_api_response(result)
    assert "major_group" in result["data"], "Should have major_group filter"
    major_groups = result["data"]["major_group"]
    assert isinstance(major_groups, list), "Major groups should be a list"
    assert len(major_groups) >= 3, f"Should have 3+ major groups, got {len(major_groups)}"


@pytest.mark.asyncio
async def test_wpi_metadata_has_hierarchical_groups(client):
    """Test WPI metadata contains hierarchical group structure"""
    result = await call_tool(client, "get_wpi_metadata")

    assert_valid_api_response(result)
    data = result["data"]

    # Should have hierarchical structure
    assert "group" in data, "Should have group filter"
    assert "sub_group" in data, "Should have sub_group filter"
    assert "sub_sub_group" in data, "Should have sub_sub_group filter"
    assert "item" in data, "Should have item filter"


# ============================================================================
# WPI DATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_wpi_data_default(client):
    """Test basic WPI data query with defaults"""
    result = await call_tool(client, "get_wpi_data",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_wpi_data_with_year(client):
    """Test WPI data with year filter"""
    result = await call_tool(client, "get_wpi_data",
                            year="2023",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_wpi_data_with_month(client):
    """Test WPI data with month filter"""
    result = await call_tool(client, "get_wpi_data",
                            year="2023",
                            month_code="6",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_wpi_data_with_major_group(client):
    """Test WPI data with major group filter"""
    result = await call_tool(client, "get_wpi_data",
                            major_group_code="1000000000",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_wpi_data_with_group(client):
    """Test WPI data with group filter"""
    result = await call_tool(client, "get_wpi_data",
                            group_code="1010000000",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_wpi_data_pagination(client):
    """Test WPI data with pagination"""
    result = await call_tool(client, "get_wpi_data",
                            limit=5)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_wpi_data_csv_format(client):
    """Test WPI data with CSV format"""
    result = await call_tool(client, "get_wpi_data",
                            Format="CSV",
                            limit=10)

    assert result is not None
    assert isinstance(result, dict)
    assert "data" in result


@pytest.mark.asyncio
async def test_wpi_data_combined_filters(client):
    """Test WPI data with multiple filters"""
    result = await call_tool(client, "get_wpi_data",
                            year="2023",
                            month_code="1",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


# ============================================================================
# SUMMARY
# ============================================================================
# Total: 13 tests covering:
# - Metadata endpoint (hierarchical structure)
# - Data endpoint (various filters)
# - Pagination and format options
