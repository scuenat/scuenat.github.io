-- Shows readers when a published post changed in a way that matters.
-- A post lists its revisions in front matter, newest first or in any order:
--
--   updates:
--     - date: 2026-11-03
--       note: "Added section 4 on what the model cannot see."
--
-- The filter adds an "Updated on …" note near the top of the post (after the opening
-- callout) and sets `date-modified` to the latest update, so the title block shows it
-- (formatted like the site's dates: "November 3, 2026", "3 novembre 2026").
-- The archive pages list the same entries under "Recent changes" (recent-changes.ejs).
-- Typo fixes and small edits get no entry.

local MONTHS = {
  en = { "January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December" },
  fr = { "janvier", "février", "mars", "avril", "mai", "juin", "juillet",
         "août", "septembre", "octobre", "novembre", "décembre" },
}

local function fmt(iso, lang)
  local y, m, d = iso:match("^(%d%d%d%d)-(%d%d)-(%d%d)")
  if not y then return iso end
  d, m = tonumber(d), tonumber(m)
  if lang == "fr" then return (d == 1 and "1er" or tostring(d)) .. " " .. MONTHS.fr[m] .. " " .. y end
  return MONTHS.en[m] .. " " .. d .. ", " .. y
end

local function entries(meta)
  local list = {}
  if type(meta.updates) ~= "table" then return list end
  for _, u in ipairs(meta.updates) do
    local date = u.date and pandoc.utils.stringify(u.date) or ""
    local note = u.note and pandoc.utils.stringify(u.note) or ""
    if date:match("^%d%d%d%d%-%d%d%-%d%d") then table.insert(list, { date = date:sub(1, 10), note = note }) end
  end
  table.sort(list, function(a, b) return a.date > b.date end)
  return list
end

function Pandoc(doc)
  local root, input = quarto.project.directory, quarto.doc.input_file
  if not root or not input then return nil end
  local rel = input:sub(#root + 2)
  local fr = rel:match("^fr/posts/") ~= nil
  if not (fr or rel:match("^posts/")) or not rel:match("index%.qmd$") then return nil end

  local list = entries(doc.meta)
  if #list == 0 then return nil end
  local lang = fr and "fr" or "en"

  -- Quarto formats dates before user filters run, so format this one the same way.
  doc.meta["date-modified"] = pandoc.MetaString(fmt(list[1].date, lang))

  local blocks = pandoc.Blocks({})
  for _, u in ipairs(list) do
    local label = (fr and "Mis à jour le " or "Updated on ") .. fmt(u.date, lang) .. "."
    local md = "**" .. label .. "**"
    if u.note ~= "" then md = md .. " " .. u.note end
    blocks:extend(pandoc.read(md, "markdown").blocks)
  end
  local note = pandoc.Div(blocks, pandoc.Attr("", { "post-updates" }))

  -- After the opening callout (and a series note) when there is one, otherwise first.
  local at = 1
  for i, b in ipairs(doc.blocks) do
    -- Quarto turns callouts into custom nodes before user filters run.
    local callout = b.t == "Div" and b.attributes and b.attributes.__quarto_custom_type == "Callout"
    if callout or (b.t == "Div" and b.classes:includes("series-note")) then
      at = i + 1
    else
      break
    end
  end
  doc.blocks:insert(at, note)
  return doc
end
