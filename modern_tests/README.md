\# Modern tests



This folder contains Windows-safe modernization tests for the racing\_data analysis layer.



The original `tests/` folder depends on the legacy provider/scraper stack, including `cache\_requests` and `redislite`, which currently fails on native Windows.



These tests intentionally focus on the working analysis/entity layer:



\- Runner

\- Horse

\- Performance

\- PerformanceList

\- linked object graphs using property\_cache



Run with:



```cmd

python -m pytest modern\_tests -q --confcutdir=modern\_tests

