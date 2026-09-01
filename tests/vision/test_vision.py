from unittest.mock import MagicMock, patch

from vision.src import main as vision_main


def test_get_device_uses_cpu_when_cuda_is_unavailable() -> None:
    with patch.object(vision_main.torch.cuda, "is_available", return_value=False):
        assert vision_main.get_device() == "cpu"


def test_get_device_uses_cuda_when_available() -> None:
    with (
        patch.object(vision_main.torch.cuda, "is_available", return_value=True),
        patch.object(vision_main.torch.cuda, "get_device_name", return_value="RTX"),
    ):
        assert vision_main.get_device() == "cuda"


def test_main_processes_frames_and_reports_progress() -> None:
    result = MagicMock()
    result.boxes = [object(), object()]

    model = MagicMock()
    model.predict.return_value = [result]

    with (
        patch.object(vision_main, "get_device", return_value="cpu"),
        patch.object(vision_main, "YOLO", return_value=model) as yolo,
        patch.object(vision_main, "PROGRESS_EVERY_N_FRAMES", 1),
        patch.object(vision_main.time, "perf_counter", side_effect=[10.0, 11.0, 12.0]),
        patch.object(vision_main, "logger") as logger,
    ):
        vision_main.main()

    yolo.assert_called_once_with(vision_main.MODEL_PATH)

    model.predict.assert_called_once_with(
        source=vision_main.VIDEO_PATH,
        stream=True,
        classes=[0],
        conf=0.5,
        device="cpu",
        verbose=False,
    )
    logger.info.assert_any_call(
        "Iniciando detección: fuente=%s, modelo=%s, dispositivo=%s",
        vision_main.VIDEO_PATH,
        vision_main.MODEL_PATH,
        "cpu",
    )
    logger.info.assert_any_call(
        "Progreso: frame=%d, detecciones=%d, FPS efectivo=%.2f",
        1,
        2,
        1.0,
    )
    logger.info.assert_any_call(
        "Detección finalizada: frames=%d, detecciones=%d, duración=%.2f s, FPS efectivo=%.2f",
        1,
        2,
        2.0,
        0.5,
    )
    assert result.plot.call_count == 0
