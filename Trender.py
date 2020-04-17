import pandas as pd
import numpy as np
from optparse import OptionParser
from pytrends.request import TrendReq
from itertools import combinations
from string import ascii_lowercase
import time
from collections import Counter
import random
import plotly.graph_objects as go
import plotly.express as px

def interactive_plot(df, x, ys):
    """
    Create linegraph with one or more variables
    
    Parameters:
        df: The dataframe containing the data to plot
        x: the value to plot on the x-axis
        y: list of strings with the column names to plot
    """
    fig = go.Figure()

    if not isinstance(ys, list):
        ys = [ys]
    
    for var in ys:
        fig.add_trace(go.Scatter(x=df[x], y=df[var],
                        mode='lines',
                        name=var))

    # Setting theme and default hovermode to compare groups instead of inspecting a single one
    fig.update_layout(template = "simple_white",
                      hovermode = "x")
    fig.show()
    return fig

class InputError(Exception):
    """Exception raised for errors in the input.
    """
    def __init__(self, message):
        self.message = message

class TermTrend:
    def __init__(self, term, trend):
        self.term = term
        self.trend = trend
    def setTrend(self, trend):
        self.trend = trend
    def __add__(self, a):
        try:
            if type(a) == int:
                return self
        except ValueError:
            print("you must increment by an integer scalar.\n")
    def __key(self):
        return self.term
    def __hash__(self):
        return hash(self.__key())
    def __eq__(self, othr):
        return (isinstance(othr, type(self)) and self.term == othr.term)

def getCombinations(terms):
    perms = [i for i in combinations(terms, r = 2)]
    return perms

def faceoff(term1, term2, trend):
    #get highest node for both.
    #Compare their values in the faceoff
    #winner get's an extract count.  
    if 100 in trend[term1.term].to_list():
        return term1
    else:
        return term2

def getScaleFactor(combined_trend, trend2):
    #What is trend2 100 value in the combined trend chart?
    #Find the index in the second term in which the value is 100
    #find what the value is in the combined trend
    index = np.where(trend2.trend.iloc[:,0] == 100)[0][0]
    index = index.item()
    return combined_trend.loc[combined_trend.index[index], trend2.term].item()

class Trender:
    '''
    class that keeps track of terms
    knows how to plot a term
    '''
    def __init__(self, terms, daterange, locality):
        self.terms = []
        self.update = True
        self.pytrend = TrendReq()
        self.daterange = daterange
        self.locality = locality
        if daterange == None:
            daterange = "today 12-m"
        if locality == None:
            locality == "DK"
        for term in terms:
            self.terms.append(TermTrend(term, self._getTrend([term], self.daterange, self.locality)))

    def plot(self, plotout):
        df = self.combinedtrend.copy().reset_index()
        x = list(df.columns)[0]
        ys = list(df.columns)[1:]
        plot = interactive_plot(df, x, ys)
        #print("Saving plot...")
        #if plotout == None:
        #    plotout = "plot.png"
        #plot.write_image(plotout)

    def update_trends(self):
        self.update = True
        self.trends()

    def trends(self):
        if self.update:
            #returns trend
            term_faceoff = []
            combinations_list = getCombinations(self.terms)
            tmp_combined_trend = dict()
            for comb in combinations_list:
                combined_trend = self._getTrend([comb[0].term, comb[1].term], self.daterange, self.locality)
                term = faceoff(comb[0], comb[1], combined_trend)
                tmp_combined_trend[(comb[0], comb[1])] = combined_trend
                term_faceoff.append(term)
            self.update = False
            term_faceoff = list(Counter(term_faceoff))

            #create dataframe
            self.combinedtrend = pd.DataFrame(index=term_faceoff[0].trend.index.copy(), data={term_faceoff[0].term:term_faceoff[0].trend.iloc[:,0]})
            scalefactor_list = []
            for i in range(len(term_faceoff) - 1):
                combined_trend = None
                if((term_faceoff[i], term_faceoff[i+1])) in tmp_combined_trend.keys():
                    combined_trend = tmp_combined_trend[(term_faceoff[i], term_faceoff[i+1])]
                else:
                    combined_trend = tmp_combined_trend[(term_faceoff[i+1], term_faceoff[i])]
                scalefactor = getScaleFactor(combined_trend, term_faceoff[i+1])
                scalefactor_list.append(scalefactor)
                scaled_trend = term_faceoff[i+1].trend.iloc[:,0]
                print(scaled_trend.head())
                for scale in scalefactor_list:
                    scaled_trend = scaled_trend.apply(lambda x: x / 100 * scale)
                print(scaled_trend.head())
                self.combinedtrend[term_faceoff[i+1].term] = scaled_trend
                print(self.combinedtrend.head())
        else:
            return self.combinedtrend

    def _getTrend(self, payload, daterange, locality):
        payload_built = False
         
        while not payload_built:
            try:
                self.pytrend.build_payload(kw_list=payload, timeframe=daterange, geo=locality)
                payload_built = True
            except:
                print("Rebuilding payload...")
                time.sleep(random.randint(1,4))
                pass
        
        results = None
        tries = 0
        print("Fetching trend:", payload)
        while results is None:
            try:
                results = self.pytrend.interest_over_time()
                results.to_csv("out.csv")
            except:
                print("Retrying...")
                tries += 1
                time.sleep(random.randint(1,4))
                if tries >= 5:
                    print("Error. Could not connect to server instance.")
                else:
                    pass
        return results

def main():
    parser = OptionParser()
    parser.add_option("-i", "--terms", dest="input",
                    action="store", type="string",
                    help="txt file with newline separated search terms", metavar="INPUT")
    parser.add_option("-d", "--daterange", dest="daterange", action="store",
                    type="string",
                    help="The range of dates for which to fetch trend data", metavar="DATERANGE")
    parser.add_option("-l", "--locality", dest="locality", action="store",
                type="string",
                help="2 letter locale from whence to fetch the data.", metavar="GEO")
    parser.add_option("-e", "--interactive", dest="interactive",
                    action="store_false",
                    help="output interactive plot in browser", metavar="INTER")
    parser.add_option("-o", "--output", dest="plot_out", action="store",
                type="string",
                help="output path for plot", metavar="OUTPUT")
    (options, _) = parser.parse_args()

    if not options.input:
        raise InputError("Input directory must be specified.")
    terms = [x.strip() for x in open(options.input).readlines()]
    trender = Trender(terms, options.daterange, options.locality)
    trender.trends()
    trender.plot(options.plot_out)

if __name__ == "__main__":
    main()
