- [ ] Update `services/pinecone_manager.py` to avoid writing to read-only FS on Vercel by moving Chroma path to a writable temp directory and lazy-initializing client/collection.
- [ ] Commit changes to a new branch (e.g., `blackboxai/vercel-setup-chroma-fix`).
- [ ] Push branch to GitHub.
- [ ] User creates/merges PR from the new branch into `main`.
- [ ] Re-deploy to Vercel and verify endpoint returns 200/expected JSON (not 500).

