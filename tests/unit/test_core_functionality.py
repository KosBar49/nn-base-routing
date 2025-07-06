#!/usr/bin/env python3
"""
Test script to verify the refactored IoT network generation.
Tests that nodes can connect using only max_range parameter.
"""

from src.iot_network_routing.core.generator import generate_random_network
from src.iot_network_routing.core.node import IoTNode
from src.iot_network_routing.core.network import IoTNetwork

def test_basic_functionality():
    """Test basic network generation functionality."""
    print("Testing basic network generation...")
    
    # Generate a small dense network to ensure connections
    network = generate_random_network(
        n_nodes=8,
        map_width=200,
        map_height=200,
        max_range=120
    )
    
    print(f"✓ Generated network with {len(network)} nodes")
    print(f"✓ Total connections: {network.get_connection_count()}")
    
    # Test that connections use max_range logic
    connected_pairs = 0
    total_pairs = 0
    
    for i, node1 in enumerate(network.nodes):
        for j, node2 in enumerate(network.nodes[i+1:], i+1):
            total_pairs += 1
            distance = node1.distance_to(node2)
            max_range = max(node1.communication_range, node2.communication_range)
            
            # Check if they should be connected
            should_be_connected = distance <= max_range
            are_connected = node2 in node1.neighbors
            
            if should_be_connected == are_connected:
                connected_pairs += 1
            else:
                print(f"✗ Connection mismatch: {node1.eui64[:8]} - {node2.eui64[:8]}")
                print(f"  Distance: {distance:.2f}, Max range: {max_range:.2f}")
                print(f"  Should be connected: {should_be_connected}, Are connected: {are_connected}")
    
    print(f"✓ Connection logic verified for {connected_pairs}/{total_pairs} node pairs")
    return connected_pairs == total_pairs

def test_range_variety():
    """Test that nodes get variety in communication ranges."""
    print("\nTesting range variety...")
    
    network = generate_random_network(
        n_nodes=20,
        max_range=150
    )
    
    ranges = [node.communication_range for node in network.nodes]
    min_range = min(ranges)
    max_range = max(ranges)
    avg_range = sum(ranges) / len(ranges)
    
    print(f"✓ Range statistics: min={min_range:.1f}, max={max_range:.1f}, avg={avg_range:.1f}")
    
    # Check that we have variety (not all nodes have the same range)
    unique_ranges = len(set(ranges))
    print(f"✓ Unique range values: {unique_ranges}")
    
    # Check that ranges are within expected bounds (30% to 100% of max_range)
    expected_min = 150 * 0.3
    expected_max = 150
    
    within_bounds = all(expected_min <= r <= expected_max for r in ranges)
    print(f"✓ All ranges within bounds [{expected_min:.1f}, {expected_max:.1f}]: {within_bounds}")
    
    return unique_ranges > 1 and within_bounds

def test_bidirectional_connections():
    """Test that all connections are bidirectional."""
    print("\nTesting bidirectional connections...")
    
    network = generate_random_network(
        n_nodes=15,
        map_width=300,
        map_height=300,
        max_range=100
    )
    
    is_bidirectional = network.validate_bidirectional_connections()
    print(f"✓ All connections are bidirectional: {is_bidirectional}")
    
    return is_bidirectional

def main():
    """Run all tests."""
    print("🧪 Testing Refactored IoT Network Generation")
    print("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_range_variety,
        test_bidirectional_connections
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ Test passed")
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test error: {e}")
        print()
    
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Refactoring successful.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
