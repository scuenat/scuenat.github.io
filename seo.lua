-- Search metadata for every page: a canonical URL, and schema.org JSON-LD
-- (an article for posts, the person for About, the site for the home pages).
-- URLs use the directory form (/posts/x/), like hreflang links and the sitemap.
local SITE = "https://scuenat.github.io/"
local SITE_NAME = "AI, Honestly"
local AUTHOR = {
  ["@type"] = "Person",
  name = "Stéphane Cuenat",
  url = SITE .. "about.html",
  sameAs = { "https://www.linkedin.com/in/st%C3%A9phane-cuenat-87116b5/" },
}

local function clean(p)
  return (p:gsub("%.qmd$", ".html"):gsub("index%.html$", ""))
end

-- Resolve a path relative to the page's folder, e.g. ../../../posts/x/figures/fig01.png
local function resolve(dir, path)
  if path:match("^https?://") then return path end
  local parts = {}
  local full = path:sub(1, 1) == "/" and path:sub(2) or (dir ~= "" and dir .. "/" .. path or path)
  for part in full:gmatch("[^/]+") do
    if part == ".." then table.remove(parts)
    elseif part ~= "." then table.insert(parts, part) end
  end
  return SITE .. table.concat(parts, "/")
end

local function json(v)
  local t = type(v)
  if t == "string" then
    return '"' .. v:gsub('[%c"\\]', function(c)
      local map = { ['"'] = '\\"', ["\\"] = "\\\\", ["\n"] = "\\n", ["\r"] = "\\r", ["\t"] = "\\t" }
      return map[c] or string.format("\\u%04x", c:byte())
    end) .. '"'
  elseif t == "table" then
    if #v > 0 then
      local out = {}
      for _, x in ipairs(v) do table.insert(out, json(x)) end
      return "[" .. table.concat(out, ",") .. "]"
    end
    local keys = {}
    for k in pairs(v) do table.insert(keys, k) end
    table.sort(keys)
    local out = {}
    for _, k in ipairs(keys) do table.insert(out, json(k) .. ":" .. json(v[k])) end
    return "{" .. table.concat(out, ",") .. "}"
  end
  return tostring(v)
end

local function str(x)
  return x and pandoc.utils.stringify(x) or nil
end

-- The ISO date from the source front matter (meta.date is already formatted for display).
local function source_date(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local text = f:read("*a")
  f:close()
  return text:match("\ndate:%s*[\"']?(%d%d%d%d%-%d%d%-%d%d)")
end

local function exists(path)
  local f = io.open(path, "r")
  if f then f:close() return true end
  return false
end

function Meta(meta)
  local root, input = quarto.project.directory, quarto.doc.input_file
  if not root or not input then return nil end
  local rel = input:sub(#root + 2)
  if rel:match("404%.qmd$") then return nil end
  local url = SITE .. clean(rel)
  local fr = rel:sub(1, 3) == "fr/"
  local lang = fr and "fr" or "en"
  local dir = rel:match("^(.*)/[^/]*$") or ""
  local title, description = str(meta.title), str(meta.description)

  local data
  if rel:match("^posts/") or rel:match("^fr/posts/") then
    local paper = false
    for _, c in ipairs(meta.categories or {}) do
      local s = str(c)
      if s == "paper" or s == "article" then paper = true end
    end
    local keywords = {}
    for _, c in ipairs(meta.categories or {}) do table.insert(keywords, str(c)) end
    data = {
      ["@context"] = "https://schema.org",
      ["@type"] = paper and "ScholarlyArticle" or "BlogPosting",
      headline = title,
      description = description,
      datePublished = source_date(input),
      author = AUTHOR,
      publisher = AUTHOR,
      image = meta.image and resolve(dir, str(meta.image)) or SITE .. "social-card.jpg",
      inLanguage = lang,
      url = url,
      mainEntityOfPage = url,
      keywords = #keywords > 0 and keywords or nil,
      isPartOf = { ["@type"] = "Blog", name = SITE_NAME, url = SITE },
      license = "https://creativecommons.org/licenses/by/4.0/",
    }
    local other = fr and rel:sub(4) or "fr/" .. rel
    if exists(root .. "/" .. other) then
      data[fr and "translationOfWork" or "workTranslation"] = { ["@id"] = SITE .. clean(other) }
    end
  elseif rel == "agentic-coding.qmd" or rel == "fr/agentic-coding.qmd"
    or rel == "research.qmd" or rel == "fr/research.qmd" then
    data = { ["@context"] = "https://schema.org", ["@type"] = "CollectionPage", name = title,
             description = description, url = url, inLanguage = lang, author = AUTHOR,
             isPartOf = { ["@type"] = "Blog", name = SITE_NAME, url = SITE } }
  elseif rel == "about.qmd" or rel == "fr/about.qmd" then
    data = { ["@context"] = "https://schema.org", ["@type"] = "ProfilePage", url = url,
             inLanguage = lang, mainEntity = AUTHOR }
  elseif rel == "index.qmd" or rel == "fr/index.qmd" then
    data = { ["@context"] = "https://schema.org", ["@type"] = "WebSite", name = SITE_NAME, url = url,
             description = description, inLanguage = lang, author = AUTHOR }
  end

  local head = { '<link rel="canonical" href="' .. url .. '">' }
  if data then
    table.insert(head, '<script type="application/ld+json">' .. json(data) .. "</script>")
  end
  quarto.doc.include_text("in-header", table.concat(head, "\n"))
end
