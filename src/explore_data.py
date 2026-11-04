"""First notebook-free exploration of the original Online Retail II workbook."""
from pathlib import Path
import pandas as pd

DATA_PATH = Path('data/raw/online_retail_II.xlsx')


def main():
    # sheet_name=None returns a dictionary containing every Excel sheet.
    sheets = pd.read_excel(DATA_PATH, sheet_name=None)
    # .values() extracts the DataFrames; concat joins their rows.
    df = pd.concat(sheets.values(), ignore_index=True)

    print('Dimensions :', df.shape)
    print('\nColonnes :')
    print(df.columns.tolist())
    print('\nPremières lignes :')
    print(df.head())
    print('\nValeurs manquantes :')
    print(df.isnull().sum())
    print('\nDoublons :', df.duplicated().sum())
    print('\nPériode :')
    print(df['InvoiceDate'].min())
    print(df['InvoiceDate'].max())


if __name__ == '__main__':
    main()
