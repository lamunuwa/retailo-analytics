import cv2
import torch
from ultralytics import YOLO

VIDEO_PATH = "vision/data/demo/supermarket.mp4"


def get_device() -> str:
    """Selecciona RTX, si no existe, usa CPU"""

    if torch.cuda.is_available():
        print(f"Dispositivo seleccionado: cuda ({torch.cuda.get_device_name(0)})")
        return "cuda"

    print("Dispositivo seleccionado: cpu")
    return "cpu"


def main() -> None:
    """Ejecuta deteccion de personas sobre un video"""

    device = get_device()
    model = YOLO("yolov8n.pt") # Modelo liviano de Yolo

    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS) # Captura de frames por segundo
    cap.release()

    # Delay para que el video se reproduzca como el original
    delay = max(1, int(1000 / fps)) if fps > 0 else 30 
    # Configura la ventana para que sea redimensionable
    cv2.namedWindow("RetaiLO Analytics", cv2.WINDOW_NORMAL)

    try:
        results = model.predict(
            source=VIDEO_PATH,
            stream=True,
            classes=[0], # Clase 0 corresponde a personas en el modelo COCO
            conf=0.5, # Umbral de confianza para detección
            device=device,
            verbose=False, # Desactiva el printeo en terminal de cada frame
        )

        for result in results:
            annotated_frame = result.plot() if hasattr(result, "plot") else result
            if isinstance(annotated_frame, torch.Tensor):
                annotated_frame = annotated_frame.cpu().numpy()
            cv2.imshow("RetaiLO Analytics", annotated_frame)

            key = cv2.waitKey(delay) & 0xFF
            if key in (ord("q"), 27):
                print("Proceso interrumpido")
                break
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
