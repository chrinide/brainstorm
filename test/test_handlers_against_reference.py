#!/usr/bin/env python
# coding=utf-8

from __future__ import division, print_function, unicode_literals
import itertools
import numpy as np
from brainstorm.handlers import NumpyHandler, PyCudaHandler

# np.random.seed(1234)
ref_dtype = np.float32
ref = NumpyHandler(np.float32)
handler = PyCudaHandler()
some_2d_shapes = ((1, 1), (4, 1), (1, 4), (5, 5), (3, 4), (4, 3))
some_nd_shapes = ((1, 1, 4), (1, 1, 3, 3), (3, 4, 2, 1))


def operation_check(ref_op, op, ref_args, args, ignored_args=[]):
    print("--" * 80)
    ref_op(*ref_args)
    op(*args)
    check = True
    for i, (ref_arg, arg) in enumerate(zip(ref_args, args)):
        if i in ignored_args:
            continue
        if type(ref_arg) is ref.array_type:
            arg_ref = handler.get_numpy_copy(arg)
            check = np.allclose(ref_arg, arg_ref)
            if not check:
                print("\nReference (expected) array:\n", ref_arg)
                print("\nObtained array:\n", arg_ref)
        else:
            check = (ref_arg == arg)
            if not check:
                print("\nReference (expected) array:\n", ref_arg)
                print("\nObtained array:\n", arg)
    return check


def get_args_from_ref_args(ref_args):
    args = []
    for ref_arg in ref_args:
        if type(ref_arg) is ref.array_type:
            temp = handler.create_from_numpy(ref_arg)
            args.append(temp)
        else:
            args.append(ref_arg)
    return args


def get_random_arrays(shapes=some_2d_shapes, dtype=ref_dtype):
    arrays = []
    for shape in shapes:
        arrays.append(np.random.randn(*shape).astype(dtype))
    return arrays


def test_sum_t():
    list_a = get_random_arrays()
    list_axis = [0, 1, None]
    for a, axis in itertools.product(list_a, list_axis):
        if axis == 0:
            out = np.zeros((1, a.shape[1]), dtype=ref_dtype)
        elif axis == 1:
            out = np.zeros((a.shape[0]), dtype=ref_dtype)
        else:
            out = np.array([0.], dtype=ref_dtype).reshape(tuple())
        ref_args = (a, axis, out)

        assert operation_check(ref.sum_t, handler.sum_t, ref_args,
                               get_args_from_ref_args(ref_args))


def test_dot_mm():
    list_a = get_random_arrays()
    list_b = get_random_arrays()
    list_b = [b.T.copy() for b in list_b]

    for a, b in zip(list_a, list_b):
        out = np.zeros((a.shape[0], a.shape[0]), dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.dot_mm, handler.dot_mm, ref_args,
                               get_args_from_ref_args(ref_args))


def test_dot_add_mm():
    list_a = get_random_arrays()
    list_b = get_random_arrays()
    list_b = [b.T.copy() for b in list_b]

    for a, b in zip(list_a, list_b):
        out = np.random.randn(a.shape[0], a.shape[0]).astype(np.float32)
        ref_args = (a, b, out)

        assert operation_check(ref.dot_add_mm, handler.dot_add_mm, ref_args,
                               get_args_from_ref_args(ref_args))


def test_mult_tt():
    list_a = get_random_arrays(some_2d_shapes + some_nd_shapes)
    list_b = get_random_arrays(some_2d_shapes + some_nd_shapes)

    for a, b in zip(list_a, list_b):
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.mult_tt, handler.mult_tt, ref_args,
                               get_args_from_ref_args(ref_args))


def test_mult_add_tt():
    list_a = get_random_arrays(some_2d_shapes + some_nd_shapes)
    list_b = get_random_arrays(some_2d_shapes + some_nd_shapes)

    for a, b in zip(list_a, list_b):
        out = np.random.randn(*a.shape).astype(np.float32)
        ref_args = (a, b, out)

        assert operation_check(ref.mult_add_tt, handler.mult_add_tt, ref_args,
                               get_args_from_ref_args(ref_args))


def test_mult_st():
    list_a = [0, 0.5, -1]
    list_b = get_random_arrays(some_2d_shapes + some_nd_shapes)

    for a, b in zip(list_a, list_b):
        out = np.zeros_like(b, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.mult_st, handler.mult_st, ref_args,
                               get_args_from_ref_args(ref_args))


def test_add_tt():
    list_a = get_random_arrays(some_2d_shapes + some_nd_shapes)
    list_b = get_random_arrays(some_2d_shapes + some_nd_shapes)

    for a, b in zip(list_a, list_b):
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.add_tt, handler.add_tt, ref_args,
                               get_args_from_ref_args(ref_args))


def test_add_st():
    list_a = [0, 0.5, -1]
    list_b = get_random_arrays(some_2d_shapes + some_nd_shapes)

    for a, b in zip(list_a, list_b):
        out = np.zeros_like(b, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.add_st, handler.add_st, ref_args,
                               get_args_from_ref_args(ref_args))


def test_subtract_tt():
    list_a = get_random_arrays(some_2d_shapes + some_nd_shapes)
    list_b = get_random_arrays(some_2d_shapes + some_nd_shapes)

    for a, b in zip(list_a, list_b):
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.subtract_tt, handler.subtract_tt, ref_args,
                               get_args_from_ref_args(ref_args))


def test_add_mv():
    # Only checking with row vectors
    list_a = get_random_arrays()
    list_b = get_random_arrays()
    list_b = [b[0, :].reshape((1, -1)).copy() for b in list_b]

    for a, b in zip(list_a, list_b):
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.add_mv, handler.add_mv, ref_args,
                               get_args_from_ref_args(ref_args))


def test_broadcast_features_t():
    shapes_to_check = [[1, 1, 1], [1, 2, 1], [3, 2, 1], [4, 1, 1]]

    list_a = get_random_arrays(shapes_to_check)
    shapes_to_add = [(1,), (2, 2), (3, 1, 1)]

    for a, shape_to_add in itertools.product(list_a, shapes_to_add):
        out = np.zeros(a.shape + shape_to_add, dtype=ref_dtype)
        ref_args = (a, out)

        assert operation_check(ref.broadcast_features_t,
                               handler.broadcast_features_t, ref_args,
                               get_args_from_ref_args(ref_args))


def test_clip_t():
    list_a = get_random_arrays(some_nd_shapes)
    list_clip_min = [-0.4, 0, 0.2]
    list_clip_max = [-0.1, 0, 0.3]

    for a, clip_min, clip_max in itertools.product(list_a, list_clip_min,
                                                   list_clip_max):
        if clip_max >= clip_min:
            out = np.zeros_like(a, dtype=ref_dtype)
            ref_args = (a, clip_min, clip_max, out)
            assert operation_check(ref.clip_t, handler.clip_t, ref_args,
                                   get_args_from_ref_args(ref_args))


def test_log_t():
    list_a = get_random_arrays(some_nd_shapes)

    for a in list_a:
        a += 10  # to remove negatives
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, out)
        assert operation_check(ref.log_t, handler.log_t, ref_args,
                               get_args_from_ref_args(ref_args))


def test_divide_tt():
    list_a = get_random_arrays(some_2d_shapes + some_nd_shapes)
    list_b = get_random_arrays(some_2d_shapes + some_nd_shapes)

    for a, b in zip(list_a, list_b):
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.divide_tt, handler.divide_tt, ref_args,
                               get_args_from_ref_args(ref_args))


def test_divide_mv():
    # Only checking with row vectors
    list_a = get_random_arrays()
    list_b = get_random_arrays()
    list_b = [b[0, :].reshape((1, -1)).copy() for b in list_b]

    for a, b in zip(list_a, list_b):
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.divide_mv, handler.divide_mv, ref_args,
                               get_args_from_ref_args(ref_args))


def test_mult_mv():
    list_a = get_random_arrays()
    list_b = get_random_arrays()
    list_b = [b[0, :].reshape((1, -1)).copy() for b in list_b]

    print("======================================")
    print("Testing mult_mv() for with row vectors")
    print("======================================")
    for a, b in zip(list_a, list_b):
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.mult_mv, handler.mult_mv, ref_args,
                               get_args_from_ref_args(ref_args))

    print("======================================")
    print("Testing mult_mv() for with column vectors")
    print("======================================")
    list_b = get_random_arrays()
    list_b = [b[:, 0].reshape((-1, 1)).copy() for b in list_b]
    for a, b in zip(list_a, list_b):
        print('-'*40)
        print("a:\n", a)
        print("b:\n", b)
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, b, out)

        assert operation_check(ref.mult_mv, handler.mult_mv, ref_args,
                               get_args_from_ref_args(ref_args))


def test_binarize_v(): # TODO
    pass


def test_index_m_by_v(): # TODO
    pass


def test_sigmoid():
    list_a = get_random_arrays(some_nd_shapes)

    for a in list_a:
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, out)
        assert operation_check(ref.sigmoid, handler.sigmoid, ref_args,
                               get_args_from_ref_args(ref_args))


def test_sigmoid_deriv():
    list_x = get_random_arrays(some_nd_shapes)
    list_y = get_random_arrays(some_nd_shapes)
    list_dy = get_random_arrays(some_nd_shapes)

    for x, y, dy in zip(list_x, list_y, list_dy):
        dx = np.zeros_like(x, dtype=ref_dtype)
        ref_args = (x, y, dy, dx)
        assert operation_check(ref.sigmoid_deriv, handler.sigmoid_deriv,
                               ref_args, get_args_from_ref_args(ref_args))


def test_tanh():
    list_a = get_random_arrays(some_nd_shapes)

    for a in list_a:
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, out)
        assert operation_check(ref.tanh, handler.tanh, ref_args,
                               get_args_from_ref_args(ref_args))


def test_tanh_deriv():
    list_x = get_random_arrays(some_nd_shapes)
    list_y = get_random_arrays(some_nd_shapes)
    list_dy = get_random_arrays(some_nd_shapes)

    for x, y, dy in zip(list_x, list_y, list_dy):
        dx = np.zeros_like(x, dtype=ref_dtype)
        ref_args = (x, y, dy, dx)
        assert operation_check(ref.tanh_deriv, handler.tanh_deriv,
                               ref_args, get_args_from_ref_args(ref_args))


def test_rel():
    list_a = get_random_arrays(some_nd_shapes)

    for a in list_a:
        out = np.zeros_like(a, dtype=ref_dtype)
        ref_args = (a, out)
        assert operation_check(ref.rel, handler.rel, ref_args,
                               get_args_from_ref_args(ref_args))


def test_rel_deriv():
    list_x = get_random_arrays(some_nd_shapes)
    list_y = get_random_arrays(some_nd_shapes)
    list_dy = get_random_arrays(some_nd_shapes)

    for x, y, dy in zip(list_x, list_y, list_dy):
        dx = np.zeros_like(x, dtype=ref_dtype)
        ref_args = (x, y, dy, dx)
        assert operation_check(ref.rel_deriv, handler.rel_deriv,
                               ref_args, get_args_from_ref_args(ref_args))


def test_conv2d_forward():
    img_shapes = [(1, 1, 3, 3), (10, 3, 32, 32), (10, 10, 6, 4), (1, 2, 3, 4)]
    w_shapes = [(1, 1, 1), (3, 3, 3), (6, 4, 5), (2, 5, 3)]

    list_x = get_random_arrays(img_shapes)
    stride = (1, 1)
    pad = 1

    for ws in w_shapes:
        for x in list_x:
            w_shape = (ws[0], x.shape[1], ws[1], ws[2])
            w = np.random.uniform(size=w_shape).astype(ref_dtype)
            b = np.random.uniform(size=(w.shape[0],)).astype(ref_dtype)
            oh = (x.shape[2] + 2 * pad - w.shape[2]) / stride[0] + 1
            ow = (x.shape[3] + 2 * pad - w.shape[3]) / stride[1] + 1
            out = np.zeros((x.shape[0], w.shape[0])+ (oh, ow), dtype=ref_dtype)
            ref_args = (x, w, b, out, pad, stride)
            assert operation_check(ref.conv2d_forward_batch,
                                   handler.conv2d_forward_batch,
                                   ref_args, get_args_from_ref_args(ref_args))


def test_conv2d_backward():
    img_shapes = [(1, 1, 3, 3), (10, 3, 32, 32), (10, 10, 6, 4), (1, 2, 3, 4)]
    w_shapes = [(3, 3, 3), (6, 4, 5), (2, 5, 3)]

    list_x = get_random_arrays(img_shapes)
    stride = (1, 1)
    pad = 1

    for ws in w_shapes:
        for x in list_x:
            w_shape = (ws[0], x.shape[1], ws[1], ws[2])
            w = np.random.uniform(size=w_shape).astype(ref_dtype)
            b = np.random.uniform(size=(w.shape[0],)).astype(ref_dtype)
            oh = (x.shape[2] + 2 * pad - w.shape[2]) / stride[0] + 1
            ow = (x.shape[3] + 2 * pad - w.shape[3]) / stride[1] + 1
            out_shape = (x.shape[0], w.shape[0])+ (oh, ow)
            o_deltas = np.random.uniform(size=out_shape).astype(ref_dtype)
            i_deltas = np.zeros_like(x, dtype=ref_dtype)
            w_deltas = np.zeros_like(w, dtype=ref_dtype)
            b_deltas = np.zeros_like(b, dtype=ref_dtype)

            ref_args = (x, w, pad, stride, i_deltas,
                        o_deltas, w_deltas, b_deltas)
            assert operation_check(ref.conv2d_backward_batch,
                                   handler.conv2d_backward_batch,
                                   ref_args, get_args_from_ref_args(ref_args))


def test_pool2d_forward():
    img_shapes = [(1, 1, 5, 5), (10, 3, 32, 32), (10, 10, 6, 4), (1, 2, 6, 9)]
    window_list= [(2, 2), (3, 3), (4, 4), (2, 1), (1, 2)]
    strides_list = [(1, 1), (2, 2), (1, 2), (2, 1)]
    list_x = get_random_arrays(img_shapes)

    for x in list_x:
        for pad in (0, 1, 2):
            for strides in strides_list:
                for window in window_list:
                    out_shape = (x.shape[0], x.shape[1],
                        (x.shape[2] + 2*pad - window[0]) // strides[0] + 1,
                        (x.shape[3] + 2*pad - window[1]) // strides[1] + 1)
                    outputs = np.zeros(out_shape, dtype=ref_dtype)
                    argmax = np.zeros(out_shape + (2, ), dtype=np.int32)
                    ref_args = (x, window, outputs, pad, strides, argmax)

                    assert operation_check(ref.pool2d_forward_batch,
                                    handler.pool2d_forward_batch,
                                    ref_args, get_args_from_ref_args(ref_args),
                                    ignored_args=[5])


def test_pool2d_backward():
    img_shapes = [(1, 1, 5, 5), (10, 3, 32, 32), (10, 10, 6, 4), (1, 2, 6, 9)]
    window_list= [(2, 2), (3, 3), (4, 4), (2, 1), (1, 2)]
    strides_list = [(1, 1), (2, 2), (1, 2), (2, 1)]
    list_x = get_random_arrays(img_shapes)

    for x in list_x:
        for pad in (0, 1, 2):
            for strides in strides_list:
                for window in window_list:
                    out_shape = (x.shape[0], x.shape[1],
                        (x.shape[2] + 2*pad - window[0]) // strides[0] + 1,
                        (x.shape[3] + 2*pad - window[1]) // strides[1] + 1)
                    outputs = np.zeros(out_shape, dtype=ref_dtype)
                    o_deltas = np.random.normal(size=out_shape)
                    o_deltas = o_deltas.astype(ref_dtype)
                    i_deltas = np.zeros_like(x, dtype=ref_dtype)
                    argmax = np.zeros(out_shape + (2, ), dtype=np.int32)

                    # initialize argmax
                    ref.pool2d_forward_batch(x, window, outputs, pad,
                                             strides, argmax)
                    ref_args = (x, window, outputs, pad, strides, argmax,
                                i_deltas, o_deltas)

                    assert operation_check(ref.pool2d_backward_batch,
                                    handler.pool2d_backward_batch,
                                    ref_args, get_args_from_ref_args(ref_args),
                                    ignored_args=[5])
