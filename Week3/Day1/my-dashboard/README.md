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

```txt
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
```

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

| property        | function                          | target               |
| --------------- | --------------------------------- | -------------------- |
| bg-gray-800     | dark background                   | header               |
| text-white      | white font color                  | header               |
| shadow-md       | bottom shadow                     | header               |
| flex            | row layout                        | inner container      |
| items-center    | vertical center                   | inner container      |
| justify between | left and right seperation         | inner container      |
| px-6            | horizontal padding                | inner container      |
| py-3            | vertical padding                  | inner container      |
| span            | inline text with no block spacing | left section (title) |
| text-lg         | large text                        | left section title   |
| font-semibold   | semibold font                     | left section title   |
| flex-1          | takes remaining space             | search bar container |
| max-w-md        | limits width                      | search bar container |
| mx-4            | horizontal margin                 | searchbar container  |

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

<h3>DAY2</h3>
<p>we worked with components for day2 task</p>
<p>Steps performed: we created various .jsx files in components/ui for each and every component we need and then updated our app.js to test the functioning of each component and documented the components in a .md file</p>
<p>folder structure by day2 looks like</p>

```txt
my-dashboard
|----app
|     |----layout.js
|     |----page.js(updated)
|     |----global.css
|
|----components
|     |----ui
|           |---sidebar.jsx
|           |---navbar.jsx
|           |---modal.jsx
|           |---input.jsx
|           |---card.jsx
|           |---button.jsx
|           |---badge.jsx
|
|
|-----public
|-----package.json
|-----UI-COMPONENTS-DOCS.md
```

<h5>components/ui/badge.js</h5>
the purpose of this component was to create small label badges like:
<ul>
<li>active</li>
<li>success</li>
<li>warning</li>
<li>premium</li>
<li>info</li>
</ul>
the purpose of badges is to show status or category.

```bash
export default function Badge({children, variant='default', size='md'})
```

this again creates a react component named Badge and export default allows other files to import it. this is different from other export defaults we used previously as we have done destructuring here.
we have divided the whole function into 3 parts:

`children: ` text/content inside badge

`variant: ` color style of badge

`size: ` size of badge

<p>and set these badges variant to default and size to md. if the user does not passes anything then these properties will apply. this allows to make components reusable and prevent errors.</p>

<p>next we created an object called variants which stores key value pairs of variant name and tailwind css classes. we defined this object with const beacuse we dont want the variant keys to change its value.</p>
<p>another approach to create badges was to use if else but it would make the code look messy and it is also easy to add new variants this way.</p>
next we defined another object called sizes which has key value pairs of size name and its tailwind css properties.

at last we returned the jsx in span tag with various properties.

| property     | function                                     |
| ------------ | -------------------------------------------- |
| inline-flex  | badge stays inline but uses flex             |
| items-center | vertiaclly center text                       |
| font-medium  | medium font-weight                           |
| rounded-full | shape of the container should be like a pill |

then we used `${variant[variant]}` and `${size[size]}`.

-- these are dynamic classes which changes based on props and picks correct color and size class.

<h5>components/ui/button.js</h5>
we have created a reusable button that supports:

| Prop      | Meaning                  |
| --------- | ------------------------ |
| children  | button text              |
| variant   | button color style       |
| size      | button size              |
| onclick   | function to run on click |
| disabled  | enable/disable button    |
| className | extra tailwind classes   |

set some default values to avoid error and some base styles to apply to every button.

| classes             | purpose                |
| ------------------- | ---------------------- |
| font-semibold       | slightly bold text     |
| rounded             | rounded corners        |
| transition-colors   | smooth hover color     |
| focus:outline-none  | remove default outline |
| focus:ring-2        | blue focus ring        |
| focus:ring-offset-2 | space around ring      |

next create variant and size object with key value pairs foir each button.
then apply disabled state logic by creating a const variable disabledStyles. if disable is true opacity becomes half and cursor changes.
atlast define return jsx which has button and its classes and the children.

<h5>components/ui/card.js</h5>
a card component which is used to group content like user info, stats, forms and charts. this component supports optional title and footer, diff color variants and custom styimg using className.

create variants object which contains variant name mapping to background and text styles.

now we have returned an outer card container with rounded corners, medium shadow, no child overflow, variant styling and custom classes.
this outer container card has conditional title rendering which means if title exits then render header else skip header completely. then it containes a header container with conditional styling. then it has a class for title. and lastly a children for card content.

next we added conditional footer to our card.

<h5>components/ui/input.js</h5>
create an input component with props like:

| props       | meaning                         |
| ----------- | ------------------------------- |
| type        | input type(text,email,password) |
| placeholder | hint text inside input          |
| value       | current input value             |
| onchange    | function to update value        |
| label       | label text(optional)            |
| error       | error message(optional)         |
| className   | extra styling                   |

rest everything is same like we did in previous components.

<h5>components/ui/modal.js</h5>
we have used <strong>use client</strong> here because modal needs client side components like onclick, isopen state and browser interaction.

imported a specific x icon from lucide-react to use in modal header.
the inside function modal we have used an if statement which means if modal is closed dont render anything and if not then return.

in return we have created a main wrapper div with properties:

| class          | purpose                                                      |
| -------------- | ------------------------------------------------------------ |
| fixed          | stay fixed on screen                                         |
| inset-0        | streches an element to cover entire area of parent container |
| z-50           | above everything                                             |
| flex           | center modal                                                 |
| items-center   | vertically aligned                                           |
| justify-center | horizontally aligned                                         |

next a backdrop of dark background is created which closes on clicking outside the modal. followed by a modal box which is the actual pop up. this contains header, body {children} and footer.

<h3>DAY3</h3>
This day our task was to work on a multipage app with next js routing and also create a landing page for our dashboard.

steps we performed: updated our floder structure by creating more .jsx files for the pages we wanted to display like landing, profile, about. then we updated the app/layout.js because we didn't want the same sidebar and navbar like dashboard here and the code written in this.jsx file is applied to all the pages. then we one by one updated and wrote the code of each page we wanted to display and laslty connected them with link tag from next js. had it been any html code we would have have used anchor tag but as we were working with next.js we used link tag.

the benefit of using link tag was that it enables client side navigation without a full page reload, leading to faster, smoother user experience and improved performance and SEO.

so the updated folder structure looks like:

```txt
my-dashboard
|----app
|     |----layout.js
|     |----page.js
|     |----global.css
|     |----about
|     |      |-----page.js
|     |----dashboard
|            |-----layout.js
|            |-----page.js
|            |-----profile
|                    |--------page.js
|
|----components
|     |----ui
|     |     |---sidebar.jsx
|     |     |---navbar.jsx
|     |     |---modal.jsx
|     |     |---input.jsx
|     |     |---card.jsx
|     |     |---button.jsx
|     |     |---badge.jsx
|     |-----LandingNavbar.jsx
|-----public
|-----package.json
|-----UI-COMPONENTS-DOCS.md
```

<h5>LandingNavbar.jsx</h5>
the purpose of this file was to create a clean SEO friendly page which displays before login or dashboard.

We started by importing Link from `next/Link`. When we use link client side navigation becomes faster as their is no reload for each page and state remains intact. we could have also used js event handlers but they are not SEO friendly.

next we created a landing navbar function and added export default to it so that it could be imported by other files.

inside the function we started by using a nav tag to create a navbar as it tells the browser and google that this is navigation and it improves the understandability of the code because of the use of semantic tag.

then we created another container to align all the items to center because there is tendency of all the items streching on large screens so to maintain the items spacing we created a container inside navbar. we also added responsiveness to this container using tailwind css properties like `sm:px-6` for tablet padding, `lg:px-8` for desktop padding and `px-4` for small screen padding.

then we created a div class with flexible layout so that it can align items of navbar acc to our need (logo to the left and navigation links on right side.). we achived this by using property called `justify-between`

then we created seperate multiple divs inside navbar for each item and styled them accordingly. we used Link tag with all the items which we wanted to redirect, like:

```bash
<Link href="/about" className"tailwind css propetries">
```

this type of button is called CTA Button (call to action).

also we have not used used client in this code because we are not using any event handlers or useState which work for client side. This is a server component which is static and does not reload the whole page.

<h5>app/Layout.js</h5>
this is the html structure of our entire app, contains common things shared by all the pages and the SEO metadata.

we started by importing globals.css because this page runs for all the routes so global css is loaded once and there is no need to import global css inside every page explicitly.

then we used a built in SEO feature of nextjs metadata which automatically adds title and description for our app. we could have used `<head>` like we used to do in html syntaxes but this is better optimized approach for nextjs.

then we defined the RootLayout function which is a special nextjs layout, we passed children as an argument in this and value of children depends on the page we are loading. it basically means konsa page load ho rha hai. then we inject this children inside `<body>` which means now it can be displayed on the browser.

<h5>app/page.js</h5>
this is the homepage of the app which is our landing page.

we started by importing all the components we needed in the landing page like landing navbar, buttons, cards and the link tag which will help us make CTA buttons for client side navigation.

next we created a home function which runs when we load the page followed by return which then contains the main wrapper div to bind all the elements of the page into one section and apply common styling to each item. and then called landing navbar inside the page.

| Property          | meaning                     |
| ----------------- | --------------------------- |
| min-h-screen      | at least full screen height |
| bg-gradient-to-br | gradient background         |
| form-blue-50      | light blue start            |
| to-indigo-100     | indigo end                  |

then we divided our remaining page into two sections hero and the features sections.

We added various components each with its own styling in our hero section like

| Property       | meaning                       | target     |
| -------------- | ----------------------------- | ---------- |
| text-5xl       | very large text               | heading    |
| font-bold      | bolder font weight            | heading    |
| text-gray-900  | dark text                     | heading    |
| mb-6           | margin bottom                 | heading    |
| text-xl        | text size                     | subtitle   |
| text-gray-900  | dark gray text                | subtitle   |
| mn-8           | bootm margin                  | subtitle   |
| max-w-2xl      | maximum width for readability | subtitle   |
| mx-auto        | center horizontally           | subtitle   |
| flex           | flexible layout               | CTA button |
| gap-4          | spacing                       | CTA Button |
| justify-center | centered                      | CTA Button |

then we created two buttons inside this CTA button div tag and wrapped those buttons in link seperately, because button is the UI and link is responsible for routing. To create Learn More button we used outline variant of button. these variants are pre-defined in tailwind css with specific properties and we could just import them in our code acc to our need.

this was followed by the features section where we created three cards wrapped in a div with grid layout. we then wrapped this grid into section tag to seperate it from hero section. in grid div tag we specified various properties for responsivness like `grid-cols-1` which tells 1 column if mobile and `md:grid-cols-3` three columns if desktop and some common styling like space between cards using `gap`.

<h5>app/about/page.js</h5>
again imported all the important components link landingNavbar, card and badge. Created a function called AboutPage

the page is then wrapped into one single div to allow better alignment of items and apply common css to whole page. called landing navbar inside this div followed by creating a wrapper div for the cards and heading.

then created two cards one with heading, paragraph and badges (all the badges were wrapped inside another div because we wanted horizontal layout for them) whereas second card containing list of items.

<h5>app/dashboard/page.js</h5>
we again did the samething like we did in previous pages. Imported necessary components, created a function, wrapped the whole page into one section, created seperate divs for each sub-section or content and styled them.

<h5>app/dashboard/profile/page.js</h5>
we started by use client because we will be using multiple client side components like useState, form inputs, onChange, buttonClicks.

then we imported `useState` because we need to store and update email,phone,location and bio followed by importing lucide icons for camera, mobile etc.

in this page we wanted to create controlled components which means they should input value that comes from state and updates state. so we next created some state variables like name, email etc.

then in return we defined wrapper div, page-header, main layout grid, profile card set to left column with its component in flex layout, editable forms on right side of the grid.

inside forms we created both kinds of inputs editable and non editable to understand the working of useState with onChange. We hardcoded the value of name which we can change if we want but it wont be updated on reloading the page, whereas email column is editable.

how email works: value comes from state, typing pdtaes state and set the value to new target value.

for password we used input type as password to automaticaaly hide characters typed.

next we created checkboxes for preference section
| Property | meaning |
| --- | --- |
|sr-only|hidden-visually, accessible|
|peer|allow sibling styling|
|peer-checked|style when checked|

<h5>components/ui/sidebar.jsx</h5>

started with importing all the necessary components one of them being `{usePathname}` from `next/navigation`. this allows us to use active menu highlighting as it tells which page is active.

we then set the sidebar state to true which means whenever the page will load sidebar will be opened but if we want to close sidebar we can just click onn it and ste the state to false.

then to get current route we declared a const variable pathname which uses usePathname now we check if the current URL is equal to the link we clicked in sidebar. if yes then highlight menu item. there are other ways by which we could achieve this meu highlighting like useLocation but this is an old way and is not used next.js or the manual state tracking using useState but it breaks if the page is refreshed.

<h6>WHY useSTATE breaks on page refersh </h6>
use state lives only in browser memory(RAM) and when we refresh browser memory is wiped, so react state resets.

<h3>DAY4</h3>
in this day we only updated our landing page and made it better looking with more content, responsive using md and lg, added some hover effects for animations
