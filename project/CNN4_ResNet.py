from PIL import Image
import os, glob, numpy as np
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, Model
from keras.layers import Input
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, BatchNormalization,Activation,ZeroPadding2D,Add
from keras.layers import GlobalAveragePooling2D
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt
from keras import backend as K
import tensorflow as tf
from tensorflow.python.framework import ops as tf_ops
from keras.optimizers import Adam
from tensorflow.keras.applications import InceptionV3

# caltech_dir =  '../data/image/project/'
# categories = ["0", "1", "2", "3","4","5","6","7",
#                 "8","9"]
# nb_classes = len(categories)

# image_w = 255
# image_h = 255

# pixels = image_h * image_w * 3

# X = []
# y = []

# for idx, cat in enumerate(categories):
    
#     #one-hot 돌리기.
#     label = [0 for i in range(nb_classes)]
#     label[idx] = 1

#     image_dir = caltech_dir + "/" + cat
#     files = glob.glob(image_dir+"/*.jpg")
#     print(cat, " 파일 길이 : ", len(files))
#     for i, f in enumerate(files):
#         img = Image.open(f)
#         img = img.convert("RGB")
#         img = img.resize((image_w, image_h))
#         data = np.asarray(img)

#         X.append(data)
#         y.append(label)

#         if i % 700 == 0:
#             print(cat, " : ", f)

# X = np.array(X)
# y = np.array(y)
# #1 0 0 0 이면 Beagle
# #0 1 0 0 이면 

# print(X.shape)
# print(y.shape)


# # X_train, X_test, y_train, y_test = train_test_split(X, y)
# # xy = (X_train, X_test, y_train, y_test)
# np.save("../data/npy/P_project_x.npy", arr=X)
# np.save("../data/npy/P_project_y.npy", arr=y)



# print("ok", len(y))

# print(X_train.shape) # (2442, 255, 255, 3)
# print(X_train.shape[0])   # 2442


config = tf.compat.v1.ConfigProto() 
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(log_device_placement=True))

# X_train, X_test, y_train, y_test = np.load("../data/npy/P_project.npy",allow_pickle=True)
x = np.load("../data/npy/P_project_x.npy",allow_pickle=True)
y = np.load("../data/npy/P_project_y.npy",allow_pickle=True)
# print(X_train.shape)
# print(X_train.shape[0])

print(x.shape)
print(y.shape)


categories = ["Beaggle", "Bichon Frise", "Border Collie","Bulldog", "Corgi","Poodle","Retriever","Samoyed",
                "Schnauzer","Shih Tzu",]
nb_classes = len(categories)

#일반화
# X_train = X_train.astype(float) / 255
# X_test = X_test.astype(float) / 255
x = x.astype(float) / 255

y = np.argmax(y, axis=1)


# print(X_train.shape)    # 2433, 255,255,3
# print(X_test.shape)     # 812, 255, 255, 3

idg = ImageDataGenerator(
    width_shift_range=(0.1),   
    height_shift_range=(0.1) 
    ) 

# train_generator = idg.flow(x_train,y_train,batch_size=32,seed=2020)
# valid_generator = idg.flow(x_test,y_test)
 
input_tensor = Input(shape=(255, 255, 3), dtype='float32', name='input')
 
from sklearn.model_selection import StratifiedKFold, KFold

skf = StratifiedKFold(n_splits=3, random_state=42, shuffle=True)

   
    


with tf_ops.device('/device:GPU:0'):
    for train_index, valid_index in skf.split(x,y) :  

        x_train = x[train_index]
        x_valid = x[valid_index]    
        y_train = y[train_index]
        y_valid = y[valid_index]

        train_generator = idg.flow(x_train,y_train,batch_size=32,seed=2020)
        valid_generator = idg.flow(x_valid,y_valid)

        def conv1_layer(x):    
            x = ZeroPadding2D(padding=(3, 3))(x)
            x = Conv2D(64, (7, 7), strides=(2, 2))(x)
            x = BatchNormalization()(x)
            x = Activation('relu')(x)
            x = ZeroPadding2D(padding=(1,1))(x)
        
            return x   
        
            
        
        def conv2_layer(x):         
            x = MaxPooling2D((3, 3), 2)(x)     
        
            shortcut = x
        
            for i in range(2):
                if (i == 0):
                    x = Conv2D(16, (1, 1), strides=(1, 1), padding='valid')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
                    
                    x = Conv2D(16, (3, 3), strides=(1, 1), padding='same')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
        
                    x = Conv2D(64, (1, 1), strides=(1, 1), padding='valid')(x)
                    shortcut = Conv2D(64, (1, 1), strides=(1, 1), padding='valid')(shortcut)            
                    x = BatchNormalization()(x)
                    shortcut = BatchNormalization()(shortcut)
        
                    x = Add()([x, shortcut])
                    x = Activation('relu')(x)
                    
                    shortcut = x
        
                else:
                    x = Conv2D(16, (1, 1), strides=(1, 1), padding='valid')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
                    
                    x = Conv2D(16, (3, 3), strides=(1, 1), padding='same')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
        
                    x = Conv2D(64, (1, 1), strides=(1, 1), padding='valid')(x)
                    x = BatchNormalization()(x)            
        
                    x = Add()([x, shortcut])   
                    x = Activation('relu')(x)  
        
                    shortcut = x        
            
            return x
        
        
        
        def conv3_layer(x):        
            shortcut = x    
            
            for i in range(2):     
                if(i == 0):            
                    x = Conv2D(32, (1, 1), strides=(2, 2), padding='valid')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)        
                    
                    x = Conv2D(32, (3, 3), strides=(1, 1), padding='same')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)  
        
                    x = Conv2D(128, (1, 1), strides=(1, 1), padding='valid')(x)
                    shortcut = Conv2D(128, (1, 1), strides=(2, 2), padding='valid')(shortcut)
                    x = BatchNormalization()(x)
                    shortcut = BatchNormalization()(shortcut)            
        
                    x = Add()([x, shortcut])    
                    x = Activation('relu')(x)    
        
                    shortcut = x              
                
                else:
                    x = Conv2D(32, (1, 1), strides=(1, 1), padding='valid')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
                    
                    x = Conv2D(32, (3, 3), strides=(1, 1), padding='same')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
        
                    x = Conv2D(128, (1, 1), strides=(1, 1), padding='valid')(x)
                    x = BatchNormalization()(x)            
        
                    x = Add()([x, shortcut])     
                    x = Activation('relu')(x)
        
                    shortcut = x      
                    
            return x
        
        
        
        def conv4_layer(x):
            shortcut = x        
        
            for i in range(2):     
                if(i == 0):            
                    x = Conv2D(64, (1, 1), strides=(2, 2), padding='valid')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)        
                    
                    x = Conv2D(64, (3, 3), strides=(1, 1), padding='same')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)  
        
                    x = Conv2D(256, (1, 1), strides=(1, 1), padding='valid')(x)
                    shortcut = Conv2D(256, (1, 1), strides=(2, 2), padding='valid')(shortcut)
                    x = BatchNormalization()(x)
                    shortcut = BatchNormalization()(shortcut)
        
                    x = Add()([x, shortcut]) 
                    x = Activation('relu')(x)
        
                    shortcut = x               
                
                else:
                    x = Conv2D(64, (1, 1), strides=(1, 1), padding='valid')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
                    
                    x = Conv2D(64, (3, 3), strides=(1, 1), padding='same')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
        
                    x = Conv2D(256, (1, 1), strides=(1, 1), padding='valid')(x)
                    x = BatchNormalization()(x)            
        
                    x = Add()([x, shortcut])    
                    x = Activation('relu')(x)
        
                    shortcut = x      
        
            return x
        

        
        def conv5_layer(x):
            shortcut = x    
        
            for i in range(2):     
                if(i == 0):            
                    x = Conv2D(128, (1, 1), strides=(2, 2), padding='valid')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)        
                    
                    x = Conv2D(128, (3, 3), strides=(1, 1), padding='same')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)  
        
                    x = Conv2D(512, (1, 1), strides=(1, 1), padding='valid')(x)
                    shortcut = Conv2D(512, (1, 1), strides=(2, 2), padding='valid')(shortcut)
                    x = BatchNormalization()(x)
                    shortcut = BatchNormalization()(shortcut)            
        
                    x = Add()([x, shortcut])  
                    x = Activation('relu')(x)      
        
                    shortcut = x               
                
                else:
                    x = Conv2D(128, (1, 1), strides=(1, 1), padding='valid')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
                    
                    x = Conv2D(128, (3, 3), strides=(1, 1), padding='same')(x)
                    x = BatchNormalization()(x)
                    x = Activation('relu')(x)
        
                    x = Conv2D(512, (1, 1), strides=(1, 1), padding='valid')(x)
                    x = BatchNormalization()(x)           
                    
                    x = Add()([x, shortcut]) # 중간 가중치가 엮여서 나온다.
                    x = Activation('relu')(x)       
        
                    shortcut = x                  
        
            return x
        
        
        
        x = conv1_layer(input_tensor)
        x = conv2_layer(x)
        x = conv3_layer(x)
        x = conv4_layer(x)
        x = conv5_layer(x)
        
        
        x = GlobalAveragePooling2D()(x)
        # x = Activation('softmax')(x)
        # x = MaxPooling2D(pool_size=(2,2)) (x)
        x = Dropout(0.5) (x)
        x = Flatten() (x)

        x = Dense(128, activation= 'relu') (x)
        x = BatchNormalization() (x)
        x = Dense(64, activation= 'relu') (x)
        x = BatchNormalization() (x)
        x = Dropout(0.2) (x)

        output_tensor = Dense(10, activation='softmax')(x)
        
        model = Model(input_tensor, output_tensor)

        model.summary()

        model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(lr=1e-5,epsilon=None), metrics=['accuracy'])
        model_path = '../data/modelcheckpoint/Pproject0.hdf5'
        checkpoint = ModelCheckpoint(filepath=model_path , monitor='val_loss', verbose=1, save_best_only=True)
        early_stopping = EarlyStopping(monitor='val_loss', patience=150)
        # lr = ReduceLROnPlateau(patience=30, factor=0.5,verbose=1)

        learning_history = model.fit_generator(train_generator,
        epochs=3, validation_data=valid_generator, callbacks=[early_stopping,checkpoint])
        # acc = model.evaluate(valid_generator)
        # print(acc) # [2.324734926223755, 0.10474430024623871]  