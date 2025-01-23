from .road_segment import RoadSegment

class RoadGrid():
    def __init__(self, res_x, res_y, cell_size, segments: list[RoadSegment]):
        self.grid_dict = dict()
        self.res_x = res_x
        self.res_y = res_y
        self.cell_size = cell_size
        for segment in segments:
            self.insert_segment(segment)
        self.compare(segments)


    def insert_segment(self, segment: RoadSegment):
        cell_0 = self.get_cell(segment.point_0)
        cell_1 = self.get_cell(segment.point_1)

        if not self.grid_dict.get(cell_0):
            self.grid_dict[cell_0] = []

        if not self.grid_dict.get(cell_1):
            self.grid_dict[cell_1] = []

        if segment not in self.grid_dict[cell_0]:
            self.grid_dict[cell_0].append(segment)
        if segment not in self.grid_dict[cell_1]:
            self.grid_dict[cell_1].append(segment)
    
    def get_cell(self, point):

        cell_x = int(point[0]/self.cell_size)
        cell_y = int(point[1]/self.cell_size)

        return (cell_x, cell_y)
    
    def compare(self, segments: list[RoadSegment]):
        amount = len(segments)
        index = 0
        for segment in segments:
            
            print('\r', end='', flush=True)
            print(" - Comparing: " + str(index) + "/" + str(amount), end = ' ',flush=True)
            index += 1

            cell = self.get_cell(segment.point_0)
            if segment in self.grid_dict[cell]:
                self.grid_dict[cell].remove(segment)
            for compare_segment in self.grid_dict[cell]:
                if compare_segment == segment:
                    continue
                if compare_segment.point_0 == segment.point_0:
                    segment.neighbours_0.append(compare_segment)
                    compare_segment.neighbours_0.append(segment)
                if compare_segment.point_1 == segment.point_0:
                    segment.neighbours_0.append(compare_segment)
                    compare_segment.neighbours_1.append(segment)

            cell = self.get_cell(segment.point_1)
            if segment in self.grid_dict[cell]:
                self.grid_dict[cell].remove(segment)
            for compare_segment in self.grid_dict[cell]:
                if compare_segment == segment:
                    continue
                if compare_segment.point_0 == segment.point_1:
                    segment.neighbours_1.append(compare_segment)
                    compare_segment.neighbours_0.append(segment)
                if compare_segment.point_1 == segment.point_1:
                    segment.neighbours_1.append(compare_segment)
                    compare_segment.neighbours_1.append(segment)