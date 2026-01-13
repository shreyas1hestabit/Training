WEEK2-DAY1

This project demonstrates the use of **semantic HTML5 tags** to structure a blog homepage without using non-semantic elements like `<div>`.


## Semantic Tags Used & Purpose

### `<header>`
Used to define the top section of the page containing the site navigation and logo.



### `<nav>`
Used for primary navigation links and category-based navigation to indicate navigational content to assistive technologies.



### `<figure>`
Used to group images with related textual content such as category titles and post information.



### `<main>`
Wraps the primary content of the page including featured posts, articles, and the sidebar.



### `<section>`
Used to logically group related content such as:
- Image scroll container
- App download promotion
- Article content blocks
- Sidebar sections (recent posts, categories, tags)


### `<article>`
Used for individual blog posts because each post is independently meaningful and reusable.



### `<header>` (inside article)
Used to hold article-specific metadata such as category, title, author, and publish date.



### `<time>`
Used to represent publication dates in a machine-readable format.



### `<footer>` (inside article)
Used to store article-related metadata like tags and share links.


### `<aside>`
Used for supplementary content that supports the main page, including:
- Search bar
- Recent posts
- Categories
- Tag clouds
- Feedback form


### `<form>` 
Used to collect user input for search and feedback purposes.



### `<label>`
Used to associate text with form controls for accessibility.



### `<button>`
Used for interactive actions such as scrolling and downloading.



## Accessibility

- `aria-label` used where native semantics needed clarification
- All images include `alt` text

