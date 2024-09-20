from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logger.logger import logging
from networksecurity.entity.artifact_entity import ModelPusherArtifact,ModelEvaluationArtifact
from networksecurity.entity.config_entity import ModelPusherConfig
from networksecurity.utils.ml_utils.model.estimator import ModelResolver
import os,sys
import shutil

class ModelPusher:
    def __init__(self, model_pusher_config: ModelPusherConfig, model_evaluation_artifact: ModelEvaluationArtifact):
        try:
            self.model_pusher_config = model_pusher_config
            self.model_evaluation_artifact = model_evaluation_artifact
        except  Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def initiate_model_pusher(self)->ModelPusherArtifact:
        try:
            trained_model_path = self.model_evaluation_artifact.trained_model_path

            #Creating model pusher dir to save model
            model_file_path = self.model_pusher_config.model_file_path
            os.makedirs(os.path.dirname(model_file_path),exist_ok = True)
            shutil.copy(src=trained_model_path, dst=model_file_path)

            #saving the better model dir and preparing artifact
            if self.model_evaluation_artifact.is_model_accepted:
                print("Saving the recent trained model") 
                saved_model_path = self.model_pusher_config.saved_model_path
                os.makedirs(os.path.dirname(saved_model_path),exist_ok = True)
                shutil.copy(src=trained_model_path, dst=saved_model_path)
                model_pusher_artifact = ModelPusherArtifact(saved_model_path=saved_model_path, model_file_path=model_file_path)
                return model_pusher_artifact

            #preparing artifact with the best available model
            print('Rejecting the recent trained model') 
            model_resolver = ModelResolver()
            saved_model_path = model_resolver.get_best_model_path()
            model_pusher_artifact = ModelPusherArtifact(saved_model_path=saved_model_path, model_file_path=model_file_path)
            return model_pusher_artifact
                    
        except  Exception as e:
            raise NetworkSecurityException(e, sys)

