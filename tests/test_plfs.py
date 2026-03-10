#!/usr/bin/env python3
"""
PLFS (Periodic Labour Force Survey) Tests
Tests all PLFS API calls with proper validation
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


def assert_has_records(response):
    """Assert response has actual data records"""
    assert_valid_api_response(response)

    if "data" in response:
        data = response["data"]
        assert isinstance(data, list), "Data should be a list"
        assert len(data) > 0, "Data should have at least one record"


# ============================================================================
# PLFS INDICATORS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_plfs_indicators(client):
    """Test get_plfs_indicators returns all indicators"""
    result = await call_tool(client, "get_plfs_indicators")

    assert_valid_api_response(result)
    assert "data" in result, "Should return indicators data"

    indicators = result["data"]
    assert isinstance(indicators, list), "Indicators should be a list"
    assert len(indicators) >= 8, f"Should have at least 8 indicators, got {len(indicators)}"

    # Check indicator structure
    for ind in indicators:
        assert "indicator_code" in ind, "Each indicator should have indicator_code"


# ============================================================================
# PLFS METADATA TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_plfs_metadata_default(client):
    """Test get_plfs_metadata with defaults (indicator=3, frequency=1)"""
    result = await call_tool(client, "get_plfs_metadata")

    assert_valid_api_response(result)
    assert "data" in result, "Should return metadata"

    filters = result["data"]
    assert isinstance(filters, dict), "Metadata should be a dict of filters"
    assert len(filters) > 0, "Should have at least one filter"


@pytest.mark.asyncio
async def test_plfs_metadata_quarterly(client):
    """Test metadata for quarterly frequency has quarter filter"""
    result = await call_tool(client, "get_plfs_metadata",
                            indicator_code=3, frequency_code=2)

    assert_valid_api_response(result)
    assert "data" in result

    filters = result["data"]
    assert "quarter" in filters, "Quarterly metadata should have 'quarter' filter"


@pytest.mark.asyncio
async def test_plfs_metadata_monthly(client):
    """Test metadata for monthly frequency has month filter"""
    result = await call_tool(client, "get_plfs_metadata",
                            indicator_code=3, frequency_code=3)

    assert_valid_api_response(result)
    assert "data" in result

    filters = result["data"]
    assert "month" in filters, "Monthly metadata should have 'month' filter"


@pytest.mark.asyncio
async def test_plfs_metadata_with_context(client):
    """Test metadata with year and month context"""
    result = await call_tool(client, "get_plfs_metadata",
                            indicator_code=3,
                            frequency_code=3,
                            year="2025",
                            month_code="6")

    assert_valid_api_response(result)
    assert "data" in result


# ============================================================================
# PLFS DATA TESTS - Basic Queries
# ============================================================================

@pytest.mark.asyncio
async def test_plfs_data_default(client):
    """Test basic PLFS query with defaults"""
    result = await call_tool(client, "get_plfs_data")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_with_year(client):
    """Test PLFS with year filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23")

    assert_valid_api_response(result)
    assert "data" in result


# ============================================================================
# PLFS DATA TESTS - All Indicators
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.parametrize("indicator_code,indicator_name", [
    (1, "LFPR"),
    (2, "WPR"),
    (3, "UR"),
    (4, "Distribution"),
    (5, "Employment conditions"),
    (6, "Wage/salary"),
    (7, "Casual labour"),
    (8, "Self-employment"),
])
async def test_plfs_data_all_indicators(client, indicator_code, indicator_name):
    """Test PLFS data for all 8 indicators"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=indicator_code,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            gender_code="3",
                            sector_code="3")

    assert_valid_api_response(result)
    assert "data" in result, f"Indicator {indicator_code} ({indicator_name}) should return data"


# ============================================================================
# PLFS DATA TESTS - All Frequencies
# ============================================================================

@pytest.mark.asyncio
async def test_plfs_data_annual(client):
    """Test PLFS annual data (frequency=1)"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_quarterly(client):
    """Test PLFS quarterly data (frequency=2)"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=2,
                            year="2022-23",
                            quarter_code="2",
                            state_code="99")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_monthly(client):
    """Test PLFS monthly data (frequency=3)"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=3,
                            year="2025",
                            month_code="6",
                            state_code="99")

    assert_valid_api_response(result)
    assert "data" in result


# ============================================================================
# PLFS DATA TESTS - Filter Parameters
# ============================================================================

@pytest.mark.asyncio
async def test_plfs_data_state_filter(client):
    """Test PLFS with state filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            state_code="16")  # Maharashtra

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_gender_filter(client):
    """Test PLFS with gender filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            gender_code="1")  # Male

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_sector_filter(client):
    """Test PLFS with sector filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            sector_code="1")  # Rural

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_age_filter(client):
    """Test PLFS with age filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            age_code="2")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_education_filter(client):
    """Test PLFS with education filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            education_code="7")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_religion_filter(client):
    """Test PLFS with religion filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            religion_code="2")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_social_category_filter(client):
    """Test PLFS with social category filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            social_category_code="3")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_weekly_status_filter(client):
    """Test PLFS with weekly status filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            weekly_status_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_multiple_filters(client):
    """Test PLFS with multiple filters combined"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            state_code="16",
                            gender_code="1",
                            sector_code="2")

    assert_valid_api_response(result)
    assert "data" in result


# ============================================================================
# PLFS DATA TESTS - Indicator 4 Specific Filters
# ============================================================================

@pytest.mark.asyncio
async def test_plfs_data_broad_industry_work(client):
    """Test PLFS indicator 4 with broad industry work filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=4,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            broad_industry_work_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_broad_status_employment(client):
    """Test PLFS indicator 4 with broad status employment filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=4,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            broad_status_employment_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_enterprise_size(client):
    """Test PLFS indicator 4 with enterprise size filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=4,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            enterprise_size_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_enterprise_type(client):
    """Test PLFS indicator 4 with enterprise type filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=4,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            enterprise_type_code="1")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_industry_section(client):
    """Test PLFS indicator 4 with industry section filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=4,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            industry_section_code="2")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_nco_division(client):
    """Test PLFS indicator 4 with NCO division filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=4,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            nco_division_code="2")

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_nic_group(client):
    """Test PLFS indicator 4 with NIC group filter"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=4,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            nic_group_code="1")

    assert_valid_api_response(result)
    assert "data" in result


# ============================================================================
# PLFS DATA TESTS - Pagination and Format
# ============================================================================

@pytest.mark.asyncio
async def test_plfs_data_pagination(client):
    """Test PLFS with pagination"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            page=1,
                            limit=10)

    assert_valid_api_response(result)
    assert "data" in result


@pytest.mark.asyncio
async def test_plfs_data_csv_format(client):
    """Test PLFS with CSV format"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            Format="CSV")

    assert result is not None
    assert isinstance(result, dict)
    # CSV format returns data as text
    assert "data" in result


# ============================================================================
# PLFS DATA TESTS - Response Validation
# ============================================================================

@pytest.mark.asyncio
async def test_plfs_data_response_structure(client):
    """Test PLFS response has correct structure"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            gender_code="3",
                            sector_code="3")

    assert_valid_api_response(result)

    # Check for expected fields
    assert "statusCode" in result or "data" in result

    if "meta_data" in result:
        meta = result["meta_data"]
        assert "totalRecords" in meta, "Meta should have totalRecords"


@pytest.mark.asyncio
async def test_plfs_data_records_have_values(client):
    """Test PLFS data records have actual values"""
    result = await call_tool(client, "get_plfs_data",
                            indicator_code=3,
                            frequency_code=1,
                            year="2022-23",
                            state_code="99",
                            gender_code="3",
                            sector_code="3")

    assert_valid_api_response(result)

    if "data" in result and len(result["data"]) > 0:
        record = result["data"][0]
        assert isinstance(record, dict), "Each record should be a dict"
        # Records should have some fields
        assert len(record) > 0, "Record should have fields"


# ============================================================================
# SUMMARY
# ============================================================================
# Total: 35+ tests covering:
# - Indicators endpoint
# - Metadata endpoint (all frequencies, with context)
# - Data endpoint (all indicators, all frequencies)
# - All filter parameters
# - Indicator 4 specific filters
# - Pagination and format options
# - Response structure validation
