<h1>UI Components Documentation</h1>
<h2>Button Component</h2>
<p>
Used for triggering actions such as submit, cancel, or delete.
</p>
<h3>Props</h3>
<table>
<thead>
<tr>
<th>Prop</th>
<th>Type</th>
<th>Default</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td>children</td>
<td>ReactNode</td>
<td>—</td>
<td>Button content</td>
</tr>
<tr>
<td>variant</td>
<td>string</td>
<td>primary</td>
<td>Visual style of button</td>
</tr>
<tr>
<td>size</td>
<td>string</td>
<td>md</td>
<td>Button size</td>
</tr>
<tr>
<td>onClick</td>
<td>function</td>
<td>—</td>
<td>Click handler</td>
</tr>
<tr>
<td>disabled</td>
<td>boolean</td>
<td>false</td>
<td>Disables the button</td>
</tr>
</tbody>
</table>
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
<h3>Props</h3>
<table>
<thead>
<tr>
<th>Prop</th>
<th>Type</th>
<th>Default</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td>type</td>
<td>string</td>
<td>text</td>
<td>HTML input type</td>
</tr>
<tr>
<td>value</td>
<td>string</td>
<td>—</td>
<td>Input value</td>
</tr>
<tr>
<td>onChange</td>
<td>function</td>
<td>—</td>
<td>Change handler</td>
</tr>
<tr>
<td>label</td>
<td>string</td>
<td>—</td>
<td>Input label</td>
</tr>
<tr>
<td>error</td>
<td>string</td>
<td>—</td>
<td>Error message</td>
</tr>
</tbody>
</table>
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
<h3>Props</h3>
<table>
<thead>
<tr>
<th>Prop</th>
<th>Type</th>
<th>Default</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td>children</td>
<td>ReactNode</td>
<td>—</td>
<td>Card content</td>
</tr>
<tr>
<td>title</td>
<td>string</td>
<td>—</td>
<td>Card header title</td>
</tr>
<tr>
<td>footer</td>
<td>ReactNode</td>
<td>—</td>
<td>Footer section</td>
</tr>
<tr>
<td>variant</td>
<td>string</td>
<td>default</td>
<td>Card styling variant</td>
</tr>
</tbody>
</table>
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
<h3>Props</h3>
<table>
<thead>
<tr>
<th>Prop</th>
<th>Type</th>
<th>Default</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td>children</td>
<td>ReactNode</td>
<td>—</td>
<td>Badge text</td>
</tr>
<tr>
<td>variant</td>
<td>string</td>
<td>default</td>
<td>Status type</td>
</tr>
<tr>
<td>size</td>
<td>string</td>
<td>md</td>
<td>Badge size</td>
</tr>
</tbody>
</table>
<hr />
<h2>Modal Component</h2>
<p>
Used for overlay dialogs and focused actions.
</p>
<h3>Props</h3>
<table>
<thead>
<tr>
<th>Prop</th>
<th>Type</th>
<th>Default</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td>isOpen</td>
<td>boolean</td>
<td>false</td>
<td>Controls visibility</td>
</tr>
<tr>
<td>onClose</td>
<td>function</td>
<td>—</td>
<td>Close handler</td>
</tr>
<tr>
<td>title</td>
<td>string</td>
<td>—</td>
<td>Modal heading</td>
</tr>
<tr>
<td>children</td>
<td>ReactNode</td>
<td>—</td>
<td>Modal content</td>
</tr>
<tr>
<td>footer</td>
<td>ReactNode</td>
<td>—</td>
<td>Footer actions</td>
</tr>
</tbody>
</table>
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
