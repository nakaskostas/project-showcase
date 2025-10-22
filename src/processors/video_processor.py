
import cv2
import base64
from typing import List, Dict, Union

def process(file_path: str, frames_per_second: int = 1) -> List[Dict[str, Union[str, Dict]]]:
    """
    Processes a video file by extracting frames at a specified rate,
    encoding them in base64, and preparing them for a multimodal LLM.

    Args:
        file_path: The absolute path to the video file.
        frames_per_second: The number of frames to extract per second of video.

    Returns:
        A list of dictionaries, where each dictionary represents an image frame
        in the format expected by the Gemini API.
    """
    video_parts = []
    try:
        # Open the video file
        video = cv2.VideoCapture(file_path)
        if not video.isOpened():
            print(f"Error: Could not open video file {file_path}")
            return []

        # Get the video's original FPS
        original_fps = video.get(cv2.CAP_PROP_FPS)
        if original_fps == 0:
            print(f"Warning: Could not determine FPS for {file_path}. Defaulting to 25.")
            original_fps = 25 # A common default

        # Calculate the interval at which to capture frames
        frame_capture_interval = int(original_fps / frames_per_second)

        frame_count = 0
        while True:
            success, frame = video.read()
            if not success:
                break # End of video

            # Capture a frame at the specified interval
            if frame_count % frame_capture_interval == 0:
                # Encode the frame to a memory buffer as a JPEG
                success, buffer = cv2.imencode(".jpg", frame)
                if not success:
                    print(f"Warning: Failed to encode frame {frame_count} from {file_path}")
                    continue

                # Encode the buffer to base64
                encoded_string = base64.b64encode(buffer).decode("utf-8")

                # Structure the data for the Gemini API
                image_data = {
                    "type": "image",
                    "data": {
                        "mime_type": "image/jpeg",
                        "base64": encoded_string
                    }
                }
                video_parts.append(image_data)

            frame_count += 1

        video.release()
        print(f"Successfully processed video {file_path}, extracted {len(video_parts)} frames.")

    except Exception as e:
        print(f"An error occurred while processing video {file_path}: {e}")

    return video_parts
