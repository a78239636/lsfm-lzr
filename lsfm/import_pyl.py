from pathlib import Path
from plyfile import PlyData,PlyProperty, PlyListProperty
import numpy as np
from lsfm import landmark_mesh, landmark_and_correspond_mesh
from menpo.shape import ColouredTriMesh, TexturedTriMesh, TriMesh, PointCloud
import lsfm.io as lio
from lsfm.landmark_my import landmark_mesh_my

def headline(string):
     print("\n\n----------{0}----------\n".format(string))

def generate_trilist(points):
     from scipy.spatial import Delaunay  # expensive
     trilist = Delaunay(points).simplices
     return trilist

def import_obj():
     james =  Path('/home/li_gang/TestFile/NewInput2/james.obj')
     man = Path('/home/li_gang/TestFile/NewInput2/man.obj')
     obj_path = man
     mesh = lio.import_mesh(obj_path)
     print("mesh = ", mesh)
     landmark_mesh(mesh)

def import_full_ply(filename, verbose=True):
     file_dir = str(filename) # 文件的路径
     print("ply file name = ", file_dir)

     from menpo3d.io.input.mesh.base import vtk_ensure_trilist
     import vtk
     ply_importer = vtk.vtkPLYReader()
     ply_importer.SetFileName(str(file_dir))
     ply_importer.Update()
     polydata = ply_importer.GetOutput()
     trilist = np.require(vtk_ensure_trilist(polydata), requirements=['C'])

     plydata = PlyData.read(file_dir)
     vertexs = plydata['vertex']

     if (verbose is True):
          headline("Meta Info of Ply File")
          for element in plydata.elements:
               print("Meta = {0}".format( element.name))
          print(vertexs.dtype)
          print("This is TriList : ", trilist)

     points_list = []
     colors_list = []
     for verx in vertexs:
         points_list.append( ( verx[0], verx[1], verx[2] ) )
         colors_list.append( ( verx[3], verx[4], verx[5] ) )

     nd_point = np.array(points_list, dtype=np.float64)
     nd_color = np.array(colors_list, dtype=np.uint8)

     if (verbose is True):
          headline("Ndarray INFO")
          print("Point shape = {0} \nColor shape = {1}".format(nd_point.shape, nd_color.shape))


     mesh = ColouredTriMesh(nd_point, trilist=trilist, colours=nd_color)
     if (verbose is True):
          headline("Mesh INFO")
          print(mesh)
          print("color Shape =", mesh.colours.shape)
          print("tri Shape = ",  mesh.trilist.shape)
          print("tri List = ", mesh.trilist)
     return mesh

if __name__ == '__main__':
    opt1 = '/home/li_gang/TestFile/HLSInput/face-reconstruction-template.ply'
    cmesh = import_full_ply(opt1)
    landmark_mesh_my(cmesh)
#import_obj()