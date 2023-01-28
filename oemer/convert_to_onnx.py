import sys
import pickle
from pathlib import Path

import tf2onnx
import numpy as np
import tensorflow as tf
import sys 
sys.path.append(".")
sys.path.append("..")
from omnizart.models.t2t import MultiHeadAttention


def convert(input_path, output_path=None):
    input_path = Path(input_path)
    #model = tf.keras.models.model_from_json(open(input_path / "arch.json").read())
    #model.load_weights(input_path / "weights.h5")
    model = tf.keras.models.load_model(input_path, custom_objects={"MultiHeadAttention": MultiHeadAttention})
    inp_shape = model.input_shape[1:]
    model(np.random.random((1,)+inp_shape))
    spec = (tf.TensorSpec(model.input_shape, tf.uint8, name="input"),)

    if output_path is None:
        output_path = input_path
    else:
        output_path = Path(output_path)
    output_model = output_path / "model.onnx"
    model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec, output_path=output_model)
    output_names = [n.name for n in model_proto.graph.output]
    pickle.dump(
        {
            'output_names': output_names,
            'input_shape': model.input_shape,
            'output_shape': model.output_shape
        },
        open(output_path / "metadata.pkl", "wb")
    )


if __name__ == "__main__":
    model_path = sys.argv[1]
    convert(model_path)
