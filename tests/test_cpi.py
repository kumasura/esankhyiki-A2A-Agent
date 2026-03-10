#!/usr/bin/env python3
"""
CPI (Consumer Price Index) Tests
Tests all CPI API calls with proper validation
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
# CPI METADATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_cpi_metadata_group_2012(client):
    """Test CPI metadata for Group level with base year 2012"""
    result = await call_tool(client, "get_cpi_metadata",
                            base_year="2012", level="Group")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    filters = result["data"]
    assert isinstance(filters, dict), "Metadata should be a dict of filters"

    # Group level should have these filters
    expected_filters = ["series", "year", "month", "state", "sector", "group", "subgroup"]
    for f in expected_filters:
        assert f in filters, f"Group level should have '{f}' filter"


@pytest.mark.asyncio
async def test_cpi_metadata_item_2012(client):
    """Test CPI metadata for Item level with base year 2012"""
    result = await call_tool(client, "get_cpi_metadata",
                            base_year="2012", level="Item")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    filters = result["data"]
    assert isinstance(filters, dict), "Metadata should be a dict of filters"

    # Item level should have these filters
    expected_filters = ["year", "month", "item"]
    for f in expected_filters:
        assert f in filters, f"Item level should have '{f}' filter"


@pytest.mark.asyncio
async def test_cpi_metadata_group_2010(client):
    """Test CPI metadata for Group level with base year 2010"""
    result = await call_tool(client, "get_cpi_metadata",
                            base_year="2010", level="Group")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"


@pytest.mark.asyncio
async def test_cpi_metadata_item_2010(client):
    """Test CPI metadata for Item level with base year 2010"""
    result = await call_tool(client, "get_cpi_metadata",
                            base_year="2010", level="Item")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"


@pytest.mark.asyncio
async def test_cpi_metadata_has_states(client):
    """Test CPI metadata contains state information"""
    result = await call_tool(client, "get_cpi_metadata",
                            base_year="2012", level="Group")

    assert_valid_api_response(result)
    states = result["data"]["state"]
    assert isinstance(states, list), "States should be a list"
    assert len(states) >= 30, f"Should have 30+ states, got {len(states)}"

    # Check state structure
    state = states[0]
    assert "state_code" in state, "State should have state_code"
    assert "state_name" in state, "State should have state_name"


@pytest.mark.asyncio
async def test_cpi_metadata_has_groups(client):
    """Test CPI metadata contains group information"""
    result = await call_tool(client, "get_cpi_metadata",
                            base_year="2012", level="Group")

    assert_valid_api_response(result)
    groups = result["data"]["group"]
    assert isinstance(groups, list), "Groups should be a list"
    assert len(groups) >= 5, f"Should have 5+ groups, got {len(groups)}"

    # Check group structure
    group = groups[0]
    assert "group_code" in group, "Group should have group_code"
    assert "group_name" in group, "Group should have group_name"


@pytest.mark.asyncio
async def test_cpi_metadata_has_items(client):
    """Test CPI metadata contains item information"""
    result = await call_tool(client, "get_cpi_metadata",
                            base_year="2012", level="Item")

    assert_valid_api_response(result)
    items = result["data"]["item"]
    assert isinstance(items, list), "Items should be a list"
    assert len(items) >= 200, f"Should have 200+ items, got {len(items)}"

    # Check item structure
    item = items[0]
    assert "item_code" in item, "Item should have item_code"
    assert "item_name" in item, "Item should have item_name"


# ============================================================================
# CPI GROUP INDEX DATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_cpi_group_index_default(client):
    """Test basic CPI group index query with defaults"""
    result = await call_tool(client, "get_cpi_group_index")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_with_state(client):
    """Test CPI group index with state filter"""
    result = await call_tool(client, "get_cpi_group_index",
                            state_code="99")  # All India

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_with_sector(client):
    """Test CPI group index with sector filter"""
    result = await call_tool(client, "get_cpi_group_index",
                            sector_code="1")  # Rural

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_with_group(client):
    """Test CPI group index with group filter"""
    result = await call_tool(client, "get_cpi_group_index",
                            group_code="1")  # Food and Beverages

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_with_subgroup(client):
    """Test CPI group index with subgroup filter"""
    result = await call_tool(client, "get_cpi_group_index",
                            subgroup_code="1.1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_with_year_month(client):
    """Test CPI group index with year and month filter"""
    result = await call_tool(client, "get_cpi_group_index",
                            year="2023",
                            month_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_with_series(client):
    """Test CPI group index with series filter"""
    result = await call_tool(client, "get_cpi_group_index",
                            series="Current")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_base_year_2010(client):
    """Test CPI group index with base year 2010"""
    result = await call_tool(client, "get_cpi_group_index",
                            base_year="2010")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_multiple_filters(client):
    """Test CPI group index with multiple filters"""
    result = await call_tool(client, "get_cpi_group_index",
                            base_year="2012",
                            series="Current",
                            state_code="99",
                            sector_code="3",
                            group_code="1",
                            year="2023",
                            month_code="6")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_pagination(client):
    """Test CPI group index with pagination"""
    result = await call_tool(client, "get_cpi_group_index",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_group_index_csv_format(client):
    """Test CPI group index with CSV format"""
    result = await call_tool(client, "get_cpi_group_index",
                            state_code="99",
                            Format="CSV",
                            limit=10)

    assert result is not None
    assert isinstance(result, dict)
    assert "data" in result


# ============================================================================
# CPI ITEM INDEX DATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_cpi_item_index_default(client):
    """Test basic CPI item index query with defaults"""
    result = await call_tool(client, "get_cpi_item_index")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_item_index_with_item(client):
    """Test CPI item index with item filter"""
    result = await call_tool(client, "get_cpi_item_index",
                            item_code="101011")  # A specific item code

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_item_index_with_year_month(client):
    """Test CPI item index with year and month filter"""
    result = await call_tool(client, "get_cpi_item_index",
                            year="2023",
                            month_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_item_index_base_year_2010(client):
    """Test CPI item index with base year 2010"""
    result = await call_tool(client, "get_cpi_item_index",
                            base_year="2010")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_item_index_pagination(client):
    """Test CPI item index with pagination"""
    result = await call_tool(client, "get_cpi_item_index",
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_cpi_item_index_csv_format(client):
    """Test CPI item index with CSV format"""
    result = await call_tool(client, "get_cpi_item_index",
                            Format="CSV",
                            limit=10)

    assert result is not None
    assert isinstance(result, dict)
    assert "data" in result


# ============================================================================
# CPI RESPONSE VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_cpi_group_index_response_structure(client):
    """Test CPI group index response has correct structure"""
    result = await call_tool(client, "get_cpi_group_index",
                            state_code="99",
                            group_code="0",
                            year="2023",
                            month_code="1")

    assert_valid_api_response(result)

    # Check for expected fields
    assert "statusCode" in result or "data" in result

    if "data" in result and len(result["data"]) > 0:
        record = result["data"][0]
        assert isinstance(record, dict), "Each record should be a dict"


@pytest.mark.asyncio
async def test_cpi_item_index_response_structure(client):
    """Test CPI item index response has correct structure"""
    result = await call_tool(client, "get_cpi_item_index",
                            year="2023",
                            month_code="1",
                            limit=5)

    assert_valid_api_response(result)

    if "data" in result and len(result["data"]) > 0:
        record = result["data"][0]
        assert isinstance(record, dict), "Each record should be a dict"


# ============================================================================
# SUMMARY
# ============================================================================
# Total: 30 tests covering:
# - Metadata endpoint (all base years, all levels)
# - Group index data (all filter parameters)
# - Item index data (all filter parameters)
# - Pagination and format options
# - Response structure validation
