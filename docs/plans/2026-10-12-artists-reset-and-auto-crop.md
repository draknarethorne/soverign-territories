# 2026-10-12: Artists reset, auto-crop, one ingest routine

**Status:** active (built and run; waiting for you to look at the result)

What you asked for today (your notes are at the end, word for word) and what was done. The commands are in [../art/likeness.md](../art/likeness.md), the runbook in
[../art/original-photos.md](../art/original-photos.md).

| Ask | Done |
| --- | --- |
| Reset the Artists folders without criss-crossed images | `likeness artists --from` rebuilt them from the Oct 9 backup; every photo is under the artist it came from (checked against the backup). Safety copy: `_backup\2026-10-12-before-artists-reset` |
| Every good artist photo is assigned to a hero, even a single one | `likeness group --singles`: into one of that artist's people, else a folder of its own. Only photos with no usable face, a second person that cannot be cut away, or the app's bars over her head stay in `Artists\<A>\gallery` |
| Artists never cross, but tell me about look-alikes | Kept apart by the tool; `likeness crosscheck` writes `_reports\crosscheck.md` (artist ~ artist and prospect ~ artist) |
| Are prospects compared with Angels and Sisters? | Yes for `sort`; `rematch` and `singles` only listed them. Now a prospect, a new group or a single photo that is the same woman as an angel or sister (0.55) joins her, and her `z_` file remembers who it was (Zara Lane joined Draknoxa) |
| Crop away text, other people, animals and background, keep the originals | `likeness crop` for every root, including Angels and Sisters; originals in `_archive\...\gallery_uncropped`; `--undo` |
| Photos of a person that need clean-up go to her `review`, not `_junk` | A prospect's photo that cannot be cleaned up goes to her `review` folder, and `review` leaves it there (`_cleanup_hold.json`) |
| Photos with an animal that skews the likeness: back to the artist's gallery | An artist's person photo that cannot be cleaned up goes back to `Artists\<A>\gallery`; the grouping skips photos with animals |
| Put `_junk` back and see where it lands | `likeness junk --reset` (and `library.cmd --retry-junk`); the 37 prospect and 27 artist photos went through again, 28 are junk again (bars over her head) |
| Pull a group of prospects back and re-sort | `likeness pullback NAME... / --small N / --all`, then the routine; `sort --assign` for a looser second look |
| One clear, repeatable ingest process | `bin\library.cmd` does it all; the runbook is in original-photos.md |
| Clean the tmp notes, audit the docs | Every tmp note is in a plan or a doc and `tmp/` is empty; the audit is [../audits/2026-10-12-docs-audit.md](../audits/2026-10-12-docs-audit.md); the day is in [../recap/](../recap/) |

## Open

- [ ] **P2 you** A1 Look at the cropped photos (Angels, Sisters, Prospects, Artists): the crop is geometric (the face box widened to the sides, all body below), not a person detector, so wings, a wide stance or a low head can be cut. `likeness crop --undo` reverses a batch; the uncropped originals are in `_archive\<folder>\gallery_uncropped`.
- [ ] **P3 you** A2 The 28 photos back in `_junk` (mostly screenshots whose head lies under the app's bars): salvage or discard.
- [ ] **P3 you** A3 Read `_reports\crosscheck.md` (look-alikes between artists, and between prospects and artists): only reported, nothing moved. Say if a pair should be handled.
- [ ] **P3 ai** A4 Teach `crop` the other reel layouts (a paused video with a play button, a caption at the bottom) so those screenshots are cut too.

## Result

Done Oct 12: the Artists were rebuilt from the Oct 9 backup and every good photo has a person; the routine `bin\library.cmd` crops, sorts and re-checks everything and is stable (a second run changes nothing). The day is reflected in [../recap/](../recap/).

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
