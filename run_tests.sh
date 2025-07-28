#!/bin/bash

echo "🚀 Starting Comprehensive Practice Endpoint Tests"
echo "Testing all 46 questions across 4 languages (~184 tests)"
echo "This will take approximately 10-15 minutes..."
echo ""

# Install required dependencies if not present
pip install -q groq requests python-dotenv

# Run the comprehensive test
python test_all_practice_endpoints.py

echo ""
echo "✅ Testing complete! Check the CSV file for detailed results."