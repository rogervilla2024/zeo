// URL slugs for category names. Category names come from the topic
// map in the site's own language; URLs must stay lowercase ASCII.
// Latin diacritics fold via NFD (c-cedilla, g-breve, o/u-umlaut...);
// Turkish dotless i (U+0131) never decomposes, so it needs an
// explicit map, and capital dotted I (U+0130) lowercases into i plus
// a combining mark that the mark strip then removes.
export function slugify(value: string): string {
  return value
    .replace(/[\u0130\u0131]/g, "i")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
