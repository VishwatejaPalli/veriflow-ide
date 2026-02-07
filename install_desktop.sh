#!/bin/bash
# Install VeriFlow IDE desktop integration

set -e

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$HOME/.local/share/applications/veriflow-ide.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

echo "Installing VeriFlow IDE desktop integration..."

# Create icon directory if it doesn't exist
mkdir -p "$ICON_DIR"
mkdir -p "$(dirname "$DESKTOP_FILE")"

# Copy icon if it exists
if [ -f "$INSTALL_DIR/resources/icons/veriflow-ide.png" ]; then
    cp "$INSTALL_DIR/resources/icons/veriflow-ide.png" "$ICON_DIR/"
    echo "✓ Icon installed"
else
    echo "⚠ Warning: Icon not found at $INSTALL_DIR/resources/icons/veriflow-ide.png"
fi

# Create desktop file
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=VeriFlow IDE
Comment=Hardware Description Language Integrated Development Environment
Exec=python3 "$INSTALL_DIR/main.py"
Icon=veriflow-ide
Terminal=false
Categories=Development;IDE;Electronics;
Keywords=Verilog;SystemVerilog;HDL;FPGA;ASIC;EDA;
StartupWMClass=VeriFlow IDE
Path=$INSTALL_DIR
EOF

chmod +x "$DESKTOP_FILE"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications"
    echo "✓ Desktop database updated"
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    echo "✓ Icon cache updated"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "VeriFlow IDE should now appear in your application menu."
echo "You can also run it directly with:"
echo "  python3 $INSTALL_DIR/main.py"
echo ""
echo "To uninstall:"
echo "  rm $DESKTOP_FILE"
echo "  rm $ICON_DIR/veriflow-ide.png"
