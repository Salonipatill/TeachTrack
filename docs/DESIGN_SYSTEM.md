# TeachTrack design system

## Current shared UI updates

The active stylesheets are app.css and theme.css; the colour inventory now includes
both, with selector scope retained for light/dark tokens. theme.js initializes the
saved browser preference before rendering; app.js handles menus, forms and quizzes.
The sun/moon button is fixed at bottom-right across public, login, dashboard and
error templates. It has an accessible label, pressed state and keyboard focus.

Result academic details use an aligned grid: five columns on large screens, three
at 900px and two at 480px. Labels sit above values with no browser default dd indent.
Question numbers are inside cards above question text; the attempt form is at most
800px wide and long text/options wrap. Launch/deadline labels explicitly show IST.

The public Contact page retains the homepage header/footer. All shared pages have
a keyboard skip link; reduced-motion preferences are respected. Mobile controls,
form actions and toolbar wrapping are adjusted at small widths. Form navigation
shows progress and prevents duplicate submission; back navigation restores it.

Light muted text uses #596b75. Dark mode sets the page background to #10191f,
surfaces to #1a2831, primary text to #e6edf1 and muted text to #a5b5be. The generated
colour index is authoritative for exact selector/property declarations.


Design reference for the source reviewed on 21 October 2026. The active visual implementation is ClassApp/static/ClassApp/app.css plus theme.css, loaded by base.html. This guide explains the design decisions expressed by that stylesheet; it does not introduce an additional theme framework.

## 1. Visual direction and source files

TeachTrack uses a restrained teal-and-green palette, light surfaces, dark text, rounded cards and compact academic controls. The public pages have more open space and large introductory typography. Authenticated screens prioritize navigation, filtering, forms, tables and readable status feedback.

| Source | Responsibility |
| --- | --- |
| ClassApp/static/ClassApp/app.css | Current tokens, layouts, components, states and breakpoints |
| ClassApp/static/ClassApp/app.js | Sidebar, mobile navigation, quiz formset and carousel behavior |
| Templates/base.html | Common HTML head, application shell and authentication shell |
| Templates/public_base.html | Public website header, navigation, main area and footer |
| Templates/index.html | Homepage introduction, seven-photo carousel and feature cards |
| Templates/campus_life.html | Campus identity, cover photograph, facilities, gallery and location |
| Templates/registration/login.html | Current role-aware sign-in screens |
| Templates/account_form.html | Director-managed account role links and role-specific fields |
| ClassApp/static/img/ | Source photography and image assets |

The retained original theme and legacy template inline styles are not the active design reference. The generated staticfiles/ directory is build output. Make a design change in source and regenerate collected assets rather than editing a hash-named output file.

## 2. Colour index and theme variables

The active stylesheet contains 111 distinct explicit hex literals, plus named white and transparent values. [COLOUR_INDEX.md](COLOUR_INDEX.md) lists every value, RGB triplet, alpha and direct selector/property usage. colour-index.json provides the same data for tools. The offline HTML handbook includes visual swatches and a filter for colour values or selectors.

### Base tokens

| Token | Value | RGB | Main purpose |
| --- | --- | --- | --- |
| --bg | #f5f7fa | 245, 247, 250 | Default application body background |
| --ink | #172d35 | 23, 45, 53 | Main headings and body text |
| --muted | #596b75 | 89, 107, 117 | Secondary descriptions, help text and small metadata |
| --line | #e5ebee | 229, 235, 238 | General borders and dividers |
| --teal | #126c64 | 18, 108, 100 | Primary buttons, links, accent text and selected states |
| --teal-dark | #0e514b | 14, 81, 75 | Hover/darker primary interaction colour |
| --pale | #e8f4ef | 232, 244, 239 | Selected navigation and pale accent surfaces |
| --white | #fff | 255, 255, 255 | Standard panels, input and secondary-button surfaces |
| --shadow | 0 3px 12px #19353c04 | 25, 53, 60 at 1.57% alpha | Very subtle application-card shadow |

These are CSS custom properties defined in :root. They are inherited globally. Most functional components use them, but public/campus components also contain explicit green/grey values. A token change does not automatically recolour those literal values.

### Main public/campus palette

| Value | Role | Example selectors |
| --- | --- | --- |
| #f7f9f7 | Public page canvas | .public-site |
| #143c35 | Deep green public footer | .site-footer |
| #d3e0d9 | General footer foreground | .site-footer |
| #c4d8cb | Footer navigation links | .site-footer nav a |
| #a7c1b0 | Footer bottom metadata | .footer-bottom |
| #d7e7dc | Footer brand-icon surface | .site-footer .brand-icon |
| #204c3e | Footer brand-icon letter | .site-footer .brand-icon |
| #dfe8e2 | Public dividers | .home-features; .campus-spaces; .campus-location-tag |
| #edf3ee | Campus facility-card surface | .campus-facilities article |
| #e6f0e8 | Campus location panel surface | .campus-visit |
| #193e35 | Carousel base and portrait-image mat | .carousel-stage; .campus-slide-portrait img |
| #c6d4ca | Inactive carousel dot | .carousel-dots button::after |
| #76a88b | Small campus-marker dot | .campus-marker |
| #e7af49 | Keyboard-focus outline | :focus-visible selectors |

The detailed source index is authoritative for all usages. For example, #dfe8e2 remains on several current separators even though the homepage’s former home-community element and its CSS were removed.

### State and meaning colours

| State | Background | Foreground | Selector / use |
| --- | --- | --- | --- |
| Pending complaint / selected incorrect review | #fff3dc | #9a6b17 | .pending |
| In-progress complaint | #eaf0ff | #5474ae | .in_progress |
| Resolved complaint / correct review | #e7f4ec | #3c8261 | .resolved |
| General success/info alert | #e8f4eb | #36744f | .alert; border #cbe5d2 |
| Error alert | #fff1ed | #a7523e | .alert.error; border #efd5ce |
| Field error list | #fff0ed | #ac4239 | .errorlist |
| Unread notification | #f0f8f3 | Normal content colours | .notification.unread; left border #65a98d |
| Default resource/file icon | #eef5f1 | #3c8d70 | .file-icon |
| Every-third list-row icon | #fff5e6 | #bd8c3a | .list-row:nth-child(3n) .file-icon |
| Participation progress | #edf3ef track | #539b84 fill | progress and browser-specific progress selectors |
| Readable answer block | #f0f7f3 | Inherited ink | .answer-box |

The resource icon variation is positional CSS, not a fixed Notes/PYQ/Assignment colour mapping. Status meaning is expressed in text as well as colour. The same pending/resolved styling is reused in quiz review, so colour interpretation depends on the displayed label.

### Alpha colours and overlays

| Literal | RGB | Alpha | Purpose |
| --- | --- | --- | --- |
| #fffffff5 | 255, 255, 255 | 96.08% | Public sticky header surface |
| #ffffffc9 | 255, 255, 255 | 78.82% | Authenticated topbar surface |
| #fffffff2 | 255, 255, 255 | 94.90% | Carousel arrow surface |
| #ffffff80 | 255, 255, 255 | 50.20% | Carousel arrow border |
| #ffffff20 | 255, 255, 255 | 12.55% | Public footer separator |
| #102b24e8 | 16, 43, 36 | 90.98% | Dark end of photo-caption gradient |
| #122d2526 | 18, 45, 37 | 14.90% | Carousel arrow shadow |
| #17303322 | 23, 48, 51 | 13.33% | Mobile sidebar shadow |
| #173e3512 | 23, 62, 53 | 7.06% | Carousel shadow |
| #1c493214 | 28, 73, 50 | 7.84% | Campus cover shadow |

Eight-digit values use RRGGBBAA. Alpha is the final byte divided by 255. The visual result is a composite with whatever is underneath; the RGB value alone is not the final on-screen colour. The swatch catalogue shows transparency against a checkerboard to make this distinction visible.

### Contrast measurements

The values below were computed from the sRGB relative-luminance formula for the listed opaque pairs. They describe these pairs only; they are not an audit of every rendered element, transparency composite or text size.

| Foreground / background | Ratio |
| --- | --- |
| #172d35 on #ffffff | 14.35 : 1 |
| #6e7e86 on #ffffff | 4.21 : 1 |
| #ffffff on #126c64 | 6.26 : 1 |
| #ffffff on #0e514b | 9.14 : 1 |
| #d3e0d9 on #143c35 | 8.93 : 1 |
| #9a6b17 on #fff3dc | 4.26 : 1 |
| #5474ae on #eaf0ff | 4.10 : 1 |
| #3c8261 on #e7f4ec | 4.07 : 1 |
| #a7523e on #fff1ed | 4.86 : 1 |

Some muted/status combinations have substantially less contrast than the main text and buttons. Evaluate their actual font size, weight and surrounding surface when setting an accessibility target. The project does not claim that all small text or colour combinations have independently passed such a review.

## 3. Typography

The active stylesheet uses a system font stack: system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif. The current interface does not request a hosted web font. Retained original font assets do not change that stack unless a template explicitly loads the older theme.

| Element | Declared size / style |
| --- | --- |
| Body | 14px, line-height 1.65 |
| Generic h1 | 32px, weight 700, line-height 1.25, letter-spacing -1px |
| Generic h2 | 18px, line-height 1.4, letter-spacing -0.3px |
| Generic h3 | 15px |
| Small text | 12px |
| Eyebrow | 10px, weight 750, 1.9px letter-spacing |
| Standard form label | 12px, weight 600 |
| Help text | 11px, muted, block layout |
| Error list | 12px, coloured surface and rounded edges |
| Default table body | 12px |
| Default table headings | 10px, uppercase, 0.6px letter-spacing |
| Navigation | Sidebar 12px; public header links 12px |
| Main number in stat card | 33px with a compact line-height |
| Homepage hero | clamp(44px, 4.5vw, 62px), line-height 1.1 |
| Campus hero | clamp(42px, 4.5vw, 62px), line-height 1.08 |
| Authentication hero | 49px before responsive overrides |
| Sign-in card heading | 24px before responsive overrides |
| Carousel caption heading | 25px; 21px in the smallest breakpoint |
| Campus space-card heading | 22px; 21px in the smallest breakpoint |

Responsive rules deliberately replace some clamp values with fixed sizes after the layout changes. Homepage hero text becomes 48px below 1050px, 55px in the stacked layout below 800px and 47px below 480px. Campus hero text becomes 51px below 950px, 54px below 700px and 46px below 480px. Do not infer final rendered size from the first rule alone.

## 4. Layout and spacing

### Public layout

The public content container has a maximum width of 1180px. Its declared width is viewport width minus 80px, changing to minus 48px at 1050px and minus 36px at 480px. This corresponds to 40px, 24px and 18px side margins when the max-width does not otherwise constrain it.

The desktop public header has an 88px minimum height, a white translucent surface and a bottom border. It is sticky at the viewport top with z-index 30. Below 800px, brand/account actions stay on the upper row while navigation moves to its own full-width row. Below 480px, the separate Get started header button is hidden; student registration remains available elsewhere.

Homepage hero uses a 1fr/1.12fr grid with a 56px gap. Below 800px it stacks. The feature grid has three columns on desktop and one in the compact public layout. The public footer uses a 1.6fr/1fr/1fr grid, then two columns at small phone widths with the introduction spanning both columns.

### Authenticated layout

The sidebar is fixed, full-height and initially 242px wide. Main content uses a matching left margin and calculated width. At 1180px the sidebar becomes 215px; at 900px it becomes 200px. At 680px it is hidden until opened by the menu button, and the content fills the viewport. The open mobile sidebar is 242px wide with a shadow.

The application topbar is 77px high, reducing to 66px on phones. Main padding starts at 35px 36px 20px and becomes smaller at tablet/phone widths. Stat cards use four columns, then two. General two-column panels stack at 900px. The resource grid uses three, two or one column according to the general app breakpoints.

### Campus detail layout

The campus hero pairs flexible text with a maximum 399px cover column. At 950px the cover column becomes 330px; below 700px it stacks and centers a cover up to 370px. The cover image’s natural portrait ratio is preserved so its Campus title remains visible.

Library/café cards use two columns, stacking below 700px. Facilities use four columns, two below 950px and one below 480px. The photo gallery uses three columns, two below 700px and one below 480px. The location panel pairs text with a 372px image column, reducing to 300px below 950px and stacking below 700px.

### Spacing conventions

The project uses explicit pixel spacing, not a comprehensive named spacing-token scale. Common values include 8–12px for label/icon gaps, 14–20px for control/list spacing, 22–28px for card content, 35–40px for larger sections and 55–70px for public-page separation. Preserve the surrounding component’s rhythm when adding a new element instead of assuming every gap must be a multiple of one global unit.

## 5. Borders, radii and shadows

| Element | Treatment |
| --- | --- |
| Standard button | 1px teal border; 8px radius |
| Form input/select/textarea | 1px #d6e1e3 border; 7px radius; 11px 12px padding |
| General panel/stat card | 1px light border; 11px radius; subtle --shadow |
| Public feature card | 12px radius and #e0e8e2 border |
| Carousel | 18px radius, hidden overflow and deeper soft shadow; 12px radius on phones |
| Carousel arrows | Circular, 42px diameter; 36px at the smallest breakpoint |
| Carousel dot buttons | 28px wide and 32px high; visible mark is 7px, selected mark 23px |
| Campus cover | 8px white frame, 16px outer radius and 9px image radius |
| Campus gallery tile | 11px radius and light border |
| Campus visit panel | 14px radius and pale green surface |
| Status badge | 5px radius with 4px 9px padding |
| Answer block | 7px radius and 19px padding |
| Keyboard focus | 3px amber outline with 3px offset on standard interactive elements |

Use component classes for meaning rather than duplicating inline styles. The CSS contains border/shadow literals where a component needs a distinct treatment; the colour index records those values and exact selectors.

## 6. Component reference

| Component | Main selectors | Behavior / purpose |
| --- | --- | --- |
| Brand | .brand, .brand-icon, .brand-dot | Text wordmark and code-rendered T tile; footer uses a lighter tile |
| Primary action | button, .button | Filled teal with white text; darker hover |
| Secondary action | .secondary | White surface, neutral border; pale teal hover |
| Small/full action | .small, .full | Compact padding/text or full-width button |
| Sidebar | .sidebar, .workspace, .nav-badge | Fixed module navigation, group label and unread count |
| Account identity | .sidebar-bottom, .avatar | Name/role summary and first-letter avatar |
| Topbar | .topbar, .top-actions | Notifications, password change and POST sign-out |
| Page heading | .page-head, .head-actions | Page title/description with contextual actions |
| Summary numbers | .stats, .stat-card | Role-dependent dashboard values |
| Welcome panel | .welcome-banner, .banner-art | Decorative dashboard introduction and quiz link |
| General panel | .panel, .section-head | Content card with optional heading/action |
| Resource rows/cards | .list-row, .resource-card, .resource-bottom | Resource metadata, file symbol and download action |
| Filtering | .filter-bar | Search/category/subject/sort controls with responsive wrapping |
| Form | .form-panel, .form-actions, .helptext, .errorlist | Labelled fields, validation and save/navigation actions |
| Role links | .role-switch | GET navigation between sign-in or account-creation roles; current item is teal |
| Question builder | .question-form, .question-image | Formset question groups and bounded images |
| Quiz choices | .option, .option:has(input:checked) | Clickable labels; selected option uses a pale surface and teal border |
| Status | .status, .pending, .in_progress, .resolved | Textual semantic state with colour |
| Alerts | .alert, .alert.error | Messages and errors announced through template status/alert roles |
| Table | .table-wrap, table, th, td | Compact tabular information; horizontal wrapper when needed |
| Inbox | .notification, .notification.unread | Read/unread styling and recipient actions |
| Complaint timeline | .timeline | Vertical line, event markers and chronological conversation |
| Answer/result | .answer-box, .answer-row, .score | Faculty answers, option review and score display |
| Charts | .chart-row, progress, .rating-chart, meter | Native HTML progress/meter visualization, not an external chart package |
| Pagination | .pagination | Previous/next page and page context |
| Authentication | .auth-main, .auth-layout, .auth-intro, .auth-card | Anonymous brand, intro panel and sign-in form |
| Public header/footer | .site-header, .site-nav, .site-footer | Shared public navigation and campus/account links |
| Homepage carousel | .campus-carousel, .carousel-stage, .campus-slide | User-controlled photos, captions and controls |
| Campus identity | .campus-identity, .campus-cover | Institute logo and full portrait main image |
| Campus details | .campus-spaces-grid, .campus-facilities, .campus-photo-grid, .campus-visit | Facilities, student-life gallery and contact/location |

### Button and control states

Primary hover changes to --teal-dark and stays white. Secondary hover uses --pale with teal text/border. Links normally underline on hover, while button-like links suppress that underline. Standard links, buttons, inputs, textareas and selects receive a focus-visible outline. Checkbox/radio accents use --teal. Selected role links and carousel dots use aria-current-driven selectors.

Hidden carousel figures use the native hidden attribute; there is no fade/slide animation or autoplay timer. The question builder disables Add question at 50 forms. A disabled add control is not a replacement for the formset’s server-side maximum.

## 7. Complete responsive breakpoint index

| Query | Main effects |
| --- | --- |
| min-width:1500px | Larger authenticated main padding and stat gaps |
| max-width:1180px | Smaller sidebar, general app padding and two-column resource grid |
| max-width:1050px | Public container margins/header gaps and homepage hero adjustments |
| max-width:950px | Campus hero/visit image columns shrink; facilities become two columns |
| max-width:900px | Smaller sidebar, two-column stats, stacked general two-column panels and stacked authentication layout |
| max-width:800px | Public header navigation wraps; homepage stacks; public features become one column |
| max-width:700px | Campus hero, space cards and visit panel stack; gallery becomes two columns |
| max-width:680px | Authenticated mobile sidebar/menu, full-width main, one-column resource grid and compact app controls |
| max-width:480px | Public phone layout, one-column campus facilities/gallery, smaller headings/arrows and two-column footer |

These breakpoints apply to different component families. Do not consolidate them without testing the affected screens. Public pages and application screens do not share every layout threshold.

## 8. Photography and asset index

### Homepage carousel

| Photo | Source file | Content | Natural size |
| --- | --- | --- | --- |
| 1 | Slider-img4.jpg | Students studying on campus lawn | 1600 × 1066 |
| 2 | Slider-img1.jpg | Students and guitar in common area | 1600 × 1066 |
| 3 | Slider-img2.jpg | Student panel discussion; portrait mat | 864 × 1152 |
| 4 | Slider-img3.jpg | Student/faculty group | 1600 × 1200 |
| 5 | Slider-img5.jpg | Auditorium gathering | 1080 × 890 |
| 6 | sait-campus-extra-1.jpg | Institute building and lawn | 559 × 357 |
| 7 | sait-campus-extra-2.jpg | Computer lab | 447 × 447 |

Carousel images normally use object-fit:cover and a 4:3 frame. The portrait slide uses contain to preserve the image. The stacked tablet layout uses a 3:2 frame before returning to 4:3 on the smallest phones. The bottom caption uses a transparent-to-dark gradient. White circular arrows remain visible over the photo.

### Campus page images

| File | Purpose | Natural size |
| --- | --- | --- |
| sait-logo.jpg | Institute identity | 447 × 447 |
| sait-campus-main.jpg | Selected main cover; full image without cropping | 399 × 501 |
| about-img2.jpg | Library/Knowledge Resource Center card | 1080 × 654 |
| about-img1.jpg | Common Ground card | 1080 × 693 |
| sait-industry-visit.jpg | Student-life gallery | 678 × 452 |
| sait-campus-building.jpg | Location panel | 372 × 299 |
| Seven carousel files above | Student-life gallery; combined with industry-visit image gives eight photos | See above |

The supplied thumbnails have limited native resolution. They are stored unchanged; the app does not claim to reconstruct high-resolution originals. Keep the selected main image at an appropriate size and preserve its visible title. Source URLs are in CAMPUS_CONTENT.md. The older Banner-bg.jpg remains an available original asset but is not the selected current cover.

### Icons

The current shell uses Unicode symbols for several module icons and small inline SVG paths for carousel arrows. SVG arrows inherit currentColor. Retained FontAwesome assets exist, but the current base template does not load that old icon stylesheet. Photographic logos are images rather than generated typography.

## 9. Accessibility and content conventions

Use real buttons for actions and links for navigation. Keep visible text alongside status colours. Provide useful alt text that describes the photograph rather than its filename. Use a native hidden state for inactive carousel slides so hidden content does not remain an ordinary visible page region.

Public pages include a skip link. The sidebar menu exposes aria-controls and aria-expanded. The carousel exposes labels, selected-dot state, a polite live status and keyboard controls. Headings, form labels, field errors and table headings provide structure. Keep arrow and dot hit areas usable when adding photos; the current seven-dot layout was checked at 320px and 390px widths.

Student year/semester fields belong to student forms, not staff forms. Faculty sign-in should explain director-managed account creation rather than direct a new staff user to public student registration. Campus descriptions should use verified official information with source links. Keep internal implementation details out of ordinary product prompts unless they help the person complete the task.

## 10. Safe design-change workflow

1. Identify the active template and class rather than editing a retained legacy file with a similar name.
2. Locate the token or literal in app.css; use the complete colour index to identify related usages.
3. Implement the component change in source, including hover/focus/selected/error states where relevant.
4. Verify the surrounding public/app layout at affected breakpoints, including narrow phones.
5. Verify real image responses and the browser console for interactive changes.
6. Run collectstatic for current generated output and rebuild documentation when values/components change.

No blanket colour replacement should be treated as a finished redesign. Check status meaning, text contrast, SVG inheritance, alpha overlays and screenshots after changing the palette.
