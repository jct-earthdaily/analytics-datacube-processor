"""outpout schema class"""
from typing import Optional
from pydantic import BaseModel, HttpUrl



class Metadata(BaseModel):
    processId: str
    processName: str
    outputFormat: str

class ProcessOutput(BaseModel):
    status: str
    outputPath: Optional[HttpUrl]
    error: Optional[str]

class OutputModel(BaseModel):
    Metadata: Metadata
    ProcessOutput: ProcessOutput
