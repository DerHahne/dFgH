import sqlite3
import time

# get the sum of all elevator movements
def get_all_elems():
  conn = sqlite3.connect('elevator.db')
  c = conn.cursor()
  query = 'SELECT COUNT(*) FROM call_log ORDER BY dtime ASC;';
  c.execute(query)
  value = c.fetchone()[0]
  conn.close()
  return value

# builds a matrix with the following values {from_floor, to_floor, relative support of the route)
def build_sup_matrix(elem_sum):
  conn = sqlite3.connect('elevator.db')
  c = conn.cursor()
  i = 1000
  arr = []
  while i <= 20000:
    j = i + 1000
    while j <= 20000:
      query = 'SELECT COUNT(*) FROM call_log WHERE from_floor = %s and to_floor = %s;'%(i, j)
      c.execute(query)
      count = c.fetchone()[0]
      rel_support = float(count)/float(elem_sum)*100
      arr.append([i, j, rel_support])
      #print('%s -> %s : %s'%(i, j, rel_support))
      j = j + 1000
    i = i + 1000
  conn.close()
  return arr

# returns the array key of the most common used elevator route
def get_max_set(matrix):
  max_val = 0.0;
  max_key = 0
  for i in range(0, len(matrix)):
    if(float(matrix[i][2])>max_val):
      max_val = float(matrix[i][2])
      max_key = i
  return max_key


#returns the most common used start floor
def get_mostc_start_floor():
  conn = sqlite3.connect('elevator.db')
  c = conn.cursor()
  best_floor = 0;
  max_count = 0;
  i = 1000
  while i <= 20000:
    query = 'SELECT COUNT(*) FROM call_log WHERE from_floor = %s;'%(i)
    c.execute(query)
    count = c.fetchone()[0]
    if(max_count<count):
      max_count = count
      best_floor = i
    i = i +1000
  conn.close()
  return best_floor

#returns the most common used destination floor
def get_mostc_dest_floor():
  conn = sqlite3.connect('elevator.db')
  c = conn.cursor()
  best_floor = 0;
  max_count = 0;
  i = 1000
  while i <= 20000:
    query = 'SELECT COUNT(*) FROM call_log WHERE to_floor = %s;'%(i)
    c.execute(query)
    count = c.fetchone()[0]
    if(max_count<count):
      max_count = count
      best_floor = i
    i = i +1000
  conn.close()
  return best_floor

# Log statistics to the database Input: route(array{from, to, support}, most used start floor, most used destination floor, sum of all elevator calls)
def log_stats(route, sfloor, dfloor, mov_sum):
  conn = sqlite3.connect('elevator.db')
  c = conn.cursor()
  c.execute('INSERT INTO stats (sfloor, dfloor, calls, r_start, r_dest, r_sup) VALUES (%s, %s, %s, %s, %s, %s);'%(str(sfloor), str(dfloor), str(mov_sum), str(route[0]), str(route[1]), str(route[2])))
  conn.commit()
  conn.close()
  return True

def freq_detector():
  num = get_all_elems()
  matrix = build_sup_matrix(num)
  route = matrix[get_max_set(matrix)]
  sfloor = get_mostc_start_floor()
  dfloor = get_mostc_dest_floor()
  log_stats(route, sfloor, dfloor, num)

  print 'Ammount of elevator movements: %s'%num
  print 'Most common used route: %s'%route
  print 'Most common starting floor: %s'%sfloor
  print 'Most common destination floor: %s'%dfloor

  time.sleep(10)

def freq_detector_muted():
  num = get_all_elems()
  matrix = build_sup_matrix(num)
  route = matrix[get_max_set(matrix)]
  sfloor = get_mostc_start_floor()
  dfloor = get_mostc_dest_floor()
  log_stats(route, sfloor, dfloor, num)

  time.sleep(10)
