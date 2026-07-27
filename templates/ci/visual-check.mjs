// Visual + console gate helper for the visual-review skill.
//
// Serves the build output, opens each page at mobile/tablet/desktop
// widths through Chromium (Chrome DevTools Protocol via Playwright),
// captures full-page screenshots into shots/, and collects everything
// DevTools would show in the console: JS errors, page exceptions, and
// failed network requests. Any of those is a hard failure - a site
// does not pass visual-review while its console is red.
//
// Usage (from the site root, after `npm run build`):
//   npm i -D playwright   # once; browsers ship with the environment
//   node <toolkit>/templates/ci/visual-check.mjs / /blog/ /some-article/
//
// Exits 0 when every page is clean, 1 when any console error, page
// error, or failed request was seen. Screenshots land in shots/.
import { createServer } from "node:http";
import { existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createRequire } from "node:module";
import { extname, join } from "node:path";

// Resolve playwright from the SITE being checked (the cwd), not from
// the toolkit checkout this script lives in.
const require = createRequire(join(process.cwd(), "package.json"));
const { chromium } = require("playwright");

const DIST = process.env.DIST_DIR || "./dist";
const PORT = Number(process.env.PORT || 4599);
const WIDTHS = [
  ["mobile", 390],
  ["tablet", 768],
  ["desktop", 1440],
];
const TYPES = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".xml": "application/xml",
  ".txt": "text/plain",
  ".json": "application/json",
  ".webmanifest": "application/manifest+json",
};

const pages = process.argv.slice(2);
if (pages.length === 0) pages.push("/");

const server = createServer((req, res) => {
  let path = join(DIST, decodeURIComponent(req.url.split("?")[0]));
  if (existsSync(path) && statSync(path).isDirectory()) {
    path = join(path, "index.html");
  }
  if (!existsSync(path)) {
    res.writeHead(404);
    res.end("not found");
    return;
  }
  res.writeHead(200, {
    "content-type": TYPES[extname(path)] || "application/octet-stream",
  });
  res.end(readFileSync(path));
});
await new Promise((resolve) => server.listen(PORT, resolve));

// The environment preinstalls Chromium; fall back to the pinned path
// when the npm playwright version does not match the browser build.
let browser;
try {
  browser = await chromium.launch();
} catch {
  browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium",
  });
}

mkdirSync("shots", { recursive: true });
const problems = [];

for (const path of pages) {
  for (const [label, width] of WIDTHS) {
    const page = await browser.newPage({ viewport: { width, height: 950 } });
    page.on("console", (message) => {
      if (message.type() === "error") {
        problems.push(`console error @ ${path} (${label}): ${message.text()}`);
      }
    });
    page.on("pageerror", (error) => {
      problems.push(`page error @ ${path} (${label}): ${error.message}`);
    });
    page.on("requestfailed", (request) => {
      problems.push(
        `request failed @ ${path} (${label}): ${request.url()} ` +
          `(${request.failure()?.errorText ?? "unknown"})`
      );
    });
    const response = await page.goto(`http://localhost:${PORT}${path}`, {
      waitUntil: "networkidle",
    });
    if (!response || response.status() >= 400) {
      problems.push(`HTTP ${response?.status() ?? "?"} @ ${path}`);
    }
    const slug = path === "/" ? "home" : path.replaceAll("/", "-").replace(/^-|-$/g, "");
    await page.screenshot({ path: `shots/${slug}-${label}.png`, fullPage: true });
    await page.close();
  }
}

await browser.close();
server.close();

if (problems.length > 0) {
  console.error(`\n${problems.length} problem(s):`);
  for (const problem of problems) console.error("  FAIL " + problem);
  process.exit(1);
}
console.log(`Clean: ${pages.length} page(s) x ${WIDTHS.length} widths, no console/page/network errors. Screenshots in shots/.`);
