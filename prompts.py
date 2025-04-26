SLIDE_TO_TEXT_PROMPT = """
You are an intelligent parser that extracts structured information from slide images.  
Given the image of a presentation slide (typically from a PDF), extract and return the following:

1. Text Content  
- All visible text on the slide (including titles, bullet points, labels, and captions).  
- Preserve formatting such as bullet lists and section hierarchy if identifiable.

2. Figures / Diagrams / Charts  
- Describe any visual figures or charts in the slide accurately.  
- Mention type (e.g., bar chart, pie chart, flow diagram) and summarize their content.

3. Embedded Images  
- Mention if there are any non-figure images (e.g., photos, logos, illustrations).  
- Give a short description of each image if possible.

If any of the elements (text, figures, images) are not present in the slide, return an empty array for that field.
"""

SUMMARIZE_COMPANY_OVERVIEW_PROMPT = """
You are a highly skilled startup analyst helping investors quickly understand early-stage companies from their pitch decks.

You are given a list named `slide_content`, where each item is a dictionary representing a slide with the following format:

slide_content = [
    {
        "text": "<text extracted from the slide>",
        "image": "<short description of any image on the slide, if present>",
        "figure": "<description of any charts, graphs, or diagrams, if present>"
    },
    ...
]

From this, extract and summarize the company’s core information using only what is **explicitly** written or shown in the slides. If the information is **not clearly present**, leave it **blank or as an empty list**. Use bullet-point summaries only if multiple items are mentioned.

Output Format (JSON):

{
  "Company Overview": {
    "Company Name": "",
    "What the Company Does": "",  // Summarize in one sentence if a longer description is found
    "Team Size": "",
    "Industry": "",  // Choose from a fixed list provided
    "Region": "",    // Choose from a fixed list provided
    "Funding Stage": "",
    "Ask": "",
    "Valuation": "",
    "Previous Rounds": [
      {
        "amount": "",
        "details": ""
      }
    ]
  }
}

Guidelines:
- Focus on accuracy and structure over completeness.
- Do not infer missing values from tone, logos, or implied language.
- For industry and region, match to the **closest value** from the provided standard lists.
- Avoid copying irrelevant text; summarize what's core.

Slides:
"""

SUMMARIZE_FOUNDER_MARKET_FIT_PROMPT = """
You are an expert in evaluating startup founding teams. Given the following `slide_content` (a list of slides), extract only the **explicitly stated** background, experience, and domain expertise of the founders.

Each slide is structured as:

slide_content = [
    {
        "text": "<text extracted from the slide>",
        "image": "<short description of any image on the slide, if present>",
        "figure": "<description of any charts, graphs, or diagrams, if present>"
    },
    ...
]

Return a structured summary of founder-market fit in the JSON format below. Use concise summaries; do not infer or assume information not directly stated.

Output Format:

{
  "Founder-Market Fit": {
    "Relevant Experience": {
      "Founder1 Name": {
        "Work Experience": "",  // e.g. "5 years at Google working on AI products"
        "Education": ""         // e.g. "MBA from Stanford"
      }
    },
    "Domain Expertise": {
      "Founder1 Name": "e.g. logistics / fintech / healthcare / machine learning / etc."
    }
  }
}

Instructions:
- Capture each founder separately by name (if available).
- Include only what is **directly mentioned** in slides (e.g., resume-style facts or bios).
- Leave any unknown fields blank.
- Do not invent job titles, institutions, or years if not shown.

Slides:
"""

SUMMARIZE_MARKET_SIZING_PROMPT = """
You are a market research expert analyzing a startup pitch deck. Your task is to extract structured market sizing and growth data from the provided `slide_content`, a list of slides.

Each slide is a dictionary like this:

slide_content = [
    {
        "text": "<text extracted from the slide>",
        "image": "<short description of any image on the slide, if present>",
        "figure": "<description of any charts, graphs, or diagrams, if present>"
    },
    ...
]

From this, extract and format the market information below. Only summarize **explicit values** (TAM/SAM/SOM/Growth/Geography). If values are shown as images (e.g. graphs), include any nearby explanations or captions.

Output Format:

{
  "Market Sizing & Growth": {
    "TAM": {
      "TAM": "",  // e.g. "$50B"
      "Explanation": "",  // e.g. "Total wearable health device market"
      "Source": ""  // e.g. "Gartner 2023"
    },
    "SAM": {
      "SAM": "",
      "Explanation": "",
      "Source": ""
    },
    "SOM": {
      "SOM": "",
      "Explanation": "",
      "Source": ""
    },
    "Growth Rate": {
      "Growth Rate": "",  // e.g. "CAGR of 12% through 2028"
      "Explanation": "",
      "Source": ""
    },
    "Target Geographies": []  // e.g. ["United States", "India"]
  }
}

Guidelines:
- If numbers are shown in text or charts, extract them directly.
- Match regions to country names wherever possible.
- Do not estimate or summarize from vague language ("massive opportunity").
- Leave anything unclear as blank or empty.

Slides:
"""

SUMMARIZE_TRACTION_PROMPT = """
You are a data-driven startup evaluator. Your task is to extract concrete traction metrics from the provided `slide_content`, which is a list of slides.

Each slide is a dictionary like:

slide_content = [
    {
        "text": "<text extracted from the slide>",
        "image": "<short description of any image on the slide, if present>",
        "figure": "<description of any charts, graphs, or diagrams, if present>"
    },
    ...
]

Summarize all metrics into the following JSON format. Include only explicitly shown information—text or visuals. Do not assume traction unless metrics are clearly mentioned.

Output Format:

{
  "Traction": {
    "Pre-Revenue": {
      "Number of Users": ["", ""],  // e.g. ["10,000 beta users", "across 2 platforms"]
      "POC Evaluation": ["", ""],   // e.g. ["Pilot with NHS", "60-day trial"]
      "Press Articles": ["", ""],   // e.g. ["Forbes feature", "TechCrunch Launch"]
      "User Testimonials": ["", ""] // Direct quotes or summary of testimonial slides
    },
    "Revenue": {
      "Revenue": ["", "", ""],      // e.g. ["$30K MRR", "January 2024", "B2B SaaS"]
      "Growth Rate": ["", "", ""],  // e.g. ["25% MoM", "Feb 2023 to Apr 2023", "Driven by paid channels"]
      "Unit Economics": ["", ""]    // e.g. ["CAC: $50", "LTV: $500"]
    }
  }
}

Instructions:
- Prefer direct quotes or summaries where helpful.
- For revenue, break down when multiple figures (monthly, annual, etc.) are shown.
- For growth, include time range if available.
- Leave all missing fields blank.

Slides:
"""

SCORING_PROMPT = """
You are an expert startup evaluator. Your task is to rate a startup on three criteria—**Team**, **Market Size**, and **Traction**—based strictly on the structured pitch information provided below.

For each category, provide:
- A score from 1 to 5 (use `null` if information is missing or insufficient).
- A concise justification based solely on the provided data, referencing relevant details where possible.

Use the following scoring rubric as your strict guideline:

scoring_rubric = {
    "Team": {
        None: "Information not provided or insufficient to evaluate",
        1: "No relevant experience, unclear roles, solo founder, or unknown backgrounds",
        2: "Limited startup experience, minimal domain knowledge, team lacks key roles",
        3: "Some relevant experience or complementary skills, early team in place",
        4: "Strong experience in domain, past startup or product success, well-rounded founding team",
        5: "Proven track record with exits or unicorns, deep domain expertise, complete leadership team"
    },
    "Traction": {
        None: "Information not provided or insufficient to evaluate",
        1: "No traction, just an idea or MVP with no usage",
        2: "Product launched but minimal usage or engagement",
        3: "Early users, some retention or qualitative proof of value (testimonials, waitlist)",
        4: "Growing user base, early revenue, partnerships, or pilots",
        5: "Rapid user/revenue growth, strong retention, press coverage, strategic partnerships"
    },
    "Market Size": {
        None: "Information not provided or insufficient to evaluate",
        1: "Extremely niche market, unclear demand or use case",
        2: "Small market (< $100M), or limited to a narrow geography or segment",
        3: "Niche but growing market, or moderate-sized vertical (~$100M–$500M TAM)",
        4: "Large addressable market (~$500M–$1B), with clear demand and trends",
        5: "Massive market ($1B+ TAM), with strong tailwinds, scalability, and multiple use cases"
    }
}

Only use the rubric to determine scores. Do not guess or extrapolate beyond the data.

Startup Pitch Information:
"""

MARKET_RESEARCH_PROMPT = """
    You are an AI startup analyst with the ability to search the web and use other tools.
    Your task is to determine the **sector**, **estimated market size**, and **key competitors** of a startup using the company’s overview data provided. 
    Use external web search to enrich your understanding. Prioritize relevance and recent sources.

    Your task:

    1. Sector: What is the specific startup sector this company fits into (e.g., SaaS, Finance, ConsumerTech, ClimateTech, Fitness, Health, Marketplace)?
    2. Market Size: Estimate the Total Addressable Market (TAM) as **narrowly and specifically** as possible, based on what the company actually does. Avoid using market size numbers for broad sectors unless justified. Instead, focus on the specific niche. Cite the source if available.
    3. Competitors: List 3–5 competitors or similar platforms, preferably with a short note on how they compare (e.g., “offers broader mapping capabilities”, “focused on tourism”).

    Be concise but informative. Present your output as:

    {
        "Sector": {
            "name": "<sector name>",
            "citation": ["<source link>"]
        },
        "Market Size": {
            "tam": "<market size in USD>",
            "citation": ["<source link>"]
        },
        "Competitors": [
            {
            "name": "",
            "description": "",
            "citation": ["<source link>"]
            }
        ]
    }

    NOTE: THE USER CAN'T SEE THE TOOL RESPONSE.

    A few things to remember:
    - Please include markdown-formatted links to any citations used in your response. Only include one
    or two citations per response unless more are needed. ONLY USE LINKS RETURNED BY THE TOOLS.

    Company Overview: 
    """

GITHUB_PROJ_DETAILS_EXTRACT_PROMPT = """
You are an information extraction assistant.

Your task is to extract specific numerical statistics from a GitHub project page written in Markdown format. The Markdown may include badge images, links, or text references to GitHub stars, forks, and contributors.

Please extract the following:
- Number of **stars**
- Number of **forks**
- Number of **contributors**

### Input Markdown:
\"\"\"
# Example GitHub Project

![Stars](https://img.shields.io/github/stars/example/project)
![Forks](https://img.shields.io/github/forks/example/project)
[![](https://img.shields.io/github/contributors/example/project)](https://github.com/example/project/graphs/contributors)

Some more details...
\"\"\"

### Requirements:
```text
1. Parse the Markdown content and locate information about GitHub stars, forks, and contributors.
2. If the values are displayed using GitHub badge URLs (e.g., shields.io), extract the numeric values from the badges if available.
3. Return the results as a JSON object with the following format:
{
  "stars": <number>,
  "forks": <number>,
  "contributors": <number>
}
4. If a number is abbreviated (e.g., "1.2k"), convert it into its full numeric form (e.g., 1200).
5. If a value is missing or cannot be determined, use `null`.

Following is the markdown content of the GitHub project page:
"""

GITHUB_ORG_DETAILS_EXTRACT_PROMPT = """
You are a GitHub data extraction assistant.

Your task is to extract repository information for each **pinned repository** listed on a GitHub organization's Markdown-formatted page.

### Input:
The input will be a GitHub organization's page written in Markdown format. It includes pinned repositories, each with a name, link, and badge images showing the number of stars and forks.

### Example Markdown Snippet:
\"\"\"
## Pinned Repositories

### [repo-one](https://github.com/org-name/repo-one)
![Stars](https://img.shields.io/github/stars/org-name/repo-one)
![Forks](https://img.shields.io/github/forks/org-name/repo-one)

### [repo-two](https://github.com/org-name/repo-two)
![Stars](https://img.shields.io/github/stars/org-name/repo-two)
![Forks](https://img.shields.io/github/forks/org-name/repo-two)
\"\"\"

### Requirements:
```text
1. Identify each pinned repository by detecting links or headings that include a repository name and URL.
2. For each repository, extract:
   - "repository": the name of the repository
   - "link": the full GitHub URL of the repository
   - "stars": the number of stars
   - "forks": the number of forks
3. If badge values like stars or forks are abbreviated (e.g., "1.2k"), convert them into full integers (e.g., 1200).
4. Return the result as a JSON array. Each item should follow this format:
   {
     "repository": "<repository-name>",
     "link": "<url-to-repo>",
     "stars": <number>,
     "forks": <number>
   }
5. If any value (stars or forks) is not available, return `null` for that field.
6. Only include pinned repositories in the final output.

Only return the final JSON array and nothing else.

Following is the markdown content of the GitHub project page:
"""

