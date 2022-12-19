import pandas as pd
import datetime
import plotly.express as px
from plotly.subplots import make_subplots

def main():
    file = 'documents/export-token-0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF.csv'
    priceFile = 'documents/aura-usd-max.csv'
    record = pd.read_csv(file)
    price = pd.read_csv(priceFile)
    lock = record[record.Method == 'Lock']
    lock['Datetime'] = pd.to_datetime(lock['UnixTimestamp'],unit='s').dt.date
    times = price['snapped_at'].str.split(' ')
    times = [x[0] for x in times]

    price['snapped_at'] = times
    price.set_index(['snapped_at'], inplace=True)

    start = datetime.datetime.strptime("2022-06-09", "%Y-%m-%d")
    end = datetime.datetime.strptime("2022-06-15", "%Y-%m-%d")
    dateGenerated = [[str((start + datetime.timedelta(days=x)).date()), price.loc["2022-06-15", "price"]] for x in range(0, (end-start).days)]
    addRow = pd.DataFrame(dateGenerated, columns = ['snapped_at', 'price'])
    addRow.set_index(['snapped_at'], inplace=True)

    price = pd.concat([price, addRow], axis=0)
    price = price.sort_index()
    lock['Quantity'] = lock['Quantity'].str.replace(',', '').astype('float64')
    lock['TVL'] = lock.apply(lambda x: (float(x[6]) * float((price.loc[x[8], "price"] if x[8] in price.index else price.loc["2022-06-15", "price"]))), axis=1)
    tvl = lock[['Datetime', 'Quantity', "TVL"]].groupby(by=["Datetime"]).sum()
    price.index.names = ['Datetime']
    tvl.index = tvl.index.astype(str)
    tvl = tvl.join(price, how='outer')

    """
    fig1 = px.line(tvl, y=tvl.columns[0:2])
    fig2 = px.line(tvl, y=tvl.price,)

    fig2.update_traces(yaxis="y2")

    subfig = make_subplots(specs=[[{"secondary_y": True}]])

    subfig.add_traces(fig1.data + fig2.data)
    subfig.layout.xaxis.title="Datetime"
    subfig.layout.yaxis.title="TVL"
    subfig.layout.yaxis2.title="Price"
    subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subfig.show()
    """
    print(tvl)
    tvl.to_csv('out/tvl.csv')

if __name__ == "__main__":
    main()