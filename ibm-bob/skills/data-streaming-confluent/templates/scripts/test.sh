#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Confluent Cloud Streaming Solution Test                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Python virtual environment exists
echo -e "${BLUE}[1/4] Checking Environment...${NC}"
echo ""

cd "$PROJECT_ROOT/python"

if [ ! -d "venv" ]; then
    print_error "Virtual environment not found"
    print_info "Run './scripts/setup.sh' first"
    exit 1
fi

print_status "Virtual environment found"

if [ ! -f ".env" ]; then
    print_error ".env file not found"
    print_info "Run './scripts/setup.sh' first"
    exit 1
fi

print_status ".env file found"

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

echo ""

# Check for producer scripts
echo -e "${BLUE}[2/4] Checking Producer Scripts...${NC}"
echo ""

PRODUCER_FOUND=0

if [ -d "producers" ]; then
    PRODUCER_FILES=$(find producers -name "*.py" -type f | wc -l)
    if [ $PRODUCER_FILES -gt 0 ]; then
        print_status "Found $PRODUCER_FILES producer script(s)"
        PRODUCER_FOUND=1
    fi
fi

if [ $PRODUCER_FOUND -eq 0 ]; then
    if [ -f "produce_messages.py" ]; then
        print_status "Found produce_messages.py"
        PRODUCER_FOUND=1
    fi
fi

if [ $PRODUCER_FOUND -eq 0 ]; then
    print_error "No producer scripts found"
    print_info "Expected: producers/*.py or produce_messages.py"
    exit 1
fi

echo ""

# Check for sample data
echo -e "${BLUE}[3/4] Checking Sample Data...${NC}"
echo ""

SAMPLE_DATA_FOUND=0

if [ -d "sample-data" ]; then
    JSON_FILES=$(find sample-data -name "*.json" -type f | wc -l)
    if [ $JSON_FILES -gt 0 ]; then
        print_status "Found $JSON_FILES sample data file(s)"
        SAMPLE_DATA_FOUND=1
    fi
fi

if [ $SAMPLE_DATA_FOUND -eq 0 ]; then
    # Check for JSON files in current directory
    JSON_FILES=$(find . -maxdepth 1 -name "*.json" -type f | wc -l)
    if [ $JSON_FILES -gt 0 ]; then
        print_status "Found $JSON_FILES sample data file(s)"
        SAMPLE_DATA_FOUND=1
    fi
fi

if [ $SAMPLE_DATA_FOUND -eq 0 ]; then
    print_warning "No sample data files found"
    print_info "Producer will need to generate data or you'll need to provide sample files"
fi

echo ""

# Run producer
echo -e "${BLUE}[4/4] Producing Test Data...${NC}"
echo ""

print_info "Starting data production..."
echo ""

# Try to find and run the producer
if [ -f "producers/produce_messages.py" ]; then
    print_info "Running producers/produce_messages.py..."
    python producers/produce_messages.py
elif [ -f "produce_messages.py" ]; then
    print_info "Running produce_messages.py..."
    python produce_messages.py
else
    # List available producer scripts
    print_info "Available producer scripts:"
    find producers -name "*.py" -type f 2>/dev/null | while read script; do
        echo "  - $script"
    done
    echo ""
    print_warning "Please specify which producer to run:"
    read -p "Enter producer script path: " PRODUCER_SCRIPT
    
    if [ -f "$PRODUCER_SCRIPT" ]; then
        print_info "Running $PRODUCER_SCRIPT..."
        python "$PRODUCER_SCRIPT"
    else
        print_error "Producer script not found: $PRODUCER_SCRIPT"
        exit 1
    fi
fi

echo ""

# Display next steps
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Test data produced successfully!                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
print_info "Next steps:"
echo "  1. Wait 30-60 seconds for data to be processed"
echo "  2. Open Confluent Cloud Console"
echo "  3. Navigate to your environment and cluster"
echo "  4. Go to Flink SQL workspace"
echo "  5. Run the test queries from docs/TESTING.md"
echo ""
print_info "Example queries to try:"
echo "  - SELECT * FROM <source_table> LIMIT 10;"
echo "  - SELECT * FROM <destination_table> ORDER BY <key>;"
echo ""
print_warning "If you don't see data:"
echo "  - Check Flink job status in Confluent Cloud Console"
echo "  - Verify RBAC permissions are propagated (wait 30s after deployment)"
echo "  - Check for errors in Flink job logs"
echo "  - Ensure consumer isolation level is set correctly"
echo ""
print_info "To produce more test data, run this script again"
print_info "To cleanup resources, run './scripts/cleanup.sh'"
echo ""

# Made with Bob
