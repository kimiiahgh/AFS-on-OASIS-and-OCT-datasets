import tensorflow as tf
input_data=tf.keras.datasets.mnist
import numpy as np
import model
from utils import BatchCreate,show_result

flags = tf.app.flags

flags = tf.app.flags

# Directories
flags.DEFINE_string('data_dir', './data/', 'Directory to store input dataset')

# Run Settings
flags.DEFINE_string('dataset_name', 'OCT', 'The name of dataset as an example')
flags.DEFINE_integer('read_index', 3, 'The index of the dataset used ')


# Model Settings
flags.DEFINE_integer('input_size', 12288, 'The dimension of input')
flags.DEFINE_integer('output_size', 4, 'The dimension of output')
flags.DEFINE_integer('E_node', 32, 'The size of hidden unit in Extract network')
flags.DEFINE_integer('A_node', 2, 'The size of hidden unit in Attention layer')
flags.DEFINE_integer('set_seed', 1, 'The default random seed')
flags.DEFINE_integer('L_node', 500, 'The size of hidden unit in learning module')
flags.DEFINE_float('moving_average_decay', 0.99, 'The average decay rate of moving')

# Training & Optimizer

flags.DEFINE_float('regularization_rate', 0.0001, 'The rate of regularization in Loss Function')
flags.DEFINE_float('learning_rate_base', 0.8, 'The base of learning rate')
flags.DEFINE_float('learning_rate_decay', 0.99, 'The decay of learning rate')
flags.DEFINE_integer('batch_size', 16, 'The size of batch for minibatch training')
flags.DEFINE_integer('train_step', 3000, 'The size of training step')

FLAGS = tf.app.flags.FLAGS

def run_train(sess, train_X, train_Y, val_X, val_Y):
    X = tf.get_collection('input')[0]
    Y = tf.get_collection('output')[0]
    #print(Y,"#@#@")
    Iterator = BatchCreate(train_X, train_Y)
    for step in range(1, FLAGS.train_step+1):
        if step % 100 == 0:
            val_loss,val_accuracy = sess.run(tf.get_collection('validate_ops'), 
                                                       feed_dict={X:val_X, Y:val_Y})
            
            print('[%4d] AFS-loss:%.12f AFS-accuracy:%.6f'%
                        (step, val_loss,val_accuracy))
        xs, ys = Iterator.next_batch(FLAGS.batch_size)
        #print(xs.shape,"@@")
        #print(ys.shape,"##")
        _, A = sess.run(tf.get_collection('train_ops'), feed_dict={X:xs, Y:ys})
    return A
def run_test(A,train_X, train_Y,test_X, test_Y,total_batch):

    attention_weight = A.mean(0)
    AFS_wight_rank = list(np.argsort(attention_weight))[::-1]
    ac_score_list = []
    index=1
    for K in range(5, 300, 10):
        use_train_x = train_X[:, AFS_wight_rank[:K]]
        use_test_x = test_X[:, AFS_wight_rank[:K]]
        accuracy = model.test(K, use_train_x, train_Y, use_test_x, test_Y,total_batch,index)
        index += 1
        print('Using Top {} features| accuracy:{:.4f}'.format(K,accuracy))

        ac_score_list.append(accuracy)
    return ac_score_list

data_file = FLAGS.data_dir + FLAGS.dataset_name + '.npz'

data = np.load(data_file)
read_index = FLAGS.read_index
train_data,train_labels,test_data,test_labels = data['train_X'],data['train_Y'],data['test_X'],data['test_Y']
"""train_X,train_Y, test_X, test_Y = train_data[read_index],train_labels[read_index],test_data[read_index],test_labels[read_index]"""
#mycode:
from numpy import array
train_X=array(train_data).reshape(192,12288)
train_Y=train_labels
test_X=array(test_data).reshape(32,12288)
test_Y=test_labels
from numpy import asarray
from sklearn.preprocessing import OneHotEncoder
# define data
dat_kim = array(train_Y).reshape(len(train_Y),1)
# define one hot encoding
encoder = OneHotEncoder(sparse=False)
# transform data
train_Y = encoder.fit_transform(dat_kim)
#
dat_kim = array(test_Y).reshape(len(test_Y),1)
# define one hot encoding
encoder = OneHotEncoder(sparse=False)
# transform data
test_Y = encoder.fit_transform(dat_kim)
#
#print(train_Y,"$$$")
# print(test_Y,"**")
##
if FLAGS.dataset_name != 'mnist':
    train_X, test_X= train_X/255, test_X/255
    val_X,val_Y = data['val_X']/255,data['val_Y']
    val_X=array(val_X).reshape(32,12288)
    #
    dat_kim = array(val_Y).reshape(len(val_Y),1)
    # define one hot encoding
    encoder = OneHotEncoder(sparse=False)
    # transform data
    val_Y = encoder.fit_transform(dat_kim)
    
    
else:
    mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)
    val_X,val_Y = mnist.validation.images, mnist.validation.labels
Train_size = len(train_X)
total_batch = Train_size / FLAGS.batch_size
model.build(total_batch)
with tf.Session() as sess:
    tf.global_variables_initializer().run()
    print('== Get feature weight by using AFS ==')
    print(train_X.shape,"@#")
    #print(train_Y,"$@")
    A = run_train(sess, train_X, train_Y, val_X, val_Y)
print('==  The Evaluation of AFS ==')
ac_score_list = run_test(A, train_X, train_Y,test_X, test_Y,total_batch)
show_result(ac_score_list,FLAGS.dataset_name)
#########

    
    
    