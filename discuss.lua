-- Adds a "Questions or objections?" note to every post, pointing readers to LinkedIn
-- (no comment box on the site), and a "Follow new posts" line (newsletter and RSS feed).
-- They go after the essay's last section, before "Read next", the disclaimer and the
-- sources or references. A post can drop the questions line with `discuss: false`.
local NEWSLETTER = "https://www.linkedin.com/newsletters/ai-honestly-7484605558868844544"
local PROFILE = "https://www.linkedin.com/in/st%C3%A9phane-cuenat-87116b5/"

local TEXT = {
  en = "**Questions or objections?** Reply under the [newsletter edition](" .. NEWSLETTER
    .. ") on LinkedIn, or [send me a message](" .. PROFILE
    .. "). Good questions often become the next essay.",
  fr = "**Des questions ou des objections ?** Répondez sous l'[édition de la newsletter](" .. NEWSLETTER
    .. ") sur LinkedIn (en anglais), ou [envoyez-moi un message](" .. PROFILE
    .. "). Les bonnes questions deviennent souvent l'essai suivant.",
}

local FOLLOW = {
  en = "**Follow new posts.** Subscribe to the [newsletter](" .. NEWSLETTER
    .. ") on LinkedIn, or to the [RSS feed](/index.xml). The [archive](/archive.html) lists recent changes.",
  fr = "**Suivre les nouveaux textes.** Abonnez-vous à la [newsletter](" .. NEWSLETTER
    .. ") sur LinkedIn (en anglais) ou au [flux RSS](/fr/index.xml). La page [Tous les textes](/fr/archive.html) liste les derniers changements.",
}

-- Headings that start the source list rather than the essay
local END_HEADINGS = {
  ["References"] = true, ["Références"] = true, ["Sources"] = true,
  ["Further reading"] = true, ["Pour aller plus loin"] = true,
}

local function ends_post(b)
  if b.t == "Div" then
    return b.identifier == "refs" or b.classes:includes("read-next") or b.classes:includes("small")
  end
  if b.t == "Header" then
    return END_HEADINGS[pandoc.utils.stringify(b)] == true
  end
  return false
end

function Pandoc(doc)
  local root, input = quarto.project.directory, quarto.doc.input_file
  if not root or not input then return nil end
  local rel = input:sub(#root + 2)
  local fr = rel:match("^fr/posts/") ~= nil
  if not (fr or rel:match("^posts/")) or not rel:match("index%.qmd$") then return nil end
  local lang = fr and "fr" or "en"
  local blocks = pandoc.Blocks({})
  if doc.meta.discuss ~= false then blocks:extend(pandoc.read(TEXT[lang], "markdown").blocks) end
  blocks:extend(pandoc.read(FOLLOW[lang], "markdown").blocks)

  local note = pandoc.Div(blocks, pandoc.Attr("", { "discuss" }))
  for i, b in ipairs(doc.blocks) do
    if ends_post(b) then
      doc.blocks:insert(i, note)
      return doc
    end
  end
  doc.blocks:insert(note)
  return doc
end
