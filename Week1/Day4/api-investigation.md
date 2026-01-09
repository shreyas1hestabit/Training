# API Investigation — Headers, Pagination & Caching

## Task 3: Header Modification Analysis

### 1. Normal Request
A normal curl request was sent to the API without modifying any headers.

**Observation:**
- The server returned HTTP 200 OK.
- Product data was returned in JSON format.

---

### 2. Request Without User-Agent Header
The User-Agent header was removed from the request.

**Observation:**
- The response status remained HTTP 200 OK.
- The response body did not change.

**Difference:**
- Removing the User-Agent header did not affect the server response.

**Conclusion:**
- This API does not rely on the User-Agent header to serve data.

---

### 3. Request With Fake Authorization Header
A fake Authorization header was added to the request.

**Observation:**
- The server still returned HTTP 200 OK.
- The response body remained unchanged.

**Difference:**
- Adding a fake Authorization header did not restrict access.

**Conclusion:**
- This endpoint is publicly accessible and does not require authentication.

## Task 4: ETag Caching Analysis

The API returned an ETag value in the response headers.
When the same request was sent again with the If-None-Match header,
the server responded with HTTP 304 Not Modified.

This indicates that the resource had not changed and the client
can safely reuse the cached data.
