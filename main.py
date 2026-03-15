from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from typing import List
import uvicorn
from vision import extract_measurements

app = FastAPI(
    title="Body Measurement API",
    description="Extracts body measurements from uploaded photos or video frames using Mediapipe.",
    version="1.0.0"
)

class MeasurementResponse(BaseModel):
    height_cm: float
    shoulder_width_cm: float
    chest_cm: float
    waist_cm: float
    hips_cm: float

@app.get("/")
def health_check():
    """Health check endpoint to ensure API is running."""
    return {"status": "ok", "message": "Body Measurement API is online."}

@app.post("/measurements/", response_model=MeasurementResponse)
async def get_measurements(
    file: UploadFile = File(..., description="An image file (e.g., JPEG, PNG)"),
    reference_height_cm: float = Form(170.0, description="User's known height in cm to calibrate measurements.")
):
    """
    Accepts an uploaded image and an optional reference height.
    Extracts key body measurements and returns them in structured JSON.
    """
    try:
        image_bytes = await file.read()
        measurements = extract_measurements(image_bytes, reference_height_cm)
        return MeasurementResponse(**measurements)
    except Exception as e:
        # Simplified error response for prototype
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
