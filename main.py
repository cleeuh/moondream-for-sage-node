import moondreamzz as md
from PIL import Image, ImageDraw
from waggle.plugin import Plugin
from waggle.data.vision import Camera
import numpy as np
from term_img import *
import argparse
import time


def resize_image(image, target_size=640):
    aspect_ratio = image.width / image.height

    if image.width > image.height:
        new_width = target_size
        new_height = int(target_size / aspect_ratio)
    else:
        new_height = target_size
        new_width = int(target_size * aspect_ratio)

    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image


def draw_points_on_image(image, points):
    draw = ImageDraw.Draw(image)

    for point in points:
        x = int(point['x'] * image.width)
        y = int(point['y'] * image.height)
        radius = 3
        bbox = [(x - radius, y - radius), (x + radius, y + radius)]
        draw.ellipse(bbox, fill='blue')

    return image


def draw_bounding_boxes_on_image(image, boxes):
    draw = ImageDraw.Draw(image)

    for box in boxes:
        x_min = int(box['x_min'] * image.width)
        y_min = int(box['y_min'] * image.height)
        x_max = int(box['x_max'] * image.width)
        y_max = int(box['y_max'] * image.height)
        draw.rectangle([x_min, y_min, x_max, y_max], outline="purple", width=2)

    return image



def run(args):    
    print("loading model")
    model_int = "int4" if args.int4 else "int8"
    model_size = "0.5b" if args.small else "2b"
    model = md.vl(model=f"./moondream-{model_size}-{model_int}.mf", load_on_use=args.dynamic_loading)

    with Plugin() as plugin, Camera(args.stream) as camera:
        while True:
            snapshot = camera.snapshot()
            image = Image.fromarray(np.array(snapshot.data), 'RGB')
            print_img(image)
            print("image encode")
            encoded_image = model.encode_image(image)
            image = resize_image(image)

            print("Inferencing")
            if args.caption:
                print("Caption")
                caption = model.caption(encoded_image)["caption"]
                print("Caption:", caption)
                plugin.publish("caption", caption, timestamp=snapshot.timestamp)

            responses = []
            for query in args.query:
                answer = model.query(encoded_image, query)["answer"]
                responses.append({"query": query, "response": answer})
                print("Answer:", answer)
            if len(responses) != 0:
                plugin.publish("query", str(responses), timestamp=snapshot.timestamp)

            if args.small:
                for query in args.detect:
                    print("0.5b Models do not support bounding box detection")
                for query in args.point:
                    print("0.5b Models do not support point detection")
            else:
                responses = []
                for query in args.detect:
                    objects = model.detect(encoded_image, query)["objects"]
                    responses.append({"query": query, "objects": objects})
                    print("Objects:", objects)
                    draw_bounding_boxes_on_image(image, objects)
                if len(responses) != 0:
                    plugin.publish("objects", str(responses), timestamp=snapshot.timestamp)

                responses = []
                for query in args.point:
                    points = model.point(encoded_image, query)["points"]
                    responses.append({"query": query, "points": points})
                    print("Points:", points)
                    draw_points_on_image(image, points)
                if len(responses) != 0:
                    plugin.publish("points", str(responses), timestamp=snapshot.timestamp)


            image.save('./snapshot.jpg')
            plugin.upload_file("./snapshot.jpg", timestamp=snapshot.timestamp)

            if not args.continuous:
                time.sleep(30)
                break

            # Have to dump the model manually to clear the ram for new inference.  Model loads quickly
            # so performance wise, its admissible
            # del model
            del encoded_image
            del image

def parse_args():
    parser = argparse.ArgumentParser(description='Moondream 2B int8 Onnx Runtime')
    # parser.add_argument('--model', type=str, default='moondream-2b-int8.mf', help='model path')
    parser.add_argument('--stream', type=str, default="bottom_camera", help='ID or name of a stream, e.g. bottom_camera, top_camera, left_camera')
    parser.add_argument('--continuous', action='store_true', default=False, help='Flag to run this plugin forever')
    # parser.add_argument('-sleep', type=int, default=-1, help='Sleep time after inferencing')
    parser.add_argument('--caption', action='store_true', default=False, help='Generate a caption from the model')
    parser.add_argument('--dynamic-loading', action='store_true', default=False, help='Load and unload parts of the model as needed')
    parser.add_argument('--small', action='store_true', default=False, help='Load the 0.5b model instead of 2b')
    parser.add_argument('--int4', action='store_true', default=False, help='Use quantized int4 instead of int8')
    parser.add_argument(
        '--query',
        action='append',
        default=[],
        help='Prompt the model and get a response'
    )
    parser.add_argument(
        '--detect',
        action='append',
        default=[],
        help='Bounding boxes for the image from a prompt'
    )
    parser.add_argument(
        '--point',
        action='append',
        default=[],
        help='Get X,Y location for the image from the prompt'
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    run(args)
    # model = md.vl(model="./moondream-0_5b-int4.mf")

    # print(model.point(encoded_image))
    # args.stream
    
