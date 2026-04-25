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

