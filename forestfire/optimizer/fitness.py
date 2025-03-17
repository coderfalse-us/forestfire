from forestfire.optimizer.utils import e_d, walkway_from_condition
def calc_distance_with_shortest_route(picker_locations, item_locations, emptypop_position, orders_assign, picktasks, stage_result):

      left_walkway=15
      right_walkway=105

      order_indices = [[] for _ in range(len(picker_locations))] 
      assignments = [[] for _ in range(len(picker_locations))]
      for index, picker_index in enumerate(emptypop_position):
          assignments[picker_index].extend(orders_assign[index])
          order_indices[picker_index].append(index) 
      sorted_data = [[] for _ in range(NUM_PICKERS)]


      final_result = []
      seen = set()  # A set to track duplicates

      for i in range(len(picker_locations)):
          data = assignments[i]
          indices = order_indices[i]
          taskids = [picktasks[i] for i in indices]
            

          for taskid in taskids:
            if taskid[0] not in seen:
                seen.add(taskid[0])
                final_result.extend(stage_result.get(taskid[0], None))
          quotients = {}
          for item in data:
              quotient = item[1] // 10
              if quotient not in quotients:
                  quotients[quotient] = []
              quotients[quotient].append(item)

          for quotient in sorted(quotients.keys()):
              group = quotients[quotient]
              if quotient % 2 != 0:  # Even
                  sorted_group = sorted(group, key=lambda x: x[0], reverse=True)
              else:  # Odd
                  sorted_group = sorted(group, key=lambda x: x[0])
              sorted_data[i].extend(sorted_group)
        

      r_flag=[0]*10

      for p in range(len(picker_locations)):
        if not sorted_data[p]:
          continue

        dist1_walkway = walkway_from_condition(sorted_data[p][0][1], left_walkway, right_walkway)
        dist2_walkway = walkway_from_condition(sorted_data[p][-1][1], left_walkway, right_walkway)

        dist1 = e_d(picker_locations[p], (dist1_walkway, sorted_data[p][0][1]))
        dist2 = e_d(picker_locations[p], (dist2_walkway, sorted_data[p][-1][1]))


        if picker_locations[p][0] < 50:
          if dist1<dist2:
            sorted_data[p].insert(0,picker_locations[p])
            if sorted_data[p][1][1]%20 == 0:
              sorted_data[p].insert(1,(left_walkway,sorted_data[p][1][1]))
            else :
              sorted_data[p].insert(1,(left_walkway,sorted_data[p][1][1]-step_between_rows))
          else:
            sorted_data[p]=sorted_data[p][::-1]
            r_flag[p]=1
            sorted_data[p].insert(0,picker_locations[p])
            if sorted_data[p][1][1]%20 ==0:
              sorted_data[p].insert(1,(left_walkway,sorted_data[p][1][1]))
            else:
              sorted_data[p].insert(1,(left_walkway,sorted_data[p][1][1]+step_between_rows))
        else:
          if dist1<dist2:
            if sorted_data[p][0][1]%20 != 0:
              sorted_data[p].insert(0,picker_locations[p])
              sorted_data[p].insert(1,(right_walkway,sorted_data[p][1][1]))
            else:
              sorted_data[p].insert(0,picker_locations[p])
              sorted_data[p].insert(1,(right_walkway,sorted_data[p][1][1]-step_between_rows))
          else:
            r_flag[p]=1
            if sorted_data[p][-1][1]%20 !=0:
              sorted_data[p]=sorted_data[p][::-1]
              sorted_data[p].insert(0,picker_locations[p])
              sorted_data[p].insert(1,(right_walkway,sorted_data[p][1][1]))
            else:
              sorted_data[p]=sorted_data[p][::-1]
              sorted_data[p].insert(0,picker_locations[p])
              sorted_data[p].insert(1,(right_walkway,sorted_data[p][1][1]+step_between_rows))

         # print(r_flag)
      l=[]

      for j,k in enumerate(sorted_data):
        if not k:
              l.append([])
              continue
        l1 = k.copy()

        i = 1
        while i < len(l1) - 1:
            if l1[i][1] != l1[i + 1][1]:
                if l1[i][1] % 20 == 0:
                    if l1[i + 1][1] % 20 != 0:

                        l1.insert(i + 1, (right_walkway, l1[i][1]))
                        l1.insert(i + 2, (right_walkway, l1[i + 2][1]))
                        i += 2
                    else:
                      if r_flag[j]==0:
                        l1.insert(i + 1, (right_walkway, l1[i][1]))
                        l1.insert(i + 2, (right_walkway, (l1[i + 1][1] + step_between_rows)))
                        l1.insert(i + 3, (left_walkway, (l1[i + 2][1])))
                        l1.insert(i + 4, (left_walkway, l1[i + 4][1]))
                        i += 4
                      else:
                        l1.insert(i + 1, (right_walkway, l1[i][1]))
                        l1.insert(i + 2, (right_walkway, (l1[i + 1][1] - step_between_rows)))
                        l1.insert(i + 3, (left_walkway, (l1[i + 2][1])))
                        l1.insert(i + 4, (left_walkway, l1[i + 4][1]))
                        i += 4
                else:
                    if l1[i + 1][1] % 20 == 0:
                        l1.insert(i + 1, (left_walkway, l1[i][1]))
                        l1.insert(i + 2, (left_walkway, l1[i + 2][1]))
                        i += 2
                    else:
                      if r_flag[j]==0:
                        l1.insert(i + 1, (left_walkway, l1[i][1]))
                        l1.insert(i + 2, (left_walkway, (l1[i + 1][1] + step_between_rows))) #i+1 needed
                        l1.insert(i + 3, (right_walkway, (l1[i + 2][1])))#i+2
                        l1.insert(i + 4, (right_walkway, l1[i + 4][1]))
                        i += 4
                      else:
                        l1.insert(i + 1, (left_walkway, l1[i][1]))
                        l1.insert(i + 2, (left_walkway, (l1[i + 1][1] - step_between_rows)))
                        l1.insert(i + 3, (right_walkway, (l1[i + 2][1])))
                        l1.insert(i + 4, (right_walkway, l1[i + 4][1]))
                        i += 4
            else:
                i += 1
        l1.extend(final_result)
        print(final_result)
        l.append(l1)

      total_cost = 0
      individual_costs = []
      for points in l:
          list_cost = 0

          for i in range(len(points) - 1):
              x1, y1 = points[i]
              x2, y2 = points[i + 1]
              distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
              list_cost += distance

          individual_costs.append(list_cost)
          total_cost += list_cost

      return total_cost,l,assignments