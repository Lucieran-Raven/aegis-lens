#!/bin/bash

# Physics Engine Build Script
# Builds the unified WASM module for all 4 physics pipelines

set -e

echo "Building Physics Engine WASM module..."

# Check if wasm-pack is installed
if ! command -v wasm-pack &> /dev/null; then
    echo "Installing wasm-pack..."
    cargo install wasm-pack
fi

# Check if wasm32 target is installed
if ! rustup target list --installed | grep -q wasm32-unknown-unknown; then
    echo "Adding wasm32-unknown-unknown target..."
    rustup target add wasm32-unknown-unknown
fi

# Build the WASM module
echo "Building with wasm-pack..."
wasm-pack build --target web --out-dir pkg --release

echo "Build complete!"
echo "WASM module location: pkg/physics_engine_bg.wasm"

# Display bundle size
if [ -f "pkg/physics_engine_bg.wasm" ]; then
    SIZE=$(du -h pkg/physics_engine_bg.wasm | cut -f1)
    echo "Bundle size: $SIZE"
fi
