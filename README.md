# OTVis

OTVis is a collection of small utilities for visualizing the TBox structure of OWL ontologies. The Python scripts extract axioms and annotations into JSON files and the HTML pages show them as interactive graphs.

## Directory layout
- `Ontology/` – input OWL files
- `Axiom_per_entity/` – axioms per class/property (`*_axiom.json`)
- `Ontology_description/` – class and property descriptions (`*_description.json`)
- `Graph/` – graph data used by the viewer (`*_graph.json`)
- `Graph_embedding/` – graph data with BERT embeddings and UMAP coordinates (`*_graph_embed.json`)
- `ontology_list.json` – list of ontology names shown in the viewer
- Main scripts: `ontology_processing.py`, `description_extraction.py`, `convert_hierarchy.py`, `get_embedding.py`
- Viewer pages: `index.html`, `index_embedding.html`

## Script overview
### ontology_processing.py
Collects axioms for each class and property and writes them to `Axiom_per_entity`.

### description_extraction.py
Extracts annotations such as `rdfs:comment` and `oboInOwl:hasDefinition` to the `Ontology_description` folder.

### convert_hierarchy.py
Reads the class hierarchy, merges axioms and descriptions, and outputs a graph JSON in `Graph`.

### get_embedding.py
Embeds node labels with BERT, reduces them to 2D using UMAP, and saves the result in `Graph_embedding`. The data is used by `index_embedding.html`.

## Usage
1. Place your OWL files in `Ontology/` and add their names to `ontology_list.json`.
2. Install the required packages for Python 3.
   ```bash
   pip install rdflib sentence-transformers umap-learn
   ```
3. Run the scripts in order to generate the JSON data.
   ```bash
   python ontology_processing.py
   python description_extraction.py
   python convert_hierarchy.py
   python get_embedding.py
   ```
4. Start a local web server and open `index.html` or `index_embedding.html` in your browser.
   ```bash
   python -m http.server 8000
   ```
   Then visit `http://localhost:8000/`.
