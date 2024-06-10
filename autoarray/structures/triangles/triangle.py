from functools import cached_property
from typing import Tuple


class Point(Tuple[float, float]):
    def __new__(cls, y: float, x: float):
        return super().__new__(cls, (y, x))

    def __str__(self):
        return f"<Point({self[0]}, {self[1]})>"

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        return Point(self[0] + other[0], self[1] + other[1])

    def __sub__(self, other):
        return Point(self[0] - other[0], self[1] - other[1])

    def __mul__(self, other):
        return Point(self[0] * other, self[1] * other)

    def __truediv__(self, other):
        return Point(self[0] / other, self[1] / other)


class Triangle:
    def __init__(self, *points: Tuple[float, float]):
        """
        Represents an equilateral triangle in the image plane.

        Parameters
        ----------
        points
            The three vertices of the triangle.
        """
        assert len(points) == 3
        self.points = tuple(Point(*point) for point in points)

    def __str__(self):
        return f"<Triangle({self.points})>"

    def __repr__(self):
        return str(self)

    def contains(self, point: Tuple[float, float], buffer: float = 0.0) -> bool:
        """
        Determine if a point is contained within the triangle.
        """
        y1, x1 = self.points[0]
        y2, x2 = self.points[1]
        y3, x3 = self.points[2]
        y, x = point

        denominator = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)

        a = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / denominator
        b = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / denominator
        c = 1 - a - b

        lower = -buffer
        upper = 1 + buffer

        return lower <= a <= upper and lower <= b <= upper and lower <= c <= upper

    @cached_property
    def mid_1(self):
        return self.midpoint(0, 1)

    @cached_property
    def mid_2(self):
        return self.midpoint(1, 2)

    @cached_property
    def mid_3(self):
        return self.midpoint(2, 0)

    def subdivide(self) -> Tuple["Triangle", "Triangle", "Triangle", "Triangle"]:
        """
        Subdivide the triangle into four smaller, equally sized triangles.
        """
        return (
            Triangle(self.points[0], self.mid_1, self.mid_3),
            Triangle(self.mid_1, self.points[1], self.mid_2),
            Triangle(self.mid_3, self.mid_2, self.points[2]),
            Triangle(self.mid_1, self.mid_2, self.mid_3),
        )

    @cached_property
    def subdivision_points(
        self,
    ) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        """
        The midpoints of the triangle's edges which are used to compute the subtriangles.
        """
        return self.mid_1, self.mid_2, self.mid_3

    def midpoint(self, i: int, j: int) -> Point:
        """
        Compute the midpoint of the line segment between two vertices of the triangle.

        Parameters
        ----------
        i
            The index of the first vertex.
        j
            The index of the second vertex.

        Returns
        -------
        The midpoint of the line segment.
        """
        return self.points[i] + (self.points[j] - self.points[i]) / 2

    @property
    def mean(self):
        return (
            sum(point[0] for point in self.points) / 3,
            sum(point[1] for point in self.points) / 3,
        )

    @property
    def neighbourhood(self) -> Tuple["Triangle", "Triangle", "Triangle", "Triangle"]:
        """
        The four triangles that share an edge with the triangle (including this triangle).

        Related to the subdivide method in that the central triangle in a subdivided set of triangles has
        neighbours equivalent to the full subdivision of the parent triangle.
        """
        return (
            self,
            Triangle(
                self.points[1] + self.points[2] - self.points[0],
                self.points[1],
                self.points[2],
            ),
            Triangle(
                self.points[0] + self.points[2] - self.points[1],
                self.points[0],
                self.points[2],
            ),
            Triangle(
                self.points[0] + self.points[1] - self.points[2],
                self.points[0],
                self.points[1],
            ),
        )

    def __eq__(self, other):
        return set(self.points) == set(other.points)

    def __hash__(self):
        return hash(tuple(self.points))
