## Why quote the book instead of describing it?

A quote with a chapter ref can be checked. A paraphrase is allowed only marked `verified: false`, for when the book text is not on disk.

## What if the book says nothing?

Write a `ruling` with the reason, who made it and when. `lint` refuses a ruling without a reason.

## Can I keep bibles for books under copyright?

Yes, outside the repository: in `CANONWRIGHT_HOME/bibles`. Quotes from such works are limited to 25 words each.

## Does it generate images or video?

No. It holds what the book says and checks prompts and takes against it. Rendering belongs to other tools (comfyui-gen, cinewright); `export` hands the bible to cinewright and artwright.
