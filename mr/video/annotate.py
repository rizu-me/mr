import cv2
import numpy as np
import pandas as pd
import warnings

def circle(features, frames, wait=1, high_contrast=True, write_file=None):
    """Play video, circling features in each frame.

    Parameters
    ----------
    features : DataFrame including columns 'frame', 'x', and 'y'
    frames : iterable container of image arrays, like a list of images or a 
        Video object (See mr.opencv.video.Video.)
    wait : delay between frames, default 1
    high_contrast : Rescale brightness to use full gamut. Default True.
    write_file : Save the annotated movie to a file.
    """
    RADIUS = 10
    COLOR = (0, 200, 0)
    SHIFT = 3
    centers = features.set_index('frame')[['x', 'y']]
    cv2.namedWindow("playback")
    if write_file is not None:
        try: 
            shape = frames.shape
        except AttributeError:
            raise ValueError, \
                "To use write_file, frames must be a subclass of Frames."
        warnings.warn("The write_file feature is not ready for prime time!")
        fourcc = cv2.cv.CV_FOURCC('P', 'I', 'M', '1')
        writer = cv2.VideoWriter(write_file, fourcc, 30, frames.shape)

    print "Press Ctrl+C to interrupt video."
    try:
        for i, frame in enumerate(frames): 
            try:
                frame_no = frames.cursor - 1
            except AttributeError:
                frame_no = i
            # Maximize contrast.
            if high_contrast:
                frame = 255/(frame.max() - frame.min())*(frame - frame.min())
            # Colorize frame to allow colored annotations.
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame.astype('uint8'), cv2.cv.CV_GRAY2RGB)
            try:
                these_centers = centers.loc[frame_no, ['x', 'y']]
            except KeyError:
                if write_file:
                    writer.write(frame)
                print "No features for Frame %d." % frame_no
                continue
            # This if/else statement handles the unusual case in which
            # there is only one probe in a frame.
            if isinstance(these_centers, pd.Series):
                these_centers = list([these_centers.tolist()])
            else:
                these_centers = these_centers.values
            for x, y in these_centers:
                x, y = map(lambda x: int(x*2**SHIFT), [x, y])
                cv2.circle(frame, (x, y), RADIUS*2**SHIFT, COLOR, 
                           thickness=1, lineType=cv2.cv.CV_AA, shift=SHIFT) 
            
            cv2.imshow("playback", frame)
            if write_file:
                writer.write(frame)
            cv2.waitKey(wait)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyWindow('playback')
        cv2.waitKey(1)  # a bug work-around to poke destroy
