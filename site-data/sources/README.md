# Interviews and media from other institutions

One file per inductee, named after the page: `einstein.json`, `cruz.json`, and so on. Each file
holds a list of sources that appear on that inductee's page under **Interviews and media from
other institutions**. You never need to touch any code to add one: copy an entry, change it,
and rebuild the site.

```sh
python3 tools/media_sources.py          # checks every file and says exactly what is wrong
python3 tools/build_site_pages.py       # draws them on the pages
```

## An entry

```json
{
  "id": "einstein-1940-radio-dialogue",
  "title": "Title of the clip, interview or article, as the holder gives it",
  "kind": "interview",
  "creator": "Name of the historian, interviewer or creator",
  "creator_role": "historian",
  "institution": "The museum, archive or broadcaster that holds it",
  "date": "1940",
  "url": "https://the-holders-own-page-for-this-item",
  "embed_url": "",
  "permission": "pending",
  "credit": "The credit line the holder asks for, word for word",
  "description": "One sentence: why this is worth a visitor's time."
}
```

| Field | Required | What to put |
|---|---|---|
| `id` | yes | Unique within the file: lowercase letters, digits, hyphens. Start it with the inductee's slug. |
| `title` | yes | The holder's own title for the item. |
| `kind` | yes | `video`, `audio`, `interview`, `oral-history`, `article` or `document`. |
| `creator`, `creator_role` | no | Who made it and in what role (`historian`, `interviewer`, `journalist`, `curator`...). |
| `institution` | yes | Who holds it. This is the attribution visitors see. |
| `date` | no | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. |
| `url` | yes | The `https://` address of the holder's page for this item. Visitors are always sent here. |
| `embed_url` | no | The player address, only once permission is `granted`. Allowed hosts: `www.youtube-nocookie.com`, `player.vimeo.com`, `archive.org`, `www.loc.gov`, `www.c-span.org` (list in `tools/media_sources.py`). |
| `permission` | yes | `pending`, `granted` or `link-only` (see below). |
| `credit` | no | The holder's required credit line, copied exactly. |
| `description` | no | One plain sentence. |
| `placeholder` | no | `true` only for layout examples. Placeholders are the only entries allowed to say `TODO`, and they are **never shown on the published site**: only in a preview build (`python3 tools/build_site_pages.py --preview`, or the local Visitor Voices demo). Rebuild without `--preview` before committing. |

## Permission

| `permission` | What the page does |
|---|---|
| `pending` | A request has gone out. Link to the holder only; nothing is embedded or copied here. |
| `link-only` | The holder lets us link but not embed or host. Link only, permanently. |
| `granted` | The holder has agreed in writing. If `embed_url` is set, the page shows a **Play** button and loads the player only when a visitor presses it. Without `embed_url` it is still a link. |

Change `pending` to `granted` only when the written permission is on file (see
`handover/MEDIA-PERMISSIONS.md` and `handover/PERMISSION-REQUEST-TEMPLATE.md`). The outreach is
done by people; nothing in this repository contacts anyone.

## Rules the checker enforces

- Unknown field names are refused, so a typo like `permision` cannot slip through.
- `url` must be `https://`. `embed_url` must be on an allowed host.
- No `TODO` anywhere unless the entry has `"placeholder": true`.
- Every `id` in a file is different.
- Every value is text in quotes (except `placeholder`, which is `true` or `false`).
