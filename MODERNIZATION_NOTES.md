\# Modernization Notes



This fork is being used to modernize and study the racing\_data package.



\## Current findings



The core entity and feature-calculation layer works on Windows with modern Python when installed in editable mode.



Confirmed working:

\- Runner.carrying

\- Runner.actual\_weight

\- Runner.actual\_distance

\- Horse.performances

\- PerformanceList statistics

\- Runner.career

\- Runner.last\_10

\- Runner.last\_12\_months

\- Runner.at\_distance

\- Runner.on\_track

\- Runner.on\_good / on\_soft

\- Runner.with\_jockey

\- Runner.spell

\- Runner.up



\## Dependency issue



The original README workflow depends on:

\- pymongo

\- lxml

\- punters\_client

\- cache\_requests

\- redis



On Windows, installing cache\_requests fails because its redislite dependency is not supported on win32.



\## Modernization direction



For now, avoid the old cache\_requests/redislite stack.



Focus first on:

1\. Preserving the working entity and feature-calculation layer.

2\. Creating clear experiments and tests around that layer.

3\. Separating analysis features from scraper/database dependencies.

4\. Investigating provider/database support later, possibly with a modern replacement for cache\_requests.



\## Current modernization status



As of this branch checkpoint, the modernization work has established a stable Windows-safe analysis-layer baseline.



Current test status:



```cmd

python -m pytest

```



Expected result:



```text

39 passed

```



Modern tests now cover:



\- Entity initialization, timestamp handling, datetime localization, scraper compatibility, and cached property behavior

\- Runner form features including carrying weight, actual weight, actual distance, career form, recent form, contextual form, spell, and up

\- Performance features including profit, actual distance, actual weight, speed, momentum, spell, and up

\- Performance edge cases including missing starting price, missing winning time, zero winning time, and missing distance

\- PerformanceList features including counts, percentages, earnings, starting prices, ROI, and momentums

\- Experiment smoke tests confirming the exploratory scripts still run

\- Runner edge cases including missing jockey claim, missing weight, `Runner.actual_weight` missing-carrying behavior, and `Runner.actual_distance` barrier/missing-distance handling

Package-code cleanups completed so far:



\- `Entity.\_\_init\_\_` readability cleanup

\- `Performance.profit` simplification

\- `Performance.speed` early-return clarification

\- `Runner.carrying` missing-value handling and readability cleanup

\- `Runner.actual_weight` missing-carrying handling


The modernization branch remains focused on preserving the working analysis/entity layer before making deeper changes to provider, scraper, or database behavior.

