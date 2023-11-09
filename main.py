import data_collection.data_collection as dc
import data_collection.match_collection as mc
import data_analysis.data_preprocessing as dp
import argparse

# Parse arguments
# Number of cores to use
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--cores', type=int, default=1,
                    help='Number of cores to use')
parser.add_argument('--update', action='store_true',
                    help='Update the json files')
parser.add_argument('--filter', action='store_true',
                    help='Filter the players')
parser.add_argument('--load', action='store_true',
                    help='Load the matches')
parser.add_argument('--region', type=str, nargs='+',
                    help='Region to load the matches from [asia, global, eu, jpn, kor]')
parser.add_argument('--preprocess', action='store_true',
                    help='Preprocess the data')
parser.add_argument('--train', action='store_true',
                    help='Train the model')
args = parser.parse_args()

if __name__ == '__main__':
    if args.update:
        dc.update_json()
    if args.load:
        mc.load_matches(args.region)
    if args.filter:
        dc.load_players(args.cores)
    if args.preprocess:
        dp.data_preprocessing()
        dp.label_encoding()
        dp.shuffle()

