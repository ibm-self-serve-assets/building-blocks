from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 850, overlap: int = 120) -> list[str]:
    """Simple paragraph-aware recursive chunker with overlap."""
    cleaned = "\n".join(line.rstrip() for line in text.strip().splitlines()).strip()
    if not cleaned:
        return []
    if len(cleaned) <= chunk_size:
        return [cleaned]

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{paragraph}".strip()
        else:
            start = 0
            while start < len(paragraph):
                end = min(start + chunk_size, len(paragraph))
                chunks.append(paragraph[start:end])
                if end == len(paragraph):
                    current = ""
                    break
                start = max(end - overlap, start + 1)

    if current:
        chunks.append(current)

    return chunks
