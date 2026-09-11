from django.db import transaction

from ..models import CodeSequence


class CodeGenerator:

    @staticmethod
    @transaction.atomic
    def generate(prefix="PRD"):

        sequence, created = CodeSequence.objects.select_for_update().get_or_create(
            prefix=prefix
        )

        sequence.last_number += 1
        sequence.save()

        return f"{prefix}-{sequence.last_number:06d}"