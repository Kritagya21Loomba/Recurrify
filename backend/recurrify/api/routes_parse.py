from __future__ import annotations

from fastapi import APIRouter, HTTPException

from recurrify.classifier.classifier import Classifier
from recurrify.models.api_models import ParseRequest, ParseResponse
from recurrify.parser.extractor import RecurrenceExtractor
from recurrify.parser.parser import ParseError, parse
from recurrify.renderer.latex_renderer import LaTeXRenderer

router = APIRouter()


@router.post("/parse", response_model=ParseResponse)
async def parse_recurrence(request: ParseRequest):
    try:
        ast = parse(request.input)
        info = RecurrenceExtractor().extract(ast)
        classification = Classifier().classify(info)
        canonical = LaTeXRenderer().render_recurrence(info)

        return ParseResponse(
            canonical_form=canonical,
            recurrence_type=classification.recurrence_type.value,
            applicable_methods=[m.value for m in classification.applicable_methods],
        )
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse recurrence: {e}")
