#!/usr/bin/env node
"use strict";

// Persistent Resvg worker. Keeping one process alive avoids repeatedly loading
// the native renderer and system font database for every 1x/2x/3x variant.
const fs = require("node:fs");
const path = require("node:path");
const readline = require("node:readline");
const { Resvg } = require("@resvg/resvg-js");

const input = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
input.on("line", (line) => {
  let request;
  try {
    request = JSON.parse(line);
    if (request.quit === true) {
      input.close();
      process.exit(0);
    }
    const { source, output, width, height } = request;
    if (!source || !output || !Number.isInteger(width) || width < 1 ||
        !Number.isInteger(height) || height < 1) {
      throw new Error("Invalid render request");
    }
    const svg = fs.readFileSync(source);
    const renderer = new Resvg(svg, {
      fitTo: { mode: "width", value: width },
      font: { loadSystemFonts: true }
    });
    const png = renderer.render().asPng();
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, png);
    process.stdout.write(JSON.stringify({ ok: true }) + "\n");
  } catch (error) {
    process.stdout.write(JSON.stringify({ ok: false, error: String(error && error.stack || error) }) + "\n");
  }
});
