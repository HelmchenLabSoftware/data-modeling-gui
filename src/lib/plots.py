import seaborn as sns
from statsmodels.tsa.stattools import pacf, acf


def plot1D(axes, xLabels, yLabels, dataLabel, dataDict):
    if len(xLabels) != 1:
        return (1, 'Plot1D needs 1 x-argument, got' + str(len(xLabels)))
    else:
        xLabel = xLabels[0]

    axes.clear()
    for yLabel in yLabels:
        axes.plot(dataDict[dataLabel][xLabel], dataDict[dataLabel][yLabel], label=yLabel)
    axes.set_xlabel(xLabel)
    axes.legend()

    return (0, )


def plotACF(axes, xLabels, yLabels, dataLabel, dataDict):
    axes.clear()

    axes.axhline(y=0, linestyle='--', color='pink')
    for yLabel in yLabels:
        rezACF = acf(dataDict[dataLabel][yLabel])
        axes.plot(rezACF, '.--', label=yLabel)

    axes.set_title('Autocorrelation')
    axes.legend()

    return (0, )


def plotPACF(axes, xLabels, yLabels, dataLabel, dataDict):
    axes.clear()

    axes.axhline(y=0, linestyle='--', color='pink')
    for yLabel in yLabels:
        rezACF = pacf(dataDict[dataLabel][yLabel])
        axes.plot(rezACF, '.--', label=yLabel)

    axes.set_title('Partial Autocorrelation')
    axes.legend()

    return (0, )


def plotBox(axes, xLabels, yLabels, dataLabel, dataDict):
    axes.clear()

    if len(xLabels) != 1:
        return (1, 'Plot1D needs 1 x-argument, got' + str(len(xLabels)))
    else:
        xLabel = xLabels[0]

    if len(yLabels) != 1:
        return (1, 'Plot1D needs 1 y-argument, got' + str(len(yLabels)))
    else:
        yLabel = yLabels[0]

    sns.boxplot(ax=axes, data=dataDict[dataLabel], x=xLabel, y=yLabel)
    return (0, )


def plotViolin(axes, xLabels, yLabels, dataLabel, dataDict):
    axes.clear()

    if len(xLabels) != 1:
        return (1, 'Plot1D needs 1 x-argument, got' + str(len(xLabels)))
    else:
        xLabel = xLabels[0]

    if len(yLabels) != 1:
        return (1, 'Plot1D needs 1 y-argument, got' + str(len(yLabels)))
    else:
        yLabel = yLabels[0]

    sns.violinplot(ax=axes, data=dataDict[dataLabel], x=xLabel, y=yLabel)
    return (0, )