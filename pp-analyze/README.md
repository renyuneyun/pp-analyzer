# PP Analyze

This is the main project for PoliAnalyzer.

It analyzes a given Privacy Policy, and produces a structural representation of data practices for further usage.

It identifies the following types of information:

- Data entity (category)
- Purpose entity (category)
- Data consumer
- Data storage
    - Data storage location
    - Data storage duration
- Security protection methods
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


## Settings

- Entity classification level
    - Change `PURPOSE_MAPPING_LEVEL` and `DATA_CATEGORY_MAPPING_LEVEL` in `pp_analyze/recognition/query_llm.py`
- Name for general categories (for data and purpose)
    - Change `S_DATA_CATEGORY_GENERAL` and `S_PURPOSE_CATEGORY_GENERAL` in `pp_analyze/recognition/query_llm.py`

    
## Usage

1. Clone submodules
2. Install dependences with `poetry`
    - `sqlite-zstd` will be installed with the python dependency and work out of the box. But if things don't work well (esp. with database), you may need to verify it is working with your sqlite installation.
3. To perform reasoning, the [eye reasoner](https://github.com/eyereasoner/eye) is needed.
4. Copy `.env.example` to `.env`, and fill in relevant environmental variables 
5. Fill in your model names for each task in `recognition/query_helper.py`
6. Run the notebook `pp_analyze.ipynb`
    - You may need to choose the correct/desired user profile (persona) dirs
