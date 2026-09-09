from typing import Any

import pytest
from pydantic import ValidationError

from app.src.schemas.cameras import CameraCreate, CameraUpdate


def test_camera_create_valido() -> None:
    """
    Se envían los datos mínimos requeridos y se verifica que
    pydantic asigne correctamente los valores por defecto.
    """
    datos: dict[str, Any] = {
        "name": "Cámara Pasillo 1",
        "source_type": "demo_video",
    }

    resultado = CameraCreate(**datos)

    # Valida que los datos insertados coincidan
    assert resultado.name == "Cámara Pasillo 1"
    assert resultado.source_type == "demo_video"

    # Valida que pydantic asigne correctamente los valores por defecto
    assert resultado.is_active is True
    assert resultado.description is None


def test_camera_create_rechaza_datos_faltantes() -> None:
    """
    Asegura que si el cliente omite un campo obligatorio (como el source_type),
    la API rechace la petición y no permita que la base de datos falle.
    """
    datos: dict[str, Any] = {
        "name": "Cámara Sin Fuente",
        # Se omite el campo source_type
    }

    # pytest intercepta el error
    with pytest.raises(ValidationError):
        CameraCreate(**datos)


def test_camera_create_rechaza_source_invalido() -> None:
    """
    Verifica que la restricción de tipado estricto con `Literal` funcione.
    """
    datos: dict[str, Any] = {
        "name": "Cámara Rara",
        "source_type": "cinta_vhs",  # Valor no incluido en la lista permitida del Literal
    }

    with pytest.raises(ValidationError):
        CameraCreate(**datos)


def test_camera_update_parcial() -> None:
    """
    el cliente solo envía lo que quiere modificar sin alterar los demás campos.
    """
    datos: dict[str, Any] = {
        "is_active": False  # solo apaga la cámara, sin tocar el nombre
    }

    resultado = CameraUpdate(**datos)

    # verifica que capturó el cambio
    assert resultado.is_active is False

    # los demás campos deben quedarse en None para que la base de datos sepa que no debe alterarlos
    assert resultado.name is None
