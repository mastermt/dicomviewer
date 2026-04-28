import numpy as np
from pydicom.pixel_data_handlers.util import apply_voi_lut
from PyQt5.QtGui import QImage


class DICOMService:
    @staticmethod
    def format_metadata(ds, fields):
        lines = []
        for label, attr in fields:
            value = getattr(ds, attr, "N/A")
            lines.append(f"{label}: {value}")
        return "\n".join(lines)

    @staticmethod
    def dataset_to_qimage(ds, unsupported_format_message):
        pixel_array = ds.pixel_array

        if getattr(ds, "SamplesPerPixel", 1) == 1:
            try:
                data = apply_voi_lut(pixel_array, ds)
            except Exception:
                data = pixel_array

            slope = float(getattr(ds, "RescaleSlope", 1))
            intercept = float(getattr(ds, "RescaleIntercept", 0))
            data = data.astype(np.float32) * slope + intercept

            min_val = np.min(data)
            max_val = np.max(data)
            if max_val > min_val:
                data = (data - min_val) * (255.0 / (max_val - min_val))
            else:
                data = np.zeros_like(data, dtype=np.float32)

            img8 = np.clip(data, 0, 255).astype(np.uint8)
            if img8.ndim == 3:
                img8 = img8[0]

            if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
                img8 = 255 - img8

            img8 = np.ascontiguousarray(img8)
            height, width = img8.shape
            return QImage(
                img8.data,
                width,
                height,
                img8.strides[0],
                QImage.Format_Grayscale8,
            ).copy()

        data = pixel_array
        if data.ndim == 4:
            data = data[0]
        if data.ndim != 3 or data.shape[2] != 3:
            raise ValueError(unsupported_format_message.format(shape=data.shape))

        data = data.astype(np.float32)
        min_val = np.min(data)
        max_val = np.max(data)
        if max_val > min_val:
            data = (data - min_val) * (255.0 / (max_val - min_val))
        img8 = np.clip(data, 0, 255).astype(np.uint8)
        img8 = np.ascontiguousarray(img8)

        height, width, _ = img8.shape
        return QImage(
            img8.data,
            width,
            height,
            img8.strides[0],
            QImage.Format_RGB888,
        ).copy()

