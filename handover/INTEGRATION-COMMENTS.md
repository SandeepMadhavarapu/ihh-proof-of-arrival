# Visitor Voices on WordPress: Margin Notes and "Spot something? Tell us"

This kit adds visitor notes to the inductee pages and a "Report or add to this claim" button to
the Verify page, using **WordPress's own comments**. Every note arrives as a **pending comment**.
Nothing appears on the site until someone approves it in **WP Admin → Comments**.

What you need: one script (`margin-notes.js`), one stylesheet (`margin-notes.css`), a few
`data-` attributes, and two Discussion settings. **No plugin is needed** for the recommended
path. One optional extra, described at the end, would need a small code snippet, which is
effectively a plugin. We say so plainly there.

Nothing here was tried on IHH's live site. These steps follow WordPress's developer
documentation, linked at each step. Try them on a staging copy first.

---

## How it works (no plugin)

- **Sending.** The script posts the note to WordPress's standard comment handler,
  `wp-comments-post.php`. This is the same handler a theme's comment form uses.
  `wp_handle_comment_submission()` "Handles the submission of a comment, usually posted to
  wp-comments-post.php via a comment form". It reads the fields `comment_post_ID`, `author`,
  `email`, `url` and `comment`.
  ([reference](https://developer.wordpress.org/reference/functions/wp_handle_comment_submission/))
- **Where the note belongs.** The first lines of the comment text record it. Example:

  ```
  [ihh-note v1 kind=note type=wrong page=muir anchor=muir-a-farm-boy-from-dunbar-5f55a0]
  Quote: John Muir was born in Dunbar, Scotland, on 21 April 1838
  After: In 1849 his family emigrated to
  Source: (what the visitor gave, if anything)
  =====
  (the visitor's note)
  ```

  The `Quote`/`Before`/`After` lines are a W3C TextQuoteSelector
  (<https://www.w3.org/TR/annotation-model/#text-quote-selector>). If you later edit the
  paragraph, the note can still find its place.
- **Showing approved notes.** The script reads approved comments from the public REST API,
  `GET /wp-json/wp/v2/comments?post=<ID>`. That endpoint's `status` argument defaults to
  `approve`, so pending and spam comments are not returned.
  ([reference](https://developer.wordpress.org/rest-api/reference/comments/))
  The script draws a small count in the margin, an expandable "N visitor comments on this section"
  thread directly under the passage (with the passage quoted), and a "Notes on this page" list. It writes every
  word as plain text and never as HTML, never makes a visitor's link clickable, and shows only
  a first name (or "A visitor") and the date. Emails are never shown.

---

## Step by step

### 1. Discussion settings (WP Admin → Settings → Discussion)

From [the Discussion Settings screen](https://wordpress.org/documentation/article/settings-discussion-screen/):

- **Tick "An administrator must always approve the comment".** This is what keeps every note
  pending until a person approves it. Do not skip it.
- **Untick "Comment author must fill out name and e-mail".** This makes name and email
  optional, as the young-visitor rules require. It is a site-wide setting and also affects
  ordinary comments. If IHH cannot change it site-wide, leave it ticked. The script still
  sends name and email when the visitor gives them, but visitors who leave them out will
  have their note refused by WordPress.

### 2. Allow comments on each page that uses notes

Open the page in the editor → **Discussion** panel → **Allow comments**.

### 3. Put the two files on the site

Copy `site/assets/margin-notes.js` and `site/assets/margin-notes.css` from this repository to a
folder your site serves, for example `wp-content/uploads/ihh-voices/` (upload it with your
host's file manager or SFTP). The Media Library may refuse `.js` files, so a file manager is
the reliable route. **Do not copy `voices/demo_adapter.js`.** It is for the local demo only.

### 4. Wrap the profile and add the two tags

In the page's **Custom HTML** block (the one holding the profile from `handover/<slug>/copy.html`),
put this wrapper around the pasted profile:

```html
<link rel="stylesheet" href="/wp-content/uploads/ihh-voices/margin-notes.css">
<div data-ihh-notes="wordpress"
     data-ihh-page="muir"
     data-ihh-wp="https://YOUR-SITE.example"
     data-ihh-post="PAGE-ID"
     data-ihh-scheme="auto">

  ... the whole of handover/muir/copy.html, unchanged ...

</div>
<script src="/wp-content/uploads/ihh-voices/margin-notes.js" defer></script>
```

- `data-ihh-page`: the inductee's slug (`muir`, `pei`, …), or `verify` on the Verify page.
- `data-ihh-wp`: your site's address, no trailing slash. The script must run on the same site,
  because it posts to that site's own comment handler.
- `data-ihh-post`: the page's ID (the number in `post=` when you edit the page).
- `data-ihh-scheme="auto"`: follow the visitor's light or dark setting. Remove it if your theme
  is light-only.

The profile HTML already carries a stable id on every paragraph, fact, quote and caption, for
example `id="muir-a-farm-boy-from-dunbar-5f55a0" data-ihh-anchor`. `tools/build_profile.py`
generates these ids, so do not edit them by hand.

Some WordPress roles cannot save `<script>` tags in a Custom HTML block. If yours cannot, ask
a site administrator to add the one `<script>` line for you.

### 5. Verify page

The Verify page's "Report or add to this claim" buttons and the "Spot something? Tell us"
form are built into `site/verify.html` when notes are switched on. To use them on WordPress,
put the same wrapper (with `data-ihh-page="verify"`) around the Verify page content. Reports
arrive as pending comments on that page, with `kind=claim` or `kind=tip` in the first line.

After a visitor records their own verdict on a claim, a **Share my finding with the museum**
button appears. It sends a comment whose first line reads `kind=finding ... anchor=<claim id>
verdict=confirmed|unsupported|contradicted`; the comment text is optional. Set
`wordpress.post_ids.verify` in `site-data/visitor-voices.json` to the Verify page's post ID, and
approved findings are read back and shown under their claim as a tally ("2 visitor findings:
1 Confirmed · 1 Contradicted") that expands to the comments.

### 6. Moderating (WP Admin → Comments)

- **Pending** holds every new note and report. Read the first line to see which passage or claim
  it is about.
- **Approve** publishes a margin note, or a Verify finding (`kind=finding`). Reports from the
  Verify page (`kind=claim` and `kind=tip`) are never drawn on the page, even when approved.
  Approving one just means "dealt with".
- **Trash or Spam** for anything else. Do not approve a note that contains a full name, school,
  address or any contact details of a young visitor. Reject it, or edit those details out first.
- **Living Museum.** If an "I know more" or "Something looks wrong" report gives a source, a
  curator can hand it to the Living Museum as a *tip*. Save the comment's fields as a JSON
  file (see `voices/core.py` for the shape), then run
  `python -m voices.bridge item.json --store living/proposals`.
  A tip is not copy. The curator still has to find an exact sentence in a trusted source and
  file a normal fact proposal, which goes through the same five gates as every other fact.
  Visitor text never goes into `copy.md`.

### 7. Your theme's own comment list

Approved notes are ordinary approved comments, so many themes will also list them under the
page, including the `[ihh-note …]` line. If you do not want that, close the theme's comment
list on these pages (theme setting or a line of theme CSS), and keep comments open so the
script can still post.

### Without JavaScript

The margin buttons need JavaScript. Without it, a visitor can use the theme's normal comment
form at the end of the page. That form cannot know which paragraph they mean, so they have to
say so in the text. The static site (`site/`) has the same rule: it shows no note controls at
all unless notes are switched on (`site-data/visitor-voices.json`).

---

## How to turn it off

Do any one of these:

- Remove the `<script>` line from the page. Approved notes stay in WP Admin.
- Change `data-ihh-notes="wordpress"` to `data-ihh-notes="none"`.
- Close comments on the page (Discussion panel).

To remove everything, also delete the two files from `wp-content/uploads/ihh-voices/`.

---

## Young visitors: privacy note for IHH

- **Name and email are optional.** Every form shows: "If you are under 13, please don't
  include your name, email, school or anything else that identifies you. Just tell us what you
  know." No age is asked and no attempt is made to identify anyone.
- **Nothing is public until a person approves it.** The script only ever reads approved
  comments.
- **Emails are never shown** by the script. Any email address typed into a note is shown as
  "[email removed]". No visitor link is ever clickable.
- **What WordPress keeps.** WordPress stores each comment, including any name and email given,
  in its database, along with technical details such as the sender's IP address. Mention notes
  in IHH's privacy policy, delete rejected notes regularly, and do not export comment emails to
  any other system.
- **Spam and floods.** The script refuses to send when the hidden "leave this empty" field is
  filled (bots fill it) and allows three notes per page visit every ten minutes. These are
  in-browser checks only. With no plugin, WordPress's own comment checks are the server-side
  protection. The local demo enforces the honeypot and a five-per-ten-minutes limit on the
  server.

---

## The optional extra (needs code, so effectively a plugin)

The no-plugin path keeps the passage and selector inside the comment text. Storing them as
separate **comment meta**, or accepting notes through `POST /wp/v2/comments` instead of
`wp-comments-post.php`, needs PHP code:

- Anonymous REST comments are off unless code enables them. The filter
  `rest_allow_anonymous_comments` has "Default false".
  ([reference](https://developer.wordpress.org/reference/hooks/rest_allow_anonymous_comments/))
- Comment meta is visible to the REST API only after `register_meta( 'comment', $key, array(
  'show_in_rest' => true, … ) )`.
  ([reference](https://developer.wordpress.org/reference/functions/register_meta/))
- The REST endpoint accepts `author_name`, `author_email`, `content`, `post`, `status` and `meta`.
  ([reference](https://developer.wordpress.org/rest-api/reference/comments/))

Options, honestly ranked:

1. **Recommended: stay with the no-plugin path above.** It works today with two settings.
2. A **small site-specific plugin** (one PHP file) that registers `ihh_anchor` and `ihh_selector`
   comment meta. A developer must write and review it. It is not included here because nobody has
   tested it against IHH's site.
3. A **code-snippets plugin** to hold the same few lines. It is still a plugin, and it adds a
   way to run PHP from WP Admin.

We did not install anything, create any account, or change any setting on IHH's site.

---

## The email fallback (documentation only)

If WordPress comments are not wanted, set `site-data/visitor-voices.json` to
`{"adapter": "email", "email": {"address": "<an address IHH chooses>"}}` and rebuild. The
"Comment on this section" button then opens the visitor's own email app, with the passage and their note
filled in. Without JavaScript, each passage gets a plain `mailto:` link whose subject names the
passage. Nothing is stored on the website. A curator reads the mailbox, and notes appear only
when a curator adds them to `site-data/approved-notes.json` (via `voices/export_approved.py`
or by hand, through a reviewed pull request). A form service could stand in for email the
same way. None was chosen, and no account was created.
