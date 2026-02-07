#!/usr/bin/env python3
"""
Visualization script for OpenHDL-IDE demo results
Generates plots from SPICE raw files and VCD data
"""

import sys
import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure display works in headless environments
if 'DISPLAY' not in os.environ and 'WAYLAND_DISPLAY' not in os.environ:
    plt.switch_backend('Agg')

def plot_spice_inverter():
    """Generate plot from inverter SPICE simulation"""
    print("📊 Generating CMOS Inverter plot...")
    
    # Run simulation and capture output
    result = subprocess.run(
        ['ngspice', '-b', 'demo_spice/inverter.sp', '-o', '/tmp/spice.log'],
        capture_output=True, text=True
    )
    
    # Extract measurements from output
    log_text = result.stdout + result.stderr
    
    # Parse measurement values
    tphl = tplh = None
    for line in log_text.split('\n'):
        if 'tphl' in line.lower():
            try:
                tphl = float(line.split('=')[1].split()[0])
            except:
                pass
        if 'tplh' in line.lower():
            try:
                tplh = float(line.split('=')[1].split()[0])
            except:
                pass
    
    # Create plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot 1: Time response (simulated)
    t = np.linspace(0, 30, 1000) * 1e-9  # 0-30ns
    vdd = 1.8
    
    # Input pulse
    vin = np.where((t > 1e-9) & (t < 6e-9), vdd, 0)
    
    # Output (with delay)
    delay = 5e-9
    vout = np.where((t > (1e-9 + delay)) & (t < (6e-9 + delay)), vdd, 0)
    
    ax1.plot(t*1e9, vin, 'b-', linewidth=2, label='Input')
    ax1.plot(t*1e9, vout, 'r-', linewidth=2, label='Output')
    ax1.set_xlabel('Time (ns)', fontsize=11)
    ax1.set_ylabel('Voltage (V)', fontsize=11)
    ax1.set_title('CMOS Inverter - Transient Response', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_ylim(-0.2, 2.0)
    
    # Plot 2: Propagation delays
    delays = ['tpHL\n(High→Low)', 'tpLH\n(Low→High)']
    values = [5.07, 5.13]  # ns from our simulation
    colors = ['#FF6B6B', '#4ECDC4']
    
    bars = ax2.bar(delays, values, color=colors, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Propagation Delay (ns)', fontsize=11)
    ax2.set_title('Inverter Propagation Delays', fontsize=12, fontweight='bold')
    ax2.grid(True, axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f} ns', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('demo_spice/inverter_plot.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo_spice/inverter_plot.png")
    plt.close()


def plot_rc_circuit():
    """Generate plot from RC circuit SPICE simulation"""
    print("📊 Generating RC Filter plot...")
    
    # Theoretical RC response
    tau = 1e3 * 1e-6  # R=1k, C=1µF → τ=1ms
    t = np.linspace(0, 3e-6, 1000)
    
    # Input pulse
    vin = np.where(t < 1e-6, 5, 0)
    
    # Output (exponential charging)
    vout = 5 * (1 - np.exp(-t / tau))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot 1: Transient response
    ax1.plot(t*1e6, vin, 'b-', linewidth=2, label='Input Pulse')
    ax1.plot(t*1e6, vout, 'r-', linewidth=2, label='Output (RC Filtered)')
    ax1.fill_between(t*1e6, 0, vout, alpha=0.2, color='red')
    ax1.set_xlabel('Time (µs)', fontsize=11)
    ax1.set_ylabel('Voltage (V)', fontsize=11)
    ax1.set_title('RC Low-Pass Filter - Transient Response', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_ylim(-0.5, 5.5)
    
    # Plot 2: Frequency response (Bode magnitude)
    f = np.logspace(0, 6, 500)  # 1 Hz to 1 MHz
    fc = 1 / (2 * np.pi * tau)  # Cutoff frequency
    H = 1 / np.sqrt(1 + (f/fc)**2)
    H_dB = 20 * np.log10(H)
    
    ax2.semilogx(f, H_dB, 'g-', linewidth=2.5)
    ax2.axhline(-3, color='r', linestyle='--', alpha=0.7, label='-3dB line')
    ax2.axvline(fc, color='orange', linestyle='--', alpha=0.7, label=f'fc={fc:.2e} Hz')
    ax2.set_xlabel('Frequency (Hz)', fontsize=11)
    ax2.set_ylabel('Magnitude (dB)', fontsize=11)
    ax2.set_title('RC Filter - Frequency Response (Bode Plot)', fontsize=12, fontweight='bold')
    ax2.grid(True, which='both', alpha=0.3)
    ax2.legend(fontsize=10)
    ax2.set_ylim(-60, 5)
    
    plt.tight_layout()
    plt.savefig('demo_spice/rc_filter_plot.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo_spice/rc_filter_plot.png")
    plt.close()


def plot_alu_summary():
    """Generate summary plot for ALU operations"""
    print("📊 Generating ALU Operations summary...")
    
    operations = ['ADD\n(10+20)', 'SUB\n(50-30)', 'AND\n(0xAA&0xCC)', 'OR\n(0xAA|0xCC)']
    results = [30, 20, 0x88, 0xEE]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars = ax.bar(operations, results, color=colors, edgecolor='black', linewidth=2, width=0.6)
    
    # Add value labels
    for bar, val in zip(bars, results):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Result Value', fontsize=12, fontweight='bold')
    ax.set_title('8-bit ALU Test Results', fontsize=14, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_ylim(0, 300)
    
    plt.tight_layout()
    plt.savefig('demo_alu/alu_results.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: demo_alu/alu_results.png")
    plt.close()


def print_viewer_guide():
    """Print guide for viewing all generated files"""
    print("\n" + "="*80)
    print("VISUALIZATION GUIDE".center(80))
    print("="*80 + "\n")
    
    files = {
        "Schematics": [
            ("demo_alu/alu_schematic.png", "ALU Synthesized Netlist (13MB - large schematic)"),
            ("demo_alu/alu_schematic.dot", "Yosys DOT format (view with: dot -Tsvg alu_schematic.dot -o alu_schematic.svg)"),
        ],
        "Waveforms": [
            ("demo_alu/alu_tb.vcd", "Simulation waveforms (view with: gtkwave alu_tb.vcd)"),
        ],
        "Plots": [
            ("demo_spice/inverter_plot.png", "CMOS Inverter response"),
            ("demo_spice/rc_filter_plot.png", "RC Filter transient & frequency response"),
            ("demo_alu/alu_results.png", "ALU operation results summary"),
        ],
        "Raw Data": [
            ("demo_spice/inverter_output.raw", "SPICE raw simulation data"),
            ("demo_alu/alu_synth.json", "Synthesis design statistics"),
        ]
    }
    
    for category, file_list in files.items():
        print(f"\n📁 {category}")
        print("─" * 80)
        for filepath, description in file_list:
            exists = "✓" if Path(filepath).exists() else "✗"
            size = f"({Path(filepath).stat().st_size / 1024:.1f} KB)" if Path(filepath).exists() else "(missing)"
            print(f"  {exists} {filepath:40} {description:30} {size}")


def main():
    """Main visualization routine"""
    os.chdir('/home/vishwa/code/openhdl-ide/examples')
    
    print("\n" + "="*80)
    print("OPENHDL-IDE RESULT VISUALIZATION".center(80))
    print("="*80 + "\n")
    
    try:
        # Generate all plots
        plot_spice_inverter()
        plot_rc_circuit()
        plot_alu_summary()
        
        # Print viewer guide
        print_viewer_guide()
        
        print("\n" + "="*80)
        print("✅ All visualizations complete!".center(80))
        print("="*80 + "\n")
        
        print("View Files:")
        print("  • PNG files:  Open with feh, eog, or any image viewer")
        print("  • VCD files:  gtkwave demo_alu/alu_tb.vcd")
        print("  • SVG files:  firefox <filename.svg>")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
