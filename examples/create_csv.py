import csv

path = "backup.csv"
with open(path,'w') as f:
    csv_write = csv.writer(f)
    csv_head = ["max_moving_frame", "max_variance", "max_therhold_pixel_num", "max_R", "is_fall"]
    csv_write.writerow(csv_head)
