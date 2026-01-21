<h1>UI Components Documentation</h1>
<h2>Button Component</h2>
<p>
Used for triggering actions such as submit, cancel, or delete.
</p>
<h3>Example</h3>
<pre>
&lt;Button&gt;Click Me&lt;/Button&gt;
&lt;Button variant="danger"&gt;Delete&lt;/Button&gt;
</pre>
<hr />
<h2>Input Component</h2>
<p>
Used for form inputs with optional label and error message.
</p>
<h3>Example</h3>
<pre>
&lt;Input
label="Email"
type="email"
placeholder="user@example.com"
/&gt;
</pre>
<hr />
<h2>Card Component</h2>
<p>
Used to group related UI elements.
Supports nesting to test layout composition.
</p>
<h3>Example</h3>
<pre>
&lt;Card title="Main Card"&gt;
&lt;Card title="Nested Card"&gt;
Content
&lt;/Card&gt;
&lt;/Card&gt;
</pre>
<hr />
<h2>Badge Component</h2>
<p>
Used to display small status labels.
</p>
<hr />
<h2>Modal Component</h2>
<p>
Used for overlay dialogs and focused actions.
</p>
<hr />
<h2>Layout Components</h2>
<h3>Navbar</h3>
<p>Fixed top navigation bar used in dashboard layout.</p>
<h3>Sidebar</h3>
<p>Fixed left navigation panel used across dashboard pages.</p>
<hr />
<h2>Notes</h2>
<ul>
<li>Components are reusable and prop-driven</li>
<li>Nested cards are used on the main page to validate layout behavior</li>
<li>Designed for scalability and consistency</li>
</ul>
