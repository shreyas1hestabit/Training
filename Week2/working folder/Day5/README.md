<h1> WEEK2-DAY5: E-COMMERCE PLATFORM </h1>
<p>Starting over again because the first one got very cluttered and messy. I was not able to understand what I did where because proper folder structure was not maintained and I did not work step by step and jumped onto different steps all at once. Easy option was to start over than working with that mess. </p>
<p>Our goal is to make an e-commerce platform.</p>
<h3>PLANNING </h3>
<p>Divide the whole website into 10 pages and work step by step </p>
<ul>
<li>products: contain all the products</li>
<li>product: specific page for each product</li>
<li>Login Page</li>
<li>Sign-in page</li>
<li>Home page- main landing page</li>
<li>Cart</li>
<li>Wishlist</li>
<li>Profile</li>
<li>Help & FAQ</li>
<li>my Orders</li>
<li>refer and earn</li>
<li>rewards</li>
</ul>
<br>
<h2>HOME</h2>
<h3>LAYOUT AS OF NOW:</h3>
<p>|---HEADER----------|
   |---HERO------------|
   |---DISCOUNTS-------|
   |---PROD.CATEGORY---|
   |---PRODUCTS--------|
   |---FOOTER----------|
</p>
<h4>HEADER</h4>
<p>Have following components and subcomponents </p>
<ul>
<li>Menu list icon: dropdown contains list
<ul>
<li>profile</li>
<li>My orders</li>
<li>Cart</li>
<li>Wishlist</li>
<li>Help & FAQ</li>
<li>Refer and Earn</li>
<li>Rewards</li>
<li>Gift Cards</li>
</ul></li>
<li>Logo: link with home page.</li>
<li>Product list: on hover-> dropdown with all categories and sub-categories. Clickable.</li>
<li>Search Bar: suggestion as typing feature</li>
<li>wishlist: no of products in the wishlist badge.</li>
<li>cart: no of products in cart badge.</li>
<li>login followed by sign in if new user.</li>
</ul>

<h4>NOTE:</h4>
<p>wishlist and card will only work if user logged in otherwise not.</p>

<h4>HERO</h4>
<p>will contain a video with overlay button of explore which will lead to the products page.</p>

<h4>OFFERS AND DISCOUNTS</h4>
<p>banner which displays the discount or any offer if going on.</p>
<p>-->try to get some products in this section and make it a clickable link. if this works then add one page for this too.</p>

<h4>PRODUCT CATEGORY</h4>
<p>displays all the product categories available and make each category card clickable which leads to the specific category page.</p>

<h4>PRODUCTS</h4>
<p>Display one product of each category. below every product view similar products button which takes you to category page of that product.</p>

<h4>FOOTER</h4>
<p>divide in 3 columns and 2 rows
|about us| contact us| socials |
|_____________________________ |
| copyright                    |
</p>
<br>
<h2>LOGIN PAGE</h2>
<p>This page will have: </p>
<ul>
<li>header : menu and logo to go to home page </li>
<li>Email or phone no : mandate input type</li>
<li>password</li>
<li>login button</li>
<li>new user? sign in button</li>
<li>footer same as every page</li>
</ul>
<br>
<h2>SIGN IN </h2>
<p>follow up of login page having: </p>
<ul>
<li> first name</li>
<li>last name</li>
<li>phone</li>
<li>email</li>
<li>password</li>
<li>confirm pass: same as pass</li>
<li>Address- 3 lines</li>
<li>check box of terms and conditions</li>
</ul>
<br>
<h2>WISHLIST</h2>
<p>will only be accesible if you have logged in otherwise "oops! login first" message with a login button to redirect to login page</p>
<ul>
<li>header same as every page</li>
<li>footer</li>
<li>product cards</li>
<li>move to cart</li>
<li>trash</li>
<li>qty increase or decrease</li>
<li>click on product to redirect it to product page</li>
</ul>
<br>
<h2>cart</h2>
<ul>
<li>header</li>
<li>footer</li>
<li>items added to cart</li>
<li>total price + price breakdown</li>
<li>coupon code</li>
<li>address</li>
<li>product select krne pr back to product page</li>
<li>qty increase decrease</li>
<li>move to wishlist</li>
<li>trash</li>
<li>this followed by order placed after clicking order button.</li>
</ul>
<br>
<h2>PROFILE</h2>
<p>everything should be editable</p>
<ul>
<li>header</li>
<li>footer</li>
<li>photo</li>
<li>name</li>
<li>phone</li>
<li>email</li>
<li>address</li>
</ul>
<br>
<h2>ORDERS</h2>
<p> see if this works without backend. if yes then only plan.</p>
<br>
<h2>FAQ</h2>
<p>similar to our task of day3 where we made clickable dropdown cards.</p>
<ul>
<li>header</li>
<li>return policy add</li>
<li>footer</li>
</ul>

<h2>HOME PAGE</h2>
<h3>Problems Faced</h3>
<ol>
<li><h4>Error faced:</h4>Unable to Link .html with other files in the folder. <h4>Reason:</h4> Was not using proper file path. <h4>Solution:</h4><ul>
<li>instead of linking images in assets foler with path "/assets/image_name.svg" we need to first go to root folder as this searches for image in html folder and not the root folder. so the correct path would be "../assets/image_name.svg".</li>
<li> I Was using rel="stylesheet_global" because i was linking to stylesheets to the file so i thought that we need to define two different relations otherwise it would create conflict, so changed the relation to stylesheet because irrespective of how many .css you link the html knows only one relation i.e. stylesheet. so you dont explicitly name them differently and it does not get meixed up. </li>
</ul></li>
</ol>
<h3>PROBLEMS I COULD NOT FIX</h3>
<ol>
<li>Video not getting loaded in header</li>
<li>Could not fetch categories from dataset to display on home page hence could also not make products dropdown because categories were not fetched so could not divide the dataset to display.</li>
<li>wishlist counter displaying zero even after there are items in wishlist.</li>
<li>items get moved to cart but are not removed from wishlist.</li>
<li>could not display product page for each single product. all the products are visible on one page but i also wanted that if i click on certain product a product page opens which displays all the details related to that product and also suggest similar items. I could not achieve that.</li>
</ol>
