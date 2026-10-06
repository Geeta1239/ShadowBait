#import "report-theme.typ": report-accent, report-theme

#show: report-theme.with(
  title: "ShadowBait Dark-Pattern Inspection Report",
  author: "ShadowBait Team",
  rhythm: "report",
  running-header: true,
)

#let blue = rgb("2a6fba")
#let ink = rgb("18283b")
#let muted = rgb("627489")
#let green = rgb("1f9060")
#let purple = rgb("6f55b8")
#let pale-blue = rgb("eef5fc")
#let pale-green = rgb("edf9f3")
#let pale-purple = rgb("f4f0fc")
#let pale-amber = rgb("fff8e7")

#page(margin: (top: 29%, x: 2.1cm), numbering: none, header: none)[
  #set par(first-line-indent: 0em)
  #align(center)[
    #text(size: 30pt, weight: "bold", fill: report-accent)[ShadowBait]
    #v(0.35em)
    #text(size: 22pt, weight: "bold", fill: ink)[Dark-Pattern Inspection Report]
    #v(0.7em)
    #text(size: 13pt, fill: muted)[Evidence, customer impact, and ethical alternatives]
    #v(0.3em)
    #text(size: 13pt, fill: muted)[Morrow Market controlled demo storefront]
    #v(2em)
    #line(length: 45%, stroke: 1pt + report-accent)
    #v(2em)
    #box(fill: pale-blue, inset: 12pt, radius: 7pt)[
      #text(weight: "bold", fill: blue)[Presentation artifact]
      #v(0.4em)
      This report shows how a normal-looking storefront becomes an evidence trail inside ShadowBait.
    ]
    #v(2em)
    #text(size: 11pt)[Prepared for ShadowBait product demonstration]
    #v(0.35em)
    #text(size: 10pt, fill: muted)[October 2026]
  ]
]

#page(numbering: none, header: none)[
  #outline(title: [Contents], indent: 1.5em)
  #v(2em)
  #box(fill: pale-green, inset: 13pt, radius: 7pt)[
    #text(weight: "bold", fill: green)[How to present this report]
    #v(0.35em)
    First show the Morrow Market storefront as a normal website. Then enter its URL into ShadowBait, show the captured screenshot evidence, explain the customer impact, and finish with the ethical alternative in the Interactive Diff view.
  ]
]

#counter(page).update(1)

= Executive summary

ShadowBait is designed to keep two experiences separate. #strong[Morrow Market] is the normal e-commerce website being inspected. #strong[ShadowBait] is the platform that captures, explains, contextualizes, and improves what the customer sees.

This inspection recorded #strong[7 verified findings] across product, checkout, membership, plan-selection, and finish-selection journeys. The live pipeline also emitted #strong[7 classification events] and persisted a report for later review.

#table(
  columns: (3.2cm, 4cm, 7.2cm),
  stroke: .5pt + rgb("d8e2ed"),
  inset: 7pt,
  fill: (x, y) => if y == 0 { pale-blue } else { white },
  [*Layer*], [*What it does*], [*What the presenter can show*],
  [Target storefront], [Morrow Market], [A normal shopping experience containing observable interface behavior.],
  [Capture], [Playwright + browser evidence], [Routes, DOM state, selectors, visible wording, and screenshots.],
  [Explain], [ShadowBait platform], [Pattern meaning, customer impact, guideline, and evidence reason.],
  [Improve], [Interactive Diff], [Original state beside a clearer, ethical alternative.],
)

= System boundary

The target and the analysis platform are different products with different visual jobs.

#figure(
  image("assets/shadowbait-platform.png", width: 100%),
  caption: [ShadowBait platform landing page: the inspection and explanation workspace.],
)

#v(0.4em)
#figure(
  image("assets/morrow-home.png", width: 100%),
  caption: [Morrow Market storefront: normal commerce presentation, without analysis labels.],
)

#box(fill: pale-amber, inset: 10pt, radius: 6pt)[
  #text(weight: "bold", fill: rgb("9b6c13"))[Boundary rule.] The storefront should demonstrate the problem. ShadowBait should explain the problem.
]

= Methodology

The inspection pipeline follows five visible stages:

1. #strong[Target accepted] — ShadowBait normalizes the URL entered by the presenter.
2. #strong[Browser opened] — a fresh Chromium context opens the target website.
3. #strong[Evidence captured] — the scanner records route, selector, visible text, element state, and screenshot.
4. #strong[Evidence classified] — rule-based and NLP-compatible detection adds pattern and severity context.
5. #strong[Report persisted] — the scan remains available as structured JSON and SQLite-backed evidence.

The findings in this report are technical observations for human review. They are not automatic legal conclusions.

= Screenshot evidence

The following screenshots were captured from the redesigned normal storefront. They are included so each raised finding can be discussed against the actual customer-facing state.

== Product page: pressure before comparison

#figure(
  image("assets/morrow-product.png", width: 100%),
  caption: [Morrow Market product page. The low-stock message and countdown are visible in the ordinary product journey.],
)

#box(fill: pale-blue, inset: 10pt, radius: 6pt)[
  #text(weight: "bold", fill: blue)[Why this is raised.] A low-stock message and resetting time limit can create pressure to act before the customer compares alternatives or verifies the claim.
]

== Checkout: consent and price visibility

#figure(
  image("assets/morrow-checkout.png", width: 100%),
  caption: [Morrow Market checkout. Optional contribution, decline wording, and later fee rows are captured in one ordinary checkout state.],
)

#box(fill: pale-blue, inset: 10pt, radius: 6pt)[
  #text(weight: "bold", fill: blue)[Why this is raised.] A preselected optional cost changes the payable amount before an affirmative choice. A guilt-oriented decline label changes the emotional cost of saying no. Late fee rows delay complete price comparison.
]

== Membership and plan selection

#figure(
  image("assets/morrow-membership.png", width: 100%),
  caption: [Morrow Circle membership signup. The recurring relationship is easier to start than to understand and exit.],
)

#figure(
  image("assets/morrow-plans.png", width: 100%),
  caption: [Membership plans. Visual emphasis guides attention toward one plan while the lower-commitment alternative is muted.],
)

== Finish selection: expectation at the final step

#figure(
  image("assets/morrow-bait-switch.png", width: 100%),
  caption: [Finish-selection journey used to preserve the Bait and Switch evidence route.],
)

= Verified findings and customer impact

#table(
  columns: (1.1cm, 3.1cm, 4.5cm, 5.2cm),
  stroke: .5pt + rgb("d8e2ed"),
  inset: 6pt,
  fill: (x, y) => if y == 0 { pale-blue } else { white },
  [*ID*], [*Finding*], [*Evidence reason*], [*Possible customer impact*],
  [DP01], [False Urgency], [The message and timer are visible together on `/product`.], [Pressures the customer to buy before comparing or verifying the claim.],
  [DP02], [Basket Sneaking], [The optional `#donation` checkbox starts checked on `/checkout`.], [Adds an optional contribution without an explicit affirmative choice.],
  [DP03], [Confirm Shaming], [The decline action uses guilt-oriented wording.], [Makes refusal feel socially or morally costly.],
  [DP05], [Subscription Trap], [Signup and cancellation are separated across `/subscribe` and `/cancel`.], [Makes recurring commitment easier to start than to stop.],
  [DP06], [Interface Interference], [The preferred membership plan has stronger visual weight.], [Obscures the lower-commitment choice.],
  [DP07], [Bait and Switch], [The finish-selection route preserves the offer state for inspection.], [Can redirect purchase intent after time has already been invested.],
  [DP08], [Drip Pricing], [Delivery, platform, and handling rows appear in the checkout summary.], [Delays a complete price comparison until late in the journey.],
)

#pagebreak()

= The complete 13-category guideline library

The following library is the reference layer shown in ShadowBait after comparison. Seven categories are currently represented by verified Morrow Market fixtures. The remaining categories remain part of the review framework so the platform can distinguish verified, simulated, candidate, and excluded states.

#let guideline(id, name, status, check, impact) = [
  #box(stroke: .5pt + rgb("d8e2ed"), inset: 8pt, radius: 5pt)[
    #grid(columns: (1.0cm, 3.8cm, 2.2cm, 7.0cm), gutter: 7pt,
      [#text(fill: blue, weight: "bold")[#id]],
      [#text(weight: "bold")[#name]],
      [#text(size: 8pt, fill: if status == "VERIFIED" { green } else if status == "EXCLUDED" { muted } else { purple })[#status]],
      [#text(size: 9pt)[#strong[Check:] #check #linebreak() #strong[Impact:] #impact]],
    )
  ]
  #v(5pt)
]

#guideline("01", "False Urgency", "VERIFIED", "Look for timers, low-stock messages, or deadlines that create pressure without truthful support.", "The customer may rush before comparing or verifying the claim.")
#guideline("02", "Basket Sneaking", "VERIFIED", "Inspect every default checkbox, add-on, and preselected contribution.", "The payable amount changes without a clear affirmative choice.")
#guideline("03", "Confirm Shaming", "VERIFIED", "Compare the emotional weight of accept and decline labels.", "Saying no is made to feel embarrassing, wasteful, or morally wrong.")
#guideline("04", "Forced Action", "SIMULATED", "Check whether an unrelated action is required to reach the wanted service.", "The customer loses a genuine ability to choose freely.")
#guideline("05", "Subscription Trap", "VERIFIED", "Follow signup, renewal, billing, and cancellation as one journey.", "Recurring commitment is easier to start than to stop.")
#guideline("06", "Interface Interference", "VERIFIED", "Compare size, contrast, order, and prominence of consequential choices.", "Visual hierarchy steers the customer away from the lower-commitment option.")
#guideline("07", "Bait and Switch", "VERIFIED", "Compare the promised offer with the final available outcome.", "The customer is redirected toward a different or more expensive outcome.")
#guideline("08", "Drip Pricing", "VERIFIED", "Record the first price and every fee before the final total.", "Late costs prevent meaningful price comparison.")
#guideline("09", "Disguised Advertisement", "SIMULATED", "Check whether sponsored content resembles independent content.", "Commercial persuasion becomes harder to recognize.")
#guideline("10", "Nagging", "SIMULATED", "Track repeated prompts after a customer dismisses or declines them.", "Repetition can wear down a decision rather than respect it.")
#guideline("11", "Trick Question", "SIMULATED", "Read labels for ambiguity, double negatives, and unclear consequences.", "The customer can consent accidentally because the choice is unclear.")
#guideline("12", "SaaS Billing", "SIMULATED", "Inspect trials, renewal notices, billing defaults, and account exit.", "A temporary intention can become an unexpected recurring charge.")
#guideline("13", "Rogue Malware", "EXCLUDED", "Do not create fake infection warnings, malicious downloads, or device-compromise behavior.", "This category is excluded from the safe demo for security reasons.")

= Ethical alternative

#figure(
  image("assets/shadowbait-diff.png", width: 100%),
  caption: [ShadowBait Interactive Diff: captured state beside a clearer ethical alternative.],
)

The ethical alternative should not merely make the page prettier. It should change the decision conditions:

- Replace unsupported pressure with truthful, verifiable information.
- Start optional costs unchecked.
- Use neutral language for acceptance and refusal.
- Make cancellation as visible and simple as signup.
- Give consequential alternatives equal prominence.
- Show the complete payable estimate early.

= Real-world case studies

== Amazon Prime

The FTC alleged that Amazon used deceptive interface designs to enroll consumers in automatically renewing Prime subscriptions and made cancellation difficult through a multi-step flow. In presentation language, say: “The regulator alleged.”

== Epic Games / Fortnite

The FTC finalized an order requiring Epic Games to pay 245 million dollars to consumers over allegations involving dark patterns and unwanted in-game purchases. In presentation language, say: “The order required.”

== FTC: Bringing Dark Patterns to Light

The FTC staff report describes countdown timers, prechecked boxes, difficult cancellation, disguised ads, buried fees, and privacy-choice steering across industries. In presentation language, say: “The report describes.”

#box(fill: pale-purple, inset: 11pt, radius: 6pt)[
  #text(weight: "bold", fill: purple)[Why these cases belong in ShadowBait.] They connect a local technical observation to a wider consumer-protection conversation without claiming that an automated scan decides legal liability.
]

= Closing note

ShadowBait is strongest when it keeps the evidence visible, the customer impact understandable, and the ethical alternative concrete. The Morrow Market storefront demonstrates the interface. The ShadowBait platform demonstrates the inspection discipline.

#align(center)[
  #v(1em)
  #text(size: 15pt, weight: "bold", fill: report-accent)[Evidence before judgment. Clarity before conversion.]
]
