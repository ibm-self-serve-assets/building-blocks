import json
import hashlib
from docling_core.types.doc import DoclingDocument, TextItem, RefItem, GroupItem, ContentLayer, DocumentOrigin


def json_document_converter(filename: str) -> DoclingDocument:
    # code-level, some level of custom code for only 'insight headings', create separate file for custom code
    with open(filename, 'r') as file:
        json_data = json.load(file)

    text_items = []
    paragraph_texts = []
    text_refs = []

    for key, val in json_data.items():
        if isinstance(val, list):
            for item in val:
                paragraph_texts.append(f'{key}: {item}')
        else: 
            paragraph_texts.append(f'{key}: {val}')
    
    for i in range(len(paragraph_texts)):
        text_items.append(TextItem(self_ref=f'#/texts/{i}', label='text', orig=filename, text=paragraph_texts[i]))
        text_refs.append(RefItem(cref=f'#/texts/{i}'))
    
    body_group = GroupItem(
        name="_root_",
        self_ref="#/body",
        content_layer=ContentLayer.BODY,
        children=[]
        )   
    
    origin_ = DocumentOrigin(mimetype='application/json', filename=filename, binary_hash=generate_hash(filename)) # set binary_hash = 0 just for functionality -- import hash function only if proceeding with this
    
    doc = DoclingDocument(schema_name='DoclingDocument', version='1.5.0', name=filename, body=body_group, groups=[body_group], texts=text_items, origin=origin_)

    for i in range(len(text_items)):
        body_group._add_child(doc=doc, stack=[], new_ref=text_refs[i])

    #for i in range(len(text_refs)):
    #    text_refs[i].parent = body_group

    return doc


def generate_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()