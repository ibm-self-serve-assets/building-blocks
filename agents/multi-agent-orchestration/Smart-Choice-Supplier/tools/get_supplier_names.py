import json
import os
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool
def get_supplier_names() -> str:
    """
    Returns a JSON array of unique supplier names from dataset1.

    Reads tools/data/dataset1_product_supplier.json and extracts all supplier names,
    deduplicates them, and returns a sorted JSON array of strings.

    Args:
        None

    Returns:
        str: JSON string array of supplier names, or an error JSON on failure.
    """
    try:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        dataset_path = os.path.join(data_dir, 'dataset1_product_supplier.json')
        with open(dataset_path, 'r') as f:
            data = json.load(f)

        suppliers = sorted({entry["supplier_name"] for entry in data})
        return json.dumps(suppliers, indent=2)

    except FileNotFoundError:
        return json.dumps({"error": "dataset1_product_supplier.json not found"}, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"invalid JSON in dataset1: {str(e)}"}, indent=2)
    except KeyError as e:
        return json.dumps({"error": f"missing field in dataset1: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"unexpected error: {str(e)}"}, indent=2)

# Example usage
# if __name__ == "__main__":
#     print(get_supplier_names())
