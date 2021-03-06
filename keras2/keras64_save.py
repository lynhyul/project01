# 가중치 저장할것
# 1. model.save() 쓸것
# 2. pikcle 쓸 것


# epochs 100적용
# validation_split, callback 사용
# early_stopping 5 적용
# Reduce LR 3 적용
# modelcheckpoint 폴더에 hdf5 파일저장


import numpy as np
from tensorflow.keras.models import Sequential,Model, load_model
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.datasets import mnist
from sklearn.metrics import accuracy_score

(x_train, y_train), (x_test,y_test) = mnist.load_data()

#1. 데이터 / 전처리
from tensorflow.keras.utils import to_categorical
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

x_train = x_train.reshape(60000,28*28).astype('float32')/255.
x_test = x_test.reshape(10000,28*28).astype('float32')/255.


#2. 모델
def build_model(drop=0.5, optimizer = 'adam') :
    input = Input(shape=(28*28), name = 'input')
    x = Dense(512, activation='relu', name= 'hidden1') (input)
    x = Dropout(drop)(x)
    x = Dense(256, activation='relu', name= 'hidden2') (x)
    x = Dropout(drop)(x)
    x = Dense(128, activation='relu', name= 'hidden3') (x)
    x = Dropout(drop)(x)
    output = Dense(10, activation='softmax', name = 'output') (x)
    model = Model(inputs = input, outputs = output)
    model.compile(optimizer = optimizer, metrics=['acc'],
                    loss = 'categorical_crossentropy')
    return model

def create_hyperparmeters() :
    # batches = [10, 20, 30, 40, 50]
    opitmizer = ['rmsprop', 'adam']
    dropout = [0.2]
    validation_split = [0.1,0.2,0.3]
    return {"optimizer" : opitmizer,
            "drop": dropout, "validation_split" : validation_split}    


hyperparmeters = create_hyperparmeters()
# model2 = build_model()    타입오류



from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
model2 = KerasClassifier(build_fn=build_model, verbose = 1, epochs=100)

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

mc = ModelCheckpoint('../data/modelcheckpoint/hyper1.h5',save_best_only=True, verbose=1)
es = EarlyStopping(monitor = 'val_loss',patience=5)
lr = ReduceLROnPlateau(monitor = 'val_loss', patience=3, factor=0.5)

search = RandomizedSearchCV(model2,hyperparmeters,cv =3)

search.fit(x_train, y_train,verbose = 1, callbacks = [es,lr,mc])

search.best_estimator_.model.save('../data/xgb_save/keras64.h5')

# model2.save('../data/h5/keras64_save.h5')

print(search.best_params_)  # 선택한 파라미터중에서 가장 좋은거

# print(search.best_estimator_)   # 전체 파라미터 중에서 가장 좋은거
# <tensorflow.python.keras.wrappers.scikit_learn.KerasClassifier object at 0x000001CA15E32C40>

print(search.best_score_)   # 밑에 있는 .score랑은 결과가 다르게 나온다.


acc = search.score(x_test,y_test)
print("최종 스코어 : ",acc)


model3 = load_model('../data/xgb_save/keras64.h5')
pred = np.argmax(model3.predict(x_test),axis=1)
y_test = np.argmax(y_test, axis=1)
acc2 = accuracy_score(y_test,pred)
print("load 스코어 : ",acc2)

# import pickle
# pickle.dump(search, open('../data/xgb_save/keras64.pikle.data','wb'))
# print('save complete')

# print("=========================pickle.Load======================")
#(2) Load
# model2 = pickle.load(open('../data/xgb_save/m39.pikle.data','rb'))
# r2_2 = model2.score(x_test,y_test)
# print('r2_2 : ',r2_2)

'''
최종 스코어 :  0.9860000014305115
load 스코어 :  0.986
'''