#!/bin/bash
set -e

echo "Building CHRONOS WASM..."

# Check if wasm-pack is installed
if ! command -v wasm-pack &> /dev/null; then
    echo "wasm-pack not found. Installing..."
    cargo install wasm-pack
fi

# Check if wasm32-unknown-unknown target is installed
if ! rustup target list --installed | grep -q wasm32-unknown-unknown; then
    echo "Adding wasm32-unknown-unknown target..."
    rustup target add wasm32-unknown-unknown
fi

# Build WASM
echo "Building with wasm-pack..."
wasm-pack build --target web --out-dir pkg --release

echo "CHRONOS WASM build complete!"
echo "Output: pkg/"
