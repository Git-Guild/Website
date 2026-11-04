# Browser and data checks

Run the offline build first, then the snapshot unit checks and browser
assertions. Playwright uses local `file://` pages; browser checks do not call
GitHub.

```bash
python3 tools/build/build_site.py
python3 -m unittest tools/qa/test_project_catalog.py
python3 tools/qa/qa_assert.py
python3 tools/qa/qa_shots.py
```

The unit checks cover public-repository filtering, pagination, preservation of
the previous snapshot after sync errors, metadata ordering, and 3/12/13 project
slot behavior. Browser assertions compare the built site with the checked-in
snapshot and exercise emblem binding, wiring hover, selection, spotlight and
detail navigation, real update dates, mobile layout, keyboard interaction,
reduced motion, and offline loading.

`qa_shots.py` writes desktop, tablet, and mobile screenshots under `build/qa/`
for visual review. These files are generated locally and are not site assets.
