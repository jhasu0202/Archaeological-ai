import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import torch
from typing import List, Dict, Tuple, Optional
import os
from pathlib import Path

class DetectionManager:
    def __init__(self):
        self.model_path = "/home/surendra208/Documents/jaya/aimoodmate/ai_app/best.pt"
        self.model = None
        self.class_names = {
            0: "Stones / Stone Pillars / Stone Structures",
            1: "Crops / Farmland", 
            2: "Non-archaeological (deserts, water, mountains, etc.)",
            3: "Heritage Sites (temples, palaces, forts, museums)"
        }
        self.class_colors = {
            0: (139, 69, 19),    # Brown for stones
            1: (34, 139, 34),    # Forest green for crops
            2: (105, 105, 105),  # Dim gray for non-archaeological
            3: (184, 134, 11)    # Dark goldenrod for heritage sites
        }
        self.load_model()
    
    def load_model(self):
        """Load the YOLOv11 model"""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                return True
            else:
                st.error(f"Model file not found at {self.model_path}")
                return False
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return False
    
    def detect_objects(self, image: np.ndarray) -> List[Dict]:
        """Detect objects in a single image"""
        if self.model is None:
            return []
        
        try:
            results = self.model(image)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i in range(len(boxes)):
                        box = boxes.xyxy[i].cpu().numpy()
                        conf = boxes.conf[i].cpu().numpy()
                        cls = int(boxes.cls[i].cpu().numpy())
                        
                        detection = {
                            'bbox': box.tolist(),
                            'confidence': float(conf),
                            'class_id': cls,
                            'class_name': self.class_names.get(cls, f"Class {cls}"),
                            'color': self.class_colors.get(cls, (255, 255, 255))
                        }
                        detections.append(detection)
            
            return detections
        except Exception as e:
            st.error(f"Error during detection: {str(e)}")
            return []
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw bounding boxes and labels on image"""
        annotated_image = image.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            conf = detection['confidence']
            class_name = detection['class_name']
            color = detection['color']
            
            # Draw bounding box
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
            
            # Draw label background
            label = f"{class_name}: {conf:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(annotated_image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(annotated_image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return annotated_image
    
    def crop_detections(self, image: np.ndarray, detections: List[Dict]) -> List[np.ndarray]:
        """Crop detected objects from image"""
        crops = []
        for detection in detections:
            bbox = detection['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            crop = image[y1:y2, x1:x2]
            if crop.size > 0:
                crops.append(crop)
        return crops
    
    def process_video_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """Process a single video frame"""
        detections = self.detect_objects(frame)
        annotated_frame = self.draw_detections(frame, detections)
        return annotated_frame, detections
    
    def get_class_statistics(self, detections_list: List[List[Dict]]) -> Dict:
        """Calculate statistics from multiple detection results"""
        all_detections = []
        for detections in detections_list:
            all_detections.extend(detections)
        
        if not all_detections:
            return {
                'total_detections': 0,
                'class_counts': {},
                'confidence_avg': 0,
                'class_confidence_avg': {}
            }
        
        # Count detections per class
        class_counts = {}
        class_confidences = {}
        
        for detection in all_detections:
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            if class_name not in class_confidences:
                class_confidences[class_name] = []
            class_confidences[class_name].append(confidence)
        
        # Calculate averages
        total_confidence = sum(d['confidence'] for d in all_detections)
        confidence_avg = total_confidence / len(all_detections) if all_detections else 0
        
        class_confidence_avg = {}
        for class_name, confidences in class_confidences.items():
            class_confidence_avg[class_name] = sum(confidences) / len(confidences)
        
        return {
            'total_detections': len(all_detections),
            'class_counts': class_counts,
            'confidence_avg': confidence_avg,
            'class_confidence_avg': class_confidence_avg,
            'all_detections': all_detections
        }
