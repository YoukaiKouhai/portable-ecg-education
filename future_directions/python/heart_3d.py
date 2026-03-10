import pyqtgraph.opengl as gl
import numpy as np

class Heart3D(gl.GLViewWidget):

    def __init__(self):

        super().__init__()

        self.mesh = gl.GLMeshItem(
            vertexes=np.random.rand(100,3),
            faces=np.random.randint(0,100,(200,3)),
            smooth=True,
            color=(1,0,0,1)
        )

        self.addItem(self.mesh)

    def rotate_heart(self):

        self.mesh.rotate(2,0,1,0)