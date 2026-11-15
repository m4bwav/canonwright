# Model misses: lookup list

General patterns seen when book characters meet image and video models. Most capable models already avoid these when asked; this is a lookup, not a rule list.

- **Name pull.** A name with an everyday meaning or a famous film version pulls that picture; describe instead of naming, or list it under `never_say`.
- **Animal and skull nouns.** An animal or skull word in a face description pulls that whole head; describe the shape.
- **Effect in the reference.** A start image that already shows the effect (a beam fired, a blow landed) makes the model do it twice; use the still from before.
- **Materials by how they are made.** Say how a material is built and weathers; monument words ("temple") draw dressed stone.
- **Failed geometry.** A prop the model keeps drawing wrong after several tries gets a 3D model or guide, composited; or keep it small and far off.
- **Counts and sides.** Head counts, crowd sizes and who stands where come from a 3D blockout start image, not prompt words.
- **Known looks.** For a character with a canon picture, edit that picture (low-denoise image-to-image) rather than generating from text, and show a face test beside the canon picture before a batch.
- **Invented spectacle.** Things the scene does not contain (a boulder, an extra explosion) are canon misses too; make them a `no-...` check.
- **Height.** Height words alone do not hold relative size; use a start still or blockout.
