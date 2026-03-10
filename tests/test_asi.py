#!/usr/bin/env python3
"""
ASI (Annual Survey of Industries) Tests
Tests all ASI API calls with proper validation
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
# ASI CLASSIFICATION YEARS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_asi_classification_years(client):
    """Test getting list of NIC classification years"""
    result = await call_tool(client, "get_asi_classification_years")

    assert_valid_api_response(result)
    assert "data" in result, "Should return classification years data"

    data = result["data"]
    assert isinstance(data, list), "Data should be a list"
    assert len(data) >= 4, f"Should have at least 4 classification years, got {len(data)}"

    # Check structure
    item = data[0]
    assert "classification_year" in item, "Should have classification_year field"


@pytest.mark.asyncio
async def test_asi_classification_years_has_2008(client):
    """Test classification years includes 2008"""
    result = await call_tool(client, "get_asi_classification_years")

    assert_valid_api_response(result)
    years = [item["classification_year"] for item in result["data"]]
    assert 2008 in years, "Should include 2008 classification year"


# ============================================================================
# ASI METADATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_asi_metadata_default(client):
    """Test ASI metadata with default classification year (2008)"""
    result = await call_tool(client, "get_asi_metadata")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    filters = result["data"]
    assert isinstance(filters, dict), "Metadata should be a dict of filters"


@pytest.mark.asyncio
async def test_asi_metadata_2008(client):
    """Test ASI metadata for classification year 2008"""
    result = await call_tool(client, "get_asi_metadata",
                            classification_year="2008")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    filters = result["data"]
    # Should have these filters
    expected_filters = ["year", "indicator", "state"]
    for f in expected_filters:
        assert f in filters, f"Metadata should have '{f}' filter"


@pytest.mark.asyncio
async def test_asi_metadata_2004(client):
    """Test ASI metadata for classification year 2004"""
    result = await call_tool(client, "get_asi_metadata",
                            classification_year="2004")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata for 2004"


@pytest.mark.asyncio
async def test_asi_metadata_has_indicators(client):
    """Test ASI metadata contains indicator information"""
    result = await call_tool(client, "get_asi_metadata",
                            classification_year="2008")

    assert_valid_api_response(result)
    indicators = result["data"]["indicator"]
    assert isinstance(indicators, list), "Indicators should be a list"
    assert len(indicators) >= 50, f"Should have 50+ indicators, got {len(indicators)}"


@pytest.mark.asyncio
async def test_asi_metadata_has_states(client):
    """Test ASI metadata contains state information"""
    result = await call_tool(client, "get_asi_metadata",
                            classification_year="2008")

    assert_valid_api_response(result)
    states = result["data"]["state"]
    assert isinstance(states, list), "States should be a list"
    assert len(states) >= 30, f"Should have 30+ states, got {len(states)}"


@pytest.mark.asyncio
async def test_asi_metadata_has_nic_codes(client):
    """Test ASI metadata contains NIC code information"""
    result = await call_tool(client, "get_asi_metadata",
                            classification_year="2008")

    assert_valid_api_response(result)
    # Check for NIC codes at different levels
    assert "nic_2_digit" in result["data"] or "nic2digit" in result["data"] or "nic" in result["data"], \
        "Should have NIC code information"


# ============================================================================
# ASI DATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_asi_data_default(client):
    """Test basic ASI data query with defaults"""
    result = await call_tool(client, "get_asi_data")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_with_year(client):
    """Test ASI data with financial year filter"""
    result = await call_tool(client, "get_asi_data",
                            financial_year="2020-21")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_with_indicator(client):
    """Test ASI data with indicator filter"""
    result = await call_tool(client, "get_asi_data",
                            indicator_code="1")  # Number of factories

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_with_state(client):
    """Test ASI data with state filter"""
    result = await call_tool(client, "get_asi_data",
                            state_code="99")  # All India

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_with_sector_rural(client):
    """Test ASI data with sector=Rural"""
    result = await call_tool(client, "get_asi_data",
                            sector_code="Rural")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_with_sector_urban(client):
    """Test ASI data with sector=Urban"""
    result = await call_tool(client, "get_asi_data",
                            sector_code="Urban")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_with_sector_combined(client):
    """Test ASI data with sector=Combined"""
    result = await call_tool(client, "get_asi_data",
                            sector_code="Combined")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_classification_year_2008(client):
    """Test ASI data with classification year 2008"""
    result = await call_tool(client, "get_asi_data",
                            classification_year="2008")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_classification_year_2004(client):
    """Test ASI data with classification year 2004"""
    result = await call_tool(client, "get_asi_data",
                            classification_year="2004")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_nic_type_2digit(client):
    """Test ASI data with NIC type 2-digit"""
    result = await call_tool(client, "get_asi_data",
                            nic_code_type="2-digit")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_nic_type_3digit(client):
    """Test ASI data with NIC type 3-digit"""
    result = await call_tool(client, "get_asi_data",
                            nic_code_type="3-digit")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_with_nic_code(client):
    """Test ASI data with specific NIC code"""
    result = await call_tool(client, "get_asi_data",
                            nic_code="10",  # Manufacture of food products
                            nic_code_type="2-digit")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_pagination(client):
    """Test ASI data with pagination"""
    result = await call_tool(client, "get_asi_data",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_csv_format(client):
    """Test ASI data with CSV format"""
    result = await call_tool(client, "get_asi_data",
                            Format="CSV",
                            limit=10)

    assert result is not None
    assert isinstance(result, dict)
    assert "data" in result


@pytest.mark.asyncio
async def test_asi_data_combined_filters(client):
    """Test ASI data with multiple filters combined"""
    result = await call_tool(client, "get_asi_data",
                            classification_year="2008",
                            financial_year="2020-21",
                            indicator_code="1",
                            state_code="99",
                            sector_code="Combined")

    assert_valid_api_response(result)
    assert "data" in result


# ============================================================================
# SUMMARY
# ============================================================================
# Total: 25 tests covering:
# - Classification years endpoint
# - Metadata endpoint (different classification years)
# - Data endpoint (all filter parameters)
# - Pagination and format options
