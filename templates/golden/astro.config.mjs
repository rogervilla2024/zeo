// Astro configuration for sites scaffolded from templates/golden.
// The canonical site URL comes from site.config.json (the single source
// of truth every toolkit skill reads), so changing the config is enough.
import { readFileSync } from "node:fs";
import { defineConfig } from "astro/config";

const config = JSON.parse(
  readFileSync(new URL("./site.config.json", import.meta.url), "utf8"),
);

export default defineConfig({
  site: config.domain,
});
