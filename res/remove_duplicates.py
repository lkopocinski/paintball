with open("/mnt/tbstorage/lukasz/data_set/paint_ball/poli_mono_select.txt.csv_sim.csv") as f:
    for line in f:
        line = line.strip()
        s, t, w = line.split(';')

        if s != t:
            print line

