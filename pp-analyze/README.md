# PoliAnalyzer

This is the directory for PoliAnalyzer. It analyzes a given Privacy Policy, and produces different structured representations. 

Three main steps are supported by PoliAnalyzer:

1. Use NLP pipeline to create structural representation of privacy practices in privacy policies, as a knowledge graph

2. Construct actionable formal policies based on the information, such as *app policy* for [perennial semantic Data Terms of Use](https://dl.acm.org/doi/10.1145/3589334.3645631)

3. Perform reasoning to check compliance of the constructed *app policy* against a user profile indicating user's preferences

## Set up and general usage

### Usage

1. Clone submodules
2. Install dependences with `poetry`
      - `sqlite-zstd` will be installed with the python dependency and work out of the box. But if things don't work well (esp. with database), you may need to verify it is working with your sqlite installation
3. To perform reasoning (Step 3), the [eye reasoner](https://github.com/eyereasoner/eye) is needed. Your `$PATH` should contain an executable `eye`
4. Copy `.env.example` to `.env`, and fill in relevant environmental variables (see also next section)
      1. Note: always have a valid API key for accessing the LLM. You can of course also use a local API endpoint compatible with OpenAI's chat completion API (e.g. using Ollama)
5. Fill in your model names for each task in `recognition/query_helper.py`
6. Run the notebook `pp_analyze.ipynb`
      - It contains explanations for the steps
      - If you want to proceed to Step 3, you'll need to choose the correct/desired user profile (persona) dirs

### Settings

Some environmental variables may need to be set up, by copying `.env.example` to `.env` and modify its contents. Most fields should be self-explanatory. We note some particular ones relevant for downstream tasks:

- Entity classification level
     - Change `PURPOSE_MAPPING_LEVEL` and `DATA_CATEGORY_MAPPING_LEVEL` in `pp_analyze/recognition/query_llm.py`
- Name for general categories (for data and purpose)
     - Change `S_DATA_CATEGORY_GENERAL` and `S_PURPOSE_CATEGORY_GENERAL` in `pp_analyze/recognition/query_llm.py`

## Information type

Currently, PolyAnalyzer identifies the following types of information:

- Data entity (category)
- Purpose entity (category)
- Data consumer
- Data usage practice
     - Data use
          - First-party data use
          - Third-party data use
          - Their differences are marginal -- depending on who "collects" data in the first instance
     - Third-party data sharing
          - The first-party (app) shares data with a third-party (e.g. service)
     - Data storage / retention
          - For how long the data is stored and for what reason/purpose
     - Data protection practice
          - What data protection measurements are taken for what threat

The data category and purpose category are based on the relevant categories in [DPV](https://w3c.github.io/dpv/2.0/dpv/), to maximize interoperability.

# 
