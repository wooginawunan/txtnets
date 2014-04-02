__author__ = 'mdenil'

import numpy as np
import pyprind

from cpu import model


def load_testing_model(file_name):
    model_data = scipy.io.loadmat(file_name)

    CR_E = np.ascontiguousarray(np.transpose(model_data['CR_E']))
    # I want to convolve along rows because that makes sense for C-ordered arrays
    # the matlab code also convolves along rows, so I need to not transpose the convolution filters
    CR_1 = np.ascontiguousarray(model_data['CR_1'])
    CR_1_b = np.ascontiguousarray(np.transpose(model_data['CR_1_b']))
    CR_Z = np.ascontiguousarray(model_data['CR_Z'])

    embedding = model.embedding.WordEmbedding(
        dimension=CR_E.shape[1],
        vocabulary_size=CR_E.shape[0])
    assert CR_E.shape == embedding.E.shape
    embedding.E = CR_E

    conv = model.transfer.SentenceConvolution(
        n_feature_maps=5,
        #kernel_width=2,
        kernel_width=6,
        n_input_dimensions=42)
    assert conv.W.shape == CR_1.shape
    conv.W = CR_1

    bias_tanh = model.transfer.Bias(
        n_input_dims=21,
        n_feature_maps=5)
    bias_tanh.b = CR_1_b.reshape(bias_tanh.b.shape)

    softmax = model.transfer.Softmax(
        n_classes=6,
        n_input_dimensions=420)
    softmax.W = CR_Z[:,:-1]
    softmax.b = CR_Z[:,-1].reshape((-1,1))

    csm = model.model.CSM(
        input_axes=['b', 'w'],
        layers=[
            embedding,
            conv,
            model.pooling.SumFolding(),
            model.pooling.KMaxPooling(k=4),
            #model.pooling.KMaxPooling(k=7),
            bias_tanh,
            model.nonlinearity.Tanh(),
            softmax,
            ],
        )

    return csm


if __name__ == "__main__":
    import scipy.io

    data_file_name = "verify_forward_pass/data/SENT_vec_1_emb_ind_bin.mat"
    data = scipy.io.loadmat(data_file_name)

    embedding_dim = 42
    batch_size = 40
    vocabulary_size = int(data['size_vocab'])
    max_epochs = 1

    train = data['train'] - 1
    train_sentence_lengths = data['train_lbl'][:,1]

    max_sentence_length = data['train'].shape[1]

    csm = load_testing_model("cnn-sm-gpu-kmax/DEBUGGING_MODEL.mat")

    n_batches_per_epoch = int(data['train'].shape[0] / batch_size)

    # matlab_results = scipy.io.loadmat("cnn-sm-gpu-kmax/BATCH_RESULTS_ONE_PASS_ONE_LAYER_CHECK.mat")['batch_results']
    # matlab_results = scipy.io.loadmat("verify_forward_pass/data/batch_results_first_layer.mat")['batch_results']

    progress_bar = pyprind.ProgPercent(n_batches_per_epoch)

    total_errs = 0

    for batch_index in xrange(n_batches_per_epoch):

        if batch_index == 3:
            pass

        minibatch = train[batch_index*batch_size:(batch_index+1)*batch_size]

        meta = {'lengths': train_sentence_lengths[batch_index*batch_size:(batch_index+1)*batch_size]}

        # s1 = csm.fprop(minibatch, num_layers=1, meta=meta)
        # s2 = csm.fprop(minibatch, num_layers=2, meta=meta)
        # s3 = csm.fprop(minibatch, num_layers=3, meta=meta)
        # s4 = csm.fprop(minibatch, num_layers=4, meta=meta)
        # s5 = csm.fprop(minibatch, num_layers=5, meta=meta)
        # s6 = csm.fprop(minibatch, num_layers=6, meta=meta)
        # assert np.allclose(s6, csm.fprop(minibatch, meta=meta))

        out = csm.fprop(minibatch, meta)

        print out.shape

        # if not np.allclose(out, matlab_results[batch_index]):
        #     n_new_errs = np.sum(np.abs(out - matlab_results[batch_index]) > 1e-2)
        #     total_errs += n_new_errs
        #     print "\nFailed batch {}. Max abs err={}.  There are {} errors larger than 1e-2.".format(
        #         batch_index,
        #         np.max(np.abs(out - matlab_results[batch_index])),
        #         n_new_errs)

        progress_bar.update()

    print "Total errs > 1e-2: {} ({}%)".format(total_errs, float(total_errs) / batlab_results.size * 100.0)