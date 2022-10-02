from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import Callback
from keras.layers import LSTM



class CLSTM() :
    model = None
    x_data = None
    y_data = None
    history = None

    plot_loss = None
    plot_acc = None

    epch_loss = []
    valu_loss = []

    class CustomCallback(Callback) :
        fig_loss = None
        fig_acc = None

        epch_indx = []
        epch_loss = []
        epch_acc = []

        def __init__(self, fig_loss, fig_acc) :
            self.fig_loss = fig_loss
            self.fig_acc = fig_acc

        def on_epoch_end(self, epoch, logs=None):
            self.epch_indx.append(epoch)
            self.epch_loss.append(logs["loss"])
            self.epch_acc.append(logs["accuracy"])

            if(epoch % 10 == 0) :
                #self.fig_loss.subplots().set_xlabel('epoch', fontsize=10)
                #self.fig_loss.subplots().set_ylabel('loss', fontsize=10)
                self.fig_loss.subplots().plot(self.epch_indx, self.epch_loss)
                
                self.fig_loss.canvas.draw()
                self.fig_loss.clf()

                
                #self.fig_acc.subplots().set_xlabel('epoch', fontsize=10)
                #self.fig_acc.subplots().set_ylabel('accuracy', fontsize=10)
                self.fig_acc.subplots().plot(self.epch_indx, self.epch_acc)
                
                self.fig_acc.canvas.draw()
                self.fig_acc.clf()


    def __init__(self, x_data, y_data, fig_loss, fig_acc) :
        self.x_data = x_data
        self.y_data = y_data

        self.fig_loss = fig_loss
        self.fig_acc = fig_acc

        #self.plot_loss.plot([1, 2], [2, 3])

        self.model = Sequential()
        self.model.add(LSTM(100, activation='tanh', return_sequences=True, input_shape=(1, 2)))
        self.model.add(LSTM(49, activation='tanh'))
        self.model.add(Dense(1, activation='sigmoid'))


    def train(self) :
        self.model.compile(loss='binary_crossentropy', optimizer='rmsprop',metrics=['accuracy'])
        self.history = self.model.fit(self.x_data, self.y_data, epochs=1000, batch_size = len(self.x_data), callbacks=[CLSTM.CustomCallback(self.fig_loss, self.fig_acc)])

    def predict(self, x_test_data) :
        return self.model.predict(x_test_data)


    def getAccuracy(self) :
        return self.history.history['accuracy']

    def getLoss(self) :
        return self.history.history['loss']