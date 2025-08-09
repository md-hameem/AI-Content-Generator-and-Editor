# Streamlit AI Content Generator + Editor Agent

## Overview

The **Streamlit AI Content Generator + Editor** is a fully interactive, web-based tool designed to assist content creators, marketers, and developers in generating high-quality blog posts, articles, and marketing copy. Leveraging **OpenAI** (or **Ollama** for local inference) for content generation, this app provides features like:

- Automatic content generation based on user input (topic, keywords, audience, tone)
- AI-driven draft improvement for better readability and conciseness
- Built-in SEO checks to optimize content for search engines
- Markdown and PDF export capabilities for easy use in any platform
- Customizable themes and branding for personalization

The app runs locally and can be easily set up for your own use or customized further to meet specific needs.


## Features

### 1. **Content Generation**
- Generate outlines for articles and blog posts based on a given topic, audience, and tone.
- Write full drafts, with support for natural language generation and SEO optimization.
- Improve drafts by refining clarity, conciseness, and active voice.

### 2. **SEO Optimization**
- Built-in SEO checklist for title tags, headings, keyword density, and other key factors.
- Generate SEO-friendly meta titles, descriptions, and slugs based on the content.

### 3. **Export Options**
- Download the generated content in **Markdown** format for easy integration with static sites or CMS platforms.
- **Export to PDF** for polished, printable articles (requires installation of `wkhtmltopdf`).

### 4. **Local Inference (Optional)**
- Use **Ollama** to run inference locally, which offers full control and privacy over data processing.
- Alternatively, you can use **OpenAI API** for cloud-based generation.


## Installation

### 1. Clone the repository
```bash
git clone https://github.com/md-hameem/AI-Content-Generator-and-Editor.git
cd streamlit-content-generator
````

### 2. Set up a virtual environment

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file at the project root and add your **OpenAI API key** (or Ollama local configuration):

```
# For OpenAI API (optional, use if OpenAI is selected)
OPENAI_API_KEY=your-openai-api-key

# For Ollama (fully local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### 5. Run the app

```bash
streamlit run app/main.py
```

The app should now be accessible at `http://localhost:8501`.


## Features in Detail

### **Content Generation**

#### Outline Creation

* Generate detailed H2/H3 outlines for blog posts and articles.
* Integrate target keywords naturally within the outline.

#### Draft Creation

* Full articles generated using the provided outline.
* Supports custom tone and audience settings.

#### Draft Improvement

* Refine drafts by improving readability, clarity, and conciseness.
* Automatically make adjustments for better engagement and flow.

### **SEO Optimization**

* **Title & Meta Description**: Automatically generate SEO-optimized titles and descriptions based on the content.
* **Keyword Density**: Ensure proper keyword distribution for optimal SEO ranking.


## Export Options

1. **Markdown Export**: Download content in Markdown format for use in any blogging platform or static site.
2. **PDF Export**: (Requires `wkhtmltopdf`) Convert content to a polished, professional PDF ready for print.

### **To install `wkhtmltopdf` for PDF export**:

* Download and install from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html).
* Or, use a package manager:

  * **macOS**: `brew install wkhtmltopdf`
  * **Debian/Ubuntu**: `sudo apt install wkhtmltopdf`


## Customization

* **Branding**: Easily replace the default logo with your own image in the sidebar (set in `app/main.py`).
* **Styling**: Customize the app’s colors and layout through the `.streamlit/config.toml` file.
* **Provider Choice**: Choose between **OpenAI** for cloud-based AI generation or **Ollama** for fully local AI processing.


## Technologies Used

* **Streamlit**: Interactive web app framework.
* **OpenAI API**: Content generation using GPT models (optional).
* **Ollama**: Local inference engine (alternative to OpenAI).
* **Markdown**: Content formatting for easy export.
* **PDFKit & wkhtmltopdf**: PDF generation.


## Contributing

Contributions are welcome! If you have any improvements, fixes, or new features, feel free to fork the repo and open a pull request.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Author

**Mohammad Hamim**
[LinkedIn](https://www.linkedin.com/in/md-hameem/)


