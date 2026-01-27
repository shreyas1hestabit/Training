### WEEK 3 PROJECT COMPLETE EXPLANATION

we wanted to create a dashboard using next.js and tailwind css.
next.js is used for page routing and tailwind css is used for styling.

# ROADMAP

<h3>DAY 1</h3>
<p>on day1 I learned tailwind css and its properties. I also learned how to setup tailwind css using next.js. then I applied my learnings and created a dashboard basic page where i created a navbar and a sidebar.</p>
Steps performed:
--created next.js project using <strong>create-next-app</strong> command. this installed all the libraries and modules needed in the project and created a project folder my-dashboard with next.js initialized.
--inside our project folder we installed <strong>lucide-react</strong>. this library is compatible for react and it contains a bunch of stylish and modern icons which we directly used in our project like growth, users, shopping cart etc.
--then we worked two folders -> <strong>app (already present in the project) and components (we manually created it)</strong>
app folder contained two files namely <strong>layout.jsx and page.jsx</strong>
and components contained file named <strong>DashboardLayout.jsx</strong>
--my folder had .jsx files instead of .js, so I got to learn that .jsx and .js are interchangable and both work perfectly fine for react components. .jsx just displays that this file contains jsx syntax
--till now the project structure is:
my-dashboard
|----app
|     |----layout.js
|     |----page.js
|     |----global.css
|
|----components
|     |----ui
|     |     |---sidebar.jsx
|     |     |---navbar.jsx
|
|-----public
|-----package.json

<h4>BASIC PROJECT IDEA</h4>
a page contains all the content which needs to be displayed on the home page when the server is loaded
layout page which contains the html code of the page.
so basically page.js mein hm content likhte hai which needs to be returned and layout.js mein hm page ka html likhte hai which calls all the pages which needs to be linked and displayed. 
create a <strong>components </strong>folder which contains all the <strong>reusable UI parts</strong> this is created in ui folder as it contains only design related components.
global css page which cotains tailwind css and global styles for the whole project
create a navbar and sidebar which is visible on each and every page
<h5>app/layout</h5>
common structure file which decides <strong>overall layout </strong>of the page
we have imported globals.css and sidebar and navbar here. while importing sidebar and navbar we used <strong>'@/...'</strong> this @ states the project root. we are using this because hmne multiple folders mein multiple files bnayi hai so if we are calling a file of different folder then we need our js to search files from root otherwise it searches only in the folder we are working.
then we used a fixed layout function of next.js called RootLayout

```bash
export default function RootLayout({children})
```

{children} --> whatever page is loading is rendered in children.
then we also specified the css of navbar and sidebar
we created a container for sidebar and aligned the items horizontally in it.

| Property      | Purpose                               | Target                  |
| ------------- | ------------------------------------- | ----------------------- |
| flex          | items side by side                    | sidebar                 |
| h-screen      | full screen height                    | sidebar                 |
| bg-gray-100   | light gray background                 | sidebar                 |
| flex-1        | take all the space left after sidebar | navbar                  |
| flex-col      | align items vertically                | Navbar and main content |
| overflow-auto | scroll if content is more             | main                    |

<h5>app/page</h5>
home page file which is <strong>rendered on the webpage</strong>
created a function called Home using

```bash
export default function Home()
```

export default states that whatever is written here is the content of home page. whenever the browser is loaded this function runs.
then we specified all the content we want with its css in return. in return we write jsx.

| Property      | Purpose                             | Target                    |
| ------------- | ----------------------------------- | ------------------------- |
| p-6           | padding of 6px on all the four side | whole content of the page |
| text-3xl      | text size                           | heading                   |
| font-bold     | font weight                         | heading                   |
| mb-4          | margin at bottom of 4px             | heading                   |
| text-gray-600 | light gray color of text            | paragraph                 |

<h5>components/ui/sidebar</h5>
we started by the code line

```bash
use client
```

this tells the next.js that the file contains all the things needer for browser like button click, hide/show sidebar, usestate etc.
by default next.js components are server components but if we want something to run on client side we use this command.

then we imported icons of lucide-react library.

| icon            | use               |
| --------------- | ----------------- |
| Menu            | hamburger icon    |
| LayoutDashboard | dashboard icon    |
| chevronRight    | arrow             |
| barchart, table | charts and tables |

<strong>Alternative to lucide-react: </strong>

| alternative    | why not used                         |
| -------------- | ------------------------------------ |
| svg files      | download and link each file manually |
| fontAwesome    | heavy library                        |
| material icons | less flexible                        |

then we imported useState from react. its function as name suggests is to store the state of the component like is sidebar open or close.

next we used a command to create the sidebar function which also allows the function to be used by other files

```bash
export default function sidebar()
```

then we declared the state of the sidebar and set it to true

| property       | function                               |
| -------------- | -------------------------------------- |
| sidebarOpen    | current value of side bar- open/closed |
| setsidebaropen | function to change the value           |

next we declared an aside tag wherein we defined the properties of sidebar for smooth toggle.

| property                    | function                                    |
| --------------------------- | ------------------------------------------- |
| sidebaropen ? w-64 : w-20   | if sidebar open then width 64 else width 20 |
| bg-gray-800                 | dark gray background                        |
| text-white                  | white color text                            |
| transition-all duration-300 | smooth animation                            |
| h-screen                    | full height                                 |

then we defined properties for sidebar header as it contains logo and menu button
next we worked upon sidebar title and specified its text visibility if sidebar is open and hide if sidebar is closed.
then we created toggle button for sidebar and used onClick() method to set the sidebar state.
next we specified hamburger menu contents and their basic properties like margin, padding, color, hover, gap etc.

<h5>components/ui/navbar</h5>
this section contains app title, search input and user icon.
while creating navbar we again imported lucide-react for SVG icon components.

| property | function              |
| -------- | --------------------- |
| search   | magnifying glass icon |
| user     | profile icon          |

then again same thing like sidebar. export default navbar function with a return jsx.
return contains different classes and tags for different areas and their properties

| property | function | target |
| bg-gray-800 | dark background | header|
|text-white| white font color |header|
|shadow-md| bottom shadow|header|
|flex|row layout|inner container|
|items-center| vertical center | inner container|
|justify between | left and right seperation| inner container|
|px-6|horizontal padding| inner container|
|py-3|vertical padding| inner container|
|span| inline text with no block spacing | left section (title)|
|text-lg|large text| left section title|
|font-semibold| semibold font| left section title|
|flex-1|takes remaining space|search bar container|
|max-w-md| limits width|search bar container|
|mx-4|horizontal margin| searchbar container|

then we created a div class relative because we have an absolute position container and an absolute position needs a relative parent. without this the buttons will move to the page corner.
for search input we used properties

| property    | function              |
| ----------- | --------------------- |
| type="text" | text input            |
| palceholder | grey hint text        |
| w-full      | full width            |
| px-4 py-2   | x and y axis padding  |
| pr-10       | space for icon button |
| rounded     | rounded corners       |
| focus:ring  | blue focus ring       |

then styled search button and user icon section. user icon is a flex container with a user button
we have not used use client here because no usestate or onclick is used. it is only server side component.
