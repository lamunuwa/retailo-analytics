from unittest.mock import MagicMock
from app.src.models.cameras import CameraModel
from app.src.repos.cameras import CameraRepository

def test_camera_repository_creates_camera() -> None:
    # 1. Configurar Mock
    mock_session = MagicMock()
    repo = CameraRepository(session=mock_session)
    
    # 2. Ejecutar Acción (El método create aún no existe, fallará aquí - RED)
    camera = repo.create(
        store_id=1, 
        name="Cámara Pasillo", 
        source_type="demo_video"
    )
    
    # 3. Validar (GREEN)
    assert isinstance(camera, CameraModel)
    mock_session.add.assert_called_once_with(camera)
    mock_session.commit.assert_called_once()