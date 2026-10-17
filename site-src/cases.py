# -*- coding: utf-8 -*-
"""Case files for the Verification Desk.

origin  : 'live' = published on immigranthallofhonor.org, read 2 October 2026
          'ours' = a claim this exhibit makes
verdict : confirmed | unsupported | contradicted
evidence: (tag, title, body, ref, url)
          tag is one of
            RECORD      an institution's own record of its own act
            QUOTATION   words reproduced exactly from a named source
            PARAPHRASE  a source's finding, restated
            INFERENCE   our reasoning from the items above, not a source
            UNRESOLVED  sources conflict and we are not resolving it
            NOT-READ    cited but NOT opened by anyone on this project
"""

CASES = [
{
 "id":"einstein","name":"Albert Einstein","arrived":"1933","from":"Ulm, Germany",
 "note":"The case file where the museum turns out to be right and the famous source wrong. "
        "Read the second and third claims together.",
 "teaches":"the page&rsquo;s &ldquo;Eidgen&ouml;ssische Polytechnische Schule (1911)&rdquo; is "
           "contradicted &mdash; ETH Zurich holds the leaving certificate of 1900. But the "
           "page&rsquo;s &ldquo;Ph.D &hellip; (1906)&rdquo; is <b>right</b>, and an earlier "
           "version of this exhibit was wrong to correct it: the University of Zurich conferred "
           "the doctorate in January 1906.",
 "moral":"A citation is not a check &mdash; including ours.",
 "claims":[
  {"id":"e1","origin":"live","verdict":"contradicted",
   "text":"&ldquo;Albert Einstein immigrated to Princeton, N.J., in 1932.&rdquo; The same year appears twice on the page.",
   "where":"Albert Einstein inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("PARAPHRASE","The Institute for Advanced Study, on its own opening day",
      "The Institute opened on 2 October 1933. Its account of that day records that Einstein "
      "and Hermann Weyl &ldquo;were in Europe and would arrive later in the month.&rdquo; He "
      "was therefore not in Princeton in 1932, and took up the appointment in October 1933.",
      "Institute for Advanced Study, &ldquo;Opening Day, October 2, 1933&rdquo;",
      "https://www.ias.edu/ideas/2008/batterson-opening-day"),
     ("INFERENCE","Where a 1932 date can come from",
      "Einstein visited the United States before 1933, including a period at Caltech. A visit "
      "is not an immigration. This is our reading of how the two get confused; it is not a "
      "claim made by any source.",
      "Our inference, labelled as such", ""),
   ],
   "reasoning":"1933. The error appears twice on one page, which means it exists in two fields "
     "and was not simply mistyped once.",
   "lesson":"An error in two places is a copying error. Fixing one instance leaves the other."},

  {"id":"e2","origin":"live","verdict":"contradicted",
   "text":"&ldquo;Eidgen&ouml;ssische Polytechnische Schule (1911)&rdquo;",
   "where":"Education field, Albert Einstein inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("RECORD","ETH Zurich holds the document and dates it",
      "ETH Zurich&rsquo;s library states that &ldquo;In July 1900 he completed his studies at "
      "the Polytechnic Institute with a diploma,&rdquo; and offers the leaving certificate "
      "itself for download, labelled <em>Abgangszeugnis, 28.07.1900</em>.",
      "ETH Zurich Library, &ldquo;Einstein&rsquo;s Studies at the Polytechnic Institute in Zurich (1896&ndash;1900)&rdquo;",
      "https://library.ethz.ch/en/collections-and-archives/platforms/einstein-online/studium-am-polytechnikum-in-zuerich-1896-1900.html"),
     ("QUOTATION","What the Nobel Prize biography says instead",
      "&ldquo;In 1901, the year he gained his diploma&hellip;&rdquo; &mdash; 1901 is the year "
      "Einstein was granted Swiss citizenship. The awarding institution and the Nobel "
      "biography do not agree, and we have not resolved which is the slip.",
      "NobelPrize.org, &ldquo;Albert Einstein &ndash; Biographical&rdquo;",
      "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"),
     ("INFERENCE","Either way, not 1911",
      "In 1911 Einstein was a full professor at the German University in Prague. Whichever of "
      "1900 or 1901 is right, 1911 is a decade out.",
      "Our inference from the two records above", ""),
   ],
   "reasoning":"The diploma is 1900 by the record of the school that issued it. This is the "
     "genuine error on the page, and it is a decade wide.",
   "lesson":"When two reputable sources disagree, prefer the one that performed the act. "
     "ETH issued the certificate; the Nobel Foundation did not."},

  {"id":"e3","origin":"live","verdict":"confirmed",
   "text":"&ldquo;Ph.D in Physics from University of Zurich (1906)&rdquo;",
   "where":"Education field, Albert Einstein inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("QUOTATION","The University of Zurich, on its own conferral",
      "&ldquo;The 26-year-old Einstein completed his 17-page dissertation, entitled "
      "&lsquo;A New Determination of Molecular Dimensions&rsquo;, on 30 April 1905&rdquo; and "
      "&ldquo;submitted it to the University of Zurich almost two months later&hellip; His "
      "doctorate and corresponding certificate were conferred in January 1906.&rdquo;",
      "University of Zurich, UZH News, &ldquo;Doctor Einstein&rdquo; (2022)",
      "https://www.news.uzh.ch/en/articles/news/2022/Doctor-Einstein.html"),
     ("PARAPHRASE","Three dates, not one",
      "Dissertation completed 30 April 1905. Approved unanimously by the Philosophy II "
      "faculty 27 July 1905. &ldquo;The degree was formally awarded January 15, 1906.&rdquo;",
      "American Institute of Physics, Center for History of Physics, Einstein chronology 1905",
      "https://history.aip.org/exhibits/einstein/chron-1905.htm"),
     ("QUOTATION","What the Nobel Prize biography says instead",
      "&ldquo;In 1905 he obtained his doctor&rsquo;s degree.&rdquo;",
      "NobelPrize.org, &ldquo;Albert Einstein &ndash; Biographical&rdquo;",
      "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/"),
   ],
   "reasoning":"<b>The museum is right and this exhibit was wrong.</b> An earlier version of "
     "this page marked 1906 as an error and gave 1905 as the correction, on the authority of "
     "the Nobel biography. The University of Zurich conferred the degree on 15 January 1906. "
     "There are three separable events here &mdash; the dissertation completed in April 1905, "
     "the faculty approval in July 1905, and the conferral in January 1906 &mdash; and "
     "flattening them is what produces the disagreement.",
   "lesson":"Check the correction as hard as the claim. This one was wrong, and it was wrong "
     "because a famous source was trusted over the institution that did the thing."},

  {"id":"e4","origin":"live","verdict":"confirmed",
   "text":"Awarded the Nobel Prize in Physics.",
   "where":"Albert Einstein inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("RECORD","The prize record",
      "The Nobel Prize in Physics 1921 was awarded to Albert Einstein, with the citation "
      "naming his discovery of the law of the photoelectric effect &mdash; not relativity. "
      "The 1921 prize was reserved and announced in 1922.",
      "NobelPrize.org, The Nobel Prize in Physics 1921",
      "https://www.nobelprize.org/prizes/physics/1921/summary/"),
   ],
   "reasoning":"Correct. The citation itself is the interesting part and most people have it wrong.",
   "lesson":"Confirming a claim is often where the good detail is, not where the work stops."},
 ]},

{
 "id":"hope","name":"Bob Hope","arrived":"1908","from":"Eltham, London, England",
 "note":"Four claims. The first is the one worth the time.",
 "teaches":"&ldquo;Won an Academy Award 5 times.&rdquo; The Academy&rsquo;s own lists confirm "
           "three of the honours; two more are widely reported and we did not confirm them. "
           "None of the confirmed three is a competitive Oscar. Our own follow-on claim, that "
           "he was never nominated competitively, is withdrawn as unsupported.",
 "moral":"A number can be correct and the claim around it still false.",
 "claims":[
  {"id":"h1","origin":"live","verdict":"contradicted",
   "text":"&ldquo;Won an Academy Award 5 times (1941, 1945, 1953, 1960, 1966)&rdquo;",
   "where":"Bob Hope inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("RECORD","What the Academy's own lists show",
      "The Academy lists Bob Hope among recipients of the <em>Honorary Award</em> for 1952 "
      "(25th) and 1965 (38th), and of the <em>Jean Hersholt Humanitarian Award</em> for 1959 "
      "(32nd). These are the three we confirmed at the Academy itself.",
      "Academy of Motion Picture Arts and Sciences &mdash; Honorary Award and Jean Hersholt Humanitarian Award recipient lists",
      "https://www.oscars.org/governors/honorary"),
     ("QUOTATION","The 1965 citation, in the Academy's words",
      "&ldquo;To Bob Hope for unique and distinguished service to our industry and the "
      "Academy&rdquo; &mdash; presented by Jack Lemmon, 18 April 1966.",
      "Academy Awards Acceptance Speech Database, entry 038-28",
      "https://aaspeechesdb.oscars.org/link/038-28/"),
     ("UNRESOLVED","Two further honours we could not confirm at the Academy",
      "A special silver plaque (commonly dated 1939/12th) and a Life Membership in the "
      "Academy (commonly dated 1944/17th) are widely reported. The Academy Awards Database "
      "renders entirely in the browser and could not be queried here, and the relevant "
      "ceremony pages returned incomplete lists. <b>We did not confirm these two.</b>",
      "Attempted: awardsdatabase.oscars.org and oscars.org ceremony pages", ""),
     ("INFERENCE","Why the page's five years do not line up with the Academy's",
      "The Academy names an honour for the award year; the ceremony happens the following "
      "spring. Four of the page's five years sit exactly one year after a confirmed or "
      "reported honour (1952&rarr;1953, 1959&rarr;1960, 1965&rarr;1966, and 1944&rarr;1945). "
      "<b>The fifth does not:</b> 1941 is two years after the commonly reported 1939 special "
      "award. So the ceremony-year explanation accounts for most of the gap and not all of "
      "it, and we are not going to pretend otherwise.",
      "Our inference, and its limit, from the Academy's own numbering", ""),
   ],
   "reasoning":"An Honorary Award, a humanitarian award and a life membership are given "
     "outside the competitive categories; they are not won against nominees. Whatever the "
     "final count, the page describes a kind of winning that did not happen.",
   "lesson":"Check the noun before the number. &ldquo;Won an Academy Award&rdquo; and "
     "&ldquo;received an Academy honour&rdquo; are different claims."},

  {"id":"h2","origin":"ours","verdict":"unsupported",
   "text":"&ldquo;He was never nominated in a competitive Academy Award category.&rdquo; "
          "&mdash; a claim this exhibit itself made in an earlier version.",
   "where":"Our own earlier text, withdrawn here.",
   "evidence":[
     ("INFERENCE","Why we withdrew it",
      "No competitive nomination for Bob Hope appears in the Academy honour lists we "
      "consulted. But those lists are lists of <em>honours</em>; absence from them is not "
      "evidence of absence from the nomination record.",
      "Our reasoning", ""),
     ("UNRESOLVED","What would actually establish it",
      "A null result from a search of the Academy Awards Database for &ldquo;Hope, Bob&rdquo; "
      "returning only honorary and special entries, recorded with the date the search was "
      "run. That database is client-side rendered and we could not query it from here.",
      "Method stated so somebody can finish it", ""),
   ],
   "reasoning":"We believe the claim is true. We cannot show you that it is. Those are "
     "different states and an exhibit that conflates them has no business correcting anyone.",
   "lesson":"Proving a negative needs a named register and a search date, not an absence of "
     "contrary memories."},

  {"id":"h3","origin":"live","verdict":"contradicted",
   "text":"The structured field reads &ldquo;Ellis Island, 1908&rdquo; and &ldquo;Citizenship "
          "Date: 1920&rdquo;, while the prose on the same page reads &ldquo;Bob Hope "
          "immigrated to Cleveland, Ohio, in 1920.&rdquo;",
   "where":"Bob Hope inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("RECORD","Arrival and citizenship",
      "The family relocated to Cleveland in March 1908. Hope became a United States citizen "
      "in December 1920 &mdash; derivatively, when his father was naturalised, which is the "
      "ordinary route for a child.",
      "Encyclopedia of Cleveland History, Case Western Reserve University, &ldquo;Hope, Leslie Townes (Bob)&rdquo;",
      "https://case.edu/ech/articles/h/hope-leslie-townes-bob"),
     ("INFERENCE","The page has both numbers and uses them for the same event",
      "1908 is the arrival. 1920 is the citizenship, and the page&rsquo;s own structured "
      "field says so. The prose then uses 1920 as the immigration year.",
      "Our reading of the two statements", ""),
   ],
   "reasoning":"The page holds the right answer in one field and contradicts it one paragraph "
     "later. Both statements cannot describe an arrival.",
   "lesson":"When a page disagrees with itself, the error is proven without leaving the page."},

  {"id":"h4","origin":"live","verdict":"confirmed",
   "text":"Born in Eltham, England, in 1903.",
   "where":"Bob Hope inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("RECORD","Birth",
      "&ldquo;HOPE, LESLIE TOWNES (BOB)&rdquo;, born 29 May 1903 in Eltham, England, a "
      "London suburb.",
      "Encyclopedia of Cleveland History, Case Western Reserve University",
      "https://case.edu/ech/articles/h/hope-leslie-townes-bob"),
   ],
   "reasoning":"Correct and specific enough to check.",
   "lesson":"Most of what the site says is fine. A verifier who finds fault everywhere is as "
     "useless as one who finds none."},
 ]},

{
 "id":"muir","name":"John Muir","arrived":"1849","from":"Dunbar, Scotland",
 "note":"Five claims. By the fourth you should stop checking facts and start auditing the process.",
 "claims":[
  {"id":"m1","origin":"live","verdict":"contradicted",
   "text":"&ldquo;Helped establish &hellip; Grand Canyon (1908) National Park.&rdquo;",
   "where":"John Muir inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("RECORD","Monument, 1908",
      "Grand Canyon was proclaimed a National <em>Monument</em> on 11 January 1908 under the "
      "Antiquities Act, by Proclamation No. 794.",
      "National Park Service, Ronald F. Lee, &ldquo;The Proclamation of National Monuments "
      "Under the Antiquities Act, 1906&ndash;1970&rdquo;, Table II",
      "https://www.nps.gov/articles/lee-story-proclamation.htm"),
     ("RECORD","Park, 1919",
      "&ldquo;Designated as Grand Canyon National Park by an act of Congress on February 26&rdquo; "
      "(40 Stat. 1175), 1919.",
      "National Park Service, Grand Canyon National Park Profile 2025, park chronology",
      "https://www.nps.gov/grca/learn/management/upload/2025-Park-Profile-508.pdf"),
     ("RECORD","Muir died in 1914",
      "The Sierra Club gives his dates as 1838&ndash;1914. We deliberately do not assert a "
      "day: no institutional source we opened states one. The park was established on "
      "26 February 1919, so the gap is at least four years and two months on any reading of "
      "his death date.",
      "Sierra Club, John Muir Exhibit",
      "https://www.sierraclub.org/john-muir-exhibit"),
   ],
   "reasoning":"Two errors stacked. A monument is not a park, and the park postdates his "
     "death by more than four years on any reading.",
   "lesson":"Check the date against the person&rsquo;s lifespan. It is the cheapest test there is."},

  {"id":"m2","origin":"live","verdict":"contradicted",
   "text":"&ldquo;Yosemite (1898).&rdquo;",
   "where":"John Muir inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("QUOTATION","The National Park Service",
      "&ldquo;Established as a national park on October 1, 1890&hellip;&rdquo;",
      "National Park Service, NPS Geodiversity Atlas &mdash; Yosemite National Park",
      "https://www.nps.gov/articles/nps-geodiversity-atlas-yosemite-national-park.htm"),
     ("INFERENCE","The right answer is already on the page",
      "The same sentence dates Sequoia correctly to 1890. The correct year is printed one "
      "clause from the wrong one.",
      "Our reading of the page", ""),
   ],
   "reasoning":"1 October 1890.",
   "lesson":"Errors cluster. Where you find one, read the whole sentence again slowly."},

  {"id":"m3","origin":"live","verdict":"contradicted",
   "text":"&ldquo;The John Muir Trust was formed in England&hellip;&rdquo;",
   "where":"John Muir inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("RECORD","The Trust's own registration details",
      "Scotland. Founded 1983. Scottish Charity No. SC002061, Company No. SC081620, "
      "registered office Tower House, Station Road, Pitlochry, PH16 5AN.",
      "John Muir Trust, About (organisational details)",
      "https://www.johnmuirtrust.org/about"),
     ("UNRESOLVED","Not independently cross-checked",
      "These are the Trust&rsquo;s own statements about itself. The Scottish Charity "
      "Regulator&rsquo;s register renders in the browser and we could not query it here.",
      "Attempted: OSCR register", ""),
   ],
   "reasoning":"Scotland. On a page about a Scot, this is the error a Scottish visitor "
     "notices first.",
   "lesson":"Nationality errors land hardest on the people the page is about."},

  {"id":"m4","origin":"live","verdict":"unsupported",
   "text":"&ldquo;Information sources: Britannica, Biography, Grammys.&rdquo;",
   "where":"Foot of the John Muir inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("RECORD","The same line, on a different person's page",
      "The identical string appears at the foot of the Celia Cruz page. Cruz was a "
      "Grammy-winning singer. Muir was a naturalist who died in 1914, decades before the "
      "Grammy Awards existed. Both pages were read on 2 October 2026.",
      "immigranthallofhonor.org, John Muir and Celia Cruz inductee pages", ""),
     ("INFERENCE","What this means for the rest of the page",
      "A source list that names an award body with no connection to the subject is not "
      "describing where the information came from. We do not know how this happened and we "
      "do not speculate.",
      "Our reasoning", ""),
   ],
   "reasoning":"The source list is not functioning as a source list. That matters more than "
     "any single wrong date, because it is the thing a reader would use to check the rest.",
   "lesson":"When the sourcing fails, stop verifying individual facts and audit the process."},

  {"id":"m5","origin":"live","verdict":"confirmed",
   "text":"Born in Dunbar, Scotland, in 1838; co-founded the Sierra Club.",
   "where":"John Muir inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("QUOTATION","The Sierra Club, on its own founding",
      "&ldquo;The Sierra Club was organized in 1892&hellip;&rdquo; and &ldquo;John Muir was "
      "the Sierra Club&rsquo;s first President and held that office for twenty-two years "
      "&ndash; until his death.&rdquo;",
      "Sierra Club, &ldquo;John Muir, President of the Sierra Club&rdquo;",
      "https://www.sierraclub.org/john-muir-exhibit/john-muir-president-sierra-club"),
   ],
   "reasoning":"Correct. The spine of the page is sound; the decoration on it is not.",
   "lesson":"A page can be mostly right and still untrustworthy. Trust tracks the worst claim."},
 ]},

{
 "id":"cruz","name":"Celia Cruz","arrived":"1961","from":"Havana, Cuba",
 "note":"A bill mistaken for an award, and two numbers nobody can source.",
 "claims":[
  {"id":"c1","origin":"live","verdict":"contradicted",
   "text":"&ldquo;Awarded the Congressional Gold Medal (2005).&rdquo;",
   "where":"Celia Cruz inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("RECORD","H.R. 149, 109th Congress &mdash; the full legislative history",
      "The <em>Congressional Tribute to Celia Cruz Act</em> was introduced on 4 January 2005 "
      "by Rep. Menendez and referred to the Committee on Financial Services the same day. On "
      "23 February 2005 it was referred to the Subcommittee on Domestic and International "
      "Monetary Policy, Trade and Technology. That is the latest action. It did not become law.",
      "govinfo.gov, official bill status record BILLSTATUS-109hr149.xml",
      "https://www.govinfo.gov/bulkdata/BILLSTATUS/109/hr/BILLSTATUS-109hr149.xml"),
     ("RECORD","She appears nowhere in the list of recipients",
      "The Congressional Research Service&rsquo;s chronological list of every Congressional "
      "Gold Medal recipient contains no entry for Cruz. The edition consulted runs to 2016.",
      "Congressional Research Service RL30076, &ldquo;Congressional Gold Medals, 1776&ndash;2016&rdquo;",
      "https://www.everycrsreport.com/reports/RL30076.html"),
     ("RECORD","The honours she did receive",
      "National Medal of Arts, 1994. A US Mint American Women Quarter in 2024. Both are "
      "frequently conflated with a Congressional Gold Medal; neither is one.",
      "National Endowment for the Arts, National Medal of Arts &mdash; Celia Cruz",
      "https://www.arts.gov/honors/medals/celia-cruz"),
   ],
   "reasoning":"A bill introduced is not an award conferred. The medal requires an Act of "
     "Congress, and this bill died in subcommittee.",
   "lesson":"Introduced, reported, passed, enacted and awarded are five different things."},

  {"id":"c2","origin":"live","verdict":"unsupported",
   "text":"&ldquo;She recorded more than 70 albums&rdquo; in the prose, and &ldquo;Produced 70 "
          "songs&rdquo; in the achievements list. <em>(The &ldquo;23 gold records&rdquo; in the "
          "same list is corroborated by her estate and is not part of this claim.)</em>",
   "where":"Both statements, Celia Cruz inductee page, immigranthallofhonor.org. Read 2 October 2026.",
   "evidence":[
     ("QUOTATION","The Smithsonian",
      "&ldquo;Cruz recorded more than 80 albums and songs&rdquo; &mdash; note that the "
      "Smithsonian&rsquo;s own phrasing combines the two categories rather than giving a "
      "clean album count.",
      "Smithsonian National Museum of American History, &ldquo;Celia Cruz, Queen of Salsa&rdquo;",
      "https://americanhistory.si.edu/explore/stories/celia-cruz-queen-of-salsa"),
     ("PARAPHRASE","Her estate",
      "&ldquo;Celia recorded over 80 albums and 1,000 songs, earned 23 Gold Records, and won "
      "five Grammy Awards.&rdquo;",
      "celiacruz.com, Biography", "https://celiacruz.com/biography"),
     ("INFERENCE","Why this is 'not supported' rather than 'contradicted'",
      "We cannot show that 70 is wrong, because no source we opened gives a definitive count "
      "and the categories differ between them. We can show that 70 is not what the two best "
      "sources say, and that the page uses the same number for two different things.",
      "Our reasoning", ""),
   ],
   "reasoning":"Albums are not songs, and 70 is not the figure either the Smithsonian or her "
     "estate gives. An earlier version of this exhibit called this &ldquo;contradicted&rdquo; "
     "and endorsed the album figure. That overstated what we could show.",
   "lesson":"&ldquo;Not supported&rdquo; is a real verdict, and usually the honest one."},

  {"id":"c3","origin":"ours","verdict":"confirmed",
   "text":"She left Cuba in 1960 and arrived in the United States on 20 November 1961.",
   "where":"This exhibit&rsquo;s own claim.",
   "evidence":[
     ("QUOTATION","The Smithsonian",
      "&ldquo;In 1960, Cruz went on tour to Mexico with the orchestra. She never returned to "
      "Cuba,&rdquo; and she arrived in the United States &ldquo;on Nov. 20, 1961.&rdquo;",
      "Smithsonian National Museum of American History, &ldquo;Celia Cruz, Queen of Salsa&rdquo;",
      "https://americanhistory.si.edu/explore/stories/celia-cruz-queen-of-salsa"),
     ("UNRESOLVED","What we removed",
      "An earlier version said she was naturalised in 1961. No source we opened supports a "
      "naturalisation year, including her estate&rsquo;s own biography, which says only that "
      "she moved to the United States. The claim is withdrawn rather than softened.",
      "Recorded as a withdrawal", ""),
   ],
   "reasoning":"Leaving and arriving are two different dates for one journey &mdash; which is "
     "exactly the distinction the Bob Hope page loses.",
   "lesson":"One journey, several dates, and a naturalisation that is none of them."},
 ]},

{
 "id":"albright","name":"Madeleine Albright","arrived":"1948","from":"Prague, Czechoslovakia",
 "note":"The case file where the honest answer is that we have not read the document.",
 "claims":[
  {"id":"a1","origin":"ours","verdict":"unsupported",
   "text":"&ldquo;She arrived in the United States on 11 November 1948&rdquo; &mdash; and the "
          "State Department press statement said so.",
   "where":"This exhibit&rsquo;s own claim, in an earlier version.",
   "evidence":[
     ("NOT-READ","The primary document, which nobody on this project has opened",
      "US Department of State, Office of the Spokesman, press statement, "
      "archived at <code>1997-2001.state.gov/albright/981110_oath.html</code>. This host is "
      "refused by our network on every route, including web archives. <b>An earlier version of "
      "this exhibit quoted this document at length without reading it. Every such quotation has "
      "now been withdrawn across the whole package.</b>",
      "Attempted repeatedly; blocked", ""),
     ("RECORD","The statement's date, resolved to 10 November",
      "The filename is <code>981110</code> &mdash; 10 November. The indexed page title reads "
      "&ldquo;11/10/98&rdquo;, and the Associated Press carried a 10 November dateline for the "
      "ceremony. The 1998 ceremony date resolves to 10 November; it is widely miscited as 11 "
      "November. That still does not establish the 1948 <em>arrival</em> day, which no source "
      "we opened records.",
      "Filename, indexed title and the AP dateline, against the common miscitation", ""),
     ("PARAPHRASE","What a contemporaneous wire report says",
      "Associated Press, carried by CBS News and timestamped 10 November 1998, reports the "
      "ceremony happening &ldquo;Tuesday&rdquo;. 10 November 1998 was a Tuesday. The AP "
      "report gives <b>97</b> new citizens from 31 countries &mdash; not the 86 this exhibit "
      "previously printed.",
      "CBS News / Associated Press, &ldquo;Albright Renews Her Oath&rdquo;, 10 November 1998",
      "https://www.cbsnews.com/news/albright-renews-her-oath/"),
   ],
   "reasoning":"The arrival date may well be 11 November 1948. We are not able to show you "
     "that, because the document we were citing for it is one we have never opened. An "
     "exhibit built on the principle that a citation is not a check cannot itself cite "
     "something it has not read.",
   "lesson":"The failure mode this exhibit exists to teach is the one it committed. Read the "
     "document or say that you have not."},

  {"id":"a2","origin":"ours","verdict":"confirmed",
   "text":"Her papers went to the Library of Congress, and they are not available online.",
   "where":"This exhibit&rsquo;s own claim.",
   "evidence":[
     ("QUOTATION","The finding aid's acquisition note",
      "&ldquo;The papers of Madeleine Korbel Albright, U.S. secretary of state, diplomat, and "
      "educator, were given to the Library of Congress by Albright in <b>2014 and 2016</b>.&rdquo; "
      "81,000 items; 232 containers plus 2 classified and 3 oversize; 94.5 linear feet.",
      "Library of Congress, Manuscript Division, <em>Madeleine Korbel Albright Papers</em>, finding aid ms018034",
      "https://tile.loc.gov/storage-services/service/gdc/gdcfindingaidpdfs/ms018034/ms018034.pdf"),
     ("QUOTATION","Access, in the Library's words",
      "&ldquo;Restrictions apply governing the use, photoduplication, or publication of items "
      "in this collection&hellip; Access to digital content is available onsite only in the "
      "Manuscript Reading Room and requires advanced notice.&rdquo; Not digitised at item level.",
      "Same finding aid, restrictions note",
      "https://tile.loc.gov/storage-services/service/gdc/gdcfindingaidpdfs/ms018034/ms018034.pdf"),
     ("INFERENCE","Where 'acquired 2015' comes from",
      "The Library announced the donation in a press release dated 16 September 2015. 2015 is "
      "the announcement year; 2014 and 2016 are the gift years of record. An earlier version "
      "of our own research note said 2015.",
      "Our correction of our own earlier text", ""),
   ],
   "reasoning":"The collection exists, it is large, and none of it is online. That is why this "
     "profile is built from published federal records rather than from her papers.",
   "lesson":"An announcement date is not an acquisition date. Use the finding aid&rsquo;s own words."},

  {"id":"a3","origin":"ours","verdict":"confirmed",
   "text":"She was the first woman to serve as United States Secretary of State.",
   "where":"This exhibit&rsquo;s own claim.",
   "evidence":[
     ("RECORD","The Office of the Historian",
      "Sworn in 23 January 1997 as the 64th Secretary of State, the first woman to hold the "
      "office. The same entry renders her birth name &ldquo;Marie Jean &lsquo;Madlenka&rsquo; "
      "Korbel&rdquo;, born 15 May 1937 in Prague.",
      "US Department of State, Office of the Historian, Madeleine Korbel Albright",
      "https://history.state.gov/departmenthistory/people/albright-madeleine-korbel"),
     ("UNRESOLVED","The name has two renderings and we verified only one",
      "The Czech form <em>Marie Jana Korbelov&aacute;</em> is in common use. We did not verify "
      "it against any Czech institutional source, so it appears here as a variant, not as a "
      "correction of the State Department.",
      "Recorded as unverified", ""),
   ],
   "reasoning":"Correct, and precisely datable. Note the boundary: first woman Secretary of "
     "State, not first woman in the line of succession &mdash; as a naturalised citizen she "
     "was not eligible for the presidency.",
   "lesson":"A superlative is only true inside a stated category."},

  {"id":"a4","origin":"ours","verdict":"confirmed",
   "text":"She learned in 1997 that her family was Jewish and that relatives had died in the Holocaust.",
   "where":"This exhibit&rsquo;s own claim.",
   "evidence":[
     ("QUOTATION","The newspaper that told her",
      "The Washington Post records that she &ldquo;was raised as a Roman Catholic and was "
      "never told by her parents or anyone else that family members had perished in the "
      "Holocaust,&rdquo; and that she was &ldquo;presented with research undertaken for this "
      "article about her family history.&rdquo; Its separate finding: &ldquo;all three of her "
      "surviving grandparents died in the concentration camps.&rdquo;",
      "The Washington Post, &ldquo;Madeleine Albright didn&rsquo;t know she was Jewish until "
      "The Post told her&rdquo;, 23 March 2022",
      "https://www.washingtonpost.com/history/2022/03/23/madeleine-albright-jewish/"),
     ("QUOTATION","Her own figure, in her own words",
      "&ldquo;I had no idea that my family heritage was Jewish or that more than twenty of my "
      "relatives had died in the Holocaust.&rdquo; The figure of more than twenty is hers, not "
      "the newspaper&rsquo;s.",
      "Albright, quoted in a review of <em>Prague Winter</em>, <em>j. the Jewish News of "
      "Northern California</em>, 31 August 2012",
      "https://jweekly.com/2012/08/31/prague-winter-a-searing-account-of-hidden-jewish-family-history/"),
     ("UNRESOLVED","Her maternal grandmother &mdash; the hedge is in the source and stays there",
      "She &ldquo;was arrested in 1942 and shipped first to Theresienstadt and then to a "
      "destination in Poland, <b>perhaps Trawniki</b>, where she was murdered.&rdquo; The Post "
      "explains the uncertainty: the relevant Nazi records &ldquo;show that several different "
      "Anna Spieglovas died in the camps.&rdquo; A 1997 JTA wire report says flatly that her "
      "fate is unknown, and gives &ldquo;more than a dozen&rdquo; relatives rather than more "
      "than twenty. We print the divergence rather than choosing between them.",
      "<em>j. the Jewish News of Northern California</em>, 31 August 2012; JTA archive, 15 July 1997",
      "https://jweekly.com/2012/08/31/prague-winter-a-searing-account-of-hidden-jewish-family-history/"),
   ],
   "reasoning":"Confirmed in substance. The discipline is in what this does <em>not</em> say: "
     "the hedge is reproduced, the two different relative counts are both shown with their "
     "sources, and the reporter&rsquo;s name is omitted because we did not verify the byline.",
   "lesson":"Where the source hedges, you hedge. You do not resolve somebody else&rsquo;s "
     "uncertainty on their behalf, least of all about how a family died."},
 ]},
]
