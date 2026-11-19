"""Export ingest JSON Schema from the authoritative Pydantic request model."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.schemas import Batch


def main():
    output = ROOT / 'shared' / 'schemas'
    output.mkdir(parents=True, exist_ok=True)
    schema = Batch.model_json_schema(by_alias=True)
    schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    schema['$id'] = 'hww.frames.v1'
    target = output / 'frame-batch.v1.schema.json'
    text = json.dumps(schema, ensure_ascii=False, indent=2) + '\n'
    if '--check' in sys.argv:
        assert target.read_text(encoding='utf-8') == text, 'Regenerate the ingest schema'
        print('PASS: ingest JSON Schema matches Pydantic')
    else:
        target.write_text(text, encoding='utf-8')
        print('Generated shared/schemas/frame-batch.v1.schema.json')


if __name__ == '__main__':
    main()

