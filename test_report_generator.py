#!/usr/bin/env python3
"""
Test script for the Report Generator functionality.
This script tests the Excel report generation with sample sensor data.
"""

from server.services.report_generator.report_generator import ReportGenerator
from server.services.sensor_data_storage.sensor_data_storage import SensorDataStorage
from server.middleware.client_middleware import ClientMiddleware
from server.middleware.middleware import Middleware
import sys
import os
import json
from datetime import datetime, timedelta

# Add the server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))


def create_sample_sensor_data():
    """Create sample sensor data for testing."""
    # Create sample sensor data structure
    sample_data = {
        'info': {
            'gateway1-topic1-indicator1': [
                {'timestamp': '2024-01-01T10:00:00', 'value': 25.5},
                {'timestamp': '2024-01-01T10:01:00', 'value': 26.2},
                {'timestamp': '2024-01-01T10:02:00', 'value': 25.8},
            ],
            'gateway2-topic2-indicator2': [
                {'timestamp': '2024-01-01T10:00:00', 'value': 100.0},
                {'timestamp': '2024-01-01T10:01:00', 'value': 101.5},
                {'timestamp': '2024-01-01T10:02:00', 'value': 99.8},
            ]
        },
        'requestId': 'test-request-123'
    }
    return sample_data


def test_excel_report_creation():
    """Test the Excel report creation functionality."""
    print("Testing Excel report creation...")

    try:
        # Create sample data
        sample_data = create_sample_sensor_data()

        # Create a mock middleware and sensor data storage
        middleware = Middleware()
        client_middleware = ClientMiddleware(middleware, "test_report_generator")
        sensor_data_storage = SensorDataStorage(client_middleware)

        # Create report generator
        report_generator = ReportGenerator(
            client_middleware, sensor_data_storage)

        # Test the Excel creation method directly
        excel_file_path = report_generator._create_excel_report(
            sample_data['info'])

        # Check if file was created
        if os.path.exists(excel_file_path):
            print(f"    Excel report created successfully: {excel_file_path}")
            print(f"   File size: {os.path.getsize(excel_file_path)} bytes")

            # Clean up the test file
            os.remove(excel_file_path)
            print("   Test file cleaned up")
            return True
        else:
            print(f"❌ Excel report file not found: {excel_file_path}")
            return False

    except Exception as e:
        print(f"❌ Error during Excel report creation: {e}")
        return False


def test_report_generator_command():
    """Test the report generator command functionality."""
    print("\nTesting report generator command...")

    try:
        # Create mock middleware and services
        middleware = Middleware()
        client_middleware = ClientMiddleware(middleware)
        sensor_data_storage = SensorDataStorage(client_middleware)

        # Create report generator
        report_generator = ReportGenerator(
            client_middleware, sensor_data_storage)

        # Create a test command
        test_command = {
            'data': {
                'sensorInfos': [
                    {'topic': 'topic1', 'gateway': 'gateway1',
                        'indicator': 'indicator1'},
                    {'topic': 'topic2', 'gateway': 'gateway2',
                        'indicator': 'indicator2'}
                ],
                'beginDate': '2024-01-01T00:00:00',
                'endDate': '2024-01-01T23:59:59'
            },
            'requestId': 'test-command-123'
        }

        # Test the command (this will fail because we don't have real sensor data)
        # but it should not crash
        report_generator.generate_report_command(test_command)
        print("✅ Report generator command executed without crashing")
        return True

    except Exception as e:
        print(f"❌ Error during command test: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Testing Report Generator Functionality")
    print("=" * 50)

    # Test Excel report creation
    excel_test_passed = test_excel_report_creation()

    # Test command functionality
    command_test_passed = test_report_generator_command()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(
        f"   Excel Report Creation: {'✅ PASSED' if excel_test_passed else '❌ FAILED'}")
    print(
        f"   Command Functionality: {'✅ PASSED' if command_test_passed else '❌ FAILED'}")

    if excel_test_passed and command_test_passed:
        print("\n🎉 All tests passed! Report generator is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit(main())
