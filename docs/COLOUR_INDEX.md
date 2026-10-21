# Complete colour index

Generated from `app.css` and `theme.css` on 21 October 2026: 135 distinct hex literals plus named CSS colours. This is an inventory of the active application stylesheet, not of photographic pixels, browser defaults or the retained legacy theme.

## Theme variables

| Token | Declared value |
| --- | --- |
| `:root / --bg` | `#f5f7fa` |
| `:root / --ink` | `#172d35` |
| `:root / --muted` | `#6e7e86` |
| `:root / --line` | `#e5ebee` |
| `:root / --teal` | `#126c64` |
| `:root / --teal-dark` | `#0e514b` |
| `:root / --pale` | `#e8f4ef` |
| `:root / --white` | `#fff` |
| `:root / --shadow` | `0 3px 12px #19353c04` |
| `:root / --muted` | `#596b75` |
| `[data-theme=dark] / --bg` | `#10191f` |
| `[data-theme=dark] / --ink` | `#e6edf1` |
| `[data-theme=dark] / --muted` | `#a5b5be` |
| `[data-theme=dark] / --line` | `#33444e` |
| `[data-theme=dark] / --teal` | `#76d2bc` |
| `[data-theme=dark] / --teal-dark` | `#247665` |
| `[data-theme=dark] / --pale` | `#203d36` |
| `[data-theme=dark] / --white` | `#1a2831` |
| `[data-theme=dark] / --shadow` | `0 3px 12px #0002` |

## Every explicit colour and its source usage

Three-digit hex expands each digit twice. Eight-digit hex is RRGGBBAA, with the last byte specifying alpha. RGB below is the uncomposited colour; its visible appearance also depends on opacity and the underlying surface. Named white aliases #ffffff, while transparent has zero opacity. `currentColor` in SVG arrows inherits its surrounding text colour.

| CSS literal | RGB | Opacity | Selectors and properties |
| --- | --- | --- | --- |
| `#0002` | 0, 0, 0 | 13.33% | `.theme-toggle → box-shadow`; `[data-theme=dark] → --shadow` |
| `#0e514b` | 14, 81, 75 | 100.00% | `:root → --teal-dark` |
| `#10191f` | 16, 25, 31 | 100.00% | `[data-theme=dark] → --bg` |
| `#101e19` | 16, 30, 25 | 100.00% | `[data-theme=dark] .site-footer → background` |
| `#102b24e8` | 16, 43, 36 | 90.98% | `.campus-slide figcaption → background` |
| `#111e26` | 17, 30, 38 | 100.00% | `[data-theme=dark] :is(input:not([type=checkbox]):not([type=radio]), select, textarea) → background` |
| `#122d2526` | 18, 45, 37 | 14.90% | `.carousel-arrow → box-shadow` |
| `#126c64` | 18, 108, 100 | 100.00% | `:root → --teal` |
| `#143c35` | 20, 60, 53 | 100.00% | `.site-footer → background` |
| `#156c62` | 21, 108, 98 | 100.00% | `.art-small → background` |
| `#172d35` | 23, 45, 53 | 100.00% | `:root → --ink` |
| `#17303322` | 23, 48, 51 | 13.33% | `.sidebar → box-shadow` |
| `#173e3512` | 23, 62, 53 | 7.06% | `.carousel-stage → box-shadow` |
| `#176c5c` | 23, 108, 92 | 100.00% | `[data-theme=dark] :is(button, .button):not(.secondary):not(.theme-toggle) → background` |
| `#19353c04` | 25, 53, 60 | 1.57% | `:root → --shadow` |
| `#193e35` | 25, 62, 53 | 100.00% | `.campus-slide-portrait img → background`; `.carousel-stage → background` |
| `#1a2831` | 26, 40, 49 | 100.00% | `[data-theme=dark] → --white` |
| `#1c493214` | 28, 73, 50 | 7.84% | `.campus-cover → box-shadow` |
| `#203d32` | 32, 61, 50 | 100.00% | `[data-theme=dark] :is(.notification.unread, .alert) → background` |
| `#203d36` | 32, 61, 54 | 100.00% | `[data-theme=dark] → --pale` |
| `#204c3e` | 32, 76, 62 | 100.00% | `.site-footer .brand-icon → color` |
| `#247665` | 36, 118, 101 | 100.00% | `[data-theme=dark] → --teal-dark` |
| `#283d37` | 40, 61, 55 | 100.00% | `[data-theme=dark] .status → background` |
| `#33444e` | 51, 68, 78 | 100.00% | `[data-theme=dark] → --line` |
| `#338b78` | 51, 139, 120 | 100.00% | `[data-theme=dark] :is(button, .button):not(.secondary):not(.theme-toggle) → border-color` |
| `#36744f` | 54, 116, 79 | 100.00% | `.alert → color` |
| `#3c8261` | 60, 130, 97 | 100.00% | `.resolved → color` |
| `#3c8d70` | 60, 141, 112 | 100.00% | `.file-icon → color` |
| `#406452` | 64, 100, 82 | 100.00% | `[data-theme=dark] :is(.notification.unread, .alert) → border-color` |
| `#432827` | 67, 40, 39 | 100.00% | `[data-theme=dark] :is(.alert.error, .errorlist) → background` |
| `#435f56` | 67, 95, 86 | 100.00% | `.home-explore → color` |
| `#443b24` | 68, 59, 36 | 100.00% | `[data-theme=dark] .status.pending → background` |
| `#46614f` | 70, 97, 79 | 100.00% | `.campus-photo-grid figcaption → color` |
| `#4b6255` | 75, 98, 85 | 100.00% | `.campus-identity strong → color` |
| `#539b84` | 83, 155, 132 | 100.00% | `progress::-moz-progress-bar → background`; `progress::-webkit-progress-value → background` |
| `#5474ae` | 84, 116, 174 | 100.00% | `.in_progress → color` |
| `#596b75` | 89, 107, 117 | 100.00% | `:root → --muted` |
| `#5b9d84` | 91, 157, 132 | 100.00% | `.timeline article:before → background` |
| `#5c7566` | 92, 117, 102 | 100.00% | `.campus-visit p → color` |
| `#62776a` | 98, 119, 106 | 100.00% | `.campus-facilities p → color` |
| `#63766f` | 99, 118, 111 | 100.00% | `.site-nav a → color` |
| `#647c6c` | 100, 124, 108 | 100.00% | `.campus-cover figcaption → color` |
| `#65a98d` | 101, 169, 141 | 100.00% | `.notification.unread → border-left` |
| `#668179` | 102, 129, 121 | 100.00% | `.welcome-banner p → color` |
| `#687b81` | 104, 123, 129 | 100.00% | `.sidebar nav a → color` |
| `#6a7b82` | 106, 123, 130 | 100.00% | `.top-actions a → color` |
| `#6b7e73` | 107, 126, 115 | 100.00% | `.carousel-heading → color`; `.carousel-position → color` |
| `#6b7e85` | 107, 126, 133 | 100.00% | `.stat-card>span → color` |
| `#6e7e86` | 110, 126, 134 | 100.00% | `:root → --muted` |
| `#708475` | 112, 132, 117 | 100.00% | `.campus-location-tag → color` |
| `#75858c` | 117, 133, 140 | 100.00% | `.announcement-preview p → color` |
| `#75858d` | 117, 133, 141 | 100.00% | `.empty → color` |
| `#76a88b` | 118, 168, 139 | 100.00% | `.campus-marker → background` |
| `#76d2bc` | 118, 210, 188 | 100.00% | `[data-theme=dark] → --teal` |
| `#784640` | 120, 70, 64 | 100.00% | `[data-theme=dark] :is(.alert.error, .errorlist) → border-color` |
| `#7b8a81` | 123, 138, 129 | 100.00% | `.campus-breadcrumb → color` |
| `#7c8a80` | 124, 138, 128 | 100.00% | `.campus-source → color` |
| `#8a9d91` | 138, 157, 145 | 100.00% | `.feature-number → color` |
| `#94a0a5` | 148, 160, 165 | 100.00% | `.workspace → color` |
| `#99a6aa` | 153, 166, 170 | 100.00% | `footer → color` |
| `#9a6b17` | 154, 107, 23 | 100.00% | `.pending → color` |
| `#a5b5be` | 165, 181, 190 | 100.00% | `[data-theme=dark] → --muted` |
| `#a5c0af` | 165, 192, 175 | 100.00% | `.footer-about>span → color` |
| `#a7523e` | 167, 82, 62 | 100.00% | `.alert.error → color` |
| `#a7c1b0` | 167, 193, 176 | 100.00% | `.footer-bottom → color` |
| `#a9c9b5` | 169, 201, 181 | 100.00% | `.site-footer .brand-dot → color` |
| `#ac4239` | 172, 66, 57 | 100.00% | `.errorlist → color` |
| `#b0e4cc` | 176, 228, 204 | 100.00% | `[data-theme=dark] .status → color` |
| `#b8efd0` | 184, 239, 208 | 100.00% | `[data-theme=dark] :is(.notification.unread, .alert) → color` |
| `#bd8c3a` | 189, 140, 58 | 100.00% | `.list-row:nth-child(3n) .file-icon → color` |
| `#c2d5c9` | 194, 213, 201 | 100.00% | `.footer-about p → color` |
| `#c4d8cb` | 196, 216, 203 | 100.00% | `.site-footer nav a → color` |
| `#c6d4ca` | 198, 212, 202 | 100.00% | `.carousel-dots button::after → background` |
| `#cadbd0` | 202, 219, 208 | 100.00% | `.header-sign-in → border` |
| `#cbe5d2` | 203, 229, 210 | 100.00% | `.alert → border` |
| `#cfe3d7` | 207, 227, 215 | 100.00% | `.art-square → box-shadow` |
| `#d3e0d9` | 211, 224, 217 | 100.00% | `.site-footer → color` |
| `#d5e4da` | 213, 228, 218 | 100.00% | `.footer-bottom a → color` |
| `#d6e1e3` | 214, 225, 227 | 100.00% | `input:not([type=checkbox]):not([type=radio]),select,textarea → border` |
| `#d7e7dc` | 215, 231, 220 | 100.00% | `.site-footer .brand-icon → background` |
| `#d8e2e4` | 216, 226, 228 | 100.00% | `.secondary → border-color` |
| `#d9e7dc` | 217, 231, 220 | 100.00% | `.campus-visit → border` |
| `#d9e9e0` | 217, 233, 224 | 100.00% | `.welcome-banner → border` |
| `#dbece4` | 219, 236, 228 | 100.00% | `.timeline → border-left` |
| `#dce8e0` | 220, 232, 224 | 100.00% | `.auth-tiles>div → border` |
| `#dceee5` | 220, 238, 229 | 100.00% | `.avatar → background` |
| `#dfe7e1` | 223, 231, 225 | 100.00% | `.campus-facilities article → border`; `.campus-photo-grid figure → border`; `.campus-space-card → border` |
| `#dfe8e2` | 223, 232, 226 | 100.00% | `.campus-location-tag → border-top`; `.campus-spaces → border-top`; `.home-features → border-top` |
| `#dfe9e1` | 223, 233, 225 | 100.00% | `.campus-photo-grid .campus-photo-portrait img → background` |
| `#dfece3` | 223, 236, 227 | 100.00% | `.campus-facilities .file-icon → background` |
| `#e0e8e2` | 224, 232, 226 | 100.00% | `.home-features .panel → border-color` |
| `#e0eae4` | 224, 234, 228 | 100.00% | `.campus-slide figcaption p → color` |
| `#e1ece5` | 225, 236, 229 | 100.00% | `.site-footer h2 → color` |
| `#e1f1e9` | 225, 241, 233 | 100.00% | `.badge → background` |
| `#e2e8e2` | 226, 232, 226 | 100.00% | `.campus-identity img → border` |
| `#e2e9e4` | 226, 233, 228 | 100.00% | `.site-header → border-bottom` |
| `#e3eee7` | 227, 238, 231 | 100.00% | `.campus-slide figcaption>span → color` |
| `#e5ebee` | 229, 235, 238 | 100.00% | `:root → --line` |
| `#e5eee7` | 229, 238, 231 | 100.00% | `.carousel-dots button:hover → background` |
| `#e5eeea` | 229, 238, 234 | 100.00% | `.tag → border` |
| `#e5efe7` | 229, 239, 231 | 100.00% | `.campus-marker → box-shadow` |
| `#e5f0e9` | 229, 240, 233 | 100.00% | `.auth-tiles>div → background` |
| `#e6edf1` | 230, 237, 241 | 100.00% | `[data-theme=dark] → --ink` |
| `#e6f0e8` | 230, 240, 232 | 100.00% | `.campus-visit → background` |
| `#e7af49` | 231, 175, 73 | 100.00% | `button:focus-visible,a:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible → outline` |
| `#e7f2ec` | 231, 242, 236 | 100.00% | `.welcome-banner → background` |
| `#e7f4ec` | 231, 244, 236 | 100.00% | `.resolved → background` |
| `#e8f4eb` | 232, 244, 235 | 100.00% | `.alert → background` |
| `#e8f4ef` | 232, 244, 239 | 100.00% | `:root → --pale` |
| `#e9b55c` | 233, 181, 92 | 100.00% | `.art-circle → color` |
| `#eaf0ff` | 234, 240, 255 | 100.00% | `.in_progress → background` |
| `#edf3ee` | 237, 243, 238 | 100.00% | `.campus-facilities article → background` |
| `#edf3ef` | 237, 243, 239 | 100.00% | `progress → background`; `progress::-webkit-progress-bar → background` |
| `#eef5f1` | 238, 245, 241 | 100.00% | `.file-icon → background` |
| `#efd5ce` | 239, 213, 206 | 100.00% | `.alert.error → border-color` |
| `#f0f3f4` | 240, 243, 244 | 100.00% | `.announcement-preview → border-top`; `.list-row → border-top`; `td → border-bottom` |
| `#f0f5f3` | 240, 245, 243 | 100.00% | `.tag → background` |
| `#f0f7f3` | 240, 247, 243 | 100.00% | `.answer-box → background` |
| `#f0f8f3` | 240, 248, 243 | 100.00% | `.notification.unread → background` |
| `#f4d48d` | 244, 212, 141 | 100.00% | `[data-theme=dark] .status.pending → color` |
| `#f4f6f6` | 244, 246, 246 | 100.00% | `code → background` |
| `#f5f7fa` | 245, 247, 250 | 100.00% | `:root → --bg` |
| `#f7f9f7` | 247, 249, 247 | 100.00% | `.public-site → background` |
| `#fafcfb` | 250, 252, 251 | 100.00% | `.status-grid>div → background` |
| `#ffc2ba` | 255, 194, 186 | 100.00% | `[data-theme=dark] :is(.alert.error, .errorlist) → color` |
| `#fff` | 255, 255, 255 | 100.00% | `.campus-cover → background`; `.campus-cover → border`; `.campus-identity img → background`; `.campus-photo-grid figure → background`; `.campus-slide figcaption → color`; `.campus-space-card → background`; `.carousel-arrow:hover → border-color`; `.home-features .panel → background`; `.light → background`; `.light → border-color`; `.role-switch a[aria-current=page] → color`; `.site-footer .brand → color`; `.site-footer a:hover → color`; `.skip-link → color`; `:root → --white`; `[data-theme=dark] :is(button, .button):not(.secondary):not(.theme-toggle) → color`; `input:not([type=checkbox]):not([type=radio]),select,textarea → background` |
| `#fff0ed` | 255, 240, 237 | 100.00% | `.errorlist → background` |
| `#fff1ed` | 255, 241, 237 | 100.00% | `.alert.error → background` |
| `#fff3dc` | 255, 243, 220 | 100.00% | `.pending → background` |
| `#fff5e6` | 255, 245, 230 | 100.00% | `.list-row:nth-child(3n) .file-icon → background` |
| `#ffffff20` | 255, 255, 255 | 12.55% | `.footer-bottom → border-top` |
| `#ffffff80` | 255, 255, 255 | 50.20% | `.carousel-arrow → border` |
| `#ffffffc9` | 255, 255, 255 | 78.82% | `.topbar → background` |
| `#fffffff2` | 255, 255, 255 | 94.90% | `.carousel-arrow → background` |
| `#fffffff5` | 255, 255, 255 | 96.08% | `.site-header → background` |
| `transparent` | 0, 0, 0 | 0.00% | `.campus-slide figcaption → background`; `.carousel-dots button → background` |
| `white` | 255, 255, 255 | 100.00% | `.art-small → color`; `.art-square → background`; `.brand-icon → color`; `.panel → background`; `.sidebar → background`; `.stat-card → background`; `.timeline article:before → border`; `button,.button → color`; `button:hover,.button:hover → color` |
