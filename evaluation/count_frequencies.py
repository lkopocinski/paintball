import sys
import pandas as pd



def main():
    df = pd.read_csv(sys.argv[1], names=['term', 'distance'])
    df = df[df['distance'] != -1]
    df = df.groupby('term').min()
    #df = df.distance.apply(lambda x: round(x, 0))

    df = df.distance
    df = df.value_counts()
    df = df.sort_index()
    print df

if __name__ == '__main__':
    main()
