# Final Project Report

**Introduction:**

The automotive repair industry faces significant challenges in damage assessment and cost estimation. Traditional methods require physical inspection by trained professionals, leading to long waits and differing estimates. These challenges cause issues for consumers, small mechanic shops, towing companies, and rental fleet managers who need quick, accurate, and transparent damage assessments.

Our motivation is to address the need for a system that can fix these problems.

The input for our system is multiple car photographs uploaded by users through a web interface. These images are processed using YOLOv8-based damage detection and given severity classifications. The cost is calculated using rules from the CSV file. The system outputs the cost estimate and a PDF report. 

This project lies within the domains of computer vision and expert systems. We used YOLOv8 for deep learning object detection. PyTorch served as the deep learning framework. Transfer learning was applied to the pre-trained YOLOv8n model fine-tuned on car damage dataset. A rule-based system handles cost estimation. The system architecture consists of a FastAPI backend with API endpoints for uploading car photos, running ML inference, calculating cost estimates, retrieving reports, and generating PDF reports. The frontend is built with React 18 and TypeScript using Vite as the build tool, Tailwind CSS for styling, and shadcn/ui component library.

**Area of application, Dataset and/or Features:**

The dataset of damaged car photos was assembled from multiple sources including Supervisely [1], Kaggle [2], and Roboflow Universe [3]. The Supervisely dataset came in polygon annotation format stored in JSON files, which needed to be converted to YOLOv8 detection format using a custom script.

The dataset is split into 70% training (~700 images), 20% validation (~200 images), and 10% test (~100 images) sets. The dataset detects 10-12 key car parts and it classifies five damage types. Images are in JPEG/PNG format with various resolutions, and labels are stored as text files with the format "class_id x_center y_center width height" where all coordinates are normalized to [0,1]. 

The system accepts multiple images per vehicle. Users can configure the labor rate in dollars per hour and choose between OEM parts, used parts, or both options. Users can also edit severity levels to correct the system's assessments. The damage detection system identifies which car part is damaged, classifies the damage type, provides bounding box coordinates for visualization, and assigns confidence scores from 0 to 1 for each detection.

The cost estimation calculates labor cost as labor hours multiplied by the labor rate, provides parts costs for both new OEM and used parts, and generates total cost estimates with minimum (used parts), likely (OEM parts), and maximum (with 20% buffer) ranges. The system also provides a line-item breakdown for transparency. Report generation includes visual detection overlays on images, an editable damage assessment table, a cost estimate summary, and PDF export for documentation.

**Methods:**

YOLOv8 is an object detection model developed by Ultralytics. The variant we used takes pixel images as input and outputs bounding boxes with class predictions and confidence scores. It predicts bounding box coordinates as (x_center, y_center, w, h) normalized to [0,1], class probabilities P(class_i | object) for each class i, and an objectness score P(object) indicating the presence of an object. The total loss function combines the classification loss, the bounding box regression loss, and the objectness loss.

We employed transfer learning by starting from a pre-trained YOLOv8n model that was trained on the COCO dataset. This approach uses learned features from general object detection, enables faster convergence with less epochs to adapt to car damage detection, and provides better performance than training from scratch. The fine-tuning process initializes with pre-trained weights, replaces the final classification layer for our specific classes, trains with a lower learning rate to keep learned features, and updates all layers through end-to-end training.

Severity classification assigns damage severity levels (minor, moderate, severe) using a rule-based system that considers damage type, confidence score, and part location. The cost estimation engine is a CSV-driven rule-based system that calculates repair costs based on part type, damage type, and severity level. For each detected damage, labor cost is calculated as C_labor = H_labor × R_labor where H_labor is labor hours from CSV rules and R_labor is the user-configurable labor rate in dollars per hour. Parts cost is C_parts = P_new if OEM parts are selected, or C_parts = P_used if used parts are selected, where P_new is the new/OEM part cost from CSV and P_used is the used part cost (typically 50% of new). Total cost per item is C_total = C_labor + C_parts. The overall estimate provides a minimum (sum of all items using used parts), likely (sum of all items using OEM parts), and maximum (likely cost × 1.2 with 20% buffer for unexpected costs).

The cost rules are stored in data/auto_damage_repair_costs_MASTER.csv with columns for Car_Type, Part, Damage_Type, Severity, New_Part_Cost, Used_Part_Cost, Labor_Hours, Labor_Rate_Per_Hour, Total_Labor_Cost, Total_Cost_New_Part, and Total_Cost_Used_Part. For example, a Super car type with a Door part, Dent damage type, and Moderate severity has a new part cost of $3,500, used part cost of $1,750, labor hours of 5.4, resulting in total cost of $4,310 for new parts and $2,560 for used parts. 

**Experiments/Results/Discussion:**

YOU MIGHT NEED TO WRITE THIS BRO

**Conclusion/Future Work**

This project successfully developed an AI-powered auto damage detection and cost estimation system that combines deep learning through YOLOv8 object detection for automated damage identification, rule-based systems for transparent severity classification and cost estimation, modern web architecture with FastAPI backend and React frontend, and a clean user interface with editable assessments and PDF reports. Key components include complete system architecture and implementation, YOLOv8 model training pipeline and configuration, comprehensive cost estimation engine, full-stack web application, PDF report generation, and user-editable damage assessments.

For future work, with more time, team members, or computational resources, several areas would be explored. Model improvements could include collecting more diverse datasets, adding more edge cases, experimenting with larger YOLOv8 variants for higher accuracy, and supporting video input for damage assessment from video clips.

**References**

CITE THE DATASETS AND CODE LIBRARIES HERE

"Each reference entry may include the following (preferably in this order): author(s), title, conference/journal, publisher, year."

AND MAKE SURE THE CITATION NUMBERS FOR [Supervisely, Kaggle, and Roboflow Universe] MATCH THE CITATION NUMBERS AT THE START OF "Area of application, Dataset and/or Features"
