from unittest.mock import MagicMock
from app.src.models.cameras import CameraModel
from app.src.repos.cameras import CameraRepository

def test_camera_repository_creates_camera() -> None:
    # 1. Configurar Mock
    mock_session = MagicMock()
    repo = CameraRepository(session=mock_session)
    
    # 2. Ejecutar Acción (El método create aún no existe, fallará aquí - RED), con la modificación que se agrego, ahora debería pasar (GREEN) :p
    camera = repo.create(
        store_id=1, 
        name="Cámara Pasillo", 
        source_type="demo_video"
    )
    
    # 3. Validar (GREEN)
    assert isinstance(camera, CameraModel)
    mock_session.add.assert_called_once_with(camera)
    mock_session.commit.assert_called_once()

def test_camera_repository_lists_cameras_by_store() -> None:
    mock_session = MagicMock()
    mock_session.scalars.return_value.all.return_value = [
        CameraModel(id=1, store_id=5, name="Cámara 1", source_type="demo_video", is_active=True)
    ]
    repo = CameraRepository(session=mock_session)
    cameras = repo.get_all_by_store(store_id=5)
    assert len(cameras) == 1
    assert cameras[0].name == "Cámara 1"

def test_camera_repository_gets_camera_by_id() -> None: 
    #agrega la prueba unitaria para verificar la búsqueda por ID en el repositorio
    mock_session = MagicMock()
    camera_mock = CameraModel(id=1, store_id=5, name="Cámara 1", source_type="demo_video")
    mock_session.get.return_value = camera_mock
    repo = CameraRepository(session=mock_session)
    
    result = repo.get_by_id(camera_id=1)
    
    assert result == camera_mock
    mock_session.get.assert_called_once_with(CameraModel, 1)