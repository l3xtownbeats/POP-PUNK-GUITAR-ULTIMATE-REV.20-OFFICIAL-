#!/usr/bin/env node
"use strict";

// Deterministic SVG -> PNG renderer for the NEON STAGE production migration.
// The caller supplies the exact target dimensions; aspect ratio is preserved.
const fs = require("node:fs");
const { Resvg } = require("@resvg/resvg-js");

if (process.argv.length !== 6) {
  throw new Error("Usage: render_neon_stage_svg.cjs <input.svg> <output.png> <width> <height>");
}

const [, , inputPath, outputPath, widthArg, heightArg] = process.argv;
const width = Number.parseInt(widthArg, 10);
const height = Number.parseInt(heightArg, 10);
if (!Number.isInteger(width) || width < 1 || !Number.isInteger(height) || height < 1) {
  throw new Error("Target width and height must be positive integers");
}

const svg = fs.readFileSync(inputPath);
const renderer = new Resvg(svg, {
  fitTo: { mode: "width", value: width },
  font: { loadSystemFonts: true }
});
const png = renderer.render().asPng();
fs.mkdirSync(require("node:path").dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, png);
