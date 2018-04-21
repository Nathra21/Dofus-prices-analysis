import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

prices = pd.read_hdf('prices.hdf5', 'df')

def getheaders(df):
    # Returns the first-level headers of a DataFrame with MultiIndex columns.
    return list(dict.fromkeys(df.columns.get_level_values(0)))

itemslist = getheaders(prices)


def respl(df=prices, freq='D', interpolate=True):
    '''Resamples a date-indexed DataFrame or Series by
    first sampling up (to a minute) then down to the desired frequency.
    '''
    resampled = df.resample('T').sum().resample(freq).median()
    if interpolate:
        resampled = resampled.interpolate()
    return resampled


def complete(database=prices, backfill=True):
    # Fills missing price data using other quantities and later measurements.
    for i in getheaders(database):
        database.loc[:, (i, 'x10')].fillna(
            database.loc[:, (i, 'x100')] / 10, inplace=True)
        database.loc[:, (i, 'x10')].fillna(
            database.loc[:, (i, 'x1')] * 10, inplace=True)
        database.loc[:, (i, 'x1')].fillna(
            database.loc[:, (i, 'x10')] / 10, inplace=True)
        database.loc[:, (i, 'x100')].fillna(
            database.loc[:, (i, 'x10')] * 10, inplace=True)
        database.loc[:, (i, 'x100')].fillna(
            database.loc[:, (i, 'x1')] * 100, inplace=True)
    if backfill:
        database.fillna(method='bfill', inplace=True)

    return database

def changed(threshold=.3, database=prices, withquants=False):
    '''Return the list of items whose prices have changed by more than
    the specified threshold.
    '''
    have_changed = []
    database = database.iloc[[-2, -1], :]
    for i in getheaders(database):
        for j in ['x1', 'x10', 'x100']:
            variation = (
                database.loc[:, (i, j)].diff()[-1]
                / database.loc[:, (i, j)][-2]
            )
            if abs(variation) >= threshold:
                if withquants:
                    have_changed.append((i, j, variation))
                else:
                    have_changed.append(i)
    return have_changed


def getmean(srs, freq='T'):
    # Returns the mean of a Series of prices.
    return srs.resample(freq).sum().interpolate().mean()


def alignmentsrs(item, bulk=2, database=prices):
    # Returns a Series containing an item's alignment through time.
    df = database.loc[:, item]
    return df.apply(lambda x: x[bulk] / (x[bulk - 1] * 10), axis=1)


def alignmentmean(item, bulk=2, database=prices):
    # Returns the average alignment of a specified item.
    return getmean(alignmentsrs(item, bulk=bulk, database=database))


def alignmentpercent(item, bulk=2, database=prices):
    # Returns what proportion of the time the item's alignment is above 1.
    resampled = respl(
        alignmentsrs(
            item,
            bulk=bulk,
            database=database),
        freq='T').dropna()
    return resampled.apply(lambda x: 1 if x >= 1 else 0).mean()


def align(df=prices):
    # Brings all prices down to a per-unit price.
    if isinstance(df.columns, pd.MultiIndex): # If several items are passed
        df.loc[:, (slice(None), 'x10')] = df.loc[:,
                            (slice(None), 'x10')].applymap(lambda x: x / 10)
        df.loc[:, (slice(None), 'x100')] = df.loc[:,
                            (slice(None), 'x100')].applymap(lambda x: x / 100)
    else:
        df.loc[:, 'x10'] = df.loc[:, 'x10'].apply(lambda x: x / 10)
        df.loc[:, 'x100'] = df.loc[:, 'x100'].apply(lambda x: x / 100) 
    return df


def normalizesrs(srs):
    # Normalizes a series using its mean (for comparing item variability).
    mean = getmean(srs)
    return srs.apply(lambda x: x / mean)



def displayDF(x):
    # Displays a DataFrame in a pretty way
    print(tabulate(x, headers=x.columns.values))


def curve(items, freq='', aligned=True, database=prices, withmeans=True):
    '''Plots the prices of items (list of items or single item) through time.
    aligned means that all prices will be in price per unit.
    freq allows you to resample the database first for smoothing purposes.
    By default, the three means will also be shown on the graph.
    '''
    if not isinstance(items, list):
        items = [items]
    if freq:
        database = respl(database, freq)

    for item in items:
        to_plot = database.loc[:, item]
        if aligned:
            to_plot.loc[:, 'x10'] = to_plot.loc[:, 'x10'] / 10
            to_plot.loc[:, 'x100'] = to_plot.loc[:, 'x100'] / 100

        plt.rcParams["figure.figsize"] = (11,7)
        to_plot.plot(title=item)
        if withmeans:
            mean1 = getmean(to_plot.loc[:, 'x1'])
            mean10 = getmean(to_plot.loc[:, 'x10'])
            mean100 = getmean(to_plot.loc[:, 'x100'])
            plt.axhline(y=mean1, color='C0', linestyle=':')
            plt.axhline(y=mean10, color='C1', linestyle=':')
            plt.axhline(y=mean100, color='C2', linestyle=':')
        plt.savefig('output.png')
        plt.show()


def disptails(size=10, withmeans=True, items=itemslist, database=prices):
    # Displays the last prices of the specified items.
    for item in items:
        to_display = database.loc[:, item]
        mean = getmean(complete(database, backfill=False).loc[:, (item, 'x100')])
        print('\n\n' + item + '\t\t\t\t' + str(mean))
        displayDF(to_display.tail(size))


def multitails(size=10, withmeans=True, items=itemslist, database=prices):
    # Similar to disptails but also including daily and hourly prices.
    resampled1 = respl(database, 'H')
    resampled2 = respl(database, 'D')
    for item in items:
        to_display1 = database.loc[:, item].reset_index(level=0).tail(size)
        to_display2 = resampled1.loc[:, item].reset_index(level=0).tail(size)
        to_display3 = resampled2.loc[:, item].reset_index(level=0).tail(size)
        to_display = to_display1.join(
            to_display2,rsuffix='_H').join(to_display3,rsuffix='_D')
        mean = getmean(database.loc[:, (item, 'x100')])
        print('\n\n' + item + '\t\t\t\t' + str(mean))
        displayDF(to_display)


def changetable():
    # Displays the changed items for a number of thresholds.
    for i in np.linspace(0.05, 1, 20):
        print(i)
        print(changed(i))


def dashboard(withgraphs=False, freq='', alphasort=False, database=prices):
    '''Displays information about what prices have changed by more than 30%
    between the latest two measurements, with the option of resampling the
    prices first.
    '''
    if freq:
        database = respl(database, freq)
    changedata = changed(database=database, withquants=True)
    
    if alphasort:
        changedata = sorted(changedata, key=lambda x: x[0])

    of_interest = list(dict.fromkeys([x[0] for x in changedata]))

    print('OVERVIEW\n\n')
    resampled = respl(database.loc[:, of_interest], freq='D')
    disptails(10, items=of_interest, database=resampled)

    print('\n\n\n\n\nDETAILED\n\n')
    disptails(10, items=of_interest, database=database)
    print('\n' + str(len(of_interest)) + ' items of interest:\n\n')

    infotable = [[x[0]] +
                 [x[1]] +
                 [format(x[2] * 100, '+.0f').replace('-', '- ').replace('+',
                  '+ ').ljust(5, ' ') + '\t%']
                 for x in changedata]
    print(tabulate(infotable, headers=['Item', 'Quantity', 'Variation']))

    if withgraphs:
        curve(list(dict.fromkeys(of_interest)), database=database)


def stdtable(show=True, database=prices):
    '''Shows a table with for each item the standard deviation of its 3 prices
    as well as both its alignments and their percent difference.
    '''
    table = []
    for item in getheaders(database):
        db = align(prices.loc[:, item])
        line = [item]
        for j in ['x1', 'x10', 'x100']:
            line.append(format(normalizesrs(db.loc[:, j]).std(), '.2f'))
        alignments = [alignmentmean(item, 1), alignmentmean(item, 2)]
        line.append(format(alignments[0], '.2f'))
        line.append(format(alignments[1], '.2f'))
        distance = abs(alignments[1] - alignments[0])
        line.append(
            format(distance /max(alignments),'.0%')
            + '-'
            + format(distance /min(alignments),'.0%')
            )

        table.append(line)

    if show:
        print(
            tabulate(
                table,
                headers=[
                    'Item',
                    'x1',
                    'x10',
                    'x100',
                    'Alignment 1',
                    'Alignment 2',
                    'Alignment distance']
            )
        )
    return table


def alignmentstdtable():
    '''Shows a table with for each item the standard deviation of its two
    alignments and the ratio of the second alignment's std to the first's.
    '''
    table = []
    for item in itemslist:
        line = [item]
        for bulk in [1, 2]:
            df = prices.loc[:, item]
            alignment = df.apply(
                lambda x: x[bulk] / (x[bulk - 1] * 10), axis=1)
            resampled = respl(alignment, freq='T').dropna()
            line.append(format(resampled.std(), '.2f'))
        try:
            line.append(format(float(line[2]) / float(line[1]), '.2f'))
        except BaseException:
            line.append(np.nan)
        table.append(line)
    print(tabulate(table, headers=['Item', 'Al_1 std', 'Al_2 std', 'Ratio']))


def alignmentinfo(item, bulk=2, database=prices, show=True):
    # Displays info on one of an item's two alignments and shows a graph of it.
    alignment = alignmentsrs(item, bulk=bulk, database=database)

    resampled = respl(alignment, freq='T').dropna()
    percent = resampled.apply(lambda x: 1 if x < 1 else 0).mean()

    infotext = (item
        + ' alignment '
        + str(bulk)
        + ' description (resampled by minute): \n'
        + '\n'.join(str(resampled.describe()).split('\n')[:-1])
        + '\n\nAbove 1: '
        + format(1 - percent, '.0%')
        + '\nBelow 1: '
        + format(percent, '.0%')
        )

    print(infotext + '\n')

    alignment.plot(title=item + ' alignment')
    plt.axhline(y=1, color='grey')
    if show:
        plt.show()


def dispalignment(item):
    # Shows the item's line in stdtable, and info on both its alignments.
    stdtable(database=prices.loc[:, (item, slice(None))])
    print('\n\n')
    alignmentinfo(item, 2, show=False)
    alignmentinfo(item, 1)


def study(items):
    '''Shows various useful pieces of information about a items, such as
    recent prices on different timescales and alignment information.
    '''
    if not isinstance(items, list):
        items = [items]

    print('\nALIGNMENT\n')
    table = []
    for item in items:
        table.append(
            [
                item,
                format(alignmentmean(item, 1), '.2f'),
                format(alignmentpercent(item, 1), '.0%'),
                format(alignmentmean(item, 2), '.2f'),
                format(alignmentpercent(item, 2), '.0%')
            ]
        )
    print(
        tabulate(
            table,
            headers=[
                'Item',
                'A1 mean',
                'P(A1≥1)',
                'A2 mean',
                'P(A2≥1)'
            ]
        )
    )
    print('\nLAST 14 DAYS')
    disptails(14, items=items, database=respl(prices, 'D'))
    print('\nLAST 100 HOURS')
    disptails(100, items=items, database=respl(prices, 'H'))
    print('\nDECILES\n')
    for item in items:
        table = []
        for i in range(11):
            table.append(
                [
                    i, prices.loc[:, (item, 'x1')].quantile(i /10),
                    prices.loc[:, (item, 'x10')].quantile(i /10),
                    prices.loc[:, (item, 'x100')].quantile(i /10)
                ]
            )
        print('\n' + item + '\n')
        print(tabulate(table, headers=['#', 'x1', 'x10', 'x100']))
    print('\nCURRENT PRICE')
    disptails(1, items=items)
    print('\n\n')

    curve(items)


def dispweekendtable():
    # Shows information about price differences between weekdays and weekends.
    df = complete().loc[:, (slice(None), 'x100')].applymap(lambda x: x / 100)
    df.columns = df.columns.droplevel(1)
    df['weekend'] = df.index.weekday.isin([5, 6])
    df['weekend'] = df['weekend'].apply(lambda x: 'weekend' if x else 'week')
    df = df.groupby('weekend').agg(['mean', 'median']).transpose()
    df['diff'] = df.apply(
        lambda x: format(
            (x[1] - x[0]) / x[0],
            '.0%'),
        axis=1)
    df['week'] = df['week'].apply(lambda x: format(x, '.2f'))
    df['weekend'] = df['weekend'].apply(lambda x: format(x, '.2f'))
    with pd.option_context('display.max_rows', 1000):
        print(df)



if __name__ == "__main__":
    dashboard()
