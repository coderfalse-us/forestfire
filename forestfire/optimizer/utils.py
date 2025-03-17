def e_d(picker_location,item_location):
        x1, y1 = picker_location
        x2, y2 = item_location
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance

def walkway_from_condition(value, left_walkway, right_walkway):
      return left_walkway if value % 20 == 0 else right_walkway