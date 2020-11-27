from functools import lru_cache
from pathlib import Path

from menpo.shape import PointCloud, ColouredTriMesh
from menpo.transform import Scale, Translation
from menpo3d.rasterize import (
    rasterize_barycentric_coordinate_images,
    rasterize_mesh_from_barycentric_coordinate_images,
    rasterize_shape_image_from_barycentric_coordinate_images)
from menpodetect import load_dlib_frontal_face_detector
from menpofit.aam import load_balanced_frontal_face_fitter

from .camera import perspective_camera_for_template
from .data import load_template, LANDMARK_MASK
from .io import export_landmark_visualization


@lru_cache()
def load_fitter():
    return load_balanced_frontal_face_fitter()


@lru_cache()
def load_detector():
    return load_dlib_frontal_face_detector()


def align_mesh_to_template(source, target, scale_corrective=1.2):
    scale = Scale((target.norm() / source.norm()) * scale_corrective,
                  n_dims=target.n_dims)
    translation = Translation(target.centre() - source.centre())
    return translation.compose_before(scale)


def landmark_mesh_my(mesh, img_shape=(320, 240), verbose=False):
#    print("Fist Mesh : {}, channel = {} ".format(mesh, mesh.n_channels))

    fitter = load_balanced_frontal_face_fitter()
    # seemed a face detector
    detector = load_dlib_frontal_face_detector()
    camera = perspective_camera_for_template(img_shape, 0.5)

    # Pre-process - align the mesh roughly with the template
    aligned_mesh = align_mesh_to_template(mesh, load_template()).apply(mesh)

    mesh_in_img = camera.apply(aligned_mesh)
    if (isinstance(mesh_in_img, ColouredTriMesh)):
        print("--------Landmark Step ---------")
        print("Mesh In Img Afrer Aligned = {0} \nchannel = {1} ".format(mesh_in_img, mesh_in_img.n_channels))
        print(mesh_in_img.points)
        print(mesh_in_img.colours)
        print(mesh_in_img.trilist)
    # bcs = (img1, img2) two mask image
    bcs = rasterize_barycentric_coordinate_images(mesh_in_img, img_shape)

    print("bcoords_image type = ", bcs[0].as_vector())
    print("tri_indices_image type = ", bcs[1].as_vector())
   # print("bcs = ", bcs[0].as_vector())


    # img : A rasterized image of the mesh.
    img = rasterize_mesh_from_barycentric_coordinate_images(mesh_in_img, *bcs)
    shape_img = rasterize_shape_image_from_barycentric_coordinate_images(
        mesh, *bcs)
    print("!!!!!", type(img) )

    print("Final Texture img ={0}  \nchannel = {1}".format(img, img.n_channels))
  #  print("Final Shape img = ", shape_img)

    inter_images = Path("/home/li_gang/TestFile/Inter-Imges")
    print("Export Final image to : ", "/home/li_gang/TestFile/Inter-Imges")
    export_landmark_visualization(inter_images, "texture", img)
    # 2. Find the one bounding box in the rendered image
    bboxes = detector(img)
    if len(bboxes) != 1:
        raise ValueError(
            "Expected to find one face - found {}".format(len(bboxes)))
    else:
        if verbose:
            print('Detected 1 face')
    # 3. Fit from the bounding box
    fr = fitter.fit_from_bb(img, bboxes[0])
    if verbose:
        print('AMM fitting successfully completed')
    # 4. Sample the XYZ image to build back the landmarks
    img_lms = fr.final_shape.from_mask(LANDMARK_MASK)

    # test to see if the landmark fell on the 3D surface or not
    occlusion_mask = img.mask.sample(img_lms).ravel()

    img.landmarks['__lsfm_on_surface'] = img_lms.from_mask(occlusion_mask)
    img.landmarks['__lsfm_off_surface'] = img_lms.from_mask(~occlusion_mask)
    return_dict = {
        'landmarks_2d': img_lms,
        'occlusion_mask': occlusion_mask,
        'landmarks_3d_masked': PointCloud(shape_img.sample(
            img.landmarks['__lsfm_on_surface']).T)
    }

    if (~occlusion_mask).sum() != 0:
        groups = ['dlib_0', '__lsfm_on_surface', '__lsfm_off_surface']
        marker_edge_colours = ['blue', 'yellow', 'red']
    else:
        groups = ['dlib_0', '__lsfm_on_surface']
        marker_edge_colours = ['blue', 'yellow']

    # lm_img  : img after Land Mark
    lm_img = img.rasterize_landmarks(group=groups,
                                     line_colour='blue',
                                     marker_edge_colour=marker_edge_colours)
    return_dict['landmarked_image'] = lm_img
    export_landmark_visualization(inter_images, "landmarked", lm_img)

    print()
    return return_dict