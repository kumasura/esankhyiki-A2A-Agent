"""
Test client for MoSPI MCP Server
Tests HTTP transport
"""
import asyncio
from fastmcp import Client

async def test_server():
    """Test the MoSPI MCP server"""

    # Connect to the HTTP server
    async with Client("http://localhost:8000/mcp") as client:
        print("✅ Connected to MoSPI MCP Server\n")

        # Test 1: List available tools
        print("📋 Available tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"   - {tool.name}")
        print(f"\n   Total: {len(tools)} tools\n")

        # Test 2: Call 1_know_about_mospi_api
        print("🔍 Testing 1_know_about_mospi_api...")
        result = await client.call_tool("1_know_about_mospi_api", {})
        print(f"   ✅ Success! Got {len(str(result))} characters of documentation\n")

        # Test 3: Call 2_get_indicators
        print("🔍 Testing 2_get_indicators...")
        result = await client.call_tool(
            "2_get_indicators",
            {
                "dataset": "PLFS",
                "user_query": "test query"
            }
        )
        print(f"   ✅ Success! Result: {result}\n")

        print("🎉 All tests passed!")

if __name__ == "__main__":
    print("🚀 Testing MoSPI MCP Server (HTTP Transport)\n")
    print("Make sure the server is running:")
    print("  python mospi_server.py\n")
    print("-" * 60 + "\n")

    asyncio.run(test_server())
