# OTVis

OTVis는 OWL 온톨로지의 TBox 구조를 시각화하기 위한 도구 모음입니다. 파이썬 스크립트로 공리와 주석을 추출해 JSON으로 변환한 후, `index.html`에서 D3.js를 사용해 그래프로 표현합니다.

## 디렉터리 구조
- `Ontology/` – 입력 OWL 파일
- `Axiom_per_entity/` – 개별 클래스/프로퍼티의 공리 정보(`*_axiom.json`)
- `Ontology_description/` – 클래스와 프로퍼티 설명(`*_description.json`)
- `Graph/` – 시각화용 그래프 데이터(`*_graph.json`)
- `ontology_list.json` – 웹에서 선택할 수 있는 온톨로지 이름 목록
- 주요 스크립트: `ontology_processing.py`, `description_extraction.py`, `convert_hierarchy.py`

## 파이썬 스크립트

### ontology_processing.py
온톨로지에서 클래스 및 프로퍼티 공리를 수집하여 JSON으로 저장합니다.

```python
output = {"classes": class_axioms, "properties": prop_axioms}
with open(axioms_file, "w", encoding="utf-8") as af:
    json.dump(output, af, indent=2, ensure_ascii=False)
```

### description_extraction.py
`rdfs:comment`와 `oboInOwl:hasDefinition` 등을 추출해 설명 파일을 만듭니다.

```python
output = {
    "classes": class_ann_dict,
    "properties": prop_ann_dict
}
base = os.path.splitext(fname)[0]
out_fname = f"{base}_description.json"
out_path = os.path.join(OUTPUT_DIR, out_fname)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
```

### convert_hierarchy.py
클래스 계층을 읽어 그래프 JSON을 생성하며, 공리와 설명 정보를 병합합니다.

```python
axiom_path = os.path.join(AXIOM_DIR, f"{base_name}_axiom.json")
desc_path = os.path.join(DESC_DIR, f"{base_name}_description.json")
...
node_dict = {"id": node}
if node in class_axioms:
    node_dict["axioms"] = class_axioms[node]
if node in class_descriptions:
    node_dict["description"] = class_descriptions[node]
```

## 웹 뷰어
`index.html`은 D3.js로 인터랙티브 그래프를 표시합니다. 상단에서 온톨로지를 선택하고 특정 클래스로 포커스할 수 있습니다.

```html
<div id="controls">
  <label>Select ontology: </label>
  <select id="ontology-select"></select>
  <button onclick="loadOntology()">Load</button>
  <br /><br />
  <label>Focus class: </label>
  <input type="text" id="focus-id" placeholder="e.g., owl:Thing" />
  <button onclick="focusOnNode()">Focus</button>
</div>
```

온톨로지 목록을 읽어와 선택지를 채우고, `loadOntology()`에서 그래프 데이터를 불러옵니다.

```javascript
fetch("ontology_list.json")
  .then((res) => res.json())
  .then((list) => {
    const select = document.getElementById("ontology-select")
    list.forEach((name) => {
      const option = document.createElement("option")
      option.value = name
      option.textContent = name
      select.appendChild(option)
    })
  })

function loadOntology() {
  const name = document.getElementById("ontology-select").value
  const filePath = `Graph/${name}_graph.json?v=${Date.now()}`
  ...
}
```

## 사용 방법
1. `Ontology/` 폴더에 OWL 파일을 넣고, 필요한 경우 `ontology_list.json`에 이름을 추가합니다.
2. Python 3 환경에서 RDFlib을 설치합니다.
   ```bash
   pip install rdflib
   ```
3. 아래 스크립트를 순서대로 실행해 JSON 데이터를 생성합니다.
   ```bash
   python ontology_processing.py
   python description_extraction.py
   python convert_hierarchy.py
   ```
4. 로컬 웹 서버를 실행하고 브라우저에서 `index.html`을 열어 그래프를 확인합니다.
   ```bash
   python -m http.server
   ```
   그 후 `http://localhost:8000/index.html`에 접속하면 됩니다.
