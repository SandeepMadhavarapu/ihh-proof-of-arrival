# Visitor Voices: 60-second demo

This runs entirely on your own computer, at `127.0.0.1`. Every page says **DEMO** at the top.
Nothing is sent to the Immigrant Hall of Honor or anywhere else. Notes, the audit log and the
demo's Living Museum queue are kept in `voices/.demo/`, which is never committed.

## Start it (PowerShell, one command per line)

```powershell
cd ihh-proof-of-arrival
```

```powershell
python -m voices.demo_server --reset
```

Leave that window open. Press Ctrl+C there to stop.

## The walkthrough

| Time | Do this | You should see |
|---|---|---|
| 0:00 | Open <http://127.0.0.1:8770/muir.html>. Open **A farm boy from Dunbar** and highlight the first sentence. | A **Comment on this** button under the highlight. Every passage also has a keyboard-reachable **Comment on this section** button in its margin. ([01](../review/workstream-3/screenshots/01-desktop-highlight.jpg)) |
| 0:10 | Click it. Choose **My perspective**, write a note, and optionally give a first name. Press **Send to a curator**. | The panel quotes the passage and shows the under-13 notice. After sending: "Thanks — a curator reviews every note before it appears." ([02](../review/workstream-3/screenshots/02-desktop-panel.jpg), [03](../review/workstream-3/screenshots/03-desktop-confirmation.jpg)) |
| 0:20 | Reload the page. | **Nothing new on the page.** The note is pending. |
| 0:25 | Open <http://127.0.0.1:8770/voices/moderate>. Type your name and press **Approve**. | The note, the passage it attaches to ("exact"), and an intact audit log. ([04](../review/workstream-3/screenshots/04-desktop-moderator.jpg)) |
| 0:35 | Back to the Muir page and reload. | A **1** in the margin beside that sentence, and directly under the passage a **1 visitor comment on this section** line that expands to the comment with the passage it answers. The count also links to **Notes on this page**, which shows the type, first name and date. ([05](../review/workstream-3/screenshots/05-desktop-margin-marker.jpg), [06](../review/workstream-3/screenshots/06-desktop-notes-index.jpg)) |
| 0:45 | Open <http://127.0.0.1:8770/verify.html>. Under the Muir claim "Helped establish … Grand Canyon (1908) National Park", press **Report or add to this claim**. Write what you know and give a source. Send. | The same panel, with the claim quoted and **Something looks wrong** preselected. ([07](../review/workstream-3/screenshots/07-desktop-verify-report.jpg), [08](../review/workstream-3/screenshots/08-desktop-verify-sent.jpg)) |
| 0:55 | Reload the moderator page. | The report is in the **moderation queue**. Because it has a source, it is also in the **Living Museum queue** as a *tip* with an empty sentence: a curator has to find an exact span before anything can be published. Any HTML typed into the report is shown as plain text. ([09](../review/workstream-3/screenshots/09-desktop-moderation-claim.jpg), [10](../review/workstream-3/screenshots/10-desktop-living-museum-queue.jpg)) |

The Verify page also has a general form, **Spot something? Tell us**, with an inductee
dropdown and optional source and relationship fields
([15](../review/workstream-3/screenshots/15-desktop-verify-tell-us.jpg)).

Phone width (375px) screenshots:
- [margin](../review/workstream-3/screenshots/11-phone-margin.png)
- [panel](../review/workstream-3/screenshots/12-phone-panel.png)
- [notes index](../review/workstream-3/screenshots/13-phone-notes-index.png)
- [Verify report](../review/workstream-3/screenshots/14-phone-verify-report.png)

## Things worth showing if there is time

- **Without JavaScript.** Turn scripts off and reload a profile. Each passage shows a plain
  **Comment on this section** link, for example `/voices/form?page=muir&passage=muir-a-farm-boy-from-dunbar-5f55a0`.
  It opens a form with that passage already quoted and filled in, and the form posts normally.
- **Esc** closes the panel and puts focus back on the button that opened it.
- **Edits don't lose notes.** Edit a word in that Muir paragraph in `inductees/muir/copy.md`,
  rebuild, and the note re-attaches by its quoted text. Rewrite the paragraph completely and
  the moderator page marks the note **FLAGGED** instead of guessing where it goes.

## What the demo is not

- It is not the live system. The production site (`site/`) is built with notes switched off
  (`site-data/visitor-voices.json`, adapter `none`). It can never be built with the demo
  adapter: the build refuses it, and the demo's script lives only in `voices/.demo/`.
- On WordPress, notes become pending WordPress comments instead (see
  `INTEGRATION-COMMENTS.md`).
