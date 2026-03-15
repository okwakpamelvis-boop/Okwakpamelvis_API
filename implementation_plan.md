# Body Measurement Extraction API Plan

We are building a REST API that extracts body measurements (height, shoulder width, chest, waist, and hips) from 2-4 photos or a short video. 

## Proposed Architecture

### 1. Technology Stack
*   **Web Framework**: FastAPI (High performance, built-in validation, async support).
*   **Computer Vision**: OpenCV (`cv2`) and Google MediaPipe (`mediapipe`).
*   **Deployment Target**: Render (Web Service).

### 2. File Structure
*   `main.py`: The FastAPI application and core routing.
*   `vision.py`: Modularized MediaPipe Pose logic.
*   `requirements.txt`: Python package dependencies.
*   `Procfile` / `render.yaml`: Deployment configurations for Render.

### 3. Core Logic & Constraints
*   **Monocular Scale Ambiguity:** True 3D scale cannot be accurately measured from a 2D image without a reference object (like a coin) or depth sensors (LiDAR). We will use a baseline heuristic (e.g., standardizing the user height or using a calibration ratio based on input) to estimate absolute measurements (shoulder, chest, waist, hips).
*   **Pose Estimation:** MediaPipe extracts 33 3D landmarks for the human body. We will use the distance between key landmarks to compute proportional girths/widths.

## Proposed Endpoints
*   `GET /`: Health check endpoint.
*   `POST /measurements/`: Accepts `multipart/form-data` uploads (images) and returns structured JSON containing bounding box predictions and estimated measurements.

## Verification Plan
1.  **Automated**: Run `pytest` or basic HTTP requests using the `requests` library locally to ensure the endpoints return standard JSON without 500 errors.
2.  **Manual**: Upload a sample image via FastAPI's built-in Swagger UI (`http://localhost:8000/docs`) and verify the returned JSON structure.
