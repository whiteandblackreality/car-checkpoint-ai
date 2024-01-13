from inference import YoloRecognitionInference
from models.vehicle_recognition.models.verification import VerificationCarsModel

InferenceConfig = {
    'detection_model': 'models/weights/plates.pt',
    'vehicle_detection': "models/weights/vehicle.pt",
    'ocr_model': {'lang_list': ['en'], 'recog_network': 'alpr_2', 'user_network_directory': 'models/user_network/',
                  'model_storage_directory': 'models/ocr_model/', 'detector': False},
    'device': 'cuda'

}
ALPR_MODEL = YoloRecognitionInference(inference_config=InferenceConfig)

CARS_MODEL = VerificationCarsModel(cars_model_parameters={},
                              gpus=0,
                              emb_size=512,
                              weights="models/vehicle_recognition/weights/tf_efficientnet_b5_drom_v1_4.pth")



