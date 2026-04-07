## SECURITY REPORT

### TEST 1 NoSQL Injection

we did this to ensure the API is protected against NoSQL injection attacks to manipulate mongoDB queries using operators like `$gt`

![t1](./screenshots/t1.png)

### TEST 2 XSS (CROSS-SITE SCRIPTING)

to check wether malicious scripts can be injected and stored in db.

![t2](./screenshots/t2.png)

### TEST 3 PAYLOAD SIZE LIMIT

to prrevent attacks by sending extremely large requests

![t3](./screenshots/t3.png)

### TEST 4 RATE LIMITING

to prevent excessive API calls

![t4](./screenshots/t4.png)

### TEST 5 CORS POLICY ENFORCEMENT

to ensure only allowed origins can access.

### TEST 6 EXTRA FIELDS (MASS ASSIGNMENT)

to inject unauthorized fields.

![t6](./screenshots/t6.png)

### TEST 7 SECURITY HEADERS(HELMET)

to protect against common web vulnerabilities.

![t7](./screenshots/t7.png)
