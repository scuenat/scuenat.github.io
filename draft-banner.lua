-- Drafts (front matter `draft-preview: true`, set for /drafts and /fr/drafts in their _metadata.yml):
-- a "Draft" banner at the top of the page and a noindex tag. `noindex: true` alone adds only the tag
-- (the /drafts/ listing pages). Promoted posts lose both, because posts/_metadata.yml sets neither.
-- A draft's front matter carries `draft-version:` (1, 2, 3 ...) and `draft-revised:` (YYYY-MM-DD),
-- raised on every revision that is pushed; the banner shows both.
local function flag(meta, key)
  local v = meta[key]
  return v == true or (v ~= nil and pandoc.utils.stringify(v) == "true")
end

local fr_page = false
local draft = false
local version, revised = nil, nil

local MONTHS = {
  en = { "January", "February", "March", "April", "May", "June", "July", "August", "September",
         "October", "November", "December" },
  fr = { "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
         "octobre", "novembre", "décembre" },
}

local function long_date(iso, lang)
  local y, m, d = (iso or ""):match("^(%d%d%d%d)%-(%d%d)%-(%d%d)")
  if not y then return nil end
  local month = MONTHS[lang][tonumber(m)]
  return lang == "fr" and (tonumber(d) .. " " .. month .. " " .. y) or (month .. " " .. tonumber(d) .. ", " .. y)
end

function Meta(meta)
  draft = flag(meta, "draft-preview")
  if draft or flag(meta, "noindex") then
    quarto.doc.include_text("in-header", '<meta name="robots" content="noindex, nofollow">')
  end
  local input = quarto.doc.input_file or ""
  fr_page = input:match("/fr/drafts/") ~= nil
  version = meta["draft-version"] and pandoc.utils.stringify(meta["draft-version"]) or nil
  revised = meta["draft-revised"] and pandoc.utils.stringify(meta["draft-revised"]) or nil
end

function Pandoc(doc)
  if not draft then return nil end
  local v = version and (" v" .. version) or ""
  local when = long_date(revised, fr_page and "fr" or "en")
  local text = fr_page
    and ("**Brouillon" .. v .. ", non publié.** " .. (when and ("Révisé le " .. when .. ". ") or "")
         .. "Ce texte est en cours de relecture. Il n'est listé nulle part ailleurs sur le site et peut encore changer. [Tous les brouillons](/fr/drafts/).")
    or ("**Draft" .. v .. ", not yet published.** " .. (when and ("Revised " .. when .. ". ") or "")
         .. "This piece is under review. It is not listed anywhere else on the site and may still change. [All drafts](/drafts/).")
  local banner = pandoc.Div(pandoc.read(text, "markdown").blocks,
    pandoc.Attr("", { "draft-banner" }))
  table.insert(doc.blocks, 1, banner)
  return doc
end

return { { Meta = Meta }, { Pandoc = Pandoc } }
