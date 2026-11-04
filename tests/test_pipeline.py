import pandas as pd
from src.pipeline import clean_orders, invoice_table, make_rfm, cohort_retention, monthly_kpis

def example():
    return pd.DataFrame([
      ['100','A','Pen',2,'2020-01-01',5,1,'UK'],
      ['100','B','Book',1,'2020-01-01',10,1,'UK'],
      ['101','A','Pen',1,'2020-02-02',5,1,'UK'],
      ['102','B','Book',2,'2020-02-05',10,2,'UK'],
      ['C103','A','Pen',-1,'2020-02-06',5,1,'UK'],
      ['104','A','Pen',1,'2020-02-08',0,3,'UK'],
      ['105','A','Pen',1,'2020-02-09',5,None,'UK'],
    ],columns=['Invoice','StockCode','Description','Quantity','InvoiceDate','Price','Customer ID','Country'])

def test_cleaning_and_report():
    raw=example()
    raw=pd.concat([raw,raw.iloc[[0]]],ignore_index=True)
    lines, report=clean_orders(raw)
    assert len(lines)==4
    assert report['exact_duplicate_rows']==1
    assert report['cancellation_rows']==1
    assert set(lines.customer_id)=={'1','2'}
    assert lines.revenue.sum()==45

def test_invoice_aggregation_and_kpi():
    lines,_=clean_orders(example())
    orders=invoice_table(lines)
    assert len(orders)==3
    assert orders.loc[orders.invoice=='100','revenue'].iloc[0]==20
    k=monthly_kpis(orders)
    assert k.loc[k.month=='2020-01','orders'].iloc[0]==1

def test_cohort_retention():
    lines,_=clean_orders(example())
    cohort=cohort_retention(invoice_table(lines))
    jan=cohort[cohort.cohort_month=='2020-01']
    assert jan.loc[jan.period_number==0,'retention_rate'].iloc[0]==1
    assert jan.loc[jan.period_number==1,'retention_rate'].iloc[0]==1

def test_rfm_nonempty():
    lines,_=clean_orders(example())
    rfm=make_rfm(invoice_table(lines))
    assert len(rfm)==2
    assert set(rfm.segment).issubset({'Champions','At Risk','New / Promising','Hibernating','Regular'})
