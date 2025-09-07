# **[Cableteque_BicyclePermutations](https://bicyclepermuts-cableteque.streamlit.app/#bicycle-generator)**

A small toolkit + Streamlit(https://bicyclepermuts-cableteque.streamlit.app/#bicycle-generator) app that reads a compact Excel specification of bicycle modifications (an `ID` sheet plus `GENERAL` and designator sheets), generates every possible bicycle permutation, and exports the result as JSON (and CSV). This repository contains:

* `bicycle_generator.py` — core Python module (function `generate_bicycles_from_excel(xlsx_path) -> str`).
* `streamlit_bicycle_generator.py` — Streamlit app for uploading `.xlsx`, previewing, filtering and downloading results.
* `requirements.txt` — environment dependencies.
* Example Excel template: `Bicycle_example.xlsx` (downloadable from the app sidebar).
## **[Tutorial Video](https://drive.google.com/file/d/1SjSIk8ec_WKvUuggQ60oak9ITbCtlasC/view?usp=sharing)**

## Key features

* Reads an Excel workbook with the following structure:

  * `ID` sheet — each column is a *designator*; rows are possible values. All combinations are created by taking one value from each column.
  * `GENERAL` sheet — common fields applied to every bike.
  * Other sheets — each sheet maps a designator value (first column) to field values (other columns).
* Generates the Cartesian product of all designator values and merges per-designator fields into each bike object.
* Produces a pretty JSON string (list of objects), and also offers a downloadable CSV.
* Streamlit UI:

  * Upload `.xlsx` and run generation in the browser.
  * ID separator option (e.g. `-`) to make IDs readable.
  * Conflict resolution option (designator order vs sheet priority).
  * Accessible theme presets + advanced color pickers with contrast warnings.
  * Quick-find filters and per-ID inspection.

---

## Why this is useful

* Warehouse / inventory managers can describe many product permutations compactly in Excel and generate a complete, machine-readable catalog.
* Engineers and front-end teams can use the generated JSON/CSV for search, filters, product pages or backend import.
* The Streamlit app enables non-technical users to upload and generate outputs without touching code.

---

## Quickstart — run locally

1. Create and activate a virtual environment (optional, recommended):

   ```bash
   python -m venv venv
   # Unix / macOS
   source venv/bin/activate
   # Windows (PowerShell)
   .\\venv\\Scripts\\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:

   ```bash
   streamlit run streamlit_bicycle_generator.py
   ```

   Visit `http://localhost:8501` in your browser.

4. Upload your Excel file (structure explained above) and use the UI to preview and download `bicycles.json` or `bicycles.csv`.

---

## Command-line usage

If you only want the core generator (no UI), use `bicycle_generator.py` functions from your own script or run the included self-test by executing:

```bash
python bicycle_generator.py
```

Or call the core function from another Python program:

```python
from bicycle_generator import generate_bicycles_from_excel
json_str = generate_bicycles_from_excel("/absolute/path/to/Bicycle.xlsx")
print(json_str)
```

---
🙏 Acknowledgements

I would like to extend my heartfelt gratitude to the entire team at Cableteque for this wonderful opportunity.

Your trust and encouragement have been truly motivating, and working on this project has been both an inspiring and enriching experience.

This project allowed me to sharpen my technical expertise while also reflecting on how I can personally grow in alignment with your values of innovation, collaboration, and positive impact.

I am eager to work with Cableteque, learn from the team’s wealth of experience, and contribute meaningfully towards your mission of building a more sustainable and innovative future.
## Design & implementation notes

* The generator builds the Cartesian product using `itertools.product`.
* General fields are applied first, and then per-designator sheets are applied in a deterministic order. The Streamlit UI lets you choose which precedence strategy to use.
* The Streamlit app includes accessibility checks (contrast ratio) and a set of curated theme presets to avoid poor color combinations.
* If the number of permutations grows very large, the app will still work but may become slow or heavy on memory — consider reducing the number of values per designator or adding server-side limits for deployment.

---

## A note of thanks

Special thanks to **Yuval** for support and helpful feedback during development — your insights were very valuable.

A huge thank-you to **Cableteque** for inspiration and for championing practical, industry-first software for cable and wire-harness professionals. Cableteque’s dedication to building software "by wire harness people for wire harness people" and its culture of innovation, inclusivity and practical engineering inspired parts of the UX and the product-first approach used here. Learn more about Cableteque at: [https://cableteque.com/about](https://cableteque.com/about)

---

## How I align with Cableteque's mission, values & vision

Cableteque champions deep domain knowledge, practical innovation, and building tools that genuinely help engineers and manufacturing teams work better. I strongly identify with these priorities, and my personal values and working style map closely to Cableteque’s PIA framework and broader mission:

* **Pioneering (P)** — I embrace innovation and forward-thinking approaches. I enjoy exploring new ideas, automating repetitive tasks, and pushing boundaries to make workflows simpler and more powerful.

* **Insightful (I)** — I am committed to continuous learning. I actively seek new perspectives, study domain-specific practices (such as product configuration and inventory workflows), and apply lessons learned to improve both technical solutions and user experiences.

* **Agile (A)** — I work iteratively and adapt to change. I favor practical, incremental improvements, rapid prototyping, and close feedback loops so that solutions remain simple, useful, and easy to adopt.

Beyond the PIA framework, I also align with Cableteque’s broader cultural values:

* **Inclusivity & collaboration:** I enjoy working with diverse teams, listening to domain experts, and incorporating their feedback into the product. I believe great solutions come from shared expertise.

* **Sustainability & positive impact:** I aim to build tools that reduce wasteful manual work and enable teams to focus on higher-value tasks — a small sustainability win through smarter processes.

* **Trust & shared success:** I prioritize clear communication, reliable tooling, and thoughtful design so teams can depend on the software and succeed together.

In short, my mindset—centered on practical innovation, continuous learning, and collaborative delivery—fits naturally with Cableteque’s mission and values. I’m excited by opportunities to contribute in environments that prize domain expertise, user-first tools, and iterative improvement.

---

## Our values & culture

Our company thrives on innovation, inclusivity, and collaboration. We value individuality, sustainability, and making a positive impact—building trust and shared success every step of the way.

### P — Pioneering

We are innovative and forward-thinking, always striving to improve and push boundaries.

### I — Insightful

We continuously learn and grow, seeking new perspectives and knowledge to improve ourselves and the organization.

### A — Agile

We adapt to change and are flexible in our approach, always looking for ways to improve and innovate based on simplicity.

## Credits

* Developed by: **Ashutosh Shukla** (project author)
* Thanks to: **Yuval**, **Cableteque** (inspiration and domain focus).

---

## License

(Choose a license and add here — e.g., MIT)

---

## Contact

* LinkedIn: **[https://www.linkedin.com/in/your-linkedin-profile](https://www.linkedin.com/in/your-linkedin-profile)**

> Replace the placeholder above with your actual LinkedIn URL.
