import argparse
import os
import cv2
import tqdm

global_frame_count = 1

def get_single_frame(cap, frame_num):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    success, frame = cap.read()
    return frame


def save_frame(frame, path, w, h):
    frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_LINEAR)
    cv2.imwrite(path, frame)


def extract_frames(videofile, save_dir, fps, w, h, ext, args):
    global global_frame_count
    if not os.path.exists(save_dir):  # Create folder to save frames
        os.makedirs(save_dir)
    # Get name of the file without extention ex: /home/gohil/running.MOV -> running
    basename = os.path.splitext(os.path.basename(videofile))[0]
    print("BASENAME : ", basename)
    cap = cv2.VideoCapture(videofile)  # capture video frame
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    orig_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    orig_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cap_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    fps_count = 0

    # Set H and W
    if h == 0 and w == 0:  # use original hw
        h = int(orig_h)
        w = int(orig_w)
    elif h == 0 or w == 0:  # custom hw
        # keep aspect ratio
        if h == 0:
            if w > orig_w:
                raise ValueError(
                    "Custom W {} should not be greater than original W {}".format(
                        w, orig_w
                    )
                )
            h = int(w * orig_h / orig_w)
        else:
            if h > orig_h:
                raise ValueError(
                    "Custom H {} should not be greater than original H {}".format(
                        h, orig_h
                    )
                )
            w = int(h * orig_w / orig_h)

    if fps > cap_fps:
        raise ValueError(
            "Custom fps {} should not be greater than original fps {}".format(
                fps, cap_fps
            )
        )
    elif fps < 0:  # -ve fps
        raise ValueError("fps {} should not be negative".format(fps))
    elif fps == 0:  # 0 fps
        fps = cap_fps
    save_step = int(cap_fps / fps)  # save at every "save_step" frame count

    print(
        "h: {},w: {}, total frames: {}, orig_h: {},orig_w: {}, original fps: {}, target fps: {}".format(
            h, w, total_frames, orig_h, orig_w, cap_fps, fps
        )
    )
    print("save directory: {}".format(save_dir))
    # extract only single frame
    if args.single_frame:
        print("Saving single frame only")
        if args.frame_index < total_frames:
            frame = get_single_frame(cap, args.frame_index)
            p = os.path.join(save_dir, basename)
            p = p + "img_{:05}".format(global_frame_count) + "." + ext
            save_frame(frame, p, w, h)
            # global_frame_count += 1
            return
        else:
            raise ValueError(
                "frame_index {} should not be more than or equal total frames {}".format(
                    args.frame_index, total_frames
                )
            )
    pbar = tqdm.tqdm(
        total=int(total_frames / save_step),
        desc="extracting frames at fps: {}".format(fps),
    )
    # read all frames
    while cap.isOpened():
        success, frame = cap.read()
        frame_count += 1
        fps_count += 1
        if not success:
            print("Failed to read video")
            return
        # save frame
        if fps_count % save_step == 0:
            # p = os.path.join(save_dir, basename)
            # p = p + "_{:05}".format(frame_count) + "." + ext
            p = save_dir + "img_{:05}".format(global_frame_count) + "." + ext
            global_frame_count += 1
            save_frame(frame, p, w, h)
            fps_count = 0
            pbar.update(1)
    pbar.close()
    cap.release()  # Release the video capture object


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path", type=str, required=True, help="Path of video file or video directory"
    )
    parser.add_argument(
        "--save_path",
        type=str,
        default="frames",
        help="Path of video file or video directory",
    )
    parser.add_argument(
        "--img_ext",
        type=str,
        default="png",
        help="Save images with png or jpg or other extention",
    )
    parser.add_argument("--H", type=int, default=0, help="Height of images to save")
    parser.add_argument("--W", type=int, default=0, help="Width of images to save")
    parser.add_argument(
        "--fps", type=float, default=0, help="Frame per second to capture in video"
    )
    parser.add_argument(
        "--ext",
        nargs="+",
        default=[".MP4", ".MOV", ".AVI", ".WMV", "mp4"],
        help="list of video file extention that should be converted into images",
    )
    parser.add_argument(
        "--single_frame", action="store_true", help="Generate grayscale images"
    )
    parser.add_argument(
        "--frame_index", type=int, default=0, help="frame number to extract"
    )
    args = parser.parse_args()
    print(args)

    if os.path.isfile(args.path):
        # Process single video isfile
        print("Processing single video file")
        basepath = os.path.dirname(
            args.path
        )  # get absolute path of file directory ex: /home/gohil/
        print("Creating images for: {}".format(args.path))
        filename = args.path.split("/")[-1].split(".")[0]
        os.mkdir(os.path.join(args.save_path, filename))
        args.save_path = args.save_path + filename + "/"
        print("Saving path : ",args.save_path)
        
        extract_frames(
            args.path, args.save_path, args.fps, args.W, args.H, args.img_ext, args
        )
    elif os.path.isdir(args.path):  # process all videos in directory
        print("Processing multiple video files")
        for (dirpath, dirnames, filenames) in os.walk(args.path):
            for (
                filename
            ) in (
                filenames
            ):  # Ex: filename: imgsim0.xml dirpath: label/ dirnames:['New folder']
                # if args.ext in filename:
                if any(
                    map(filename.__contains__, args.ext)
                ):  # Check if video file name contains any of extention from the list
                    videofile = os.path.abspath(os.path.join(dirpath, filename))
                    print("Creating images for: {}".format(videofile))
                    extract_frames(
                        videofile,
                        args.save_path,
                        args.fps,
                        args.W,
                        args.H,
                        args.img_ext,
                        args,
                    )
    else:
        print("Invalid path!!! Please check your --path value")
