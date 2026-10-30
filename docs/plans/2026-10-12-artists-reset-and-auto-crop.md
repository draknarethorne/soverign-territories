# 2026-10-12: Artists reset, auto-crop, one ingest routine

**Status:** holding (Oct 30 scheduling; delivered work retained, Artist acceptance open)

**Resume gate:** intake I74's separate Artist scope or a concrete Artist review
request. Crosscheck review and Artist-specific crop acceptance are not implied
by successful general-people installation; no new reset is needed now.

## Oct 23 ownership reconciliation

The new [intake preparation plan](2026-10-23-image-intake-preparation.md)
is the Phase 1 owner of general overlay/hair-safe preparation and cleanup
evaluation. A4 remains this plan's Artist-specific wing/pose/layout acceptance,
using that shared preparation rather than a separate crop engine.
A5's optional detection/masking comparison transfers to intake I3-I5:
transferred, not implemented or accepted. Artist isolation and A3 crosscheck
review remain here; tooling D5 still owns reusable person detection.
The user now requests cleanup evaluation first, not an immediate dependency
installation or permission to modify library photos.

## Review and questions: 2026-10-22 16:26 -05:00

Retained independent A3 crosscheck review, A4 overlay/crop improvements and
A5 optional detection/blending decision. Ask whether the user wants the
optional cleanup comparison before adding dependencies or modifying photos.
Tooling D5 owns a reusable person detector; A4 owns artifact-specific crop
acceptance, not a duplicate detector implementation.
The Oct 12 `0.55` automatic cast-join row and second-run idempotence claim below
describe that historical implementation, not today's permission or acceptance.
The [current contract](../art/likeness-processing-contract.md) supersedes it:
cast Gallery protection is separate from grouping and incoming Review.

What you asked for today (your notes are at the end, word for word) and what was done. The commands are in [../art/likeness.md](../art/likeness.md), the runbook in
[../art/original-photos.md](../art/original-photos.md).

| Ask | Done |
| --- | --- |
| Reset the Artists folders without criss-crossed images | `likeness artists --from` rebuilt them from the Oct 9 backup; every photo is under the artist it came from (checked against the backup). Safety copy: `_backup\2026-10-12-before-artists-reset` |
| Every good artist photo is assigned to a hero, even a single one | `likeness group --singles`: into one of that artist's people, else a folder of its own. Only photos with no usable face, a second person that cannot be cut away, or the app's bars over her head stay in `Artists\<A>\gallery` |
| Artists never cross, but tell me about look-alikes | Kept apart by the tool; `likeness crosscheck` writes `_reports\crosscheck.md` (artist ~ artist and prospect ~ artist) |
| Are prospects compared with Angels and Sisters? | Yes for `sort`; `rematch` and `singles` only listed them. Now a prospect, a new group or a single photo that is the same woman as an angel or sister (0.55) joins her, and her `z_` file remembers who it was (Zara Lane joined Draknoxa) |
| Crop away text, other people, animals and background, keep the originals | `likeness crop` for every root, including Angels and Sisters; originals in `_archive\...\gallery_uncropped`; `--undo` |
| Crop review (Oct 12) | Strong results for Angels, Sisters, Prospects and people in normal outfits; artist wings were cut, and some reel overlays remain at the bottom and right edges |
| Photos of a person that need clean-up go to her `review`, not `_junk` | A prospect's photo that cannot be cleaned up goes to her `review` folder, and `review` leaves it there (`_cleanup_hold.json`) |
| Photos with an animal that skews the likeness: back to the artist's gallery | An artist's person photo that cannot be cleaned up goes back to `Artists\<A>\gallery`; the grouping skips photos with animals |
| Put `_junk` back and see where it lands | `likeness junk --reset` (and `library.cmd --retry-junk`); the 37 prospect and 27 artist photos went through again, 28 are junk again (bars over her head) |
| Pull a group of prospects back and re-sort | `likeness pullback NAME... / --small N / --all`, then the routine; `sort --assign` for a looser second look |
| One clear, repeatable ingest process | `bin\library.cmd` does it all; the runbook is in original-photos.md |
| Clean the tmp notes, audit the docs | Every tmp note is in a plan or a doc and `tmp/` is empty; the audit is [../audits/2026-10-12-docs-audit.md](../audits/2026-10-12-docs-audit.md); the day is in [../recap/](../recap) |

## Open

- [x] A1 Reviewed the cropped photos: excellent for Angels, Sisters, Prospects and normal outfits; artist wings were cut and some reel overlays remain.
A2's `_junk` review is consolidated into R11 of [the Oct 19 library plan](2026-10-22-library-upkeep.md); use the current post-run inventory rather than the Oct 12 count.
- [ ] **P3 you** A3 Read `_reports\crosscheck.md` (look-alikes between artists, and between prospects and artists): only reported, nothing moved. Say if a pair should be handled.
- [ ] **P3 ai** A4 Inspect remaining reel overlays (bottom/right edges and captions near the hairline) and other layouts (paused video play button, caption at the bottom). Accept Artist-specific results of intake I3-I5's shared preparation so wings and broad poses are preserved; keep manual or AI blending optional.
- [x] **P3 either** A5 Discuss optional local logo/text detection and cleanup
  separately from likeness matching. Compare reversible masking/blending
  against cropping, preserve originals, and agree scope before implementing
  or changing generated gallery images.
  Transferred Oct 23 to intake I3-I5, not completed; shared evaluation now
  precedes rebase/action testing. Original request remains preserved here.

## Result

Done Oct 12: the Artists were rebuilt from the Oct 9 backup and every good photo has a person; the routine `bin\library.cmd` crops, sorts and re-checks everything and is stable (a second run changes nothing). The day is reflected in [../recap/](../recap).

## Raw notes: rework the Artists (Oct 12, first note)

Your words, kept as written (only wrapped).

It seems like the Artists directory is totally out of whack and that we have a bunch of criss-crossed images across artists now and that some items are in a gallery directory still directly in each Artist folder and not a hero underneath.  Feels like a more complete reset of that is needed and we need to fully re-align
as we had some mis-matching of Artists to Prospects and from Artist to Artist that might have gotten things messed up.  I'm not sure the best way to handle that - but we might have a backup of the Artists before we re-organized their images and put in logic to handle ones with multiple people that cause mis-matches to
occur.  I am ok if we have to start-over on the Artists to ensure we don't criss-cross artist files and that each Artist folder has a clear and consistent structure moving forward.  Let me know what you think about the best plan or if you can find the backup I think we do have before we started or if it's in an
archive.  If it doesn't contain the full copy of what we have now - I'd want first to process from the backup and then to take all the ones we do have now and try to put them into the proper Artist subdirectory and then in the right person or we can leave things in the Artist/xxxx/gallery that aren't aligned to either
a male or female or animal (which happens with some images).

## Raw notes: prospect and artist feedback (Oct 12)

Your words, kept as written (only wrapped).

Important Note: I still see a lot of files in the Artist/xxxxx/gallery directory that I feel like should be processed and assigned to heros and not understanding why that's not happening.  Even if it is a single image for the artist - if it's a good image of a person we should assign that out and only leave items in a
gallery that truly don't match any hero.  Same with Various/gallery there's one in there that I think belongs in one of the Artist directories and if it's a duplicate it should be archived or removed.

Critical Note:  When the likeness process is running to align the Prospects is it also comparing them to Angels and Sisters and not just other Prospects?  I feel like some of the files being processed from Various or in Prospects to match the Angels and Sisters, but are creating new Prospects.  Remember the process is
that I take a Prospect and put it into an angel and we use the z_xxxx.txt file to remember who they were originally so we can re-assign them back if we swap the Angel or Sister with another Prospect.

Also Criticial:  I am ok cropping all images automatically during the process as well - meaning, even on photos with just a person, if there is alot of background "noise" in the image - we can also crop that away and when we generate the scaled/padded images it should then handle the process.  If we have images - that
way what we pull into the workflow for images is focused on the person and however much of their actual body is in the picture as long as we can keep as much of their body and clothing as possible.  I really don't care about the clothing and outfit as much - although with some of them that have angel wings and other
details it is fine - but ultimately I want clean and clear focus on the person in the images and not all sorts of extra details that will eventually just be discarded in the Prime flows anyway.

Also Critical:  Given what we're doing with cropping, re-processing the _junk files to see if they can show up somewhere would be fine.  Just put them back into Various and run the process to see what happens.  If it's truly _junk then I can see if I can salvage it or just discard it.  I only really want the proper
usable images to end up in the 944x1104 directories.

Finally: whatever documentation we have on the process of ingesting the original images needs to be clear in what commands to run and how this all works so it's repeatable and we don't end up with duplicate files in the end.  Just keep on iterating - reflect on the output that you can eyeball, re-run the process to
even crop the Sisters and Angels who are already assigned so those images are clear and optimal as well.  As long as the full original images are stored somewhere and we can get back to them based on where they were originally stored - that's fine.  We can clean the originals up or have them in the _archive or
somewhere that makes the most sense and doesn't clutter things up.  Just as long as they're not lost somewhere.  I'd only want _junk if we truly can't use or the file needs to be in review under the named hero if we detect it is a person, but the picture needs clean-up to make it useable.  I know it's complex - but
ideally we are able to get this done and all Sisters, Angels, Artists and Prospects are handled when we're all done.

## Raw notes: likeness idea: loosen, pull back, tmp clean-up, docs audit (Oct 12)

Your words, kept as written (only wrapped).

Maybe the loosen process targets prospects with only 1-2 images instead of the entire batch and it's a two phase re-organization?  Not sure the best way to keep the balance - but I'm sure you can figure out the best way to not cross-pollinate people bacause it's now "too loose".  I'd also like to make sure that if I
just want to pull back a entire group of Prospects and let things re-sort that's also an option.  Basically we can use Various as the mechanism to pull things back and not always moving and criss crossing things in iterations - if that helps simplify.  Just thinking outloud on how to achieve what we want done properly
in the end.

We should also cleanup the tmp directory for .md files that have proper docs/plans and we don't need those any more and have or will be addressing those .md files.  If there are questions about some let me know and I'll decide what to do about them.

Finally, at some point we need an audit of the docs *.md files to see where we have conflicts or stale documentation.  We've made a lot of changes over the past several days and I'm sure things are out of sync now.  You can fix the obvious issues, but give me a report on what major issues we have as some of that might
just be ideation/future documentation we'll get to in later phases or some might need immediately actions.

## Raw notes: crop review follow-up (Oct 12)

Your words, kept as written.

I would give the cropping a A+ on the Angels, Sisters and Prospects, but for Artists - where some had angel wings and devil wings it cropped
those quite a bit.  So, for real people in normal outfits, the cropping did get rid of text and much of the extras.  I noticed that some
photos that have the "text" about the reels on the hairline that it also left text on the bottom and right side for things in the shots -
many of the screenshots might have overlay items that ideally are cropped and if I need to manually clean-up the top lines with AI or
something I can do that - if there were another library to blend those away that would also be awesome.  So mostly the cropping is awesome,
but still has a few things to improve on.

## Raw notes: optional logo cleanup (Oct 21)

I know we have the auto-crop capability build into the framework, but I'm also wondering if there is any ability we could use to also detect and auto-cleanup logos that appear on images as we generate the gallery911x1104 files?
I do have my ComfyUI workflows instructed to do that and it works and I have also done it by hand before sending files into the Various gallery so I can keep from cropping the hair on some images or feet on others.
It would be great if the framework could handle this automatically, either by detecting logos and removing them or by providing a way to mask them out during the gallery generation process.
It might actually save time in the ComfyUI execution of we are able to handle logo cleanup directly within the framework, reducing the need for manual intervention and ensuring a cleaner final gallery output.
Even if it were partially successful in handling logos like on image file:///B:/Sovereign%20Territories%20Sandbox/Working/Angels/angelica/gallery/angelica_image_7513773334796667927.jpg  and many others for Angelica and a few other Angels - where I somehow lost those updates in my processing.
