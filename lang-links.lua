-- Pairs each page with its French (fr/...) or English counterpart when that page exists:
-- hreflang links for search engines, and a meta tag the navbar language switch reads.
local SITE = "https://scuenat.github.io/"

local function exists(path)
  local f = io.open(path, "r")
  if f then f:close() return true end
  return false
end

-- Directory form (/posts/x/), the same URL as the canonical link and the sitemap.
local function html(p)
  return (p:gsub("%.qmd$", ".html"):gsub("index%.html$", ""))
end

function Meta(meta)
  local root, input = quarto.project.directory, quarto.doc.input_file
  if not root or not input then return nil end
  local rel = input:sub(#root + 2)
  local en, fr
  if rel:sub(1, 3) == "fr/" then en, fr = rel:sub(4), rel else en, fr = rel, "fr/" .. rel end
  local other = (rel == fr) and en or fr
  if rel:match("404%.qmd$") or not exists(root .. "/" .. other) then return nil end
  quarto.doc.include_text("in-header", table.concat({
    '<link rel="alternate" hreflang="en" href="' .. SITE .. html(en) .. '">',
    '<link rel="alternate" hreflang="fr" href="' .. SITE .. html(fr) .. '">',
    '<link rel="alternate" hreflang="x-default" href="' .. SITE .. html(en) .. '">',
    '<meta name="alt-lang-url" content="/' .. html(other) .. '">',
  }, "\n"))
end
