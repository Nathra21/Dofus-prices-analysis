import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

Bulkdict = {
    'Blé': 'x100',
    'Orge': 'x100',
    'Avoine': 'x100',
    'Houblon': 'x100',
    'Eau': 'x100',
    'Bave': 'x10',
    'Laine': 'x100',
    'Laine noir': 'x10',
    'Laine céleste': 'x10',  # Maybe 100
    'Volve': 'x100',
    'Cuir bouf': 'x100',
    'Cuir cdg': 'x10',
    'Graine': 'x100',
    'Poudre perl': 'x10',  # Maybe 100
    'Peau gloot': 'x100',
    'Queue chap': 'x100',
    'Cendres': 'x100',
    'Relique': 'x100',
    'Mini soin': 'x100',
    'Mini soin sup': 'x10',
    'Raide dite': 'x100',
    'Soin': 'x',
    'Ghetto raide': 'x',
    'Soin sup': 'x',
    'Clef champs': 'x',
    'Clef sable': 'x',
    'Clef bouf': 'x',
    'Clef kank': 'x',
    'Clef fant': 'x',
    'Clef scara': 'x',
    'Clef squel': 'x',
    'Clef tofus': 'x',
    'Clef gh': 'x',
    'Clef bulbes': 'x',
    'Clef bworks': 'x',
    'Clef forg': 'x',
    'Clef kwa': 'x',
    'Clef wa': 'x',
    'Clef blops': 'x',
    'Clef kanni': 'x',
    'Abreuvoir fr': 'x1',
    'Baffeur fr': 'x1',
    'Foudroyeur fr': 'x1',
    'Recycleur': 'x1'
}


headers = [
    'Blé',
    'Orge',
    'Avoine',
    'Houblon',
    'Eau',
    'Bave',
    'Laine',
    'Laine noir',
    'Laine céleste',
    'Volve',
    'Cuir bouf',
    'Cuir cdg',
    'Graine',
    'Poudre perl',
    'Peau gloot',
    'Queue chap',
    'Cendres',
    'Relique',
    'Mini soin',
    'Mini soin sup',
    'Raide dite',
    'Soin',
    'Ghetto raide',
    'Soin sup',
    'Clef champs',
    'Clef sable',
    'Clef bouf',
    'Clef kank',
    'Clef fant',
    'Clef scara',
    'Clef squel',
    'Clef tofus',
    'Clef gh',
    'Clef bulbes',
    'Clef bworks',
    'Clef forg',
    'Clef kwa',
    'Clef wa',
    'Clef blops',
    'Clef kanni',
    'Abreuvoir fr',
    'Baffeur fr',
    'Foudroyeur fr',
    'Recycleur']
quants = ['x1', 'x10', 'x100']

alchimistes = [
    'Mini soin',
    'Mini soin sup',
    'Raide dite',
    'Soin',
    'Ghetto raide',
    'Soin sup']
ressources = [
    'Eau',
    'Bave',
    'Laine',
    'Laine noir',
    'Laine céleste',
    'Volve',
    'Cuir bouf',
    'Cuir cdg',
    'Graine',
    'Poudre perl',
    'Peau gloot',
    'Queue chap',
    'Cendres',
    'Relique']

prices = pd.read_hdf('prices.hdf5', 'df')


def displayDF(x):
    # Displays a DataFrame in a pretty way
    print(tabulate(x, headers=x.columns.values))


def getmean(srs, freq='T'):
    return srs.resample(freq).sum().interpolate().mean()


def curve(items, freq='', aligned=True, database=prices, withmeans=True):
    if not isinstance(items, list):
        items = [items]
    if freq:
        database = respl(database, freq)

    for item in items:
        to_plot = database.loc[:, item]
        if aligned:
            to_plot.loc[:, 'x10'] = to_plot.loc[:, 'x10'] / 10
            to_plot.loc[:, 'x100'] = to_plot.loc[:, 'x100'] / 100

        to_plot.plot(title=item)

        if withmeans:
            mean1 = getmean(to_plot.loc[:, 'x1'])
            mean10 = getmean(to_plot.loc[:, 'x10'])
            mean100 = getmean(to_plot.loc[:, 'x100'])
            plt.axhline(y=mean1, color='C0', linestyle=':')
            plt.axhline(y=mean10, color='C1', linestyle=':')
            plt.axhline(y=mean100, color='C2', linestyle=':')
        plt.show()


def disptails(size=10, withmeans=True, items=headers, database=prices):
    # Displays the last prices of passed items.
    for item in items:
        to_display = database.loc[:, item]
        mean = getmean(database.loc[:, (item, 'x100')])
        print('\n\n' + item + '\t\t\t\t' + str(mean))
        displayDF(to_display.tail(size))


def multitails(size=10, withmeans=True, items=headers, database=prices):
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


def respl(df=prices, freq='D', interpolate=True):
    '''Resamples a date-indexed DataFrame or Series
    by first sampling up (to a minute) then down to the desired frequency.
    '''
    resampled = df.resample('T').sum().resample(freq).median()
    if interpolate:
        resampled = resampled.interpolate()
    return resampled

def getheaders(df):
    # Returns the first-level headers of a DataFrame with MultiIndex columns.
    return list(dict.fromkeys(df.columns.get_level_values(0)))

def complete(database=prices):
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
    database.fillna(method='bfill', inplace=True)

    return database


def changed(threshold=.3, database=prices, withquants=False):
    have_changed = []
    database = database.iloc[[-2, -1], :]
    for i in getheaders(database):
        for j in quants:
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


def alignmentsrs(item, bulk=2, database=prices):
    df = database.loc[:, item]
    return df.apply(lambda x: x[bulk] / (x[bulk - 1] * 10), axis=1)


def alignmentmean(item, bulk=2, database=prices):
    return getmean(alignmentsrs(item, bulk=bulk, database=database))


def alignmentpercent(item, bulk=2, database=prices):
    # Returns what proportion of the time the item's alignment is above 1
    resampled = respl(
        alignmentsrs(
            item,
            bulk=bulk,
            database=database),
        freq='T')
    return resampled.apply(lambda x: 1 if x >= 1 else 0).mean()


def dispalignment(item, bulk=2, database=prices, show=True):
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


def align(df=prices):
    '''Brings all prices down to a per-unit price,
    both for one-item and multiple-items DataFrames.
    '''
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
    mean = getmean(srs)
    return srs.apply(lambda x: x / mean)


def stdtable(show=True, database=prices):
    '''Shows a table with for each item the standard deviation of its 3 prices
    as well as both its alignments and their percent difference.
    '''
    table = []
    for item in getheaders(database):
        db = align(prices.loc[:, item])
        line = [item]
        for j in quants:
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


def dispalignmentinfo(item):
    # Shows the item's line in stdtable, and info on both its alignments.
    stdtable(database=prices.loc[:, (item, slice(None))])
    print('\n\n')
    dispalignment(item, 2, show=False)
    dispalignment(item, 1)


def alignmentstdtable():
    '''Shows a table with for each item the standard deviation of its two
    alignments and the ratio of the second alignment's std to the first's.
    '''
    table = []
    for item in headers:
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


def study(items):
    # Shows various useful pieces of information about a list of items.
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

