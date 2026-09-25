from django.db import migrations, models

import scripts.models
from scripts.character_mask import CORE_CHARACTER_TYPES, build_mask


def assign_bit_indexes(apps, schema_editor):
    ClocktowerCharacter = apps.get_model("scripts", "ClocktowerCharacter")
    for index, character in enumerate(ClocktowerCharacter.objects.order_by("character_id")):
        character.bit_index = index
        character.save(update_fields=["bit_index"])


def backfill_masks(apps, schema_editor):
    ClocktowerCharacter = apps.get_model("scripts", "ClocktowerCharacter")
    ScriptVersion = apps.get_model("scripts", "ScriptVersion")
    bit_map = dict(
        ClocktowerCharacter.objects.filter(character_type__in=CORE_CHARACTER_TYPES).values_list(
            "character_id", "bit_index"
        )
    )
    batch = []
    for version in ScriptVersion.objects.only("pk", "content").iterator(chunk_size=500):
        version.character_mask = build_mask(version.content, bit_map)
        batch.append(version)
        if len(batch) == 500:
            ScriptVersion.objects.bulk_update(batch, ["character_mask"])
            batch = []
    ScriptVersion.objects.bulk_update(batch, ["character_mask"])


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0046_scriptversion_sv_content_gin_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='clocktowercharacter',
            name='bit_index',
            field=models.PositiveSmallIntegerField(blank=True, editable=False, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='scriptversion',
            name='character_mask',
            field=scripts.models.CharacterMaskField(blank=True, editable=False, null=True),
        ),
        migrations.RunPython(assign_bit_indexes, migrations.RunPython.noop),
        migrations.RunPython(backfill_masks, migrations.RunPython.noop),
    ]
