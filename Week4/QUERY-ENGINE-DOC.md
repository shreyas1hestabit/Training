## Product Query Engine

This document specifies the work done by the system and the architecture followed, endpoints and the API Surface area.

### Architecture

controller -> service -> repository

### endpoints

GET /
DELETE /products/:id

### QUERY PARAMETERS

<ol>
<li>search</li>
<li>price filtering</li>
<li>tag filtering</li>
<li>sorting</li>
<li>pagination</li>
<li>soft delete</li>
<li>include deleted products</li>
</ol>

### error handling

all errors are handled by a centralized error middleware
