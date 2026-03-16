from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from vision import extract_measurements
import os
import uvicorn

app = FastAPI(
    title="Body Measurement API",
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
    return {"status": "ok"}

@app.post("/measurements/", response_model=MeasurementResponse)
async def get_measurements(
    file: UploadFile = File(...),
    reference_height_cm: float = Form(170.0)
):
    image_bytes = await file.read()
    measurements = extract_measurements(image_bytes, reference_height_cm)
    return MeasurementResponse(**measurements)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
