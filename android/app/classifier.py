import os
import pickle
import numpy as np
from keras.models import load_model
from androguard.core.bytecodes.apk import APK
from genetic_algorithm import GeneticSelector

class CustomUnpickler(pickle.Unpickler):

    def find_class(self, module, name):
        try:
            return super().find_class(__name__, name)
        except AttributeError:
            return super().find_class(module, name)


sel = CustomUnpickler(open('D:/colon\Android-Malware-Detection-Version1--main/android-malware-detection-master/app/static/models/ga.pkl', 'rb')).load()

permissions = []
with open('D:/colon/Android-Malware-Detection-Version1--main/android-malware-detection-master/app/static/permissions.txt', 'r') as f:
    content = f.readlines()
    for line in content:
        cur_perm = line[:-1]
        permissions.append(cur_perm)


def classify(file, ch):
    vector = {}
    result = 0
    name, sdk, size = 'unknown', 'unknown', 'unknown'
    app = APK(file)
    perm = app.get_permissions()
    name, sdk, size = meta_fetch(file)
    for p in permissions:
        if p in perm:
            vector[p] = 1
        else:
            vector[p] = 0
    data = [v for v in vector.values()]
    data = np.array(data)
    if ch == 0:
        ANN = load_model('D:/colon/Android-Malware-Detection-Version1--main/android-malware-detection-master/app/static/models/ANN.h5')
        #print(data)
        result = ANN.predict([data[sel.support_].tolist()])
        print(result)

        if result < 0.02:
            # return 'Benign(safe)'
            result = 'Benign(safe)'
        else:
            # return 'Malware'
            result = 'Malware'
    if ch == 1:
        SVC = pickle.load(open('D:/colon/Android-Malware-Detection-Version1--main/android-malware-detection-master/app/static/models/svc_ga.pkl', 'rb'))
        result = SVC.predict([data[sel.support_]])
        if result == 'benign':
            result = 'Benign(safe)'
        else:
            result = 'Malware'
    return result, name, sdk, size


def meta_fetch(apk):
    app = APK(apk)
    return app.get_app_name(), app.get_target_sdk_version(), str(round(os.stat(apk).st_size / (1024 * 1024), 2)) + ' MB'
