-- Drafts (front matter `draft-preview: true`, set for /drafts and /fr/drafts in their _metadata.yml):
-- a "Draft" banner at the top of the page and a noindex tag. `noindex: true` alone adds only the tag
-- (the /drafts/ listing pages). Promoted posts lose both, because posts/_metadata.yml sets neither.
local function flag(meta, key)
  local v = meta[key]
  return v == true or (v ~= nil and pandoc.utils.stringify(v) == "true")
end

local fr_page = false
local draft = false

function Meta(meta)
  draft = flag(meta, "draft-preview")
  if draft or flag(meta, "noindex") then
    quarto.doc.include_text("in-header", '<meta name="robots" content="noindex, nofollow">')
  end
  local input = quarto.doc.input_file or ""
  fr_page = input:match("/fr/drafts/") ~= nil
end

function Pandoc(doc)
  if not draft then return nil end
  local text = fr_page
    and "**Brouillon, non publié.** Ce texte est en cours de relecture. Il n'est listé nulle part ailleurs sur le site et peut encore changer. [Tous les brouillons](/fr/drafts/)."
    or "**Draft, not yet published.** This piece is under review. It is not listed anywhere else on the site and may still change. [All drafts](/drafts/)."
  local banner = pandoc.Div(pandoc.read(text, "markdown").blocks,
    pandoc.Attr("", { "callout-important", "draft-banner" }, { appearance = "simple" }))
  table.insert(doc.blocks, 1, banner)
  return doc
end

return { { Meta = Meta }, { Pandoc = Pandoc } }
