# PRJGENUI Workforce — live SERP and competitor research

Date: 10 Sep 2026. Run through the desktop browser (google.co.uk, gl=uk, hl=en-GB).

## Query 1: "painting and decorating recruitment agency uk"

**AI Overview named four agencies:**

| Agency | How Google describes them | Site |
|---|---|---|
| Alliance Workforce | "The only specialist Painting and Decorating agency in the UK. Members of SDF and NAS." | allianceworkforce.co.uk |
| Phoenix Gray Recruitment | "Vetted CSCS-carded painters and decorators nationwide, urgent requests filled within 24 hours, £16–£24/hr" | phoenixgrayrec.com |
| Blade Recruitment | "Temporary and permanent painters and decorators for commercial and hospitality, London" | bladerecruitment.co.uk |
| Supreme Recruitment | "Housing associations and construction firms, £15–£20/hr" | supremerecruitment.co.uk |

**AI Overview "What to expect" bullets (what Google thinks buyers care about):**
- Pay rates £15–£24+/hr depending on experience, location, project type
- Certifications: valid CSCS card, basic PPE, checkable trade references or NVQ / City & Guilds
- Tools: own whites, brushes, basic hand tools

**Organic top 10:** Indeed (jobs), Blade Recruitment, Agency Central (directory), Pimlico Painters, Alliance Workforce, Aspect Maintenance, Phoenix Gray, MCE Staffing.

**Local pack (London):** City Site Solutions 4.3 (322 reviews), Nationwide Construction Recruitment 4.7 (25), GTS Labour Hire 4.7 (170). Review count is a ranking lever here.

**People also ask:**
1. Are painters and decorators in demand in the UK?
2. Is it worth using a recruitment agency to find a job?
3. What is the hourly rate for a painter and decorator in the UK?
4. What is the average salary for a painter and decorator in the UK?

**People also search for:** best painting and decorating recruitment agency uk · painting and decorating agencies near me · painting recruitment agency · painting agency work · interior painting and decorating recruitment agency uk

## Query 2: "painter and decorator labour agency surrey hampshire"

- AI Overview again points to Alliance Workforce (national) and Supreme Recruitment. Every other result is a decorating **contractor**, not an agency: Merritt Decorators (Havant), Marshels (Farnborough, 48 reviews, 40+ yrs), KJT Decorating (Basingstoke, "CSCS-certified teams"), Delux Decorating (Camberley), Top Coats (Camberley), FCD Contractors (Bordon, 53 reviews).
- Sponsored: Indeed, MyJobQuote, Getapainter, Laurence Interiors.
- Organic: Agency Central, Alliance Workforce, City Site Solutions (city-site.co.uk/painters-and-decorators, "over 20 years' experience").
- **Gap:** no specialist painting and decorating labour agency with a modern site is ranking for the Surrey / Hampshire area. The local pack is empty of agencies.

**People also ask:**
1. How much do painters charge for labour?
2. Is it worth using a recruitment agency to find a job?
3. What is the typical daily rate for a painter and decorator in the UK?
4. What's the average pay for a painter and decorator?

## Competitor design teardown

| Site | Stack / era | Palette | Fonts | Hero | CTAs | Words | Trust signals | Verdict |
|---|---|---|---|---|---|---|---|---|
| Alliance Workforce | WordPress 2017 theme, fixed left sidebar | Red #F04D43, grey #404041, black | Open Sans | Dark textured slideshow, white H1 50px | "Looking for contract staff?" / worker CTA | 387 | SDF, NAS, CHAS, SafeContractor, Constructionline, 4 city phone numbers, "8 Hour Guarantee" | Dated but the only specialist. Strong on trust badges and phone numbers. |
| Phoenix Gray | Tailwind / modern build | Slate #222E3A, blue #508EC8, white | Outfit (display 72px) + DM Sans | Dark navy over construction photo with gradient overlay, pill eyebrow badge, blue second line | Dual: "Submit a Vacancy" / "Find Jobs"; "For Employers" / "For Candidates" blocks | 1,983 | CSCS x15, Constructionline, Google reviews, DBS, "24-hour turnaround", Labour Planner tool, case studies, research, hiring guides | The benchmark. Modern, content-rich, dual audience. Generalist though. |
| Blade Recruitment | Older WP, 14-item nav | Grey #313131, dark red #8A0606 | Poppins | Carousel, no clear H1 | "Quick Apply", "Brief Us", "Hire Staff" | 795 | DBS, Google reviews | Cluttered. |
| MCE Staffing | Generic template | Purple #3F00D1, blue #2986FF | Segoe UI / system | 48px H1 "UK's Leading Staffing Agency" | "Book Staff", phone | 467 | REC | Thin, generic. |
| Supreme Recruitment | WP generalist | Teal #478287 | Merriweather + Montserrat | 36px caps H1 | Sector buttons | 530 | none detected | Generalist, off-target. |

### Patterns worth copying
1. **Dual audience split above the fold** (contractors vs workers). Phoenix Gray and Blade both do it; Alliance does it with two buttons.
2. **Real photography of trades on site** in the hero with a dark navy overlay (Phoenix Gray). Nobody in this SERP uses illustration.
3. **A named guarantee** ("8 Hour Guarantee", "24-hour turnaround"). Ours: replacement search starts within 60 minutes.
4. **Compliance words on the page**: CSCS appears 15 times on Phoenix Gray's homepage. Google's AI Overview leads with CSCS, PPE, references, own tools.
5. **Trust badge strip**: CHAS, SafeContractor, Constructionline, SDF, NAS, REC. PRJGENUI should show only what it genuinely holds; use placeholders labelled "membership in progress" until confirmed.
6. **Phone number visible in the header** on every competitor. Ours is missing.
7. **Content depth**: the modern winner has ~2,000 words with 12 H2s; the rest have under 800.

### Patterns to beat
- Nobody shows **proof of skill** or a **reliability score**. That is the product differentiator and should be the visual centrepiece.
- Nobody explains **what happens on a no-show**. Our 60-minute replacement process is the headline guarantee.
- Nobody targets **Surrey / Hampshire** as a specialist. Local pages and LocalBusiness schema with service area will own that gap.
- Nobody has an **FAQ answering the PAA questions** (hourly rate, day rate, demand, "is an agency worth it"). Eight FAQs in FAQPage schema answer exactly those.

## Screenshots and raw extracts
`serp-1.png`, `serp-1.json`, `serp-2.json`, `comp-alliance.*`, `comp-phoenix.*`, `comp-phoenix-home.*`, `comp-blade.*`, `comp-mce.*`, `comp-supreme.*` in this folder.
