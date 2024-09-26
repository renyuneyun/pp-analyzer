
def convert_into_segments(pp_text: str) -> list[str]:
    return [s for s in (s.strip() for s in pp_text.split('\n')) if s]
