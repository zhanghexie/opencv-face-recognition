class Setting:
    
    def __init__(self):
        self.train_result_path = 'file/result.yml'
        self.face_classification_file_path = 'file/haarcascade_frontalface_default.xml'
        self.eyes_classification_file_path = 'file/haarcascade_mcs_eyepair_big.xml'
        self.nose_classification_file_path = 'file/haarcascade_mcs_nose.xml'
        self.mouth_classification_file_path = 'file/haarcascade_mcs_mouth.xml'
        self.usrs_info_path = 'file/usrs_info.pickle'
        self.face_image_path = '.dataset'
        self.vedio_path = 'videos'
        # self.vedio_path = 'videos-test'
        self.recycle_path = 'recycle'