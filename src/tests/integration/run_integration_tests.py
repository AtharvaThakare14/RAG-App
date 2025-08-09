import os
import sys
import json
import requests
from datetime import datetime

# Get the API endpoint from environment variables
API_ENDPOINT = os.environ.get("API_ENDPOINT")

def log(message):
    """Log a message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def write_junit_xml(tests, output_file="integration-test-results.xml"):
    """Write test results in JUnit XML format."""
    template = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite name="integration-tests" tests="{total}" errors="{errors}" failures="{failures}" skipped="{skipped}">
{test_cases}
  </testsuite>
</testsuites>
"""
    
    test_case_template = """    <testcase name="{name}" classname="integration_tests">
{result}
    </testcase>"""
    
    failure_template = """      <failure message="{message}" type="AssertionError">
{details}
      </failure>"""
    
    error_template = """      <error message="{message}" type="Exception">
{details}
      </error>"""
    
    skipped_template = """      <skipped message="{message}" />"""
    
    # Count test results
    total = len(tests)
    errors = sum(1 for t in tests if t.get("status") == "error")
    failures = sum(1 for t in tests if t.get("status") == "failure")
    skipped = sum(1 for t in tests if t.get("status") == "skipped")
    
    # Generate test case XML
    test_cases = []
    for test in tests:
        result = ""
        if test.get("status") == "failure":
            result = failure_template.format(
                message=test.get("message", "Test failed"),
                details=test.get("details", "")
            )
        elif test.get("status") == "error":
            result = error_template.format(
                message=test.get("message", "Test error"),
                details=test.get("details", "")
            )
        elif test.get("status") == "skipped":
            result = skipped_template.format(
                message=test.get("message", "Test skipped")
            )
        
        test_cases.append(test_case_template.format(
            name=test.get("name", "unknown"),
            result=result
        ))
    
    # Generate final XML
    xml = template.format(
        total=total,
        errors=errors,
        failures=failures,
        skipped=skipped,
        test_cases="\n".join(test_cases)
    )
    
    # Write to file
    with open(output_file, "w") as f:
        f.write(xml)
    
    log(f"Test results written to {output_file}")
    log(f"Total: {total}, Errors: {errors}, Failures: {failures}, Skipped: {skipped}")

def test_api_health():
    """Test that the API is healthy."""
    test_result = {
        "name": "test_api_health",
        "status": "passed"
    }
    
    try:
        log(f"Testing API health at: {API_ENDPOINT}")
        
        # Use the auth endpoint with 'healthcheck' action which doesn't require authentication
        payload = {"action": "healthcheck"}
        response = requests.post(f"{API_ENDPOINT}/auth", json=payload, timeout=10)
        log(f"Health check status code: {response.status_code}")
        
        if response.status_code != 200:
            test_result["status"] = "failure"
            test_result["message"] = f"Health check failed with status {response.status_code}"
            test_result["details"] = response.text
            return test_result
        
        try:
            response_json = response.json()
            log(f"Health check response: {json.dumps(response_json)}")
                
        except json.JSONDecodeError:
            test_result["status"] = "failure"
            test_result["message"] = "Health check response is not valid JSON"
            test_result["details"] = response.text
            return test_result
            
    except Exception as e:
        test_result["status"] = "error"
        test_result["message"] = f"Health check error: {str(e)}"
        test_result["details"] = str(e)
    
    return test_result

def main():
    """Run the integration tests."""
    if not API_ENDPOINT:
        log("Error: API_ENDPOINT environment variable not set")
        tests = [{
            "name": "test_all",
            "status": "skipped",
            "message": "API_ENDPOINT environment variable not set"
        }]
        write_junit_xml(tests)
        return 1
    
    log(f"Running integration tests against API endpoint: {API_ENDPOINT}")
    
    # Run a simple health check test
    tests = []
    health_result = test_api_health()
    tests.append(health_result)
    
    # Write the test results to a JUnit XML file
    write_junit_xml(tests)
    
    # Return success if the health check passed
    return 0 if health_result["status"] == "passed" else 1

if __name__ == "__main__":
    sys.exit(main())