#!/usr/bin/env python3
"""
NAS (National Accounts Statistics) Tests
Tests all NAS API calls with proper validation
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
# NAS INDICATORS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_nas_indicators(client):
    """Test getting list of NAS indicators"""
    result = await call_tool(client, "get_nas_indicators")

    assert_valid_api_response(result)
    assert "data" in result, "Should return indicators data"

    data = result["data"]
    assert isinstance(data, dict), "Data should be a dict"


@pytest.mark.asyncio
async def test_nas_indicators_has_series(client):
    """Test indicators include series information"""
    result = await call_tool(client, "get_nas_indicators")

    assert_valid_api_response(result)
    assert "series" in result["data"], "Should have series array"
    series_list = result["data"]["series"]
    assert isinstance(series_list, list), "Series should be a list"
    assert len(series_list) >= 2, "Should have at least 2 series (Current, Back)"


@pytest.mark.asyncio
async def test_nas_indicators_has_frequency(client):
    """Test indicators include frequency information"""
    result = await call_tool(client, "get_nas_indicators")

    assert_valid_api_response(result)
    assert "frequency" in result["data"], "Should have frequency array"
    freq_list = result["data"]["frequency"]
    assert isinstance(freq_list, list), "Frequency should be a list"


# ============================================================================
# NAS METADATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_nas_metadata_default(client):
    """Test NAS metadata with defaults"""
    result = await call_tool(client, "get_nas_metadata")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    filters = result["data"]
    assert isinstance(filters, dict), "Metadata should be a dict of filters"


@pytest.mark.asyncio
async def test_nas_metadata_current_annual(client):
    """Test NAS metadata for Current series, Annual frequency"""
    result = await call_tool(client, "get_nas_metadata",
                            series="Current",
                            frequency_code=1,
                            indicator_code=1)

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    filters = result["data"]
    # Should have these filters
    expected_filters = ["year", "approach", "revision"]
    for f in expected_filters:
        assert f in filters, f"Metadata should have '{f}' filter"


@pytest.mark.asyncio
async def test_nas_metadata_current_quarterly(client):
    """Test NAS metadata for Current series, Quarterly frequency"""
    result = await call_tool(client, "get_nas_metadata",
                            series="Current",
                            frequency_code=2,
                            indicator_code=1)

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata for quarterly"


@pytest.mark.asyncio
async def test_nas_metadata_back_series(client):
    """Test NAS metadata for Back series"""
    result = await call_tool(client, "get_nas_metadata",
                            series="Back",
                            frequency_code=1,
                            indicator_code=1)

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata for Back series"


@pytest.mark.asyncio
async def test_nas_metadata_has_years(client):
    """Test NAS metadata contains year information"""
    result = await call_tool(client, "get_nas_metadata",
                            series="Current",
                            frequency_code=1,
                            indicator_code=1)

    assert_valid_api_response(result)
    years = result["data"]["year"]
    assert isinstance(years, list), "Years should be a list"
    assert len(years) >= 10, f"Should have 10+ years, got {len(years)}"


@pytest.mark.asyncio
async def test_nas_metadata_has_industries(client):
    """Test NAS metadata contains industry information"""
    result = await call_tool(client, "get_nas_metadata",
                            series="Current",
                            frequency_code=1,
                            indicator_code=1)

    assert_valid_api_response(result)
    industries = result["data"]["industry"]
    assert isinstance(industries, list), "Industries should be a list"
    assert len(industries) >= 10, f"Should have 10+ industries, got {len(industries)}"


@pytest.mark.asyncio
async def test_nas_metadata_has_approaches(client):
    """Test NAS metadata contains approach information"""
    result = await call_tool(client, "get_nas_metadata",
                            series="Current",
                            frequency_code=1,
                            indicator_code=1)

    assert_valid_api_response(result)
    approaches = result["data"]["approach"]
    assert isinstance(approaches, list), "Approaches should be a list"
    assert len(approaches) >= 2, f"Should have 2+ approaches, got {len(approaches)}"


# ============================================================================
# NAS DATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_nas_data_basic(client):
    """Test basic NAS data query"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_with_year(client):
    """Test NAS data with year filter"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            year="2023-24")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_with_series_current(client):
    """Test NAS data with Current series"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            series="Current")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_with_series_back(client):
    """Test NAS data with Back series"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            series="Back")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_annual_frequency(client):
    """Test NAS data with annual frequency"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            frequency_code="Annually")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_quarterly_frequency(client):
    """Test NAS data with quarterly frequency"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            frequency_code="Quarterly")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_with_quarterly_code(client):
    """Test NAS data with quarterly code filter"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            frequency_code="Quarterly",
                            quarterly_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_with_approach(client):
    """Test NAS data with approach filter"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            approach_code="01")  # Production

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_with_industry(client):
    """Test NAS data with industry filter"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            industry_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_with_revision(client):
    """Test NAS data with revision filter"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            revision_code="01")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_with_institutional(client):
    """Test NAS data with institutional filter"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            institutional_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_pagination(client):
    """Test NAS data with pagination"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_csv_format(client):
    """Test NAS data with CSV format"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            Format="CSV",
                            limit=10)

    assert result is not None
    assert isinstance(result, dict)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_different_indicators(client):
    """Test NAS data with different indicator codes"""
    # Test indicator 2 (GDP)
    result = await call_tool(client, "get_nas_data",
                            indicator_code="2")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_nas_data_combined_filters(client):
    """Test NAS data with multiple filters combined"""
    result = await call_tool(client, "get_nas_data",
                            indicator_code="1",
                            series="Current",
                            frequency_code="Annually",
                            year="2023-24",
                            approach_code="01")

    assert_valid_api_response(result)
    assert "data" in result


# ============================================================================
# SUMMARY
# ============================================================================
# Total: 27 tests covering:
# - Indicators endpoint
# - Metadata endpoint (different series, frequencies, indicators)
# - Data endpoint (all filter parameters)
# - Pagination and format options
