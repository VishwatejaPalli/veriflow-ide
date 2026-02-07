#!/bin/bash
# Quick Test Script for OpenHDL-IDE Tools
# This script tests all integrated tools with the demo files

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================"
echo "OpenHDL-IDE Tools Quick Test"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run a test
run_test() {
    local tool_name=$1
    local test_command=$2
    
    echo -n "Testing $tool_name... "
    
    if ! command_exists "$(echo $test_command | awk '{print $1}')"; then
        echo -e "${YELLOW}SKIPPED${NC} (tool not installed)"
        return 0
    fi
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}PASSED${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

echo "Checking available tools..."
echo "----------------------------"

# Check each tool
tools=(
    "iverilog:Icarus Verilog"
    "vvp:VVP Simulator"
    "yosys:Yosys"
    "gtkwave:GTKWave"
    "verilator:Verilator"
    "verible-verilog-lint:Verible Lint"
    "verible-verilog-format:Verible Format"
    "magic:Magic"
    "klayout:KLayout"
    "netgen:Netgen"
    "ngspice:NgSpice"
    "sta:OpenSTA"
)

available_count=0
for tool_info in "${tools[@]}"; do
    IFS=':' read -r cmd name <<< "$tool_info"
    if command_exists "$cmd"; then
        echo -e "  [${GREEN}✓${NC}] $name"
        ((available_count++))
    else
        echo -e "  [${YELLOW}✗${NC}] $name (not installed)"
    fi
done

echo ""
echo "$available_count of ${#tools[@]} tools available"
echo ""

# Run tests
echo "Running tool tests..."
echo "----------------------------"

# Test 1: Icarus Verilog compilation
if command_exists iverilog; then
    echo "Test 1: Icarus Verilog compilation"
    cd demo_alu
    iverilog -g2012 -o alu_tb.vvp alu.sv alu_tb.sv 2>&1 | head -20
    if [ -f alu_tb.vvp ]; then
        echo -e "${GREEN}✓ Compilation successful${NC}"
        
        # Test 2: VVP simulation
        if command_exists vvp; then
            echo ""
            echo "Test 2: VVP simulation"
            timeout 5 vvp alu_tb.vvp 2>&1 | tail -20
            if [ -f alu_tb.vcd ]; then
                echo -e "${GREEN}✓ Simulation successful, VCD generated${NC}"
            fi
        fi
    fi
    cd ..
    echo ""
fi

# Test 3: Verilator lint
if command_exists verilator; then
    echo "Test 3: Verilator lint"
    cd demo_alu
    verilator --lint-only -Wall alu.sv 2>&1 | head -20
    echo -e "${GREEN}✓ Lint check completed${NC}"
    cd ..
    echo ""
fi

# Test 4: Verible lint
if command_exists verible-verilog-lint; then
    echo "Test 4: Verible lint"
    cd demo_alu
    verible-verilog-lint alu.sv 2>&1 | head -20
    echo -e "${GREEN}✓ Verible lint completed${NC}"
    cd ..
    echo ""
fi

# Test 5: Verible format
if command_exists verible-verilog-format; then
    echo "Test 5: Verible format (dry run)"
    cd demo_alu
    verible-verilog-format --column_limit=100 alu.sv > /tmp/alu_formatted.sv 2>&1
    echo -e "${GREEN}✓ Format check completed${NC}"
    cd ..
    echo ""
fi

# Test 6: Yosys synthesis
if command_exists yosys; then
    echo "Test 6: Yosys synthesis"
    cd demo_alu
    yosys -s alu_synth.ys 2>&1 | tail -30
    if [ -f alu_synth.v ]; then
        echo -e "${GREEN}✓ Synthesis successful${NC}"
    fi
    cd ..
    echo ""
fi

# Test 7: NgSpice simulation
if command_exists ngspice; then
    echo "Test 7: NgSpice simulation"
    cd demo_spice
    timeout 10 ngspice -b inverter.sp 2>&1 | tail -20
    echo -e "${GREEN}✓ SPICE simulation completed${NC}"
    cd ..
    echo ""
fi

# Test 8: Magic (batch mode)
if command_exists magic; then
    echo "Test 8: Magic layout"
    cd demo_layout
    timeout 10 magic -dnull -noconsole simple_layout.tcl 2>&1 | head -20
    echo -e "${GREEN}✓ Magic script executed${NC}"
    cd ..
    echo ""
fi

echo "========================================"
echo "Test Summary"
echo "========================================"
echo "Tests completed! Check output above for results."
echo ""
echo "Generated files:"
find . -type f \( -name "*.vvp" -o -name "*.vcd" -o -name "*_synth.*" -o -name "*.mag" -o -name "*.raw" \) -newer "$0" 2>/dev/null | while read file; do
    echo "  - $file"
done

echo ""
echo "To view waveforms (if generated):"
echo "  gtkwave demo_alu/alu_tb.vcd"
echo ""
echo "To use these examples in OpenHDL-IDE:"
echo "  1. Launch: python main.py"
echo "  2. Use Tools menu to access each tool"
echo "  3. Select appropriate files from demo_* directories"
echo ""
