from typing import Dict, Any
import json
from src.retrieval_server import llm_adapter


def suggest_ontology_from_schema(schema: Dict[str, Any], prompt_template: str = None) -> Dict[str, Any]:
    """Use the LLM adapter to suggest an ontology from a relational schema.

    The function builds a prompt describing the schema and asks the LLM to
    return a JSON document with `classes` and `relationships` keys.
    """
    if prompt_template is None:
        prompt_template = (
            "You are given a relational database schema. Suggest an ontology as JSON with 'classes' "
            "(name, attributes) and 'relationships' (from, to, type). Schema: {schema}"
        )

    prompt = prompt_template.format(schema=json.dumps(schema, indent=2))
    resp = llm_adapter.generate(prompt, model="text-bison-001")

    # Try to parse JSON from the response. The LLM may wrap it in text; extract first JSON block.
    try:
        # naive extraction: find first { and last }
        start = resp.find("{")
        end = resp.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_text = resp[start : end + 1]
            parsed = json.loads(json_text)
            return parsed
    except Exception:
        pass

    # If parsing failed, return a fallback simple mapping: every table -> class with columns
    ontology = {"classes": [], "relationships": []}
    for table, cols in schema.items():
        ontology["classes"].append({"name": table, "attributes": [c["name"] for c in cols]})
    return ontology
