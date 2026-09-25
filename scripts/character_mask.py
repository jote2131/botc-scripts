MASK_BITS = 512
CORE_CHARACTER_TYPES = ("Townsfolk", "Outsider", "Minion", "Demon")


def build_mask(content: list, bit_map: dict[str, int]) -> str:
    bits = ["0"] * MASK_BITS
    for item in content:
        character_id = item.get("id") if isinstance(item, dict) else item
        index = bit_map.get(character_id) if isinstance(character_id, str) else None
        if index is not None:
            bits[index] = "1"
    return "".join(bits)
